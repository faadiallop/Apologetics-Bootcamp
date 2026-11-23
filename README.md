# Apologetics Boot Camp

A Claude skill that trains a beginner, step by step, to bring members of a specific false religion or cult to Christ. It teaches briefly, drills in spoken role-play, coaches after each round, and keeps going until the trainee can do it himself and teach someone else.

Everything the skill needs is in this repo: the skill itself, the SOPs it trains from, and the writing-and-thinking rule skills it applies when it coaches.

## What's inside

```
.claude-plugin/
  plugin.json              Plugin manifest (Claude Code)
  marketplace.json         Lets Claude Code install this repo as a plugin
skills/
  apologetics-boot-camp/
    SKILL.md               The boot camp: stages, sessions, role-play, scoring
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

This installs all eight skills together. Update later with `/plugin marketplace update apologetics-bootcamp`.

### Claude.ai or the Claude desktop app

Each skill is uploaded on its own.

1. Download this repo (**Code → Download ZIP**) and unzip it.
2. For each folder under `skills/`, zip that folder by itself (for example, `apologetics-boot-camp.zip` containing the `apologetics-boot-camp` folder, with `SKILL.md` and `sops/` inside).
3. In Claude, open **Settings → Capabilities → Skills**, choose **Upload skill**, and upload each zip.
4. Make sure each skill is turned on.

Upload `apologetics-boot-camp` first. The rule skills are optional but recommended: the boot camp tells Claude to apply them when it coaches.

## Use

Start a chat and ask for it, for example:

> Train me to talk with Jehovah's Witnesses.

The coach will ask a few questions to find where you are (which group, whether you can explain the gospel in a minute, how long your sessions are), then start at the right stage.

- **Use voice mode for drills.** Role-play is the heart of the training and works best spoken.
- **Groups covered so far:** Muslims, Jehovah's Witnesses, and Jewish people. For any other group the coach will offer to draft a new SOP in the same template for your approval before training from it.
- **Training log.** At the end of each session the coach writes a short card (stage, scores, next drill, verses to review). Keep it somewhere it can read next time, such as a `training-log.md` file in your working folder.

## The training path

| Stage | What you learn |
| --- | --- |
| 0. The gospel | Explain the gospel in a minute, true to Scripture |
| 1–8. The group's training plan | Their beliefs in their words, the argument, Koukl's three questions, killer questions, staying in control, full conversations |
| 9. The field | Real conversations, each one debriefed |
| 10. Teach another | Coach a newer trainee |

You pass a stage on knowledge, wisdom and character, three rounds in a row. A round fails on character, however well argued, if you mock or anger the person.

## Editing the SOPs

The files in `skills/apologetics-boot-camp/sops/` are exported from the *Apologetics SOPs* doc. If you keep that doc as the working copy, export its tabs again as Markdown after changes and replace these files, so the repo stays current. Every SOP follows the template in `00-overview-and-template.md`; add a new group as a new file in that same form and list it in the overview's index.
