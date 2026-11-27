-- The website's database. Safe to run more than once.

-- Switches the owner can flip without a deploy. key 'kill' = '1' pauses all training.
CREATE TABLE IF NOT EXISTS settings (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

-- One row for every call to a model, with what it cost in micro-dollars. The quotas are sums over this table.
CREATE TABLE IF NOT EXISTS usage (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id            TEXT    NOT NULL,
  session_id         TEXT    NOT NULL,
  day                TEXT    NOT NULL,  -- YYYY-MM-DD, UTC
  at                 INTEGER NOT NULL,  -- milliseconds since 1970
  role               TEXT    NOT NULL,  -- coach, router or member
  model              TEXT    NOT NULL,
  input_tokens       INTEGER NOT NULL DEFAULT 0,
  output_tokens      INTEGER NOT NULL DEFAULT 0,
  cache_read_tokens  INTEGER NOT NULL DEFAULT 0,
  cache_write_tokens INTEGER NOT NULL DEFAULT 0,
  cost_micros        INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS usage_day ON usage (day, user_id);

-- A training session: the conversation so far, and what it has cost.
CREATE TABLE IF NOT EXISTS sessions (
  id          TEXT    PRIMARY KEY,
  user_id     TEXT    NOT NULL,
  grp         TEXT    NOT NULL,
  state       TEXT    NOT NULL,  -- JSON
  turns       INTEGER NOT NULL DEFAULT 0,
  cost_micros INTEGER NOT NULL DEFAULT 0,
  created_at  INTEGER NOT NULL,
  updated_at  INTEGER NOT NULL
);

-- The training log: one card for each session, replaced as the session goes on.
CREATE TABLE IF NOT EXISTS cards (
  session_id TEXT    PRIMARY KEY,
  user_id    TEXT    NOT NULL,
  grp        TEXT    NOT NULL,
  body       TEXT    NOT NULL,
  saved_at   INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS cards_newest ON cards (user_id, grp, saved_at);

-- The people who may train. The owner signs in with a secret of his own and has no row here.
-- An invited trainee signs in with a code; only its SHA-256 hash is kept.
CREATE TABLE IF NOT EXISTS users (
  id         TEXT    PRIMARY KEY,
  name       TEXT    NOT NULL,
  code_hash  TEXT    NOT NULL UNIQUE,
  active     INTEGER NOT NULL DEFAULT 1,
  created_at INTEGER NOT NULL
);
