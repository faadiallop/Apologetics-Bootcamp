# The measure

This folder and `skills/apologetics-boot-camp/evals/` hold the tests the boot camp skill is judged by. Only the author changes them, with one exception: the weekly improvement run may add a new conversation test, as "Tests added by the weekly run" allows below. Whatever improves the skill, a person or a scheduled run, may read the measure and run it, but may not alter anything already in it.

## Why the measure stands outside

**A measure that moves to suit the result measures nothing.** "A false balance is abomination to the LORD: but a just weight is his delight" (Prov. 11:1). "Divers weights, and divers measures, both of them are alike abomination to the LORD" (Prov. 20:10). The quickest way to raise any score is a lower pass line or a softer opponent, so the pass lines, and how hard the member argues, belong to the measure too.

**No one grades his own work.** Those "measuring themselves by themselves, and comparing themselves among themselves, are not wise" (2 Cor. 10:12), for "he that is first in his own cause seemeth just; but his neighbour cometh and searcheth him" (Prov. 18:17). So a change to the skill is graded by a grader that did not make it, and a test the weekly run adds is written by an agent that did not make the change and never saw it.

## What it measures

Three kinds of test, the cheapest first.

### 1. Script checks (`measure/checks.py`)

What a script can settle. Run `python3 measure/checks.py` from the repo. It reports PASS, FAIL, INSPECT (for a person to look at) or SKIP.

| Check | Passes when |
| --- | --- |
| `kjv-quotations` | Every quoted line followed by a Bible reference matches the King James text word for word. A quoted line that comes after its reference is only listed for a person to look at. Lines that are not quotations are named in `not-kjv-quotations.md` |
| `references-exist` | Every chapter and verse cited exists |
| `named-files` | Every file the skill, the README and CLAUDE.md name exists, and every SOP has its table in the response bank and its plan in the training plans |
| `bank-rows` | Every bank row a training plan names is in the response bank. Opponents the bank does not define are listed for a person to look at |
| `saved-skills` | The saved copy of each skill matches GitHub. Skipped on a machine with no saved copies |
| `skill-stamp` | The stamp in SKILL.md and in `VERSION` matches the skill's text, so a saved copy can tell from one line whether it is current. After any change to SKILL.md, `python3 measure/checks.py --stamp` sets both |
| `skill-length` | SKILL.md is under 500 lines |

One check is left to the run that syncs the *Apologetics SOPs* doc: that each tab matches its file (CLAUDE.md).

### 2. Conversation tests (`skills/apologetics-boot-camp/evals/`)

Each test hands the coach one moment and checks what it does next. Each is a folder in the layout that skill-creator and `claude plugin eval` read: `prompt.md`; `case.yaml`, which says what a good result is and which part of the skill it guards; one statement per file in `graders/`; and the transcript and the trainee's card in `files/`.

**Marking tests** give the coach a finished practice conversation with planted hits and misses.

| Test | The coach must |
| --- | --- |
| `marks-missed-requests-for-reasons` | count two hits out of four on the drilled tactic, quote a line he missed with, and not pass him |
| `refuses-a-false-pass` | refuse to pass a trainee who knew every passage and stayed kind but never used the drilled tactic |
| `fails-a-round-on-character` | fail a well-argued round in which the trainee mocked the man |
| `passes-without-chapter-and-verse` | pass a trainee who says the passages correctly without references, and count one pass as the first of two |
| `notes-awkward-wording-without-marking-down` | count a clumsy but working request for reasons as a hit, never mark it down, and offer a smoother wording |
| `notes-a-clumsy-way-back-without-marking-down` | the same for a clumsy but working way back to the topic, so the note is tested beyond requests for reasons |

**Next-turn tests** give the coach a practice conversation up to the trainee's latest line.

| Test | The coach must |
| --- | --- |
| `pauses-on-a-drilled-miss` | call a short time-out when he misses the tactic he is drilling |
| `no-pause-for-an-undrilled-miss` | stay in the role-play when he misses a tactic he is not drilling |
| `lets-a-second-miss-pass` | stay in the role-play when a second miss comes right after a pause |
| `member-neither-invents-nor-folds` | as the member, give ground like a cornered person or give one more recorded answer, invent nothing, and leave his argument for him to finish |
| `closes-when-he-crosses-early` | close the round in a sentence when he tells the gospel before the round's goal is met, leave how he told it out of the coaching, and count the claim he crossed past as a miss |
| `answers-his-time-out-briefly` | answer his own time-out with one move in a few sentences |
| `ends-the-round-when-the-goal-is-met` | end the round as soon as its goal is met and he has used his two closing turns, remind him that her leaving was the moment to turn to Christ, and still count the pass |

**Opening tests** give the coach a trainee's first message.

| Test | The coach must |
| --- | --- |
| `opens-for-a-beginner` | introduce the training to a beginner without asking what he has already said, and without quizzing him on what it has not taught |
| `offers-to-draft-for-a-new-group` | say there is no material for a new group, offer to draft it for approval, and teach nothing for that group meanwhile |

**Tests added by the weekly run.** The weekly improvement run may add a conversation test when real sessions show a weakness that no test here covers. Each is a folder in `evals/` like the others, and the `expected_outcome` in its `case.yaml` opens with "Added by the weekly run" and the date. The journal (`loop/journal.md`) names each one. They are not listed in the tables above until the author has reviewed them. A test is added only if all of these hold:

1. **The weakness is real.** At least two independent pieces of evidence from real sessions or cards show it.
2. **Another hand writes it.** A separate agent writes the test from the evidence and from the skill on `main`. It never sees the fix, and the agent that makes the fix does not read the test's statements until the result is settled.
3. **It is no softer than the rest.** It has the same layout, invented names and words, and statements a grader can judge. It sets no pass line, changes nothing in how hard the member argues, and makes no doctrinal claim.
4. **It fails first, then passes.** It fails on `main` in at least two of the three runs (rule 7 under "Rules for every run"), and it passes in all three on the changed copy, which breaks no other test.
5. **It stays.** Once a test is added, no run changes or removes it. The author may rewrite or remove any of them.

### 3. Live rounds (`measure/live-rounds/`)

A whole session between the coach and a simulated trainee who has planted habits. Each file gives the trainee's instructions and what the grader checks. A live round needs a run that passes turns between two agents, so `claude plugin eval` cannot run it.

| Round | The trainee | What is checked |
| --- | --- | --- |
| `beginner-is-taught-before-tested` | Lydia, new to Muslims | teaching in short pieces, never asking what is untaught, teaching again after a miss |
| `drills-his-hard-tactic` | Daniel, who answers claims instead of asking for reasons | three chances a round, rare and short pauses, true counts, the card saved as he goes |
| `keeps-him-on-the-one-question` | Silas, who takes up every burden and follows every side issue | side issues from the materials, a pause for a burden he never claimed, the on-topic score |

## What it does not measure

- **Whether the teaching is true.** Scripture judges that (Isa. 8:20), and the author answers for it (Jas. 3:1). The script checks only that quotations are exact.
- **Voice.** A written test cannot hear a call: its mis-hearings, its pauses, its time limit.
- **Whether a trainee truly learns.** A simulated trainee shows that the coach follows the skill, not that the skill makes anyone capable. That shows only in real trainees: their training log, their conversations in the field, and whether they can train another (Luke 6:40; 2 Tim. 2:2).

## Rules for every run

1. **Fix the copy under test.** The skill tells the coach to fetch the GitHub copy and never to use a local one. In a test that would make every version behave like `main`, so each prompt says which copy is the true one for that run.
2. **Stay out of the real training log.** Each test brings its own log file, and the coach reads and saves cards there.
3. **Keep the grader apart.** The grader sees the statements and what the coach did. It is never the one that made the change being tested.
4. **Weigh old and new on the same tests.** A change is kept only if it does better than the copy on `main` and breaks nothing that passed.
5. **Keep trainees out of this repo.** The repo is public. Trainees in the tests have invented names and words, and nothing is copied from the real training log (Prov. 11:13).
6. **Never change the skill and the measure in one commit.** A commit that changes one leaves the other alone. A test added by the weekly run comes in a commit of its own, before the fix it was written for.
7. **Run every test three times: twice with Sonnet, once with Opus.** Trainees may train with either model, and most are expected to use Sonnet, so every conversation test and live round is run three times on the same copy: twice with Sonnet as the coach and once with Opus. A model does not answer the same way every time, so one run can pass or fail by chance. A statement passes only if it passes in all three runs. It fails if it fails in at least two; one that fails in only one run is unsteady, and is not by itself evidence of a weakness. Report each model's score separately, and name the model behind each failure. The grader is always Opus, whichever model coached, and is not told which model wrote the answer. On Nov 27, 2026, a slip on crossing to the gospel early showed up only with Sonnet; a run on Opus alone would have missed it.

## Running it

- **Script checks:** `python3 measure/checks.py`. The first run fetches the King James text and checks it against a fixed checksum.
- **Conversation tests:** with skill-creator, which runs each case on the copy under test and on the copy from `main`, then grades both. Or, from `skills/apologetics-boot-camp/`, `claude plugin eval . --allow-tools Write,Edit,Bash --scaffold`. Either way these are real model runs. Run each case twice with Sonnet and once with Opus as the coach (rule 7), with Opus as the grader.
- **Live rounds:** by a run that can pass turns between a coach, a trainee and a grader.

## Changing the measure

Only the author changes a test, a pass line, how hard the member argues, or these rules. The weekly run may add a test as "Tests added by the weekly run" allows, and nothing more. Anyone may propose a change, in a pull request of its own that names the real conversation or the failed test that called for it.
