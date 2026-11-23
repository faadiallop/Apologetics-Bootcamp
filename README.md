# Apologetics Boot Camp

A Claude skill that trains a Christian, from beginner up, to bring members of a specific false religion or cult to Christ. It explains the method, teaches a beginner each part before testing it, drills in spoken role-play, coaches after each conversation, and keeps going until the trainee can do it himself and teach someone else.

Everything the skill needs is in this repo: the skill itself, the SOPs it trains from, and the writing-and-thinking rule skills it applies when it coaches.

## What's inside

```
.claude-plugin/
  plugin.json              Plugin manifest
  marketplace.json         Lets Claude and Claude Code install this repo as a plugin
skills/
  apologetics-boot-camp/
    SKILL.md               The boot camp: paths, lessons, role-play, scoring
    sops/                  The material it trains from
      00-overview-and-template.md
      01-methodology-questioning-them-to-death.md
      10-islam.md                    The Islamic Dilemma
      11-jehovahs-witnesses.md       The Bread of Life
      12-jewish-people.md            The Suffering Servant
      20-response-bank.md            What members actually say, for role-play
      21-training-plans.md           Stage-by-stage drills and pass lines
  thought-and-word-rules/  Index of the rules below and how they fit together
  presupposition-rule/     Reason from Scripture; no neutral ground
  witness-rule/            Every claim needs two or three witnesses
  teachers-rule/           Argue from the user's chosen teachers, under Scripture
  plainness-rule/          Be understood on the first reading
  economy-rule/            Every word must serve the reader
  chiasm-rule/             Prefer chiastic structure where the material allows
  writing-dialogue/        Work out a piece of writing with the user in dialogue
```

## Install

### Claude Code

In Claude Code, run:

```
/plugin marketplace add faadiallop/Apologetics-Bootcamp
/plugin install apologetics-boot-camp@apologetics-bootcamp
```

This installs all nine skills together. To get changes as they land, open `/plugin`, go to **Marketplaces**, select this one, and choose **Enable auto-update**; or update by hand with `/plugin marketplace update apologetics-bootcamp`.

### Claude on the web, the desktop app, or Cowork

Claude syncs this repo for you, so there is nothing to upload. Plugins need a paid plan.

1. Open **Customize → Plugins**, click **Add**, choose **Add marketplace → Add from a repository**, and enter `faadiallop/Apologetics-Bootcamp`.
2. Turn on **Sync automatically** for that marketplace.
3. Install **apologetics-boot-camp** from it. The plugin is saved to your account, so its skills work in chat, Cowork and Claude Code.
4. If you uploaded any of these skills by hand before, remove those copies so only the repo's versions load.

## Changing the skills

This repo is the source. Make every change here, as a commit to `main`, and Claude picks it up at its next sync. Don't edit the installed copies in Claude: a sync would replace them.

`plugin.json` has no `version` on purpose. Without one, each commit counts as a new version; with a fixed one, installed copies stay as they are until it's raised.

## Use

Start a chat and ask for it, for example:

> Train me to talk with Jehovah's Witnesses.

The coach asks which group, whether you're a beginner with it, and whether you'll train by voice. Then it explains the method, gives the argument in a sentence, says why this approach was chosen over others, and tells you what the training will involve.

- **Beginners are taught before they're tested.** You can start with background on the group. You can learn by plain teaching (the default) or by dialogue: you talk with a member of the group, played by the coach, to understand their view, then the coach sums it up and gives the verses.
- **Not a beginner?** You go straight into practice conversations and are taught only what you miss.
- **Use voice mode for practice.** Role-play is the heart of the training and works best spoken.
- **Groups covered so far:** Muslims, Jehovah's Witnesses, and Jewish people. For any other group the coach will offer to draft a new SOP in the same template for your approval before training from it.
- **Training log.** At the end of each session the coach writes a short card in plain words: what you learned, how you did, what's next, and verses to review. Keep it somewhere it can read next time, such as a `training-log.md` file in your working folder.

## The training path

| Path | What happens |
| --- | --- |
| Beginner | Background on the group (if you want it), the gospel in your own words, what the group believes, the argument and its verses, their usual answers, and the killer questions; then practice: asking questions, spotting flaws, staying in control and on topic, and full conversations; then real conversations, each debriefed; and last, teaching someone else |
| Not a beginner | A practice conversation first, then lessons and drills only where you need them, then the field and teaching someone else |

You pass each drill on knowledge, wisdom and character, three conversations in a row. Verse references must be exact; figures and dates need only be roughly right. A conversation fails on character, however well argued, if you mock or anger the person.

## Editing the SOPs

The files in `skills/apologetics-boot-camp/sops/` are exported from the *Apologetics SOPs* doc. If you keep that doc as the working copy, export its tabs again as Markdown after changes and replace these files, so the repo stays current. Every SOP follows the template in `00-overview-and-template.md`; add a new group as a new file in that same form and list it in the overview's index.
