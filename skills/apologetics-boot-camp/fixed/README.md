# Fixed pieces

Text that is said word for word, the same to every trainee, so it need not be composed afresh each time. It belongs to the skill, not to any one place the skill runs: the coach can read a piece aloud as it stands, and an app built on the skill can serve it with no model call. Each group has one file here, and `TO-CHECK.md` lists what the writers of the drafts ask the author to look at before approving. The pieces are drafts until the author approves them; only a file whose first line after the title reads `Status: approved` is to be used with trainees.

The skill (`../SKILL.md`) and the group's SOP files (`../sops/`) are the source. A piece says nothing they don't say. When the skill or an SOP changes, the group's file here is checked against it.

## What is fixed, and what is not

Fixed: what every trainee of a group hears the same way the first time.

- the opening for a trainee new to the group, in two forms (a beginner, and one who is not);
- the background on the group, offered to a beginner;
- the first telling of each lesson piece, with its check question;
- the first teaching of each tactic, with its check question.

Not fixed: anything that answers what he said. A second telling after a missed check, the role-play, hints, coaching, scores and the card are composed for him each time.

## Layout of a group's file

```
# <Group> (<name of the argument>)

Status: draft

Source: skill stamp <the stamp in skills/apologetics-boot-camp/VERSION when the file was written or last checked>

## opening-beginner

<what he hears>

## opening-not-beginner

<what he hears>

## background-1

say: <what he hears>

check: <one question or request about what was just said>

expect: <what a right answer holds, for whoever judges his answer; he never hears this>
```

Each of `say`, `check` and `expect` is one line, with a blank line between them, so that the file reads well on GitHub and a few lines of code can read it.

**Why Markdown, and not JSON or YAML.** The author reads and approves every piece, and a change shows as a plain diff. The pieces are full of quotation marks and colons, which JSON and YAML would need escaped or quoted, and a slip there breaks the whole file. Here a slip breaks one piece, and the check names it.

**Piece names,** in the order they are served: `opening-beginner`, `opening-not-beginner`, `background-N`, `foundation-N`, `know-them-N`, `argument-N`, `tactic-<name>`, `their-answers-N`, `gospel-N`, `bridge-N`. Numbers run from 1 with none skipped.

**Tactic names** are fixed, so the piece for the tactic on a trainee's card can be found by name. A group has a piece only for the tactics its material uses, in this order: `gather`, `burden-of-proof`, `rescues` (or, where the material has an example of each, `rescues-professors-ploy` and `rescues-hot-seat`), `staying-on-topic`, `steamroller`, `lead`, `turnabout`, `suicide`, `practical-suicide`, `sibling-rivalry`, `infanticide`, `taking-the-roof-off`, `unfalsifiable`, `rhodes-scholar`, `just-the-facts`.

**Check the files** with `python3 measure/checks.py`, whose `fixed-pieces` check reads every group's file as a program would and reports any piece that could not be used: a name the layout doesn't allow, a piece out of order, a missing or doubled field, an opening over 350 words, a tactic taught in more than 100, or markup that would be read aloud. It also notes a file whose stamp is behind the skill's. It does not judge whether a piece is true.

## Rules for every piece

1. **The skill's limits hold.** An opening is 350 words at most, the offer of background included, and has the four parts the skill names: the method, the argument in one sentence, why this approach, what will happen. The beginner's opening ends with the offer of background; the other has no offer. A lesson piece is two or three spoken sentences and one idea. A tactic's teaching is 100 words at most: what it is, which move by the member calls for it, the question it asks, and one example from this group's material. Each piece has exactly one check question, about what was just said.
2. **Spoken.** Every `say` and `check` is read aloud. No lists, headings, bold or brackets inside them. Say references as people do ("John six, verse fifty-three").
3. **Scripture is King James, word for word,** copied from the SOP's own quotation, never from memory.
4. **Speak of the content, never the documents.** No file, tab, section, row, stage or step numbers.
5. **Keep two words apart.** "Jehovah's Witnesses" or "JWs" for the group; never "witnesses" for evidence.
6. **The opening reminds him to pray** in one sentence; it does not pray for him.
7. **Nothing addressed to one trainee.** No names, no "as you said."
8. **The author's thought-and-word rules apply** (the `thought-and-word` plugin of the GitHub repo faadiallop/foundations).

## How the skill uses them

Section B.5 of `SKILL.md` tells the coach to say a group's pieces as written, but only from a file marked `Status: approved`. While a file reads `Status: draft` the coach composes those parts itself, as before. So the author switches a group over by approving its file.
