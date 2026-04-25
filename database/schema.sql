-- BROCK Internal Database Schema
-- Tracks agents built, builds, issues, and self-improvement

-- Agent registry: every agent BROCK has built or assessed
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT UNIQUE NOT NULL,
    domain TEXT,
    brief_hash TEXT,
    built_by TEXT DEFAULT 'BROCK',
    status TEXT DEFAULT 'active',  -- active, archived, rebuilding
    first_built TEXT DEFAULT (datetime('now')),
    last_updated TEXT DEFAULT (datetime('now')),
    total_builds INTEGER DEFAULT 0,
    current_version TEXT DEFAULT 'v1.0',
    notes TEXT
);

-- Builds log: every build attempt
CREATE TABLE IF NOT EXISTS builds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    version TEXT NOT NULL,
    brief_hash TEXT,
    build_time_seconds REAL,
    gates_passed INTEGER,
    gates_total INTEGER DEFAULT 20,
    issues_found INTEGER DEFAULT 0,
    pattern_used TEXT,
    status TEXT DEFAULT 'success',  -- success, partial, failed
    error_log TEXT,
    built_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (agent_name) REFERENCES agents(agent_name)
);

-- Issues log: problems found during builds or in production
CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT,
    issue_description TEXT NOT NULL,
    severity TEXT DEFAULT 'medium',  -- low, medium, high, critical
    source TEXT DEFAULT 'build',  -- build, production, review
    resolution TEXT,
    resolved INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    resolved_at TEXT
);

-- Versions: version history for each agent
CREATE TABLE IF NOT EXISTS versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    version TEXT NOT NULL,
    build_id INTEGER,
    changelog TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (agent_name) REFERENCES agents(agent_name)
);

-- Pattern usage: which patterns are used, how often
CREATE TABLE IF NOT EXISTS pattern_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL,
    agent_name TEXT,
    used_at TEXT DEFAULT (datetime('now')),
    notes TEXT
);

-- Intelligence briefs: market research outputs
CREATE TABLE IF NOT EXISTS intelligence_briefs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    content TEXT,
    sources_found INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Self-review log: when BROCK did a self-improvement review
CREATE TABLE IF NOT EXISTS self_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_type TEXT NOT NULL,  -- periodic, triggered, daily
    builds_since_last_review INTEGER DEFAULT 0,
    issues_reviewed INTEGER DEFAULT 0,
    patterns_updated INTEGER DEFAULT 0,
    skill_updates TEXT,
    output_summary TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_builds_agent ON builds(agent_name);
CREATE INDEX IF NOT EXISTS idx_builds_status ON builds(status);
CREATE INDEX IF NOT EXISTS idx_issues_agent ON issues(agent_name);
CREATE INDEX IF NOT EXISTS idx_issues_severity ON issues(severity);
CREATE INDEX IF NOT EXISTS idx_issues_unresolved ON issues(resolved);
CREATE INDEX IF NOT EXISTS idx_versions_agent ON versions(agent_name);
CREATE INDEX IF NOT EXISTS idx_intel_topic ON intelligence_briefs(topic);
CREATE INDEX IF NOT EXISTS idx_selfreviews_date ON self_reviews(created_at);
