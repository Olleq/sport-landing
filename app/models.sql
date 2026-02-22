PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS campaigns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1,
  is_default INTEGER NOT NULL DEFAULT 0,
  mode TEXT NOT NULL DEFAULT 'fixed',   -- 'fixed' | 'individual'
  primary_code TEXT
);

CREATE TABLE IF NOT EXISTS codes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  camp_id INTEGER NOT NULL,
  code TEXT NOT NULL,
  is_used INTEGER NOT NULL DEFAULT 0,
  used_by_signup_id INTEGER,
  used_at TEXT,
  FOREIGN KEY (camp_id) REFERENCES campaigns(id) ON DELETE CASCADE,
  UNIQUE (camp_id, code)
);

CREATE TABLE IF NOT EXISTS signups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  camp_id INTEGER NOT NULL,
  channel TEXT,
  email TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending', -- pending | confirmed
  token TEXT NOT NULL,
  assigned_code TEXT,
  created_at TEXT NOT NULL,
  confirmed_at TEXT,
  FOREIGN KEY (camp_id) REFERENCES campaigns(id) ON DELETE CASCADE,
  UNIQUE (camp_id, email)
);

CREATE INDEX IF NOT EXISTS idx_signups_token ON signups(token);
CREATE INDEX IF NOT EXISTS idx_signups_status ON signups(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_default ON campaigns(is_default);
