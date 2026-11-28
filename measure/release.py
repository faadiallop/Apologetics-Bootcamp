#!/usr/bin/env python3
"""The release's decisions, for .github/workflows/release.yml (measure/PLAN.md, section 7).

Run from the repo:
  python3 measure/release.py summary FROM TO [--measure results.json]
      The summary sent to the author: every change from FROM (main) to TO (the
      commit to release), its tier, whether the site deploys, and the measure.
  python3 measure/release.py site FROM TO
      Whether the release deploys the site: prints "deploy", "schema" (the
      database changed, so the author applies it first) or "none".
  python3 measure/release.py decide OPENED COMMENTS.json AUTHOR [--now ISO]
      Whether a waiting release goes: prints "wait", "hold" or "go".

A script decides these, not a model (PLAN.md, section 2). Standard library only.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.environ.get("GATE_REPO") or os.path.dirname(HERE))

HOLD_HOURS = 48
# What the site bundles when it is built (PLAN.md, section 7, "Deploying the site").
SITE_PATHS = ("site/", "skills/apologetics-boot-camp/SKILL.md", "skills/apologetics-boot-camp/sops/",
              "skills/apologetics-boot-camp/fixed/", "skills/thought-and-word-rules/")
SCHEMA = "site/schema.sql"
MARK = "<!-- release {sha} from {base} -->"
MARK_RE = re.compile(r"<!-- release ([0-9a-f]{40}) from ([0-9a-f]{40}) -->")
HOLD_RE = re.compile(r"\bhold\b", re.I)


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], check=True, capture_output=True, text=True).stdout


def changed(base, head):
    return [p for p in git("diff", "--name-only", base, head).splitlines() if p]


def site(base, head):
    files = changed(base, head)
    if SCHEMA in files:
        return "schema"
    return "deploy" if any(f.startswith(SITE_PATHS) for f in files) else "none"


def is_ancestor(a, b):
    return subprocess.run(["git", "-C", ROOT, "merge-base", "--is-ancestor", a, b]).returncode == 0


def changes(base, head):
    """Each change on the first-parent line: a merged pull request, or a commit made on next itself."""
    out = []
    for line in git("log", "--first-parent", "--reverse", "--format=%H%x00%P%x00%s%x00%b%x1e",
                    f"{base}..{head}").split("\x1e"):
        if not line.strip():
            continue
        sha, parents, subject, body = line.strip("\n").split("\x00")
        parents = parents.split()
        m = re.match(r"Merge pull request #(\d+)", subject)
        if m and len(parents) == 2:
            if is_ancestor(parents[1], base):
                continue  # it only brings in what main already has
            title = next((l.strip() for l in body.splitlines() if l.strip()), subject)
            out.append({"pr": int(m.group(1)), "title": title, "from": parents[0], "to": sha})
        else:
            out.append({"pr": None, "title": subject, "from": parents[0] if parents else base, "to": sha})
    return out


def tier(base, head):
    """The tier script's verdict on one change, or None if it can't be run."""
    try:
        out = subprocess.run([sys.executable, os.path.join(HERE, "gate.py"), base, head, "--json",
                              "--no-script-checks"], capture_output=True, text=True, check=True,
                             env={**os.environ, "GATE_REPO": ROOT}).stdout
        return json.loads(out)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def measure_lines(path):
    if not path or not os.path.exists(path):
        return ["**Not run.** No key for the tests is in the `measure` environment yet, so the "
                "conversation tests did not run on this release. Read the changes to the skill above "
                "with that in mind."]
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    by_model = {}
    for row in data["results"]:
        n = by_model.setdefault(row["coach"], [0, 0])
        n[0] += sum(v["passes"] for v in row["verdicts"].values())
        n[1] += len(row["verdicts"])
    lines = [f"Every test, three times (cost ${data['cost']:.2f}):", ""]
    lines += [f"- {model}: {p} of {n} statements pass" for model, (p, n) in by_model.items()]
    bad = [(t, s, v) for t, stmts in data["verdicts"].items() for s, v in stmts.items() if v != "pass"]
    if bad:
        lines += ["", "Failing, two runs of three or more:", ""]
        lines += [f"- `{t}/{s}`" for t, s, v in bad]
    errors = [r for r in data["results"] if r.get("error")]
    if errors:
        lines += ["", "Runs that failed to finish:", ""]
        lines += [f"- `{r['test']}` ({r['coach']}): {r['error']}" for r in errors]
    return lines


def summary(base, head, measure):
    rows = changes(base, head)
    when = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=HOLD_HOURS))
    lines = [
        f"This release moves `main` from `{base[:8]}` to `{head[:8]}` "
        f"no sooner than {when:%a %b %-d, %H:%M} UTC, {HOLD_HOURS} hours from now. "
        "Trainees hear it from their next session.",
        "",
        "**You need do nothing for it to go out.** To stop it, comment **hold**. To let a held release go, "
        "comment just **go**. To drop one change, comment which one: it is reverted on `next`, and this issue is "
        "closed so the release runs again without it. Closing this issue drops the release.",
        "",
        "## What changes",
        "",
    ]
    for r in rows:
        v = tier(r["from"], r["to"])
        name = f"#{r['pr']} " if r["pr"] else ""
        t = f"Tier {v['tier']}" if v else "tier unknown"
        lines.append(f"- {name}{r['title']} ({t})")
        if v and v["tier"] == 2:
            lines += [f"  - {why}" for why in v.get("why_this_tier", [])[:3]]
    if not rows:
        lines.append("- Nothing.")
    s = site(base, head)
    lines += ["", "## The site", ""]
    lines.append({
        "deploy": "The site is deployed from `main` right after it moves, then checked; if the check fails, "
                  "the site and `main` both go back.",
        "schema": "**The database changes** (`site/schema.sql`), so the site is not deployed by itself. "
                  "After `main` moves, apply the change and deploy by hand, as `site/README.md` says.",
        "none": "Nothing the site bundles changed, so it is not deployed.",
    }[s])
    lines += ["", "## The measure", ""] + measure_lines(measure)
    lines += ["", "The script checks and the site checks passed on this commit. They cannot judge whether "
              "the teaching is true; that is what these 48 hours are for.", "", MARK.format(sha=head, base=base)]
    return "\n".join(lines)


def decide(opened, comments, author, now):
    """Held by any comment of the author's that says "hold", until a later comment of his that is only "go".
    Otherwise it goes once 48 hours have passed."""
    word = None
    for c in sorted(comments, key=lambda c: c["createdAt"]):
        if c.get("author", {}).get("login", "").lower() != author.lower():
            continue
        body = c.get("body", "")
        if HOLD_RE.search(body):
            word = "hold"
        elif re.sub(r"[^a-z]", "", body.lower()) == "go":
            word = "go"
    if word == "hold":
        return "hold"
    opened = datetime.datetime.fromisoformat(opened.replace("Z", "+00:00"))
    if word == "go" or now - opened >= datetime.timedelta(hours=HOLD_HOURS):
        return "go"
    return "wait"


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("summary")
    s.add_argument("base")
    s.add_argument("head")
    s.add_argument("--measure")
    w = sub.add_parser("site")
    w.add_argument("base")
    w.add_argument("head")
    d = sub.add_parser("decide")
    d.add_argument("opened")
    d.add_argument("comments")
    d.add_argument("author")
    d.add_argument("--now")
    m = sub.add_parser("mark")
    m.add_argument("body")
    a = p.parse_args()
    if a.cmd == "summary":
        print(summary(git("rev-parse", a.base).strip(), git("rev-parse", a.head).strip(), a.measure))
    elif a.cmd == "site":
        print(site(a.base, a.head))
    elif a.cmd == "decide":
        with open(a.comments, encoding="utf-8") as f:
            comments = json.load(f)
        now = (datetime.datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now
               else datetime.datetime.now(datetime.timezone.utc))
        print(decide(a.opened, comments, a.author, now))
    elif a.cmd == "mark":
        m = MARK_RE.search(a.body)
        if not m:
            return 1
        print(m.group(1), m.group(2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
