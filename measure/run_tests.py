#!/usr/bin/env python3
"""Run the conversation tests through the Claude API, cheaply (PLAN.md, section 4).

Each test is sent straight to the API, as the site's coach is (site/src/anthropic.ts):
the skill and the group's materials as a cached system prompt, then the test's prompt
and files. Where the coach would save a card, it returns the whole new training log.
Opus then grades each statement. Both steps go through the Batch API at half price.

  python3 measure/run_tests.py run    --rev REV [--tests a,b] [--coaches sonnet,sonnet,opus] --out F --cap USD
  python3 measure/run_tests.py screen --rev REV --baseline F [--tests a,b] --out F --cap USD
  python3 measure/run_tests.py show   F

`run` is the full measure of rule 7 (by default three runs: twice Sonnet, once Opus).
`screen` runs each test once with Sonnet, compares it with a stored full run, and runs
a test twice more (Sonnet, then Opus) only where a statement comes out differently.
Every command takes --dry-run, which prints the requests' most possible cost and sends
nothing. Before sending, the most possible cost is checked against --cap, since a batch
cannot be stopped partway. Needs ANTHROPIC_API_KEY and the anthropic package.

This run does not test fetching from GitHub or saving with tools; a release still runs
the measure as its README describes, for that.

With --engine claude-code, the tests run through Claude Code's own runner
(`claude plugin eval`) instead, on whatever Claude credential the machine has: in CI,
the author's subscription token. The coach then reads and writes the test's files with
tools, as in a real session, and Opus grades each statement three times. It costs more
of the plan's usage than the API way costs in money, and the Batch API is not used.
--root names the plugin to test (by default, this repo).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import coverage  # noqa: E402  (git access, the tests, and each test's group)

MODELS = {"sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}
GRADER = "claude-opus-5-5"
# US dollars per million tokens, list prices (Nov 2026); the Batch API charges half.
PRICES = {
    "claude-sonnet-5-5": {"input": 2.0, "output": 10.0, "cache_read": 0.10, "cache_write": 2.5},
    "claude-opus-5-5": {"input": 4.0, "output": 20.0, "cache_read": 0.20, "cache_write": 5.0},
}
BATCH = 0.5
CHARS_PER_TOKEN = 3.0  # on the low side, so estimates err high
COACH_MAX_TOKENS = 6000
GRADER_MAX_TOKENS = 3000
COACH_EFFORT = "low"   # as the site's coach (site/src/anthropic.ts)
GRADER_EFFORT = "high"

SKILL_DIR = "skills/apologetics-boot-camp"
GROUP_NAMES = {"islam": "Muslims", "jehovahs-witnesses": "Jehovah's Witnesses", "jewish-people": "Jewish people",
               "atheism": "Atheists", "icon-veneration": "Icon veneration"}
SOP_NUMBER = {"islam": "10", "jehovahs-witnesses": "11", "jewish-people": "12", "atheism": "13",
              "icon-veneration": "14"}

HARNESS = (
    "This is a test, and you have no tools. The files the trainee names are given below, in full. "
    "Answer as the coach would, exactly as you would say it aloud. Where the skill has you save or update "
    "his card, end your reply with the whole new contents of training-log.md between the lines "
    "<training-log> and </training-log>; say nothing after them.")

GRADER_SYSTEM = (
    "You grade one answer from a coach in a test of a training skill. You are given what the trainee "
    "asked, the files the coach was given, the coach's answer as it would be spoken, and the training log "
    "the coach left behind, if any. Judge each statement on its own, strictly and by its words: it passes "
    "only if the answer plainly does what it says. Give a reason of one or two sentences, quoting the "
    "answer where it helps.")


# ---------------------------------------------------------------- building the requests

def file_block(name, text):
    return f'\n\n<file name="{name}">\n{text.strip()}\n</file>'


def strip_front(text):
    return re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S).strip()


def test_group(name, rev):
    """The one group a test's conversation is with, or None."""
    text = coverage.test_text(name, rev)
    counts = {g: len(re.findall(p, text, re.I)) for g, (p, _) in coverage.GROUPS.items()}
    best = max(counts, key=counts.get)
    return best if counts[best] else None


def coach_system(rev, group):
    """Two cached parts, as the site builds them: what every group shares, then the group's own."""
    sops = f"{SKILL_DIR}/sops/"
    shared = ("You are the coach of the apologetics boot camp. The skill and its materials follow; "
              "follow the skill." +
              file_block("SKILL.md", coverage.read(f"{SKILL_DIR}/SKILL.md", rev)) +
              file_block("thought-and-word-rules/SKILL.md", coverage.read(coverage.RULES, rev)) +
              file_block("sops/00-overview-and-template.md", coverage.read(sops + "00-overview-and-template.md", rev)) +
              file_block("sops/01-methodology-questioning-them-to-death.md",
                         coverage.read(sops + "01-methodology-questioning-them-to-death.md", rev)) +
              file_block("sops/20-response-bank.md", coverage.read(sops + "20-response-bank.md", rev)) +
              file_block("sops/21-training-plans.md", coverage.read(sops + "21-training-plans.md", rev)))
    parts = [{"type": "text", "text": shared, "cache_control": {"type": "ephemeral"}}]
    if group:
        sop = f"{SOP_NUMBER[group]}-{group}.md"
        fixed = coverage.read(f"{SKILL_DIR}/fixed/{group}.md", rev)
        own = (f"The trainee's group is {GROUP_NAMES[group]}. Its materials follow." +
               file_block(f"sops/{sop}", coverage.read(sops + sop, rev)) +
               file_block(f"sops/20-response-bank-{group}.md", coverage.read(sops + f"20-response-bank-{group}.md", rev)) +
               file_block(f"sops/21-training-plans-{group}.md", coverage.read(sops + f"21-training-plans-{group}.md", rev)))
        own += (file_block(f"fixed/{group}.md", fixed) if re.search(r"^Status: approved\s*$", fixed, re.M)
                else "\n\nThis group has no approved fixed pieces, so compose those parts yourself.")
        parts.append({"type": "text", "text": own, "cache_control": {"type": "ephemeral"}})
    return parts


def test_files(name, rev):
    """{file name: text} for the files a test places beside the coach."""
    base = f"{coverage.EVALS}/{name}/files/"
    paths = [p for p in coverage.git("ls-tree", "-r", "--name-only", rev, base).split()]
    return {p[len(base):]: coverage.read(p, rev) for p in paths}


def coach_user(name, rev):
    prompt = strip_front(coverage.read(f"{coverage.EVALS}/{name}/prompt.md", rev))
    files = "".join(file_block(n, t) for n, t in test_files(name, rev).items())
    return f"{HARNESS}\n\n{prompt}{files}"


def statements(name, rev):
    base = f"{coverage.EVALS}/{name}/graders/"
    paths = sorted(coverage.git("ls-tree", "-r", "--name-only", rev, base).split())
    return {os.path.splitext(p[len(base):])[0]: strip_front(coverage.read(p, rev)) for p in paths}


def coach_request(cid, name, rev, model):
    return {"custom_id": cid, "params": {
        "model": MODELS[model], "max_tokens": COACH_MAX_TOKENS,
        "output_config": {"effort": COACH_EFFORT},
        "system": coach_system(rev, test_group(name, rev)),
        "messages": [{"role": "user", "content": coach_user(name, rev)}]}}


def split_reply(text):
    m = re.search(r"<training-log>\n?(.*?)\n?</training-log>", text, re.S)
    if not m:
        return text.strip(), None
    return text[:m.start()].strip(), m.group(1).strip()


def grader_request(cid, name, rev, reply, log_after):
    stmts = statements(name, rev)
    prompt = strip_front(coverage.read(f"{coverage.EVALS}/{name}/prompt.md", rev))
    files = "".join(file_block(n, t) for n, t in test_files(name, rev).items())
    body = (f"# What the trainee asked\n\n{prompt}\n\n# The files the coach was given{files}\n\n"
            f"# The coach's answer\n\n{reply}\n\n# training-log.md after the answer\n\n"
            f"{log_after if log_after is not None else '(The coach did not change it.)'}\n\n# The statements\n\n" +
            "\n\n".join(f"{sid}: {text}" for sid, text in stmts.items()))
    schema = {"type": "object", "additionalProperties": False, "required": ["verdicts"], "properties": {
        "verdicts": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["statement", "passes", "reason"],
            "properties": {"statement": {"type": "string", "enum": list(stmts)},
                           "passes": {"type": "boolean"}, "reason": {"type": "string"}}}}}}
    return {"custom_id": cid, "params": {
        "model": GRADER, "max_tokens": GRADER_MAX_TOKENS, "output_config": {"effort": GRADER_EFFORT,
                                                                             "format": {"type": "json_schema", "schema": schema}},
        "system": GRADER_SYSTEM, "messages": [{"role": "user", "content": body}]}}


# ---------------------------------------------------------------- cost

def request_chars(req):
    p = req["params"]
    system = p["system"] if isinstance(p["system"], str) else "".join(b["text"] for b in p["system"])
    return len(system) + sum(len(m["content"]) for m in p["messages"])


def most_cost(requests):
    """The most a batch can cost: every input token uncached, every output token used."""
    total = 0.0
    for r in requests:
        price = PRICES[r["params"]["model"]]
        tokens_in = request_chars(r) / CHARS_PER_TOKEN
        total += (tokens_in * price["cache_write"] + r["params"]["max_tokens"] * price["output"]) / 1e6
    return total * BATCH


def actual_cost(model, usage):
    p = PRICES[model]
    return BATCH * ((usage.get("input_tokens") or 0) * p["input"] + (usage.get("output_tokens") or 0) * p["output"]
                    + (usage.get("cache_read_input_tokens") or 0) * p["cache_read"]
                    + (usage.get("cache_creation_input_tokens") or 0) * p["cache_write"]) / 1e6


# ---------------------------------------------------------------- the API

def send_batch(requests, label):
    """Send one batch, wait for it, and return {custom_id: (text, usage, model) or error}."""
    import anthropic
    client = anthropic.Anthropic()
    batch = client.messages.batches.create(requests=requests)
    print(f"{label}: batch {batch.id}, {len(requests)} requests", flush=True)
    while True:
        batch = client.messages.batches.retrieve(batch.id)
        if batch.processing_status == "ended":
            break
        time.sleep(30)
    out = {}
    for item in client.messages.batches.results(batch.id):
        if item.result.type != "succeeded":
            out[item.custom_id] = {"error": item.result.type}
            continue
        msg = item.result.message
        text = "".join(b.text for b in msg.content if b.type == "text")
        out[item.custom_id] = {"text": text, "model": msg.model, "stop": msg.stop_reason,
                               "usage": msg.usage.model_dump()}
    return out


# ---------------------------------------------------------------- running

def run(rev, plan, cap, dry_run, label):
    """plan: [(test, coach model)]. Returns [{test, coach, reply, log_after, verdicts, cost}]."""
    coach_reqs = [coach_request(f"c{i}", t, rev, m) for i, (t, m) in enumerate(plan)]
    # The grader's input is unknown until the coach answers; bound it by the coach's most output.
    grade_most = sum(most_cost([grader_request("g", t, rev, "x" * int(COACH_MAX_TOKENS * CHARS_PER_TOKEN), None)])
                     for t, _ in plan)
    most = most_cost(coach_reqs) + grade_most
    print(f"{label}: {len(plan)} runs; at most ${most:.2f} (the cap is ${cap:.2f})")
    if dry_run:
        return None
    if most > cap:
        sys.exit(f"{label}: refused, since it could cost more than the cap")

    coached = send_batch(coach_reqs, f"{label}, coach")
    results, grade_reqs = [], []
    for i, (test, model) in enumerate(plan):
        got = coached[f"c{i}"]
        row = {"test": test, "coach": model, "verdicts": {}, "cost": 0.0}
        if "error" in got or got["stop"] == "refusal":
            row["error"] = got.get("error") or "refusal"
        else:
            row["reply"], row["log_after"] = split_reply(got["text"])
            row["cost"] += actual_cost(got["model"], got["usage"])
            grade_reqs.append(grader_request(f"g{i}", test, rev, row["reply"], row["log_after"]))
        results.append(row)
    graded = send_batch(grade_reqs, f"{label}, grader") if grade_reqs else {}
    for i, row in enumerate(results):
        got = graded.get(f"g{i}")
        if not got:
            continue
        if "error" in got:
            row["error"] = "grader " + got["error"]
            continue
        row["cost"] += actual_cost(got["model"], got["usage"])
        for v in json.loads(got["text"])["verdicts"]:
            row["verdicts"][v["statement"]] = {"passes": v["passes"], "reason": v["reason"]}
    return results


def run_claude_code(root, plan, cap, label):
    """The same as run(), through `claude plugin eval`. plan: [(test, coach model)]."""
    counts = {}
    for test, model in plan:
        counts[(test, model)] = counts.get((test, model), 0) + 1
    results, spent = [], 0.0
    for (test, model), runs in counts.items():
        left = cap - spent
        if left <= 0:
            results.append({"test": test, "coach": model, "verdicts": {}, "cost": 0.0, "error": "cap reached"})
            continue
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "result.json")
            cmd = ["claude", "plugin", "eval", root, "--eval-dir", coverage.EVALS, "--case", test,
                   "--trust-plugin", "--no-publish", "--ablation", "none", "--scaffold",
                   "--allow-tools", "Write", "Edit", "--model", model, "--judge-model", "opus",
                   "--runs", str(runs), "--threshold", "0", "--max-cost-usd", f"{left:.2f}",
                   "--output-dir", os.path.join(tmp, "out"), "--report", os.path.join(tmp, "report.html"),
                   "--json", out]
            print(f"{label}: {test}, {runs} run(s) with {model}", flush=True)
            subprocess.run(cmd, cwd=root, check=False)
            if not os.path.exists(out):
                results.append({"test": test, "coach": model, "verdicts": {}, "cost": 0.0, "error": "no result"})
                continue
            with open(out, encoding="utf-8") as f:
                data = json.load(f)
        spent += data.get("costUsd") or 0.0
        for case in data.get("cases", []):
            for one in case.get("arms", {}).get("with", []):
                row = {"test": test, "coach": model, "cost": one.get("costUsd") or 0.0, "verdicts": {
                    g["name"]: {"passes": bool(g["passed"]), "reason": g.get("explanation", "")}
                    for g in one.get("graders", []) if g.get("scored", True)}}
                if one.get("error"):
                    row["error"] = one["error"][:300]
                    row["verdicts"] = {}
                results.append(row)
    return results


def verdicts(results):
    """{test: {statement: 'pass' | 'fail' | 'unsteady'}} under rule 7: all pass, or two fail."""
    seen = {}
    for row in results:
        for sid, v in row["verdicts"].items():
            seen.setdefault(row["test"], {}).setdefault(sid, []).append(v["passes"])
    out = {}
    for test, stmts in seen.items():
        for sid, runs in stmts.items():
            fails = runs.count(False)
            if len(runs) == 1:  # a screen that agreed with the stored run, so was not run again
                verdict = "fail" if fails else "pass"
            else:
                verdict = "pass" if fails == 0 else ("fail" if fails >= 2 else "unsteady")
            out.setdefault(test, {})[sid] = verdict
    return out


def save(path, rev, kind, results):
    data = {"rev": coverage.git("rev-parse", rev).strip(), "kind": kind, "results": results,
            "verdicts": verdicts(results), "cost": round(sum(r["cost"] for r in results), 4)}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    return data


def show(data):
    print(f"{data['kind']} of {data['rev'][:8]}: ${data['cost']:.2f}")
    by_model = {}
    for row in data["results"]:
        passed = sum(v["passes"] for v in row["verdicts"].values())
        by_model.setdefault(row["coach"], [0, 0])
        by_model[row["coach"]][0] += passed
        by_model[row["coach"]][1] += len(row["verdicts"])
    for model, (p, n) in by_model.items():
        print(f"  {model}: {p} of {n} statements pass")
    for test, stmts in data["verdicts"].items():
        bad = {s: v for s, v in stmts.items() if v != "pass"}
        if bad:
            print(f"  {test}: " + ", ".join(f"{s} {v}" for s, v in bad.items()))
    for row in data["results"]:
        if row.get("error"):
            print(f"  {row['test']} ({row['coach']}): {row['error']}")


# ---------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    for cmd in ("run", "screen"):
        p = sub.add_parser(cmd)
        p.add_argument("--rev", default="HEAD")
        p.add_argument("--tests", default="all")
        p.add_argument("--out", required=True)
        p.add_argument("--cap", type=float, required=True, help="refuse to send if it could cost more (USD)")
        p.add_argument("--dry-run", action="store_true")
        if cmd == "run":
            p.add_argument("--coaches", default="sonnet,sonnet,opus")
        else:
            p.add_argument("--baseline", required=True, help="a stored full run to compare with")
        p.add_argument("--engine", choices=("api", "claude-code"), default="api")
        p.add_argument("--root", default=coverage.ROOT, help="with --engine claude-code: the plugin to test")
    p = sub.add_parser("show")
    p.add_argument("file")
    args = parser.parse_args()

    if args.cmd == "show":
        with open(args.file, encoding="utf-8") as f:
            show(json.load(f))
        return 0

    tests = coverage.tests(args.rev) if args.tests == "all" else [t for t in args.tests.split(",") if t]
    if not tests:
        print("No tests to run.")
        return 0

    def go(plan, cap, dry_run, label):
        if args.engine == "claude-code":
            if dry_run:
                print(f"{label}: {len(plan)} runs through Claude Code; the cap is ${cap:.2f}")
                return None
            return run_claude_code(args.root, plan, cap, label)
        return run(args.rev, plan, cap, dry_run, label)

    if args.cmd == "run":
        plan = [(t, m) for t in tests for m in args.coaches.split(",")]
        results = go(plan, args.cap, args.dry_run, "full run")
        if results is not None:
            show(save(args.out, args.rev, "full run", results))
        return 0

    with open(args.baseline, encoding="utf-8") as f:
        base = json.load(f)["verdicts"]
    first = go([(t, "sonnet") for t in tests], args.cap, args.dry_run, "screen")
    if first is None:
        return 0
    spent = sum(r["cost"] for r in first)
    differ = sorted({r["test"] for r in first for s, v in r["verdicts"].items()
                     if base.get(r["test"], {}).get(s) != ("pass" if v["passes"] else "fail")})
    results = first
    if differ:
        more = go([(t, m) for t in differ for m in ("sonnet", "opus")], args.cap - spent, False,
                  "screen, again where it differs")
        results = first + more
    data = save(args.out, args.rev, "screen", results)
    now = data["verdicts"]
    regressions = [(t, s) for t in tests for s, v in now.get(t, {}).items()
                   if base.get(t, {}).get(s) == "pass" and v == "fail"]
    gains = [(t, s) for t in tests for s, v in now.get(t, {}).items()
             if base.get(t, {}).get(s) == "fail" and v == "pass"]
    data.update({"regressions": regressions, "gains": gains})
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    show(data)
    print(f"  {len(regressions)} statements now fail that passed; {len(gains)} now pass that failed")
    return 1 if regressions else 0


if __name__ == "__main__":
    sys.exit(main())
