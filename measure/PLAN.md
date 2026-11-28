# Plan: verifying every change so it can merge itself

The plan for checking each change to this repo well enough that it can merge without the author, and for the agents that will propose those changes. The author approved it on Nov 27, 2026; an independent review the same day changed it in the ways noted at the end. The build order says what is done.

## 1. Merging is not publishing

The skill tells every coach to fetch `SKILL.md`, the thought-and-word rules, `sops/` and `fixed/` from the `main` branch at the start of each session (`SKILL.md`, "Always use the GitHub copy"). Saved copies on phones do the same: when `main`'s `VERSION` differs from their own stamp, they fetch `main`'s `SKILL.md` and follow it. So whatever is on `main` reaches every trainee in his next session.

So **`main` becomes the release branch, and changes merge into a branch called `next`.** Nothing reaches `main` except through a release (section 7), and every link in the skill, and every saved copy already on a phone, keeps working unchanged. This does what the `live` tag in the first draft was for, without changing a URL.

No check can approve whether the teaching is true. The measure says so ("What it does not measure"): Scripture judges that (Isa. 8:20), and the author answers for it (Jas. 3:1). Checks can show that a change is well formed, quotes Scripture exactly, breaks nothing and coaches better. So the plan:

- **sorts each change by what it touches** (section 2);
- **checks each class as hard as its risk calls for** (sections 3 and 4);
- **publishes only through a release the author can stop** (section 7), and leaves doctrine to him throughout.

## 2. Sort every change into a tier

A script decides the tier from which files changed and which lines in them, not a model, since a model can be talked into a lower tier. A model review may raise a change's tier, never lower it. **Anything not listed below is Tier 2.**

| Tier | What it covers | How it merges into `next` |
| --- | --- | --- |
| **0. Records and reverts** | Additions only to `loop/journal.md` and `loop/harvest-log.md`; any revert | As soon as the script checks pass |
| **1. Behaviour** | Lines of `SKILL.md` that carry no Scripture and lie outside its sections A ("Why we train") and C ("The models, measured against Scripture"); response bank rows that hold only a member's words with a public source; new conversation tests that meet section 5; on the site, `public/index.html`, `src/engine.ts`, `src/round.ts`, `src/materials.ts` and `test/` | As soon as every check that applies passes. The author can still stop it at release (section 7) |
| **2. Author only** | Everything else, including what is listed below | Never by itself |

Tier 2 includes:

- sections A and C of `SKILL.md`, and any line in the skill that carries Scripture;
- all of `sops/` except the member's-words rows above, and all of `fixed/` and `site/prompts/`;
- any response bank row drawn from trainee logs, and any reply in a row;
- anything already in `measure/`, including a pass line and these rules;
- the rule skills, `writing-dialogue`, `CLAUDE.md` and `README.md`;
- on the site: `src/index.ts`, `src/anthropic.ts`, `src/auth.ts`, `src/quota.ts`, `src/pricing.ts`, `public/admin.html`, `schema.sql`, `package.json`, `package-lock.json` and all of `wrangler.jsonc`, since these hold the money, the sign-ins and the data;
- `.github/`, which holds the CI and the list of protected files.

The checking code is in `measure/` and `.github/`, so it is Tier 2: no one grades his own work, for "he that is first in his own cause seemeth just; but his neighbour cometh and searcheth him" (Prov. 18:17).

A change takes the highest tier of anything in it. These also go to Tier 2: a change over the size cap; one that changes both `skills/` and `measure/` (rule 6 of the measure); and a Tier 1 change to the skill that reaches no test (section 4), since nothing would then check it.

**The author's own sign-off.** GitHub does not let a person approve his own pull request, and Claude's cloud sessions push and open pull requests as the author's own account. So the agents' pull requests are opened by a GitHub App, "bootcamp-agents": an agent pushes its work to a branch named `agent/...`, and a workflow holding the App's key opens the pull request in the App's name. The App can write branches and pull requests, but cannot change `.github/` (it has no permission over workflows) and cannot update `main`. The author approves a Tier 2 change by approving the App's pull request. His own changes are Tier 2 by being his: he merges them himself, as a bypass of the branch rules on `main`. A second App, used only by the release (section 7), is the only other thing allowed to update `main`.

## 3. The checks, cheapest first

**A. May this PR merge itself at all?** It was opened by the agents' App (section 2); a PR from anyone else, or from a fork, never merges itself. No history was rewritten. A secret scan finds nothing. It is under the size cap and makes one change.

**Keeping the checks honest.** A PR could change the CI or the checks themselves to let itself through, or to read the secrets CI holds (the API key, the name hashes). So the checks always run from `next`'s copy of `.github/` and `measure/`, never the PR's; and the jobs that need a secret run only in a protected GitHub environment that a PR's own code cannot reach.

**B. Script checks** (`measure/checks.py`; no model; seconds)

- The checks listed in the measure's README: King James quotations (now including the fixed pieces and the site's prompts), references, named files, bank rows, the stamp, the fixed pieces and the skill's length.
- **Compared with `next`.** Some checks report INSPECT: something a person should look at, which a script cannot judge. An INSPECT item that the change brings in blocks it from merging itself.
- **Additions only, where records must not change.** In the journal, the harvest log and the response bank, no existing line changes and no row is given a new number, since the training plans cite rows by number.
- **Protected text untouched.** Lines carrying Scripture, approved fixed files, and the `Status:` lines of the fixed files.
- **Links and planted instructions.** No new web address outside a list (the King James source, this repo, the harvest's sources), and no new text that tells the coach to fetch, ignore or obey something. A word filter is easily dodged, so this check only catches the careless; review E is the real guard.
- **Privacy.** No email addresses or phone numbers, and no real trainee's name. The names are kept as scrambled codes (hashes) in a CI secret, refreshed from the site's list of users, since the repo is public (measure rule 5).
- **Test layout.** Every test folder has `prompt.md`, `case.yaml`, `graders/` and `files/`, and the README's tables list every test except those still awaiting the author's review.

**C. The site** (when `site/` changes): `npm run typecheck`, `npm test`, `npm run check-bundle`. Deploying stays a separate step after release.

**D. The measure** (when `SKILL.md`, `sops/`, `fixed/` or `site/prompts/` change): section 4.

**E. Independent model reviews,** each by a fresh agent that never saw how the change was made: one against the thought-and-word rules; one for doctrine, which reads the change with the SOPs and Scripture and sends anything that contradicts them to Tier 2; and one for planted instructions, which reads every new line of untrusted text (above all, member's words in the response bank). These can only raise a tier.

**The merge rule.** A Tier 0 change merges when B passes. A Tier 1 change merges only when every check that applies passes and two independent kinds agree: the scripts (B) and the measure (D) for the skill, or B and the site checks (C) for the site. "At the mouth of two witnesses, or at the mouth of three witnesses, shall the matter be established" (Deut. 19:15).

## 4. Running the measure for as little as it can cost

The measure will run constantly, so it is split between each PR and each release. Rule 7 in the measure's README is changed to say so.

**On each PR, a screen:**

- No model runs unless the skill's text changed (`SKILL.md`, `sops/`, `fixed/`, `site/prompts/`).
- Only the tests the change can reach: those whose `case.yaml` guards the part of the skill that changed, and those that use the group whose materials changed. A change that reaches no test goes to Tier 2.
- One run, with Sonnet, since most trainees use it.
- No runs of `next` itself: the PR is compared with results stored for `next`, refreshed after each merge for the tests that merge could reach.
- Where a statement's result differs from the stored one, that test runs twice more (Sonnet, then Opus), and two of three decides. For the weekly run's change, which must do better than before (rule 4), this is where the improvement is confirmed.

**At each release, the full measure:** every test three times, twice with Sonnet and once with Opus, graded by Opus; and the live rounds when `SKILL.md` changed. This also catches two changes that each passed alone but clash together.

**How the calls are made.** The screen uses a small program that sends each test straight to the API, as the site's coach does (`site/src/anthropic.ts`), instead of a full agent session per test. The skill and one group's materials come to about 50,000 tokens, the same for every test of that group, so they are held in the API's cache; rereading cached tokens costs a twentieth of the normal price on Sonnet 5.5 and Opus 5.5. The runs go through the Batch API, which charges half price for answers no one waits on; inside a batch, cache hits are not guaranteed, so the saving is less than the two together suggest. The screen therefore does not test fetching from GitHub or saving cards; the release run, made as the measure has always run, does. The coach runs at "low" effort, as the site's coach does, since most trainees will train on the site (the author, Nov 27, 2026).

**Spending.** By file sizes and list prices, one test with its grading should cost a few cents, a PR touching five tests under a dollar, and a release a few dollars. These are estimates; the first release measures the real figures. Before it sends a batch, the program works out its most possible cost and refuses to send it over the cap (about twice the measured cost of that kind of run), since a batch cannot be stopped partway. A spending limit on the Anthropic workspace is the backstop.

## 5. Adding tests and checks automatically

No existing test or check is changed or softened without the author. Within that, the rest runs by itself. The measure's README is changed to allow it: it now lets "an agent" add tests under these conditions, not the weekly run alone, and says that this is the one way `measure/` changes without the author.

**Conversation tests.**

1. *What needs a test.* A coverage map, built from each `case.yaml`, lists every part of `SKILL.md` and the tests that guard it. A test is written for, in order: a change that had to be reverted; a finding from the logs with two independent sessions (section 6); a part of the skill no test guards.
2. *Written by another hand.* The test writer works from the finding and the skill on `next`, and never sees a fix.
3. *Proved before it counts:*
   - layout, invented names, and nothing copied from the logs;
   - it guards what it claims: on a copy of the skill with the guarded rule removed, it fails;
   - it fails on `next` in at least two of three runs when a fix is to follow, or passes in all three when it guards a rule the skill already keeps;
   - two separate gradings of the same answer agree on every statement;
   - it sets no pass line, changes nothing in how hard the member argues, and makes no doctrinal claim;
   - it duplicates no existing test.
4. *Added in a PR of its own,* touching no existing file, merged before any fix it was written for. A test that waits on its fix is marked as expected to fail, so it does not block a release; if no fix passes within two weeks, the author is told. The test is not listed in the README's tables until the author has reviewed it, and a script drafts that entry for him.

**Script checks.**

1. A repeated finding that a script could detect becomes a proposed check.
2. It must pass on `next` (or flag only items already listed), raise nothing on the last twenty commits, and fail on a planted case of the fault.
3. The author approves its code once.
4. It reports only (INSPECT) at first, and starts to block (FAIL) by itself after four weeks or ten PRs with no false alarm. A false alarm resets the count and tells the author.

## 6. The agent that reads the training logs

An agent will read what trainees' sessions leave and fix what it finds. The logs bring three new dangers: their text is untrusted (a trainee, or a member quoted in a round, can write an instruction into it); they are private, and the repo is public; and they pull toward softness, since what trainees find hard shows up as complaints.

**Five hands, not one.**

| Step | Who | Sees | Can do |
| --- | --- | --- | --- |
| Read | Reader | The site's logs, and the doc's *Training log* tab | Read the logs, and write findings to the site's `findings` table, through a token that can do only those two things. Cannot push to the repo |
| Sort | Sorter (a script) | Findings | Decide each finding's kind and whether its evidence suffices |
| Test | Test writer | The finding, and the skill on `next` | Write a test (section 5). Never sees the fix |
| Fix | Fixer | The finding, the skill, the test's name | One change on a branch. Never sees the raw logs or the test's statements |
| Verify | CI and reviewers | The PR | Sections 2 to 4 |

A finding has a fixed shape: date, group, the part of `SKILL.md` it concerns, and two short fields for what the coach did and what it should have done. The short fields are still free text, so the sorter limits their length, and review E reads every finding before a fix is written from it.

The reader's token is limited so that the one agent that reads untrusted text can do nothing else even if it is misled; the owner token can also invite people and pause training. The `findings` table keeps findings after conversations are deleted at 14 days, so that two sessions weeks apart can both count, and so that a PR can name its evidence without putting trainees' words in a public repo. The author opens them from the owner's page.

**Kinds of finding.**

| The logs show | What happens | Tier |
| --- | --- | --- |
| The coach broke a rule in `SKILL.md` | A test PR, then a fix PR | 1, under section 2 |
| A new objection or escape | A response bank row, the member's words only | 2 while it comes from the logs |
| A site fault | A site fix with a test | Under section 2 |
| The content looks wrong | An issue for the author, never a fix | 2 |
| Trainees find something hard | A note in the journal, never a fix | none |
| Anything that would change a pass line, how hard the member argues, or the measure | Refused, and noted in the journal | none |

**Evidence.** A fix needs findings from two independent sessions: two trainees, or one trainee on different days. One session counted twice is one witness. The test comes first, in a PR of its own (section 5).

**Further checks on these PRs.** No eight-word run of a PR file matches a stored conversation; the reader's side runs this, so the logs never reach CI. The PR names its findings by number. A fix that reverses a change made in the last eight weeks goes to Tier 2, so the skill does not swing back and forth. At most one fix per run, and none while another fix waits for release.

**Closing the loop.** After release the reader watches for the same finding. If it stops, the journal records the fix as confirmed; if it recurs in two independent sessions, the fix goes to the author with an offer to revert it. Every finding, fix and result goes in `loop/journal.md`.

**To review later.** The reader reads the doc's *Training log* tab as well as the site. That tab is free text and harder to strip of names; the author chose to include it for now, and it should be weighed again once the reader runs.

Trainees are not told that an agent reads their sessions (the author's decision).

## 7. Release: from `next` to `main`

1. **Once a week, on Monday, if `next` has changed and no release is waiting,** a release run fixes on the latest commit of `next`. Only one release waits at a time; changes merged meanwhile go in the next one. (Weekly, not daily, since the full measure is what costs: the author's decision, Nov 28, 2026. A daily run, which makes no model calls, moves `main` once the hold window ends.)
2. **It runs the full measure** (section 4) and every script and site check on that commit.
3. **It sends the author one summary** of every change since the last release, in plain words, with the measure's results and any flag a review raised.
4. **The hold window.** Forty-eight hours later, `main` is moved to that commit, unless the author has replied "hold." The window exists because the checks cannot judge truth or wisdom: it is the author's time to read what trainees are about to hear. He need not act; silence lets the release go. To stop one change, he says which; it is reverted on `next` (Tier 0), and the release runs again without it.
5. **After `main` moves:** check that the stamp the coach fetches is the new one; deploy the site (below); and a scheduled Claude session does what `CLAUDE.md` requires: it updates the *Apologetics SOPs* doc, and proposes each changed skill as a card for the author to save (a card needs his hand). It reports anything it could not do.
6. **If anything fails after release,** `main` moves back to the last good release, the site goes back to its last good version, and the author is told.

**Deploying the site.** The site bundles the skill's files when it is built, so it is deployed with each release, and trainees on the site and in Claude hear the same version.

- **When.** Right after `main` moves, from `main`'s commit, and only if the site's checks (C) passed on it. A release that changes nothing the site bundles (`site/`, `SKILL.md`, the rules, `sops/`, `fixed/`) does not deploy it.
- **How.** `wrangler deploy`, run by the release workflow with a Cloudflare API token that can deploy this one Worker and nothing more. The token lives in a protected GitHub environment named `release`, open to `main` only, so no pull request's code can reach it. The site's own secrets (its Anthropic key, the owner token) stay in Cloudflare, as now, and never enter GitHub.
- **The database is never changed automatically.** If `schema.sql` changed since the last release, the release stops before deploying and asks the author to apply the change himself (the command is in `site/README.md`). A database change is hard to undo, so it waits for his hand.
- **A quick check after deploying.** The release asks the live site for its page and for a sign-in it should refuse. If either answer is wrong, it rolls the Worker back to its previous version (`wrangler rollback`), moves `main` back, and tells the author.
- **By hand, still.** The author can deploy as he does now. The release then deploys again from `main` at the next release, so the site does not stay on a copy that has not passed the checks.

Only the release App and the author can move `main`: a branch rule in GitHub forbids every other update to it.

## 8. Where the files live

`measure/` is the one home for checking; only the author changes it, except for tests added under section 5. The conversation tests are in `measure/evals/`, so they no longer travel with every install of the skill, and "never change the skill and the measure in one commit" is a check on two paths. The fixed pieces' check is part of `measure/checks.py`. The tier script, the test program and the coverage map will go in `measure/` too. The site's own tests stay in `site/test/`, where `npm test` expects them. CI lives in `.github/`.

## 9. What the author does himself

- In GitHub's settings: protect `main` and `next` (section 7); create the agents' App and, at step 4, the release App (section 2); and set up the protected environments that hold their keys and CI's other secrets (section 3).
- Set a spending limit on the Anthropic workspace the tests use. The tests draw on the API credits that come with his Max plan, through a workspace of their own, kept apart from the site's.
- At step 4: make a Cloudflare API token that can deploy only this Worker, and put it in the `release` environment.
- Read each release summary when he can, and reply "hold" to stop one.
- Approve or merge Tier 2 changes, approve each new script check's code once, and review added tests when convenient.
- Save the skill cards each release proposes.

## 10. Build order

1. **Protection, without self-merging.** Move the tests to `measure/evals/`; fold in the fixed check; extend the King James check to the fixed pieces and the site's prompts; change rule 7 and the rule on added tests in the measure's README; CI running the script and site checks on every PR; a CODEOWNERS file for Tier 2 paths. *Done Nov 27, 2026, except what needs the author's hand in GitHub's settings (section 9).*
2. **`next` and sorting.** *Started Nov 27, 2026: `SKILL.md` no longer has the coach commit new objections; the tier script (`measure/gate.py`) runs in CI and only reports; the workflow that opens agents' pull requests through the App (`.github/workflows/agent-pr.yml`); `next` created. Still to come: the privacy check's name hashes. The weekly run is to be redone from the start (the author's decision), so it is not pointed at `agent/` branches. Until the release (step 4) exists, the author's own changes still merge into `main`, and `next` is brought up to `main` after each.* Create `next`; point the agents' PRs at it; the tier script and the new B checks, run beside the author for a few weeks to see whether they sort as he would. Change `SKILL.md` so the coach puts a new objection on the trainee's card or in an issue, and no longer commits it to the Response Bank itself (now line 277), since that bypasses every check here.
3. **The measure in CI.** The test program, the coverage map, the PR screen and stored results, with spending limits. *Started Nov 27, 2026: `measure/run_tests.py` (the test program, through the Batch API with caching, refusing any batch that could cost more than its cap), `measure/coverage.py` (the coverage map, now also used by the tier script, so a change to the skill that reaches no test goes to Tier 2), and the `measure` workflow (the screen on each pull request, and a full run by hand). Until the Max plan's API credits can be claimed, the tests run on the author's subscription through Claude Code's own runner (`--engine claude-code`), with the token `CLAUDE_CODE_OAUTH_TOKEN` in the `measure` environment; a pull request's screen then uses the base branch's tests and settings, so that nothing a pull request wrote runs beside the token. One test was run this way on Nov 27 and passed.*
4. **Release.** The weekly release run, the summary and hold window, moving `main`, the site deploy, and the move back on failure. Change `CLAUDE.md` so the copies are updated after a release, not after each push. *Built Nov 28, 2026: `.github/workflows/release.yml`, with its decisions in `measure/release.py`; the summary is an issue labelled `release`, assigned to the author, and he holds it by commenting "hold". `CLAUDE.md` now has the copies follow `main` after each release. It cannot move `main` until the author has done his part of section 9 (the release App, the `release` environment with the Cloudflare token, `measure` allowed for `main`), and the schedule runs from `main`'s copy of the workflow, so the first release is the author's own merge of `next` into `main`. Still to come: the scheduled Claude session that updates the copies after each release, and the live rounds at release.*
5. **Merging itself.** Tier 0 first, then Tier 1, once step 2's record shows no Tier 2 change sorted lower.
6. **Adding tests and checks** (section 5).
7. **The log reader and fixer** (section 6): the reader's limited token and the `findings` table on the site, the private check against stored conversations, and the refresh of the name hashes; at first proposing PRs only, with no self-merging, until its findings are seen to match the author's judgment.

## What the review changed

An independent review on Nov 27, 2026 found these, and the plan above now meets them:

- Saved copies follow `main`'s `SKILL.md` when its stamp changes, so a `live` tag would not have kept unreleased changes from trainees. Changes now merge into `next`, and `main` is the release.
- A PR could change the CI to read its secrets or pass itself. The checks now run from `next`'s copy, with secrets kept apart.
- Several site files that hold the money were Tier 1; anything unlisted had no tier. They are now Tier 2, as is anything unlisted.
- A change that no test reaches would have passed the measure untested. It now goes to Tier 2.
- A test and its fix in one PR would have touched both `skills/` and `measure/`. They are now separate PRs.
- Batch spending can't be stopped partway, so the limit is now checked before a batch is sent.
- Two tests, `steamroller-steps-in-order` and `teaches-a-new-tactic-first`, were missing from the README's tables. They are now listed.

The review also suggested holding any release that changes `SKILL.md` until the author has opened its summary, and keeping member's-words rows in Tier 2 until review E has a record of catching planted instructions. The author declined both on Nov 27, 2026: a release that changes `SKILL.md` goes out when its hold window ends, as any other does, and member's-words rows from public sources stay in Tier 1. Rows drawn from trainee logs stay in Tier 2 (section 6).
