# Apologetics Boot Camp

A Claude skill that trains a Christian, from beginner up, to bring Muslims, Jehovah's Witnesses, Jewish people, atheists, or members of any false religion or cult, to Christ. It explains the method, teaches a beginner each part before testing it, drills in spoken role-play, coaches after each conversation, and keeps going until the trainee can do it himself and teach someone else.

The skill and the SOPs it trains from are in this repo. The thought-and-word rules it applies when it coaches are kept in [faadiallop/foundations](https://github.com/faadiallop/foundations), in the `thought-and-word` plugin.

## What's inside

```
.claude-plugin/
  plugin.json              Plugin manifest
  marketplace.json         Lets Claude and Claude Code install this repo as a plugin
measure/                   The tests the boot camp skill is judged by, and the plan for checking every change; start with its README
  evals/                   Conversation tests, one folder each
skills/
  apologetics-boot-camp/
    SKILL.md               The boot camp: paths, lessons, role-play, scoring
    sops/                  The material it trains from
      00-overview-and-template.md
      01-methodology-questioning-them-to-death.md
      10-islam.md                    The Islamic Dilemma
      11-jehovahs-witnesses.md       The Bread of Life
      12-jewish-people.md            The Suffering Servant
      13-atheism.md                  Borrowed Ground
      14-icon-veneration.md          Icon Veneration
      20-response-bank.md            Personas and rules for role-play, shared by every group
      20-response-bank-islam.md      What members actually say, one file for each group
      20-response-bank-jehovahs-witnesses.md
      20-response-bank-jewish-people.md
      20-response-bank-atheism.md
      20-response-bank-icon-veneration.md
      21-training-plans.md           How training works and the rubric, shared by every group
      21-training-plans-islam.md     Stage-by-stage drills and pass lines, one file for each group
      21-training-plans-jehovahs-witnesses.md
      21-training-plans-jewish-people.md
      21-training-plans-atheism.md
      21-training-plans-icon-veneration.md
    fixed/                 Drafts of what every trainee hears the same way (openings, lessons), one file for each group; the coach says a group's pieces as written once its file is approved
    VERSION                The stamp of SKILL.md, so a saved copy can tell whether it is current
  writing-dialogue/        Work out a piece of writing with the user in dialogue
```

## Install

### Claude Code

In Claude Code, run:

```
/plugin marketplace add faadiallop/Apologetics-Bootcamp
/plugin install apologetics-boot-camp@apologetics-bootcamp
```

This installs both skills together. For the thought-and-word rules as skills, also add the `faadiallop/foundations` marketplace and install its `thought-and-word` plugin; without it, the coach reads the rules from GitHub. To get changes as they land, open `/plugin`, go to **Marketplaces**, select this one, and choose **Enable auto-update**; or update by hand with `/plugin marketplace update apologetics-bootcamp`.

### Claude on the web, the desktop app, or Cowork

Claude syncs this repo for you, so there is nothing to upload. Plugins need a paid plan.

1. Open **Customize → Plugins**, click **Add**, choose **Add marketplace → Add from a repository**, and enter `faadiallop/Apologetics-Bootcamp`.
2. Turn on **Sync automatically** for that marketplace.
3. Install **apologetics-boot-camp** from it. The plugin is saved to your account, so its skills work in chat, Cowork and Claude Code.
4. If you uploaded any of these skills by hand before, remove those copies so only the repo's versions load.

## Changing the skills

This repo is the source. Make every change here, as a commit to `main`, and Claude picks it up at its next sync. Don't edit the installed copies in Claude: a sync would replace them. Two other copies are kept in step with the repo, your saved copy of each skill and the *Apologetics SOPs* doc; `CLAUDE.md` tells Claude to update both whenever it pushes a change.

`plugin.json` has no `version` on purpose. Without one, each commit counts as a new version; with a fixed one, installed copies stay as they are until it's raised.

## Use

Start a chat and ask for it, for example:

> Train me to talk with Jehovah's Witnesses.

The training is by voice only: you speak, and the coach answers aloud. The coach asks only what it doesn't already know: which group, and whether you're a beginner with it. Then it reads your newest training card for that group. If you're new to the group, it explains the method, gives the argument in a sentence, says why this approach was chosen over others, and tells you what the training will involve. If you've trained with that group before, it skips this introduction.

- **Beginners are taught before they're tested.** You can start with background on the group. Lessons come in short spoken pieces, each followed by a question.
- **Not a beginner?** You go straight into practice conversations and are taught only what you miss.
- **Practice goes where you struggle.** The coach marks each moment that called for one of Koukl's tactics, finds the ones you miss most, and drills them one at a time, in the order of his book, except that the steamroller is drilled with the rescues, since both keep control of the conversation.
- **Voice only.** Start it in voice mode. Nothing is taught or practised in writing, because the conversations it trains for are spoken.
- **Groups covered so far:** Muslims, Jehovah's Witnesses, Jewish people, and atheists. For any other group the coach will offer to draft a new SOP in the same template for your approval before training from it.
- **Training log.** The coach keeps a short card for each session in plain words: what you learned, how you did, your count on each tactic, your hard tactics, what's next, and passages to review. It saves the card to your training log after each drill or conversation, without asking, so a call that ends early loses nothing, and reads your newest card there as soon as it knows the group. The author's log is the Training log tab of the *Apologetics SOPs* doc; anyone else's is a doc of his own, titled "Boot camp training log," which the coach creates with the first card. New objections you meet go on your card, and you can send them to the author as an issue on this repo. A tactic you find hard stays on your list until you clear it.

## The training path

| Path | What happens |
| --- | --- |
| Beginner | In the order of the SOP: what Scripture says about the group's error and how to carry yourself toward its members; background on the group (if you want it) and what it believes; the argument and its verses, then Koukl's tactics in the order of his book, with the questions that expose each flaw; and their usual answers. Then practice in the same order, with most of the time on what you find hardest: asking questions, the rescues and staying on topic, meeting a steamroller, leading, and finding the flaws. Once every tactic is cleared, the gospel in your own words and the bridge to Christ, taught and drilled as a stage of their own; then full conversations; then real conversations, each debriefed; and last, teaching someone else |
| Not a beginner | One or two practice conversations to find what you find hardest, then drills on those in the book's order; once your tactics are cleared, the gospel and the bridge to Christ; then full conversations, the field, and teaching someone else |

You pass each drill on its tactic and on knowledge, wisdom and character, two conversations in a row; leading with questions (step 3) takes three, and finding the flaws takes three passing sets in a row, each of three rounds, where a set passes on two of its three. You must say correctly what the key passages say, but you needn't cite their references; figures and dates need only be roughly right. A conversation fails on character, however well argued, if you mock or anger the person.

## Editing the SOPs

The files in `skills/apologetics-boot-camp/sops/` are the true copy. The *Apologetics SOPs* doc keeps a copy of each as a tab, for reading and comments; after a change here, update its tab there (`CLAUDE.md` says how). Every SOP follows the template in `00-overview-and-template.md` and quotes Scripture from the King James Version; add a new group as a new file in that same form and list it in the overview's index.
