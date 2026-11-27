# The website

A Cloudflare Worker that runs the boot camp skill for invited trainees, and keeps the cost within a fixed budget. This is rollout step 1: one user, the owner, testing in one group.

## How a turn is answered

The Worker holds the Anthropic key. The browser never sees it. For each message it:

1. checks the sender's token, the pause switch and the spending limits, before anything is spent;
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

## Pause everything

The test page has a "Pause all training" button. From a terminal:

`wrangler.cmd d1 execute bootcamp-site --remote --command "INSERT INTO settings (key, value) VALUES ('kill', '1') ON CONFLICT(key) DO UPDATE SET value = '1'"`

Set the value to `'0'` to resume.

## Check a change

- `npm.cmd run typecheck`
- `npm.cmd test` (limits, prices, and who speaks when; no model is called)
- `npm.cmd run check-bundle` (builds the Worker without deploying it)

## Not built yet

Invites and trainee sign-in, the trainee's own pages, voice, email alerts at $10 and $16, serving approved fixed pieces with no model call, and streaming.
