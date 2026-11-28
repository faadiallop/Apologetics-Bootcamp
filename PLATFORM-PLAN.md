# Plan: from one skill to a training tool for every Christian

**Status: a draft for the author's approval, written Nov 28, 2026. Nothing in it is built, and nothing will be until he approves it.** Section 13 lists the decisions it needs from him.

## 1. The goal, and what governs it

**The goal.** Any Christian, in his own language, on the phone he already has or in his car, can train by voice to answer any false religion or cult on any question it raises, until he can do it himself and train another. Agents improve the tool every day; checks keep it from drifting or breaking; those who oppose it cannot corrupt it, drain it or expose its trainees; and it costs little enough to give away.

**What governs it.** Christ sent his people to "teach all nations" (Matt. 28:19; Acts 1:8), and what is learned is to be committed "to faithful men, who shall be able to teach others also" (2 Tim. 2:2; Titus 2:3–4). Four things follow for this plan, each from the author's own request:

| He asked for | Scripture | What the plan does |
| --- | --- | --- |
| Every language | "how hear we every man in our own tongue, wherein we were born?" (Acts 2:8; Rev. 7:9) | Section 5 |
| Checking without drift | "Prove all things; hold fast that which is good" (1 Thess. 5:21; Acts 17:11) | Section 7 |
| Security against opponents | "be ye therefore wise as serpents, and harmless as doves" (Matt. 10:16; Neh. 4:17) | Section 9 |
| Low cost | "freely ye have received, freely give" (Matt. 10:8; Luke 14:28) | Section 10 |

**What no part of this plan may do.** No check, agent, translator or reviewer here decides what is true. Scripture judges the teaching (Isa. 8:20), and the author answers for it (Jas. 3:1), as `measure/PLAN.md` already says. Every part below is built so that more work can be done without that judgment passing to a machine.

## 2. What stands today, and what is missing

**What stands** (read from the repo on Nov 28, 2026):

- **The skill**: `SKILL.md`, five groups with one argument each (Muslims, Jehovah's Witnesses, Jewish people, atheists, icon veneration), each with an SOP, a response bank, a training plan and draft fixed pieces. English only.
- **The measure**: script checks, 17 conversation tests, three live rounds, and an approved plan for sorting, checking and releasing every change (`measure/PLAN.md`). Its build steps 1 to 4 are built or started; steps 5 to 7 (merging itself, added tests, the log reader) are not.
- **The site**: a Cloudflare Worker that runs the coach by voice for the owner and those he invites, with spending limits sized for $20 a month and five testers. No trainee has used it yet (`loop/journal.md`, Nov 27).

**What is missing, set against the goal:**

| The goal needs | Today |
| --- | --- |
| Any topic for a group | One argument for each group; the file layout allows no second one |
| Any language | English only, in the text, the speech and the King James check |
| Phone apps, and the car | A web page; no installable app |
| Agents improving it daily | The checking is half built; the weekly run is to be redone; no agent runs on a schedule |
| Safety against opponents | Good for five invited testers; not designed for strangers or for hostile countries |
| A cost that scales | About $3.50 a trainee a month at the cap, paid from one pocket |

## 3. Five decisions that shape everything else

Each is a recommendation with its grounds. The author's answers are asked for in section 13.

**1. One engine, thin apps.** The Worker keeps all the logic: who speaks, the prompts, the limits, the content. The web page, the iPhone app, the Android app and the car screens only listen, send text, receive text and speak. Grounds: every surface then runs the engine the measure has already tested, so one check covers four surfaces; and a fault is fixed by rolling the server back in minutes, where an app already installed on a phone cannot be recalled.

**2. One source, generated copies.** Each piece of teaching is written once, in English, in the repo. Everything else is made from it by a script and carries its stamp: the site's bundle, the apps' content, each translation, the reading copy. Grounds: `CLAUDE.md` already records that hand-kept copies "fall behind"; and a script can tell a stale copy from a current one by its stamp at no cost, as `VERSION` does today.

**3. Scripts place Scripture; models never write it.** Wherever the trainee hears Scripture, in any language, the words come from a stored Bible text by reference. Grounds: the King James check already catches a misquoted verse only after it is written, and this prevents it; and in a language the author cannot read, it is the one way he can know that the verse was not altered.

**4. The author's attention is the scarce thing, so the plan spends it only where no check can stand in.** Agents may produce far more than one man can read. So the plan caps how much waits for him, gives him one summary a week, and lets him appoint reviewers under him (section 8). Grounds: Moses could not judge every matter alone and set able men over the smaller ones (Exod. 18:17–22; Acts 6:2–4); and the measure plan already rests on this split, where scripts and tests clear Tier 1 and doctrine waits for him.

**5. Build in stages, and open each to no more people than its checks can bear.** Grounds: "which of you, intending to build a tower, sitteth not down first, and counteth the cost, whether he have sufficient to finish it?" (Luke 14:28; Prov. 24:27); and the site's own limits were sized this way, for five testers before more.

## 4. Content: any group, any topic

**The change.** Today a group has one argument. The goal needs many: for Muslims, the Islamic Dilemma (written), then child marriage, the crucifixion, the deity of Christ; for Jehovah's Witnesses, the Bread of Life (written), then the deity of Christ, the name Jehovah, 1914; and so on for each group.

**The layout.** A group keeps what is common to it once (the foundation, the background, its beliefs and terms, its personas). Each topic under it is one argument in the standard template, with its own response bank, training plan, fixed pieces and tests:

```
skills/apologetics-boot-camp/content/
  manifest.json                  made by a script: every group, topic and language, with status and stamp
  en/
    shared/                      overview, methodology, the shared rubric and personas
    islam/
      group.md                   A and B of today's SOP: said once for the group
      islamic-dilemma/           sop.md  bank.md  plan.md  fixed.md
      child-marriage/            the same four files
```

It stays inside the skill's folder so that an install of the plugin still carries it. The coach loads the group file and one topic, never the whole group, which also keeps each call small (section 10).

**Moving without breaking.** Saved copies on phones fetch today's paths from `main`. So the new layout is added beside the old; the skill is changed to read the manifest; and the old paths are removed only at a later release, once the stamps show the saved copies have moved over. No release ever leaves a coach pointing at a missing file; `named-files` already checks this.

**A topic's life.** `proposed → sourced → drafted → approved → tested → released`, and then the same for each language. Only an approved topic is used with trainees, as only an approved fixed file is today.

**The rule for sources.** Every claim about what another religion teaches rests on that religion's own texts, quoted with edition and reference, stated as its members would state it, with two witnesses. The template already requires this (`00-overview-and-template.md`, parts B and C). Three grounds for holding to it without exception as topics multiply: it is true dealing (Exod. 20:16; Prov. 18:13); it is the argument's strength, since the method works inside the other side's own authority; and it is the defence if a store or a court is told the app slanders a religion (section 9). Hard topics such as child marriage are put as questions about the person's own sources, "with meekness and fear" (1 Pet. 3:15; 2 Tim. 2:24–25), and the rubric already fails a round on mockery.

**Checks that grow with the topics:**

- **Quotations match their source, for every registered text.** The King James check becomes one check that takes a list of texts: the King James Bible, each language's Bible, and each other text that can lawfully be stored (a public-domain Qur'an translation, for one). A quotation from an unregistered source is listed for a person to look at.
- **Citations exist.** An agent that did not write the topic opens each cited source and confirms the quotation is there, in context. It can only raise a flag.
- **Template and witness counts.** A script confirms that every part of the template is present and every premise and reply names at least two sources.
- **A standard set of tests for each topic,** written from the topic by a hand that did not draft it: the coach states the argument as the SOP does; the member says only what the bank records; the coach catches a planted error of fact by the trainee; the gospel is not altered. The 17 tests of the coach's conduct stay as they are and run across a rotating sample of topics.

**Which topic is next.** A queue the author orders. It is fed by what trainees ask for (a count, kept without their words), by what members actually say in debriefed field conversations, and by the harvest of public sources.

## 5. Every language

A language is ready only when eight things are ready. Translation of the text is one of them.

| # | What must be ready | How |
| --- | --- | --- |
| 1 | A Bible in that language | The author, with the language's reviewers, chooses one translation whose text may lawfully be stored (public domain or licensed). Scripts place every verse from it (decision 3). For English this stays the King James Version |
| 2 | The other group's texts in that language | The editions its members actually read there, registered for the quotation check where lawful |
| 3 | A list of fixed terms | The names of the tactics, "supporting verses", and the words doctrine turns on (person, nature, begotten). The reviewers approve the list once; a script enforces it |
| 4 | The teaching, translated | See the pipeline below |
| 5 | What members say there | A Muslim in Jakarta does not argue as one in London does. The response bank is harvested afresh from sources in that language; a translated bank is only a start |
| 6 | Speech on the phone | The phone's own speech recognition and voice must handle the language well, since they are free (section 10). Where they do not, the language waits, or the author accepts a cost for each minute |
| 7 | The coach in that language | The measure is run in the language, and must pass at the English pass lines before trainees meet it |
| 8 | Two reviewers | Native speakers, sound in doctrine, whom the author appoints. Nothing in their language is approved without both (Deut. 19:15; 2 Cor. 13:1) |

**The pipeline for item 4.** The approved English is the source, cut into numbered units.

1. A translator agent translates a unit, leaving every verse as a reference for the script to fill.
2. A second agent, which never sees the English, translates it back.
3. A third compares the two English texts and flags any change of meaning.
4. Scripts fill the verses, enforce the term list, and check the layout and word limits.
5. The two reviewers read it and approve it, or correct it.

**Keeping translations from drifting.** Each translated unit carries the stamp of the English it was made from. When the English changes, a script marks the unit stale, with no model call. An English change marked as a **correction** (the old text was wrong) withdraws the stale translation at once, and the coach falls back to saying that the piece is being revised; an **improvement** leaves the old translation in use until the new one is approved. The author marks which it is.

**What stays in English.** The coach's instructions (`SKILL.md`) stay in English, so there is one engine to test. Everything the trainee hears as teaching comes from the approved translation. The coach's own remarks (a hint, a score, a correction) are composed in the language as he speaks; item 7 and the term list are what check them, and this is the weakest link in a language the author cannot read.

**Order of languages.** By where the need is, where two reviewers can be found, and where the phone speaks the language. Reviewers take longest to find, so that search starts first (section 11). The first language is a pilot, to learn the real cost in the author's time.

## 6. The apps: web, phone and car

**The path, cheapest first:**

1. **The web page, made installable** (a "progressive web app"): an icon on the home screen of any phone, with no store and no fee. This reaches both kinds of phone, in every country, while the native apps are built, and it remains the one channel no store can take away (section 9).
2. **An iPhone app and an Android app,** each thin (decision 1): sign in, choose a group and topic, one screen for talking, and the trainee's progress. Each uses the phone's own speech recognition and voice.
3. **The car.**

**Why two small native apps, not one shared codebase.** The car screens must be written with each platform's own tools in any case; so must the speech; and beyond those the apps hold only a few screens. A shared layer would add a large dependency to save little. The cost is two codebases that can drift apart, which section 7 guards against with one written contract and one scripted session that both must pass. The alternative, if the author prefers it, is a shared codebase (React Native or Flutter) with native car and speech parts; it would reach the stores a little sooner and carry more to keep up to date.

**The car.**

- **iPhone (CarPlay).** Since iOS 26.4 (March 2026) Apple allows voice-based conversational apps in CarPlay. The reported rules fit a voice-only coach closely: the app must be granted an entitlement by Apple, start by voice, use no wake word, show at most three screens built on Apple's voice template, and show no text of the replies. Apple approves each request, so the request goes in early (section 11). These rules are from press reports; Apple's own CarPlay guide is to be read before building.
- **Android (Android Auto).** I found no category for third-party conversational apps; the published categories are navigation, media, calling and messaging, points of interest, smart-home devices and weather. Until Google opens one, Android in the car works two ways: the phone app over the car's Bluetooth, which works in any car; and the fixed lessons offered as audio through Android Auto's media screens. This is to be checked again when the car stage begins.
- **Safety.** A practice round asks more of the mind than a podcast does. Section 13 asks the author whether the car offers full rounds, or only lessons, review and recall drills.

**What a trainee can do with no network and no cost:** hear the approved fixed lessons, stored on the phone, and drill the key passages, with the phone comparing what he said to the stored verse. Practice rounds need the network.

**Design rules for every surface** (from the platform makers' guidelines): each platform's own conventions; text that scales with the phone's setting; right-to-left layout for Arabic, Urdu and Persian; sound and a visible state for every action, since nothing is read; and nothing that needs the eyes in the car.

## 7. Verification: no drift, no regression

`measure/PLAN.md` stays the base: tiers, scripts first, the measure on each change and in full at each release, the hold window, and the rule that nothing already in the measure is softened without the author. This section adds what the larger tool needs.

**Drift: seven kinds, each with its guard.**

| What drifts | Guard |
| --- | --- |
| Copies from their source | Decision 2: copies are generated and stamped; a script fails any copy whose stamp is old. Fewer copies are kept by hand (section 13, decision 9) |
| A translation from its English | Stamps on each unit, and the correction rule (section 5) |
| The teaching, by many small changes | Lines of Scripture stay protected and doctrine stays Tier 2, as now. Added: a short **statement of what the boot camp affirms and denies**, written by the author, which a reviewing agent checks every content change against. It can only raise a flag |
| The coach, by changes that each passed alone | The full measure at each release, as now. Added: a **held-back set** of tests kept in a private repo, run only at release and never shown to the agents that write fixes. Agents can read every test in this public repo, and what is aimed at too directly stops measuring (the measure's own README says a measure that moves to suit the result measures nothing) |
| The model | Model names are pinned. A new model is adopted only as a change of its own, after the full measure and the live rounds pass on it, in every language in use. A retirement notice from Anthropic opens that work at once |
| The apps from the engine | One written contract for the engine's interface (`/v1`), checked on both sides. Recorded sessions from each released app version are replayed against every new engine, so an old app in someone's pocket keeps working. The engine can tell an app too old to be safe to update itself |
| What it depends on | Lockfiles, CI actions pinned to exact commits, weekly grouped updates as Tier 2 changes |

**Regression: checks in order of cost.**

1. Script checks: seconds, free, on every change.
2. Unit tests: the site's, and now each app's.
3. Contract tests between apps and engine.
4. Conversation tests: the screen on each change, the full measure at release (as now), with each topic's standard set and each language's run chosen by the coverage map.
5. One scripted voice session from start to finish in each app, on a simulated phone, with the speech fed in as text.
6. Hostile tests (section 9): attempts to pull the coach out of its work.
7. The live rounds, and at each app release a check on a real phone and a real car by a person, since no simulator proves a car.
8. After release: the quick check, the roll-back, and for the apps a staged rollout (a few percent of phones first).

**Measuring the mission, not only the machine.** Counts kept without anyone's words: how many trainees pass each stage, where they stop, how many debrief a real conversation, how many go on to train another, and the cost of each stage passed. These show whether the tool does what it is for. They never move a pass line; that stays in the measure.

**Every failure becomes a test,** as the measure plan already provides (its section 5).

## 8. The agents

**How they work.** Each agent is a scheduled Claude session with one job, the least access that job needs, and a brief that names the author's rule skills. Each pushes to an `agent/...` branch; the agents' App opens the pull request into `next`; the tiers decide what merges. All of this is the measure plan's design, extended to more jobs.

| Agent | Job | Its changes |
| --- | --- | --- |
| Planner | Once a week, reads this plan's backlog, the journal and what is waiting, and hands out the next jobs. Agents do not choose their own goals | Records only |
| Log reader, test writer, fixer | As `measure/PLAN.md`, section 6 | As planned there |
| Harvester | Gathers what members actually say, from public sources, for each group, topic and language | Member's words with a public source: Tier 1 |
| Topic drafter | Takes the next topic in the queue, gathers its sources, drafts the SOP, bank, plan and fixed pieces by the author's rules | Tier 2: the author approves |
| Source checker | Confirms each citation in a draft, independently | Flags only |
| Translator, back-translator, comparer | Section 5 | To the language's reviewers |
| App builders | One feature at a time from the backlog, proved from start to finish before it is offered | Tier 1 or 2 by path |
| Keeper | Dependency updates, the price table, dead links, stale references, the secret scan | Tier 2 |
| Guard | Runs the hostile tests each week against the live coach; reviews changes that touch sign-in or money | Flags only |
| Steward | A weekly cost report, and proposals to lower the cost of a turn, each proved by the measure | Tier 1 or 2 by path |
| Releaser, and the copies updater | As planned | As planned |

**Tiers for the new paths.** Tier 2: every topic's teaching, every translation until its two reviewers approve it, the term lists, the statement of what is affirmed, the apps' sign-in, storage and network code, and anything a store or a user's safety depends on. Tier 1, once its tests exist: app screens and wording drawn from the approved strings, and the engine files already listed as Tier 1.

**Keeping the author from being buried.**

- **A cap on what waits for him.** When more than a set number of Tier 2 changes wait (five, to begin), the agents that make Tier 2 work stop, and the planner turns them to tests, checks and Tier 1 work.
- **One summary a week,** the release issue, as now.
- **Reviewers under him.** He may appoint a reviewer for a group's topics, as he must for each language. GitHub's code-owner rules then let that person's approval stand for that folder only. Doctrine common to all, and the measure, stay his.

**Trust is earned by record.** Each agent begins by proposing only. Its Tier 1 class starts to merge itself after a set run of its changes (ten, to begin) that the author did not reverse; one reversal resets the count. The measure plan already does this for new script checks.

**One switch stops them all.** A repo setting that every agent's workflow reads first. The author flips it from his phone.

**What the agents run on.** The author's Max plan, as the tests do now. Its limits are the agents' budget, and the planner spends it on the stage in hand.

## 9. Security

**Who is against it, and what they would want.**

| Opponent | Aim |
| --- | --- |
| Those hostile to the work | Corrupt the teaching; make the coach say something shameful and publish it; get the app removed from the stores; expose the author |
| A hostile state or community where a trainee lives | Learn who is training |
| Anyone | Steal the keys; run up the bill; take the site down |

**What is protected, most important first:** the trainees' safety; the truth of what is taught; the money; the site's being up; the author's accounts and name.

**1. The trainees.** In some countries a brother found with this app could lose his liberty or his life. So:

- **Collect almost nothing.** No real name, no email required, no phone number, no contacts, no location. Sign-in is by invite code now, and by the phone's own passkey later.
- **Keep almost nothing.** The trainee's card lives on his phone where there is an app. What was said is removed from the server at the end of the session unless he has agreed to share it for improving the training (decision 4 in section 13). Logs never hold what was said, as now. The sign-in record drops the country.
- **On the phone:** a lock on the app, an option for a plain name and icon, no notification that shows content, and one action that wipes it.
- **Say plainly what cannot be hidden.** His network can see which site his phone reaches, and what he says is sent to Anthropic to be answered. A notice in his language tells him so before he begins, so that he and his church can judge the risk; they know their country.

**2. The teaching.** The ways in are a pull request, an issue, harvested text, a training log, a translation, a misled agent, a dependency, and a stolen account. The measure plan answers the first four and the agent. Added here: two reviewers for every language, so one hostile or careless translator cannot change doctrine alone; scripts that place Scripture; signed commits on `main`; and the release App as the only hand that moves it.

**3. The live coach.** Someone will try to turn it into a free chatbot, or make it mock a religion and record that. So the coach's prompt confines it to the training and treats whatever a trainee says as speech to answer, never as orders; the hostile tests in section 7 run at every release; each person's allowance bounds what misuse can cost; and the apps show no text of the conversation, which leaves little to screenshot.

**4. The money and the site.** No call to a model is ever made for someone unknown. A person trains through an invite that traces to a sponsor (section 10); the phone proves it is a real copy of the app (Apple's and Google's free attestation checks), and the web page uses a free challenge against scripts; allowances apply to each person, each phone, each sponsor's pool and the whole site; one pool's abuse cannot touch another's; and the hard limit at Anthropic stands behind all of it, as now.

**5. The accounts.** GitHub, Cloudflare, Anthropic, Apple, Google and the domain's registrar each get a hardware key or passkey, recovery codes kept offline, and a second trusted owner, so that the work does not hang on one man's phone or one man's life. Tokens stay narrow and short-lived, as the measure plan already has them.

**6. What it is built from.** Few dependencies, pinned; GitHub's free secret scanning and push protection; a `SECURITY.md` that tells a finder how to report a weakness privately.

**7. The stores.** Apple's rule 1.1.1 names "mean-spirited" commentary about religion as grounds for refusal, and Google's forbids inciting hatred of a religion. The app's defence is what it is: it trains Christians to ask questions gently, from the other side's own sources (section 4). The listing says so. The risk remains that a campaign of reports gets it removed, so the web app stays whole and equal, and the Android app can also be downloaded straight from the site.

**8. The law.** Four matters need a lawyer's reading once, before strangers are admitted: privacy law where trainees live; how much of living authors' books and of copyrighted translations may be quoted; a minimum age; and who owns the accounts. I am not a lawyer. Section 13 recommends that a church or a nonprofit own them, which also shields the author's own name.

**9. When something goes wrong.** One page, rehearsed once: pause training (the switch exists), revoke the key, roll back, tell those affected.

**The repo stays public.** Opponents can read every prompt and plan in it. But the coach fetches the skill from it, CI is free because of it, and safety that depends on hiding the design is weak in any case. Keys, the held-back tests and the findings stay private.

## 10. Cost

**What it costs to keep the doors open.**

| Item | Cost | Note |
| --- | --- | --- |
| GitHub, with CI on Linux and Mac | Free | For a public repo; from memory, to confirm |
| Cloudflare | Free, then $5 a month | The free database allows 5 GB and 100,000 rows written a day; the paid plan's minimum is $5 |
| Apple's developer program | $99 a year | Waived for a nonprofit that is a legal entity and offers only free apps; not for an individual |
| Google Play | $25, once | From memory; to confirm |
| A domain | About $12 a year | |
| Speech, both ways | Free | The phone's own, on every surface |
| Agents and tests | Nothing added | They run on the Max plan the author already has |

So the standing cost is under $20 a month. **The cost that grows is the model's answers.**

**What a trainee costs.** By list prices and file sizes, a full session of 40 turns costs about 15 to 45 cents, most of it the coach rereading the skill and the group's materials (about 50,000 tokens) on each turn. This is an estimate; the site already records the real cost of every call, and the first outside trainees will give the true figure. At today's cap of $3.50 a trainee a month:

| Trainees active in a month | At the cap | At a target of $1 each |
| --- | --- | --- |
| 100 | $350 | $100 |
| 1,000 | $3,500 | $1,000 |
| 10,000 | $35,000 | $10,000 |

One pocket cannot carry that. So two things are needed: a lower cost for each trainee, and an answer to who pays.

**Lowering it.** In order of gain for effort. Each is adopted only if the measure still passes, since cost is never cut below the quality bar.

1. **Measure first.** A weekly report from the site's own records: cost for each turn by role, how often the cache was hit, cost for each stage passed.
2. **Fixed pieces with no model call.** Already designed (`fixed/README.md`), waiting on the author's approval of the files. A beginner's first sessions are mostly fixed pieces, so they then cost close to nothing, and they work offline.
3. **Load less.** One topic and the part of the skill for the stage in hand, not the whole. Halving what the coach rereads nearly halves the cost of a turn.
4. **Share the cache.** What is common to all trainees of a topic is placed first, so one trainee's call warms the cache for the next. The busier the site, the cheaper each trainee. A one-hour cache is used where traffic is thin.
5. **The cheapest model that passes.** The member and the router already run on Haiku. Each narrower coaching job (a hint, a fixed check question) is tried on Haiku and moved only if the measure holds. Haiku as the whole coach scored 86 of 104, so not that, yet.
6. **Free practice.** Lessons and verse drills on the phone (section 6) give a trainee something to do every day that costs nothing.

**Who pays.** I recommend two ways together, and no payments inside the apps:

- **His own Claude plan.** A trainee who already pays for Claude uses the skill there, as today. It costs the project nothing.
- **Sponsor pools.** A church or a giver funds a pool and receives invite codes for its people. Each pool has its own allowance and stops when it is spent. The author's own pool is the first, and serves as a small free door for those with no sponsor. Giving happens outside the app, to a church or nonprofit, which keeps Apple's waiver and its rules on in-app payments out of the way.

To ask, since I could not confirm either: whether Anthropic gives nonprofits a lower price on API use, and whether Cloudflare's free protection programme for at-risk groups would take this work.

**Guards against a runaway bill:** the allowances above; an alert at each provider; the refusal to send any batch of tests over its cap; the hard limit at Anthropic.

## 11. The stages

Each stage ends in a release, and the next opens only when its gate is met. Stages 2, 3 and 5 can overlap, since agents do the building; where the author's time is short, the order below is the order of priority. I give no dates: the pace is set chiefly by his reviewing time, the reviewers he finds, and the stores' own reviews, and "if the Lord will, we shall live, and do this, or that" (Jas. 4:15; Prov. 16:9).

| Stage | What is built | Gate to the next |
| --- | --- | --- |
| **0. Finish the base** | Steps 2 to 7 of `measure/PLAN.md`, with the author's part in GitHub's settings. The security basics that cost nothing: keys on every account, a second owner, pinned CI actions, `SECURITY.md`. The held-back tests. The planner, the keeper and the kill switch. Begin now, since they take longest: the search for reviewers, the choice of an owning body, the lawyer's reading | A release has moved `main` by itself; a Tier 1 change has merged itself; the author has stopped an agent with the switch |
| **1. Open the English site safely** | The privacy notice and consent; deleting a person's records; fixed pieces served with no model call; streaming, so the coach answers sooner; the installable web app; sponsor pools and invite chains; the challenge against scripts; the hostile tests; the cost report | Twenty-five trainees from outside the author's circle have trained for a month within budget; the real cost of a trainee is known; no trainee's words have leaked |
| **2. Any topic** | The new layout and manifest; the quotation check for every registered text; the topic drafter and source checker; each topic's standard tests; a topic chooser; the statement of what is affirmed. First topics: the two the author named, the deity of Christ for Jehovah's Witnesses and child marriage for Islam | Two new topics have been released through the pipeline, and the author's time on each is known |
| **3. Phone apps** | The engine's written contract; the iPhone and Android apps; the app lock and plain icon; the scripted session in CI; test releases, then the stores. The CarPlay request is sent at the start of this stage | Both stores have accepted the app; a trainee has passed a stage on each |
| **4. The car** | CarPlay screens; the Android car path as found then; the car mode the author chose | Checked by a person in a real car on each platform |
| **5. The first other language** | One pilot language through all eight items of section 5, on the web app first | A group of its speakers has passed a stage, and both reviewers have signed |
| **6. Many hands** | More topics and languages at a steady pace; reviewers for groups; tools for a trainer to follow those he trains, with their consent; more sponsor pools | None: this is the work itself |

## 12. Risks this plan cannot remove

- **A store may refuse or remove the app,** or Apple may refuse the car entitlement. The web app is the answer, not a cure.
- **A language the author cannot read rests on two reviewers and on the tests.** If no two sound reviewers can be found, that language should wait.
- **The coach's live remarks are composed by a model.** Tests reduce the errors; they do not end them. The more of the teaching that is fixed and approved, the smaller this risk.
- **A trainee in a hostile country takes a real risk** that no design removes. The plan lowers it and tells him the truth about it.
- **The Max plan's limits bound the agents.** "Constantly" will mean as much as that budget allows, spent on the stage in hand.
- **Costs here are estimates** until the site has real trainees.

## 13. Decisions for the author

Each has my recommendation first.

1. **Who pays for trainees' sessions?** Sponsor pools and each trainee's own Claude plan, with the author's pool as a small free door (section 10).
2. **Who owns the accounts?** A church or nonprofit, not the author in his own name: it can receive gifts, qualify for Apple's waiver and shield him (sections 9, 10).
3. **Who may train?** Invites that trace to a sponsor, not open sign-up, until the cost and the abuse are known (section 9).
4. **Are trainees told that their sessions may be read to improve the training?** Yes, and they choose. This would change the author's earlier decision (`measure/PLAN.md`, end of section 6). That decision was made for five invited testers. For strangers, both stores require an app to declare what it collects and why, privacy law in many countries requires it, and we are to provide "for honest things, not only in the sight of the Lord, but also in the sight of men" (2 Cor. 8:21; Rom. 12:17). The log reader then works from the sessions of those who agreed.
5. **Is the tool offered where it is dangerous to have?** Yes, with the plain warning and the protections of section 9, leaving the judgment to the believers there.
6. **Will he appoint reviewers under him,** for groups and for languages, and write the statement of what the boot camp affirms and denies? Yes to both (decision 4 in section 3).
7. **Which languages first, and which Bible in each?** His to name. I would start with one, chosen by where two reviewers are already known to him.
8. **Two native apps, or one shared codebase?** Two native apps (section 6).
9. **May the *Apologetics SOPs* doc stop mirroring every file?** Yes: with many topics and languages its tabs cannot keep up. A reading copy generated from the repo replaces them, and the doc keeps only his training log.
10. **What may be done in the car?** Lessons, review and verse drills by default; full practice rounds only if the trainee turns them on.
11. **Which topics first?** The two he named, then the queue as he orders it.
12. **May the content move to the new layout** (section 4), by the careful path described there? Yes.
13. **May a held-back set of tests be kept in a private repo?** Yes (section 7).

## 14. What the author does himself

- Answers section 13.
- Finishes his part of `measure/PLAN.md`, section 9, on which stage 0 depends.
- Puts a key on each account and names a second owner.
- Finds reviewers, and the body that will own the accounts.
- Approves the fixed pieces now in draft, which lowers the cost at once.
- Approves each topic's teaching, and reads the weekly summary.
- Enrols in Apple's and Google's developer programs when stage 3 begins.

The first step after approval is stage 0: to finish the base the rest stands on, so that every later change, in any topic, language or app, is proved before a trainee hears it, and he is sent out with what is true.

## Sources

Checked on Nov 28, 2026. Where a fact above is marked as from memory or from press reports, it is to be confirmed at the source before anything is built on it.

- CarPlay's category for voice-based conversational apps: [9to5Mac](https://9to5mac.com/2026/02/18/ios-26-4-adds-support-for-voice-based-ai-apps-to-carplay/), [MacRumors](https://www.macrumors.com/2026/02/18/ios-26-4-carplay-support/), [AppleInsider](https://appleinsider.com/articles/26/02/18/ai-agents-are-coming-to-carplay-but-theyre-not-getting-the-keys)
- Android Auto's app categories: [Android for Cars overview](https://developer.android.com/auto/overview.html), [Android Developers Blog, I/O 2025](https://android-developers.googleblog.com/2025/05/android-for-cars-google-io-2025.html)
- Store rules on religion: [Apple's App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), [Google Play's policy](https://www.support.google.com/googleplay/android-developer/answer/9878810)
- Apple's fee waiver: [Apple's account help](https://developer.apple.com/support/fee-waiver)
- Cloudflare's prices: [Workers](https://developers.cloudflare.com/workers/platform/pricing/), [D1](https://developers.cloudflare.com/d1/platform/pricing/)
- Model prices, caching and batches: the design-principles reference for applications on the Claude API (refreshed Nov 27, 2026), and `site/src/pricing.ts`
- Agent design, security, cloud, CI and interface principles: the design-principles references of the same date
