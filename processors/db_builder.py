"""Database schema builder — generates SQLite schema from brief."""

BASE_SCHEMA = """-- {agent_name} Database Schema
-- Built by BROCK on {date}

-- State table (key-value store for agent memory)
CREATE TABLE IF NOT EXISTS {agent_name_lower}_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Session log
CREATE TABLE IF NOT EXISTS {agent_name_lower}_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_date TEXT NOT NULL,
    trigger TEXT,
    inputs TEXT,
    outputs TEXT,
    status TEXT DEFAULT 'ok',
    error TEXT,
    duration_seconds REAL,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Activity log (audit trail)
CREATE TABLE IF NOT EXISTS {agent_name_lower}_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_type TEXT NOT NULL,
    description TEXT,
    metadata TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_state_key ON {agent_name_lower}_state(key);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON {agent_name_lower}_sessions(session_date);
CREATE INDEX IF NOT EXISTS idx_activity_type ON {agent_name_lower}_activity(activity_type);
CREATE INDEX IF NOT EXISTS idx_activity_created ON {agent_name_lower}_activity(created_at);
"""


def create_database_schema(agent_name: str, brief: dict = None) -> str:
    """Generate SQLite schema for agent."""

    from datetime import datetime

    return BASE_SCHEMA.format(
        agent_name=agent_name,
        agent_name_lower=agent_name.lower().replace("-", "_"),
        date=datetime.now().strftime("%Y-%m-%d")
    )


def init_database(db_path: str, schema: str) -> bool:
    """Initialize database with schema. Returns True on success."""
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        conn.executescript(schema)
        conn.close()
        return True
    except Exception as e:
        print(f"DB init error: {e}")
        return False


if __name__ == "__main__":
    schema = create_database_schema("TEST_AGENT")
    print(schema)
