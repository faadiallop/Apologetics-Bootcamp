# Working in this repo

This repo is the true copy of the apologetics boot camp skill and its SOPs. Two other copies must match it, and they fall behind unless they are updated with each release.

## When the author says to release now

A release waits 48 hours for the author to read its summary, unless the author comments `go` on its issue (`measure/PLAN.md`, section 7). When the author tells you to release now, do this, and never move `main` or deploy the site by hand:

1. **Find the release.** Look for an open issue labelled `release`. If there is none, start the release workflow by hand (`gh workflow run release.yml --ref main`), wait for that run to finish, and use the issue it opens. If the run fails, stop and tell the author why.
2. **Read the summary.** If any check or conversation test failed, or the site round failed, stop and tell the author what failed. Release only on the author's answer.
3. **Release.** Comment exactly `go` on the issue, and nothing else: the release counts only a comment that is that one word, from the author's account. Then start the release workflow by hand again.
4. **Watch it to the end.** Wait for that run to finish, then tell the author that `main` has moved, whether the site was deployed, and whether the live site passed its check. If the release stopped for a database change, or put `main` and the site back, say so and give the reason from the run's log and the issue.

Then do what the next section requires.

## After a release moves `main`

Changes merge into `next`, and reach `main` only through a release (`measure/PLAN.md`, section 7). The copies follow `main`, not `next`, so update them when a release has moved `main` (the release closes its issue, labelled `release`, saying so), not when you push to `next`. Compare `main` with the commit the copies were last brought up to, which is named in the last such issue's "Copies updated" comment, and then:

1. **The user's saved skills.** For every `skills/<name>/SKILL.md` that changed, propose the same change to the user's saved copy of that skill with `propose_skills`, so the saved copy matches GitHub once he saves the card. Phone and voice sessions load the saved copy first.
2. **The *Apologetics SOPs* doc** (https://claude.ai/artifact/QNCnLJ2zj8F7bYETwZpLEa). For every file that changed in `skills/apologetics-boot-camp/sops/`, make its tab in the doc match the file. Add a tab for a new SOP, placed after the other group tabs. The tabs are:

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

Then comment "Copies updated to `<commit>`" on the release's issue. Tell the user if either copy couldn't be updated, and why.

## After you open a pull request

Watch it, and handle its checks and review comments, without asking first.

Merge your own pull requests into `next` once every check passes. Leave `main` to releases.

## When you change the boot camp's SKILL.md

Run `python3 measure/checks.py --stamp` before you commit, and commit `skills/apologetics-boot-camp/VERSION` with it. The stamp lets a saved copy of the skill tell from one short line whether it is current, so it need not fetch the whole of SKILL.md at the start of every session.

## Writing here

- Apply the user's thought-and-word rules. Their true copy is the `thought-and-word` plugin of the GitHub repo faadiallop/foundations; change them there, never here. The site bundles a copy of their index, `site/prompts/thought-and-word-rules.md`. When `measure/checks.py` reports it behind (`rules-copy`), open a pull request that makes it match.
- Quote Scripture from the King James Version, checked word for word.
