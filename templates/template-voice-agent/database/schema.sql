-- {{AGENT_NAME}} Schema
-- Built by BROCK
CREATE TABLE IF NOT EXISTS {{AGENT_NAME_LOWER}}_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS {{AGENT_NAME_LOWER}}_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_date TEXT NOT NULL,
    status TEXT DEFAULT 'ok',
    duration_seconds REAL,
    created_at TEXT DEFAULT (datetime('now'))
);
