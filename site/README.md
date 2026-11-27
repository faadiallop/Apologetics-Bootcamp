# The website

A Cloudflare Worker that runs the boot camp skill, by voice only, for the owner and the people he invites, and keeps the cost within a fixed budget.

## How a turn is answered

The Worker holds the Anthropic key. The browser never sees it. For each message it:

1. checks who is asking (the owner's token, or an invite code that still stands), the pause switch and that person's spending limits, before anything is spent;
2. decides who speaks:
    - outside a practice round, the **coach** (Sonnet), with the whole skill and the group's materials;
    - inside a round, a small **router** (Haiku) reads the round so far and chooses: the **member** (Haiku) answers, or the coach is called back for a hint or to close the round;
3. records what each call cost, from the token counts the API reports, and saves the session and the trainee's card.

The skill's files are bundled in when the Worker is built (`src/materials.ts`), so a change to the skill reaches the site at the next deploy. A group's fixed pieces are included only once its file is marked approved.

## Limits

Set in `wrangler.jsonc` under `vars`, in US dollars. They are sized for $20 a month and five testers.

| Limit | Value |
| --- | --- |
| One trainee, a day | $0.50 |
| One trainee, a month | $3.50 |
| The whole site, a day | $1.50 |
| The whole site, a month | $20 |
| One session | $0.60 or 40 turns |
| Messages a minute | 6 |

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

## Server logs

The Worker's logs are kept by Cloudflare (`observability` in `wrangler.jsonc`). Each turn logs who, which session, which models were called, the cost, and any error. It never logs what was said. Read them in the Cloudflare dashboard under Workers & Pages, `bootcamp-site`, Logs, or watch them live with `wrangler.cmd tail bootcamp-site`.

## Check a change

- `npm.cmd run typecheck`
- `npm.cmd test` (limits, prices, invite codes, and who speaks when; no model is called)
- `npm.cmd run check-bundle` (builds the Worker without deploying it)

## Not built yet

Email sign-in, email alerts at $10 and $16, a page where a trainee can read his own training log, a way to delete a person's records, serving approved fixed pieces with no model call, and streaming.

To run the site on this machine, give Wrangler a short folder for its local database, since the repo's own path may be too long for it: `wrangler.cmd dev --persist-to C:\wstate`, after `wrangler.cmd d1 execute bootcamp-site --local --persist-to C:\wstate --file=schema.sql`, with `OWNER_TOKEN` and `ANTHROPIC_API_KEY` in a `.dev.vars` file.
