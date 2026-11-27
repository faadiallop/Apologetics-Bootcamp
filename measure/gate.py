#!/usr/bin/env python3
"""Sort a change into a tier, and say whether it may merge itself.

Run from the repo:  python3 measure/gate.py BASE [HEAD] [--json] [--no-script-checks]

BASE and HEAD are git commits (HEAD defaults to the working tree's HEAD). The
tiers and the checks are those of measure/PLAN.md, sections 2 and 3B. A model
never decides a tier here: only the files and lines a change touches.

Build step 2 runs this beside the author, to see whether it sorts as he would.
It only reports, and always exits 0, so it never blocks a merge yet.
Standard library only.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
# CI runs the base branch's copy of this file from outside the repo (PLAN.md, section 3),
# so GATE_REPO names the repo to read; by default it is the repo this file is in.
ROOT = os.path.abspath(os.environ.get("GATE_REPO") or os.path.dirname(HERE))
sys.path.insert(0, HERE)
import checks  # noqa: E402  (REF_RE, the reference pattern the script checks use)

SKILL_MD = "skills/apologetics-boot-camp/SKILL.md"
VERSION = "skills/apologetics-boot-camp/VERSION"
BANK = re.compile(r"^skills/apologetics-boot-camp/sops/20-response-bank-[a-z-]+\.md$")
RECORDS = {"loop/journal.md", "loop/harvest-log.md"}
SITE_TIER_1 = {"site/public/index.html", "site/src/engine.ts", "site/src/round.ts",
               "site/src/materials.ts"}
SIZE_CAP = 500  # changed lines; a test folder counts toward it too
STAMP_LINE = re.compile(r"This copy's stamp is `[0-9a-f]{8}`")
TIER_1_SKILL_SECTIONS_EXCLUDED = ("A", "C")  # "Why we train", "The models, measured against Scripture"

URL = re.compile(r"https?://([A-Za-z0-9.-]+)")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
EMAIL_OK = re.compile(r"noreply@anthropic\.com$|@example\.(com|org)$")
PHONE = re.compile(r"(?<![\w:])\+?\d[\d ().-]{8,}\d(?![\w:])")
INSTRUCTION = re.compile(
    r"\b(ignore|disregard|forget)\b.{0,40}\b(instructions?|rules|above|previous|everything)\b"
    r"|\bsystem prompt\b|\byou (must|should|will) now\b|\bnew instructions\b"
    r"|\b(curl|wget)\s+https?://", re.I)
UNTRUSTED_PATHS = ("skills/", "site/prompts/", "loop/")


def git(*args, cwd=ROOT):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def show(rev, path):
    try:
        return git("show", f"{rev}:{path}")
    except subprocess.CalledProcessError:
        return None


# ---------------------------------------------------------------- the diff

def changed_files(base, head):
    """[(status, path)] with renames split into a delete and an add."""
    out = []
    for line in git("diff", "--name-status", "--no-renames", base, head).splitlines():
        status, path = line.split("\t", 1)
        out.append((status[0], path))
    return out


def hunks(base, head, path):
    """[(old_start, removed_lines, new_start, added_lines)] for one file."""
    diff = git("diff", "-U0", "--no-color", base, head, "--", path)
    result, cur = [], None
    for line in diff.splitlines():
        m = re.match(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
        if m:
            cur = [int(m.group(1)), [], int(m.group(2)), []]
            result.append(cur)
        elif cur is not None and line.startswith("-") and not line.startswith("---"):
            cur[1].append(line[1:])
        elif cur is not None and line.startswith("+") and not line.startswith("+++"):
            cur[3].append(line[1:])
    return result


def size(base, head):
    total = 0
    for line in git("diff", "--numstat", base, head).splitlines():
        a, d, _ = line.split("\t", 2)
        total += (int(a) if a != "-" else 0) + (int(d) if d != "-" else 0)
    return total


def is_revert(base, head):
    """True when the change undoes one recent commit exactly (same patch, reversed)."""
    def patch_id(diff):
        if not diff.strip():
            return None
        out = subprocess.run(["git", "patch-id", "--stable"], cwd=ROOT, input=diff,
                             capture_output=True, text=True).stdout.split()
        return out[0] if out else None
    want = patch_id(git("diff", base, head))
    if not want:
        return False
    for sha in git("rev-list", "--no-merges", "-n", "200", base).split():
        parent = git("rev-list", "--parents", "-n", "1", sha).split()
        if len(parent) == 2 and patch_id(git("diff", sha, parent[1])) == want:
            return True
    return False


# ---------------------------------------------------------------- sorting

def section_at(text, line_no):
    """The letter of the SKILL.md section ('A', 'C', "C′"...) holding a line; '' before A."""
    letter = ""
    for i, line in enumerate(text.split("\n"), 1):
        if i > line_no:
            break
        m = re.match(r"## ([A-Z]′?)\. ", line)
        if m:
            letter = m.group(1)
    return letter


def sort_skill_md(base, head, reasons):
    """Tier 1 unless a changed line is in the preamble, in sections A or C, or carries Scripture."""
    old, new = show(base, SKILL_MD) or "", show(head, SKILL_MD) or ""
    tier = 1
    for old_start, removed, new_start, added in hunks(base, head, SKILL_MD):
        # A change to the stamp alone is bookkeeping, not a change of meaning.
        if [STAMP_LINE.sub("", x) for x in removed] == [STAMP_LINE.sub("", x) for x in added]:
            continue
        places = [(old, old_start + i, x) for i, x in enumerate(removed)]
        places += [(new, new_start + i, x) for i, x in enumerate(added)]
        for text, n, line in places:
            sec = section_at(text, n)
            if sec == "":
                reasons.append(f"{SKILL_MD}:{n} is in the opening part, which holds what the skill fetches")
                tier = 2
            elif sec in TIER_1_SKILL_SECTIONS_EXCLUDED:
                reasons.append(f"{SKILL_MD}:{n} is in section {sec}")
                tier = 2
            elif checks.REF_RE.search(line):
                reasons.append(f"{SKILL_MD}:{n} carries Scripture")
                tier = 2
    return tier


def bank_row(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells if line.lstrip().startswith("|") and len(cells) == 4 and cells[0].isdigit() else None


def sort_bank(base, head, path, reasons):
    """Tier 1 only for new rows, at the end of a table, with a source link and no reply."""
    tier = 1
    old_rows = [bank_row(x) for x in (show(base, path) or "").split("\n")]
    numbers = [int(r[0]) for r in old_rows if r]
    for _, removed, new_start, added in hunks(base, head, path):
        if removed:
            reasons.append(f"{path}: changes or removes existing lines")
            tier = 2
        for i, line in enumerate(added):
            row = bank_row(line)
            if not row:
                if line.strip():
                    reasons.append(f"{path}:{new_start + i} adds a line that is not a response row")
                    tier = 2
                continue
            if not URL.search(row[2]):
                reasons.append(f"{path}:{new_start + i} row {row[0]} gives no public source")
                tier = 2
            if row[3] not in ("", "—", "-"):
                reasons.append(f"{path}:{new_start + i} row {row[0]} has a reply")
                tier = 2
            if numbers and int(row[0]) <= max(numbers):
                reasons.append(f"{path}:{new_start + i} row {row[0]} reuses or skips back over a number")
                tier = 2
            numbers.append(int(row[0]))
    return tier


def sort_change(base, head, files, reasons):
    tiers = []
    paths = [p for _, p in files]
    eval_dirs = {p.split("/")[2] for p in paths if p.startswith("measure/evals/")}
    new_evals = {d for d in eval_dirs if show(base, f"measure/evals/{d}/case.yaml") is None}

    for status, path in files:
        if path in RECORDS:
            if any(removed for _, removed, _, _ in hunks(base, head, path)):
                reasons.append(f"{path}: changes or removes existing lines")
                tiers.append(2)
            else:
                tiers.append(0)
        elif path == SKILL_MD:
            tiers.append(sort_skill_md(base, head, reasons))
        elif path == VERSION and SKILL_MD in paths:
            tiers.append(0)
        elif BANK.match(path):
            tiers.append(sort_bank(base, head, path, reasons))
        elif path.startswith("measure/evals/") and path.split("/")[2] in new_evals and status == "A":
            tiers.append(1)
        elif path in SITE_TIER_1 or path.startswith("site/test/"):
            tiers.append(1)
        else:
            reasons.append(f"{path}: only the author changes this")
            tiers.append(2)

    if any(p.startswith("skills/") for p in paths) and any(p.startswith("measure/") for p in paths):
        reasons.append("changes both skills/ and measure/ (measure rule 6)")
        tiers.append(2)
    n = size(base, head)
    if n > SIZE_CAP:
        reasons.append(f"{n} changed lines; the cap is {SIZE_CAP}")
        tiers.append(2)
    return max(tiers) if tiers else 0


# ---------------------------------------------------------------- checks on what was added

def known_hosts(base):
    hosts = {"github.com", "raw.githubusercontent.com", "www.youtube.com", "youtube.com",
             "youtu.be", "claude.ai"}
    for path in git("ls-tree", "-r", "--name-only", base).splitlines():
        if path.endswith(".md") and path.startswith(UNTRUSTED_PATHS):
            hosts.update(h.lower() for h in URL.findall(show(base, path) or ""))
    return hosts


def check_added(base, head, files, holds):
    hosts = known_hosts(base)
    for status, path in files:
        if status == "D" or not path.endswith((".md", ".ts", ".html", ".yaml", ".sh", ".json", ".py")):
            continue
        for _, _, new_start, added in hunks(base, head, path):
            for i, line in enumerate(added):
                where = f"{path}:{new_start + i}"
                for email in EMAIL.findall(line):
                    if not EMAIL_OK.search(email):
                        holds.append(f"{where} adds an email address")
                if PHONE.search(line) and sum(c.isdigit() for c in PHONE.search(line).group()) >= 10:
                    holds.append(f"{where} adds what looks like a phone number")
                if path.startswith(UNTRUSTED_PATHS):
                    for host in URL.findall(line):
                        if host.lower() not in hosts:
                            holds.append(f"{where} adds a link to a new site, {host}")
                    if INSTRUCTION.search(line):
                        holds.append(f"{where} reads like an instruction to the coach: "
                                     f"\"{INSTRUCTION.search(line).group(0)}\"")


def check_test_layout(head, files, holds):
    dirs = {p.split("/")[2] for _, p in files if p.startswith("measure/evals/") and p.count("/") >= 3}
    for d in sorted(dirs):
        tree = git("ls-tree", "-r", "--name-only", head, f"measure/evals/{d}/").splitlines()
        if not tree:
            continue
        names = [t[len(f"measure/evals/{d}/"):] for t in tree]
        for need in ("prompt.md", "case.yaml"):
            if need not in names:
                holds.append(f"measure/evals/{d} has no {need}")
        if not any(n.startswith("graders/") for n in names):
            holds.append(f"measure/evals/{d} has no graders")
        if not any(n.startswith("files/") for n in names):
            holds.append(f"measure/evals/{d} has no files")


def script_report(rev, kjv):
    """measure/checks.py run on a commit, as {(status, check, item)} with line numbers removed."""
    with tempfile.TemporaryDirectory() as tmp:
        git("worktree", "add", "--detach", "-q", tmp, rev)
        try:
            args = [sys.executable, os.path.join(tmp, "measure", "checks.py"), "--json"]
            if kjv and os.path.exists(kjv):
                args += ["--kjv", kjv]
            out = subprocess.run(args, cwd=tmp, capture_output=True, text=True).stdout
        finally:
            git("worktree", "remove", "--force", tmp)
    rows = json.loads(out) if out.strip() else []
    found = set()
    for r in rows:
        if r["check"] == "saved-skills":
            continue  # depends on the machine, not on the change
        items = r["items"] or [r["detail"]]
        for item in items:
            found.add((r["status"], r["check"], re.sub(r":\d+\b", "", item)))
    return found


def check_scripts(base, head, holds):
    kjv = os.path.join(ROOT, "measure", ".cache", "en_kjv.json")
    before, after = script_report(base, kjv), script_report(head, kjv)
    for status, check, item in sorted(after - before):
        if status not in ("FAIL", "INSPECT"):
            continue
        # A draft fixed file is never read to trainees, so its being behind the skill holds nothing.
        m = re.match(r"([a-z-]+\.md): written from skill stamp", item)
        if m and "Status: draft" in (show(head, f"skills/apologetics-boot-camp/fixed/{m.group(1)}") or ""):
            continue
        holds.append(f"script check {check} gives a new {status}: {item}")


# ---------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("base")
    parser.add_argument("head", nargs="?", default="HEAD")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-script-checks", action="store_true",
                        help="skip running measure/checks.py on both commits")
    args = parser.parse_args()
    base = git("rev-parse", args.base).strip()
    head = git("rev-parse", args.head).strip()

    files = changed_files(base, head)
    reasons, holds = [], []
    if is_revert(base, head):
        tier = 0
        reasons.append("undoes one earlier commit exactly")
    else:
        tier = sort_change(base, head, files, reasons)
    if tier == 1 and any(p == SKILL_MD for _, p in files):
        holds.append("which tests this change reaches is not yet known (the coverage map comes in build step 3)")
    check_added(base, head, files, holds)
    check_test_layout(head, files, holds)
    if not args.no_script_checks:
        check_scripts(base, head, holds)

    verdict = {
        "tier": tier,
        "may_merge_itself": tier < 2 and not holds,
        "why_this_tier": reasons,
        "holds": holds,
        "files": len(files),
        "note": "Observation only (build step 2): this verdict does not block or allow anything yet.",
    }
    if args.json:
        print(json.dumps(verdict, indent=2, ensure_ascii=False))
    else:
        print(f"## Tier {tier}: {'may merge itself' if verdict['may_merge_itself'] else 'needs the author'}\n")
        print(verdict["note"] + "\n")
        if reasons:
            print("**Why this tier**\n")
            print("\n".join(f"- {r}" for r in reasons) + "\n")
        if holds:
            print("**What holds it**\n")
            print("\n".join(f"- {h}" for h in holds) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
