# The website

A Cloudflare Worker that runs the boot camp skill, by voice only, for the owner and the people he invites, and keeps the cost within a fixed budget.

## How a turn is answered

The Worker holds the Anthropic key. The browser never sees it. For each message it:

1. checks who is asking (the owner's token, or an invite code that still stands), the pause switch and that person's spending limits, before anything is spent;
2. decides who speaks:
    - outside a practice round, the **coach** (Sonnet), with the whole skill and the group's materials;
    - inside a round, a small **router** (Haiku) reads the round so far and chooses: the **member** (Haiku) answers, or the coach is called back for a hint or to close the round;
3. records what each call cost, from the token counts the API reports, and saves the session and the trainee's card.

The skill's files are bundled in when the Worker is built (`src/materials.ts`), so a change to the skill reaches the site at the next deploy. Each release deploys the site from `main` by itself (`.github/workflows/release.yml`), once the `release` environment holds a Cloudflare token; a deploy by hand, as below, still works. A group's fixed pieces are included only once its file is marked approved.

## Turning the microphone off

While training, a microphone button sits at the bottom of the screen (or press M on a keyboard). Off, the browser stops listening at once and anything half heard is dropped; the coach finishes what he is saying, then waits, with the bars dimmed, until the microphone is turned back on.

## When training ends

The coach never ends a training on its own; it goes on, round after round, until one of these stops it:

| What stops it | What the trainee sees | Can he start again? |
| --- | --- | --- |
| He taps End, at the top right | "You ended the training" | Yes, at once |
| His allowance for the day or the month is used up | "Today's (or this month's) allowance is used up", with the local time it renews | No, until it renews |
| The site's budget for the day or the month is used up | "Training is closed for today (or this month)", with when it opens | No, until it opens |
| The owner pauses training | "Training is paused" | No, until the owner resumes it |
| The owner revokes his invite | The sign-in sheet, with "Your invite code is no longer accepted" | No, unless the owner restores it or gives him a new code |
| The session reaches 40 turns | "This session reached its limit" | Yes, as a new session |
| The session was cleared after 14 days idle | "That session has ended" | Yes, as a new session |
| More than six messages in a minute | "That was too fast for the site" | Yes, after a minute |
| Anthropic's service is overloaded | "The coach is busy" | Yes, after a moment |
| The microphone is blocked, or fails | "The microphone is blocked" or "The coach couldn't hear you" | Yes, once it works |

The coach says the reason aloud, and the group sheet comes back with it at the top. When he can't start again, the groups are greyed out. The foot of the sheet shows how much of his allowance is left, today's or this month's, whichever is less. A new session starts from his newest card, so rounds he finished carry over; a round cut off part-way is not saved.

## Limits

Set in `wrangler.jsonc` under `vars`, in US dollars. They are sized for $20 a month and five testers.

| Limit | Value |
| --- | --- |
| One trainee, a day | $0.50 |
| One trainee, a month | $3.50 |
| The whole site, a day | $1.50 |
| The whole site, a month | $20 |
| One session | 40 turns |
| Messages a minute | 6 |

When a turn takes a person past four fifths of an allowance (the day's, the month's, or the session's 40 turns), the coach's voice tells him so, once. While training, a note under the bars stays up after that. When a limit is reached, see [When training ends](#when-training-ends).

Once the site has spent $16 in a month, the daily budget shrinks to what is left divided by the days left. The hard limit on the Anthropic workspace is the backstop behind all of these.

## Set up, once

Run these from the `site` folder. On this machine use `npm.cmd` and `wrangler.cmd`.

1. `npm.cmd install`
2. `wrangler.cmd d1 create bootcamp-site`, then put the `database_id` it prints into `wrangler.jsonc`.
3. `wrangler.cmd d1 execute bootcamp-site --remote --file=schema.sql`
4. `wrangler.cmd deploy`
5. `wrangler.cmd secret put ANTHROPIC_API_KEY` (the key from the site's own Anthropic workspace)
6. `wrangler.cmd secret put OWNER_TOKEN` (a long random string of your own; it is your sign-in for step 1)

Until both secrets are set, every request is refused. Then open the address `deploy` printed, and sign in with the owner token.

## Invite someone

Open `/admin` on the site and sign in with the owner token. Type the person's name and choose "Create invite code". The code is shown once; the site keeps only its hash. Give the person the code and the site's address. He enters the code once on his device, picks a group, and trains by voice.

The same page shows what each person has spent today and this month, lets you revoke or restore an invite, and pauses all training. Under "Training log" it shows each person's sessions, the card the coach saved in each, and what was said. Under "Sign-ins" it lists the last hundred times a code was entered, accepted or refused; after twenty refusals in ten minutes from one place, that place is turned away for a while. Each person has his own allowance, sessions and training log.

## Pause everything

The owner's page has a "Pause all training" button. From a terminal:

`wrangler.cmd d1 execute bootcamp-site --remote --command "INSERT INTO settings (key, value) VALUES ('kill', '1') ON CONFLICT(key) DO UPDATE SET value = '1'"`

Set the value to `'0'` to resume.

## What is kept, and for how long

A trainee's card is kept, since it is how the coach remembers his progress. What was said in a session is removed 14 days after the session was last used (`KEEP_CONVERSATIONS_DAYS` in `wrangler.jsonc`), by a job that runs once a day. The session's group, number of turns and cost stay on record.

## Server logs

The Worker's logs are kept by Cloudflare (`observability` in `wrangler.jsonc`). Each turn logs who, which session, which models were called, the cost, and any error. It never logs what was said. Read them in the Cloudflare dashboard under Workers & Pages, `bootcamp-site`, Logs, or watch them live with `wrangler.cmd tail bootcamp-site`.

## Check a change

- `npm.cmd run typecheck`
- `npm.cmd test` (limits, prices, invite codes, and who speaks when; no model is called)
- `npm.cmd run check-bundle` (builds the Worker without deploying it)

## Train on it as a trainee would

`rounds/run.mjs` runs a private copy of the site (its own empty database), opens its page in a real browser, signs in with a fresh invite, picks a group and trains for a few turns. Only the microphone and the voice are stood in for: a Claude Code agent plays the trainee from the round's instructions (`rounds/short-round.md`), and a second one grades the transcript. It also checks, without a model, that every turn was answered and spoken, that the cost was recorded and stayed within the cap, and that the owner's page shows the session.

It is paid for, so it never runs on a schedule or a pull request. It runs at a release that changes what the site bundles, and by hand from Actions, "site round" (`.github/workflows/site-round.yml`). The site's replies use the author's personal key, `SITE_TEST_ANTHROPIC_API_KEY`, never the site's own, and every spending limit of the copy is set to the cap (`--cap`, $1 unless told otherwise). The trainee and the grader run on the author's subscription, `CLAUDE_CODE_OAUTH_TOKEN`. Both secrets live in the `measure` environment.

On this machine, from `site`, with `claude` signed in: `cd rounds; npm.cmd install; npx.cmd playwright install chromium; cd ..`, then `node rounds/run.mjs --cap 0.5`, with `SITE_TEST_ANTHROPIC_API_KEY` set in the terminal.

## Not built yet

Email sign-in, email alerts at $10 and $16, a page where a trainee can read his own training log, a way to delete a person's records, serving approved fixed pieces with no model call, and streaming.

To run the site on this machine, give Wrangler a short folder for its local database, since the repo's own path may be too long for it: `wrangler.cmd dev --persist-to C:\wstate`, after `wrangler.cmd d1 execute bootcamp-site --local --persist-to C:\wstate --file=schema.sql`, with `OWNER_TOKEN` and `ANTHROPIC_API_KEY` in a `.dev.vars` file.
