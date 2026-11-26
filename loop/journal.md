# Improvement loop journal

The record of the weekly runs that test the boot camp skill against the measure and make at most one improvement. Each run reads this first; it has no other memory of earlier runs. Newest entry at the bottom.

## 2026-11-25: first run (baseline, no change)

As the task directs for a first run, nothing in the skill was changed. This entry sets the baseline.

**Repo.** Cloned at `523ca26` (main). The `add_repo` tool was not in this session; the repo was already cloned with push access to `origin`, so the run went on from that clone.

**Script checks** (`python3 measure/checks.py`): nothing fails.

- PASS kjv-quotations: 214 quotations match the King James text; 14 listed as not quotations; 0 do not match.
- INSPECT kjv-quotations: two lines quoted after a reference are not King James wording: `sops/13-atheism.md:183` (Mark 10:18, "No one is good except God alone") and `sops/20-response-bank.md:72` ("one flock", John 10:16). For the author to look at.
- PASS references-exist: 1190 checked, 0 point to no verse.
- PASS named-files: 8 SOP files, 4 groups, 0 out of step.
- PASS bank-rows: 55 row numbers, 0 missing.
- INSPECT personas: the full conversations stage of Bread of Life names an opponent "publisher pair" that the response bank doesn't define; Borrowed Ground's personas "Humanist chaplain" and "Seasoned debater" are never used in its plan.
- PASS saved-skills: 9 saved skills match GitHub.
- PASS skill-length: SKILL.md is 252 lines.

**Conversation tests on main.** Each case was run once by a fresh subagent on a scratch copy of the skill from main (SKILL.md and `sops/`, without `evals/`), with the case's files; a separate grader subagent judged each statement. Result: **59 of 67 statements pass.**

| Test | Pass | Failed statements |
| --- | --- | --- |
| answers-his-time-out-briefly | 4/5 | 04 the recorded move: it gave "ask him how he knows that's what the verse means," not the recorded question (how he knows which parts are true without first assuming the Qur'an is right) |
| closes-when-he-crosses-early | 3/4 | 04 coaches the drilled tactic: the coaching never named the claim he passed over when he crossed to the gospel |
| ends-the-round-when-the-goal-is-met | 5/5 | |
| fails-a-round-on-character | 6/7 | 07 spoken and short: 241 words (limit about 180) |
| lets-a-second-miss-pass | 3/3 | |
| marks-missed-requests-for-reasons | 5/6 | 04 spoken and short: 191 words |
| member-neither-invents-nor-folds | 4/4 | |
| no-pause-for-an-undrilled-miss | 3/3 | |
| offers-to-draft-for-a-new-group | 3/3 | |
| opens-for-a-beginner | 9/10 | 10 a minute or two: 379 words (limit about 350) |
| passes-without-chapter-and-verse | 4/6 | 05 first of two in a row: it treated one premises check as enough and moved on; 06 spoken and short: 226 words |
| pauses-on-a-drilled-miss | 5/5 | |
| refuses-a-false-pass | 5/6 | 06 spoken and short: 299 words |

Patterns in the failures, for the next run to weigh:

- **Coaching runs long.** Five of the eight failures are length: every marking test went over its word limit (191 to 299 words against about 180), and the opening ran to 379 against about 350. The skill says "under a minute," but the coach keeps adding full score explanations, homework and reminders.
- **The crossing miss.** When he crossed to the gospel early, the coach counted only the chances before it (2 of 2) and gave a pass, though the claim he skipped was itself a chance at the drilled tactic; the grader judged the count 2 of 3.
- **One pass treated as enough** for a knowledge stage, though the training plans say every stage takes two rounds in a row.
- **Time-out answered with a near move** rather than the recorded one.

These are single runs, so each failure is one piece of evidence; a rerun may differ.

**Past-chat search.** Did not work: `conversation_search`, `recent_chats` and `read_conversation` are not in this session (ToolSearch found none, by name or by keyword), so no search could be tried. No sessions were read.

**Evidence gathered.** None: on a first run the task goes straight from the tests to this entry.

**The author's flag of Nov 25, 2026** (judging the trainee's own wording: don't "sharpen" a question that already does the tactic's job; note awkward wording at the debrief with a smoother version, never scored). **Not yet handled.** The first run makes no change, so the next run should take it up as its weakness unless a failed test shows a graver one. The sessions it names can't be read without the past-chat tools.

**Change tried.** None (first run).

**Tests that may be wrong or missing** (graders' notes, for the author):

- `opens-for-a-beginner/case.yaml` still says the coach offers "plain teaching or dialogue"; the dialogue way was removed from the skill (`3fa56ab`). No statement checks it, so scores are unaffected.
- Several length statements say "about 180" or "about 350", and `pauses-on-a-drilled-miss/04` gives both four sentences and 60 words; graders asked which limit governs and whether short cues like "Time out." count as sentences.
- `closes-when-he-crosses-early`: no statement checks the count or the pass; this run's coach gave a pass that the grader doubted.
- `member-neither-invents-nor-folds/02` passes any unused recorded answer, even one that doesn't bear on the trainee's question (this run's answer didn't).
- `lets-a-second-miss-pass` and `no-pause-for-an-undrilled-miss`: no statement checks that the member's reply gives him a new chance at his tactic, or that no card is saved mid-round.
- `fails-a-round-on-character`: no statement checks that the coach shows him what to do instead.
- No test covers the author's flag (substance scored, smoothness noted but never scored). Suggested test for the author to add: a finished drill in which the trainee asks for reasons at every chance, once in clumsy words ("So how is it that you came to be thinking that, would you say?"). The coach must count it a hit, not change its score or call it a miss, and at the debrief offer a smoother wording in his own plain words.

**Live rounds.** Not run.

## 2026-11-25: author's review of the first run (made by hand, not by the loop)

The author reviewed the first run with Claude in an interactive session, which could read past chats, and directed these changes. The next run should test main as it now stands; its baseline is no longer the 59 of 67 above.

**Evidence read.** Three sessions (the ones the Nov 25 flag names). In all three the coach judged a working move against its own sample: once it "sharpened" a correct hand-back of the burden into its own question, and twice it scored a working way back to the topic as a miss, then admitted it was too strict and corrected the card. No session was checked for awkward wording the coach left unremarked.

**Skill changes** (one commit): coaching is about 150 words, with fuller reasons left for the card; after a first pass, the same drill again; a time-out gives the reply the material records; an early crossing to the gospel still counts the chance he crossed past as a miss; a move that does the tactic's job is a hit whatever its words; awkward wording gets one sentence with a smoother version and is never scored.

**The author's flag of Nov 25.** **Handled** by the skill changes above, and by the new tests `notes-awkward-wording-without-marking-down` and `notes-a-clumsy-way-back-without-marking-down`. The note covers anything he says, question or statement, on any tactic. Later runs should skip it.

**SOP fixes:** Mark 10:18 and John 10:16 now in King James wording; the JW full conversations name the Senior publisher; the atheist full conversations add the Humanist chaplain and the Seasoned debater.

**Measure changes** (separate commit, by the author): one plain length limit per statement; the stale "dialogue" line removed; the crossing test counts the crossed chance; the new awkward-wording test.

**Script checks after the changes:** all pass except `saved-skills`, which differs until the author saves the proposed update to his saved boot camp skill.

## 2026-11-26: author's change to the measure's rules (made by hand, not by the loop)

The author changed `measure/README.md` so that the weekly run may add a conversation test to `evals/` when real sessions show a weakness that no test covers. The conditions are in that file under "Tests added by the weekly run": a separate agent writes the test without seeing the fix, it must fail on main and pass on the changed copy in both runs, and no run changes or removes a test once it is added. Everything else in the measure is still the author's alone. No test was run for this entry, and no test has been run on main since the changes of Nov 25, so the next run sets a new baseline.

## 2026-11-26: author's changes to cut what a session loads (made by hand, not by the loop)

Two changes, made after reviewing Anthropic's guidance on writing skills (keep SKILL.md lean; load only what the task needs). Neither changes what the coach is told to do in a round.

**The response bank and the training plans are split by group.** `sops/20-response-bank.md` now holds only what every group shares (the personas and the rules for playing a member), and each group's responses are in a file of their own, named after its SOP: `20-response-bank-islam.md`, `-jehovahs-witnesses.md`, `-jewish-people.md`, `-atheism.md`. The training plans are split the same way. No text changed: joined in that order, the files are identical to the old ones. A session now loads its own group's files and no other's, where before it loaded all four. Row numbers are unchanged.

**SKILL.md carries a stamp.** The coach used to fetch the whole of SKILL.md from GitHub at the start of every session to compare it with the saved copy. Now it fetches `skills/apologetics-boot-camp/VERSION`, one line, and fetches SKILL.md only if the stamps differ. After any change to SKILL.md, `python3 measure/checks.py --stamp` sets the stamp in both files, and the new `skill-stamp` check fails if they fall behind.

**Measure changes** (separate commit): `checks.py` reads the split files as one text, and has the `skill-stamp` check and the `--stamp` flag.

**Script checks after the changes:** all pass except `saved-skills`, which differs until the author saves the proposed update to his saved boot camp skill.

No conversation test was run on these changes. The next run's baseline is the first on this layout, and the first on main since the changes of Nov 25.

