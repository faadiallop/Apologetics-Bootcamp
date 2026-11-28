# Working in this repo

This repo is the true copy of the apologetics boot camp skill, its SOPs, and the thought-and-word rule skills. Two other copies must match it, and they fall behind unless they are updated with each change.

## After you push a change, in the same session

1. **The user's saved skills.** For every `skills/<name>/SKILL.md` you changed, propose the same change to the user's saved copy of that skill with `propose_skills`, so the saved copy matches GitHub once he saves the card. Phone and voice sessions load the saved copy first.
2. **The *Apologetics SOPs* doc** (https://claude.ai/artifact/QNCnLJ2zj8F7bYETwZpLEa). For every file you changed in `skills/apologetics-boot-camp/sops/`, make its tab in the doc match the file. Add a tab for a new SOP, placed after the other group tabs. The tabs are:

   | File | Tab |
   | --- | --- |
   | `00-overview-and-template.md` | Overview & Template |
   | `01-methodology-questioning-them-to-death.md` | Methodology: Questioning Them to Death |
   | `10-islam.md` | Islam |
   | `11-jehovahs-witnesses.md` | Jehovah's Witnesses |
   | `12-jewish-people.md` | Jewish people |
   | `13-atheism.md` | Atheists |
   | `14-icon-veneration.md` | Icon Veneration |
   | `20-response-bank.md`, then `20-response-bank-islam.md`, `20-response-bank-jehovahs-witnesses.md`, `20-response-bank-jewish-people.md`, `20-response-bank-atheism.md`, `20-response-bank-icon-veneration.md` | Response Bank (role-play) |
   | `21-training-plans.md`, then `21-training-plans-islam.md`, `21-training-plans-jehovahs-witnesses.md`, `21-training-plans-jewish-people.md`, `21-training-plans-atheism.md`, `21-training-plans-icon-veneration.md` | Training Plans (role-play) |

   The Response Bank and the Training Plans are each kept as one shared file and one file for each group, so that a training session loads only its own group's. Their tab holds those files joined in the order given. A new group gets its own two files, named after its SOP.

   Leave the Training log tab alone; the boot camp itself writes there.

Tell the user if either copy couldn't be updated, and why.

## After you open a pull request

Watch it, and handle its checks and review comments, without asking first.

## When you change the boot camp's SKILL.md

Run `python3 measure/checks.py --stamp` before you commit, and commit `skills/apologetics-boot-camp/VERSION` with it. The stamp lets a saved copy of the skill tell from one short line whether it is current, so it need not fetch the whole of SKILL.md at the start of every session.

## Writing here

- Apply the user's thought-and-word rules (`skills/thought-and-word-rules/`).
- Quote Scripture from the King James Version, checked word for word.
