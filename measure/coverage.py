#!/usr/bin/env python3
"""The coverage map: which conversation tests guard which parts of the skill.

Run from the repo:  python3 measure/coverage.py [BASE HEAD] [--json]

With no commits, prints every test with the lines of SKILL.md it guards and
its group, then the parts of SKILL.md that no test guards (PLAN.md, section 5).
With BASE and HEAD, prints the tests a change between them can reach
(PLAN.md, section 4): those whose part of SKILL.md changed, and those whose
group's materials changed. Standard library only.

A test's part is read from its case.yaml, from the quoted name in "Guards
"..."": a heading of SKILL.md, or a bold phrase that opens a paragraph or a
list item. A test that quotes no part is listed under OVERRIDES by hand.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.environ.get("GATE_REPO") or os.path.dirname(HERE))
EVALS = "measure/evals"
SKILL_MD = "skills/apologetics-boot-camp/SKILL.md"
SOPS = "skills/apologetics-boot-camp/sops/"
FIXED = "skills/apologetics-boot-camp/fixed/"
# The site's copy of the thought-and-word rules index (the true copy is in faadiallop/foundations).
RULES = "site/prompts/thought-and-word-rules.md"

# Words that show which group a test's conversation is with, and the file names of that group.
GROUPS = {
    "islam": (r"\bMuslim|\bQur'?an|\bIslam|\bInjil", "islam"),
    "jehovahs-witnesses": (r"Jehovah's Witness|\bJWs?\b|Watchtower|Kingdom Hall", "jehovahs-witnesses"),
    "jewish-people": (r"\bJewish\b|\brabbi|\bTalmud|Isaiah 53", "jewish-people"),
    "atheism": (r"\batheis", "atheism"),
    "icon-veneration": (r"\bicons?\b|\bvenerat", "icon-veneration"),
}
# Files every group's training reads, so a change to them reaches every test.
SHARED = {SOPS + "00-overview-and-template.md", SOPS + "01-methodology-questioning-them-to-death.md",
          SOPS + "20-response-bank.md", SOPS + "21-training-plans.md",
          RULES}
# Tests whose case.yaml names its part without quoting it: the words to look for in SKILL.md.
OVERRIDES = {"steamroller-steps-in-order": ["steamroller"]}


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def read(path, rev=None):
    if rev:
        try:
            return git("show", f"{rev}:{path}")
        except subprocess.CalledProcessError:
            return ""
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------- the parts of SKILL.md

def parts(text):
    """[(name, first, last, level)]: every heading and every bold opening, with its line span.
    A heading runs to the next heading at its level or above; a bold opening runs to the next
    bold opening or heading."""
    lines = text.split("\n")
    marks = []
    for i, line in enumerate(lines, 1):
        h = re.match(r"(#{2,3}) (.+)", line)
        b = re.match(r"\s*(?:[-*]|\d+\.)?\s*\*\*(.+?)\*\*", line)
        if h:
            marks.append((re.sub(r"^[A-Z]′?\.\s+|^\d+\.\s+", "", h.group(2)).strip(), i, len(h.group(1))))
        elif b:
            marks.append((b.group(1).strip(" .:,"), i, 9))
    out = []
    for k, (name, start, level) in enumerate(marks):
        end = len(lines)
        for name2, start2, level2 in marks[k + 1:]:
            if level2 <= level or (level == 9):
                end = start2 - 1
                break
        out.append((name, start, end, level))
    return out


def find_part(text, phrase):
    """The span of the part a test names, or None."""
    want = phrase.lower().strip(" .:,\"")
    for name, start, end, level in parts(text):
        if name.lower() == want or (level < 9 and want in name.lower()):
            return (start, end)
    for name, start, end, level in parts(text):
        if name.lower().startswith(want):
            return (start, end)
    return None


# ---------------------------------------------------------------- the tests

def tests(rev=None):
    if rev:
        names = sorted({p.split("/")[2] for p in git("ls-tree", "-r", "--name-only", rev, EVALS + "/").split()
                        if p.count("/") >= 3})
    else:
        names = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(ROOT, EVALS, "*", "case.yaml")))
    return names


def test_text(name, rev=None):
    if rev:
        paths = [p for p in git("ls-tree", "-r", "--name-only", rev, f"{EVALS}/{name}/").split()
                 if not p.split("/")[3].startswith("graders")]
        return "\n".join(read(p, rev) for p in paths)
    out = []
    for p in glob.glob(os.path.join(ROOT, EVALS, name, "**", "*"), recursive=True):
        if os.path.isfile(p) and "/graders/" not in p:
            with open(p, encoding="utf-8", errors="replace") as f:
                out.append(f.read())
    return "\n".join(out)


def guards(name, skill, rev=None):
    """[(phrase, (first, last) or None)] for one test."""
    case = read(f"{EVALS}/{name}/case.yaml", rev) if rev else read(f"{EVALS}/{name}/case.yaml")
    case = re.sub(r"\s+", " ", case)
    m = re.search(r"Guards (.+?)(?::|\. [A-Z])", case)
    phrases = re.findall(r'"([^"]+?),?"', m.group(1)) if m else []
    phrases += re.findall(r'\(([^)]+?)\)', m.group(1)) if m and not phrases else []
    found = [(p, find_part(skill, p)) for p in phrases]
    for word in OVERRIDES.get(name, []):
        for i, line in enumerate(skill.split("\n"), 1):
            if word in line.lower():
                found.append((word, (i, i)))
    return found


def group_of(name, rev=None):
    text = test_text(name, rev)
    return sorted(g for g, (pattern, _) in GROUPS.items() if re.search(pattern, text, re.I))


def coverage(rev=None):
    skill = read(SKILL_MD, rev) if rev else read(SKILL_MD)
    return {n: {"guards": guards(n, skill, rev), "groups": group_of(n, rev)} for n in tests(rev)}


# ---------------------------------------------------------------- what a change reaches

def changed_lines(base, head, path):
    """Line numbers changed in path, in base and in head."""
    old, new = set(), set()
    for line in git("diff", "-U0", base, head, "--", path).splitlines():
        m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
        if m:
            a, an = int(m.group(1)), int(m.group(2) or 1)
            b, bn = int(m.group(3)), int(m.group(4) or 1)
            old.update(range(a, a + max(an, 1)))
            new.update(range(b, b + max(bn, 1)))
    return old, new


def reached(base, head):
    """{test: [why]} for the tests a change can reach."""
    files = git("diff", "--name-only", base, head).split()
    out = {}

    def add(test, why):
        out.setdefault(test, []).append(why)

    maps = {"base": coverage(base), "head": coverage(head)}
    if SKILL_MD in files:
        old, new = changed_lines(base, head, SKILL_MD)
        for side, lines in (("base", old), ("head", new)):
            for test, info in maps[side].items():
                for phrase, span in info["guards"]:
                    if span and any(span[0] <= n <= span[1] for n in lines):
                        add(test, f"guards \"{phrase}\", which changed")
    for f in files:
        if f in SHARED:
            for test in maps["head"]:
                add(test, f"every group reads {f}")
            continue
        for g, (_, stem) in GROUPS.items():
            if f.startswith((SOPS, FIXED)) and stem in os.path.basename(f):
                for test, info in maps["head"].items():
                    if g in info["groups"]:
                        add(test, f"its group's {os.path.basename(f)} changed")
    for test in maps["head"]:
        if any(p.startswith(f"{EVALS}/{test}/") for p in files):
            add(test, "the test itself is new or changed")
    return {t: sorted(set(w)) for t, w in sorted(out.items())}


# ---------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("base", nargs="?")
    parser.add_argument("head", nargs="?", default="HEAD")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.base:
        result = reached(args.base, args.head)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"{len(result)} tests reached")
            for t, why in result.items():
                print(f"- {t}: {'; '.join(why)}")
        return 0

    cov = coverage()
    skill = read(SKILL_MD)
    guarded = set()
    for info in cov.values():
        for _, span in info["guards"]:
            if span:
                guarded.update(range(span[0], span[1] + 1))
    unguarded = [(name, s, e) for name, s, e, level in parts(skill)
                 if level == 3 and not guarded & set(range(s, e + 1))]
    unmapped = [(t, p) for t, info in cov.items() for p, span in info["guards"] if not span]
    untied = [t for t, info in cov.items() if not any(span for _, span in info["guards"])]
    if args.json:
        print(json.dumps({"tests": {t: {"guards": [[p, s] for p, s in i["guards"]], "groups": i["groups"]}
                                    for t, i in cov.items()},
                          "unguarded_parts": unguarded, "unmapped": unmapped, "untied": untied},
                         indent=2, ensure_ascii=False))
        return 0
    print("Tests, the lines of SKILL.md each guards, and its group\n")
    for t, info in cov.items():
        spans = ", ".join(f"{p} ({s[0]}-{s[1]})" if s else f"{p} (not found)" for p, s in info["guards"])
        print(f"- {t}: {spans or 'names no part'}; {', '.join(info['groups']) or 'no group'}")
    print("\nParts of SKILL.md (### headings) that no test guards\n")
    for name, s, e in unguarded:
        print(f"- {name} ({s}-{e})")
    if untied:
        print("\nTests tied to no part of SKILL.md\n")
        print("\n".join(f"- {t}" for t in untied))
    return 0


if __name__ == "__main__":
    sys.exit(main())
