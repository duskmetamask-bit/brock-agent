"""
BROCK Version Control
Git-style versioning backed by database. Tracks versions per agent.

Usage:
    python3 processors/version_control.py versions AGENT_NAME    — list versions
    python3 processors/version_control.py diff AGENT_NAME v1.0 v1.1  — diff two versions
    python3 processors/version_control.py rollback AGENT_NAME v1.0   — rollback to version
"""

import sys
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional

BROCK_DIR = Path.home() / ".hermes" / "agents" / "brock"
DB_PATH = BROCK_DIR / "database" / "brock.db"


def _conn():
    return sqlite3.connect(DB_PATH)


def _hash_file(path: Path) -> str:
    """Create SHA256 hash of a file."""
    if not path.exists():
        return "MISSING"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _hash_dir(dir_path: Path) -> dict[str, str]:
    """Create file manifest (path -> hash) for a directory."""
    manifest = {}
    if not dir_path.exists():
        return manifest
    for f in sorted(dir_path.rglob("*")):
        if f.is_file() and not any(p.startswith(".") for p in f.parts):
            rel = str(f.relative_to(dir_path))
            manifest[rel] = _hash_file(f)
    return manifest


def record_version(agent_name: str, version: str = None, build_id: int = None, changelog: str = "") -> dict:
    """Record a new version. Auto-increments if version not specified."""
    agent_dir = Path.home() / ".hermes" / "agents" / agent_name
    if not agent_dir.exists():
        return {"success": False, "error": f"Agent not found: {agent_name}"}
    
    conn = _conn()
    cur = conn.cursor()
    
    # Get or bump version
    if version is None:
        cur.execute("SELECT MAX(CAST(SUBSTR(version, 2) AS REAL)) FROM versions WHERE agent_name = ?", (agent_name,))
        row = cur.fetchone()[0]
        next_v = (row or 0) + 0.1
        version = f"v{next_v:.1f}"
    
    # Create manifest
    manifest = _hash_dir(agent_dir)
    manifest_json = str(manifest)  # Simple serialization
    
    # Store in versions table
    cur.execute("""
        INSERT INTO versions (agent_name, version, build_id, changelog)
        VALUES (?, ?, ?, ?)
    """, (agent_name, version, build_id, changelog))
    
    # Store manifest entries
    version_id = cur.lastrowid
    for file_path, file_hash in manifest.items():
        cur.execute("""
            INSERT INTO file_manifests (version_id, agent_name, version, file_path, content_hash)
            VALUES (?, ?, ?, ?, ?)
        """, (version_id, agent_name, version, file_path, file_hash))
    
    # Update agent current version
    cur.execute("UPDATE agents SET current_version = ? WHERE agent_name = ?", (version, agent_name))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "version": version, "manifest_size": len(manifest)}


def list_versions(agent_name: str) -> list[dict]:
    """List all versions for an agent."""
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT version, changelog, created_at FROM versions
        WHERE agent_name = ? ORDER BY created_at DESC
    """, (agent_name,))
    rows = cur.fetchall()
    conn.close()
    return [{"version": r[0], "changelog": r[1], "created_at": r[2]} for r in rows]


def diff_versions(agent_name: str, v1: str, v2: str) -> dict:
    """Compare two versions — show what files changed."""
    conn = _conn()
    cur = conn.cursor()
    
    # Get manifests for both versions
    cur.execute("""
        SELECT file_path, content_hash FROM file_manifests
        WHERE agent_name = ? AND version = ?
    """, (agent_name, v1))
    m1 = {r[0]: r[1] for r in cur.fetchall()}
    
    cur.execute("""
        SELECT file_path, content_hash FROM file_manifests
        WHERE agent_name = ? AND version = ?
    """, (agent_name, v2))
    m2 = {r[0]: r[1] for r in cur.fetchall()}
    
    conn.close()
    
    all_files = set(m1.keys()) | set(m2.keys())
    
    added = [f for f in all_files if f in m2 and f not in m1]
    removed = [f for f in all_files if f in m1 and f not in m2]
    changed = [f for f in all_files if f in m1 and f in m2 and m1[f] != m2[f]]
    
    return {
        "agent": agent_name,
        "from": v1,
        "to": v2,
        "added": added,
        "removed": removed,
        "changed": changed,
        "summary": f"{len(added)} added, {len(removed)} removed, {len(changed)} changed"
    }


def rollback(agent_name: str, target_version: str) -> dict:
    """Note: actual file rollback requires git. This logs the intent and warns."""
    agent_dir = Path.home() / ".hermes" / "agents" / agent_name
    if not agent_dir.exists():
        return {"success": False, "error": f"Agent not found: {agent_name}"}
    
    # Log the rollback intent
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE agents SET status = 'rollback_pending', last_updated = ?
        WHERE agent_name = ?
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), agent_name))
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "message": f"Rollback to {target_version} noted. BROCK uses git for file history.",
        "recommendation": "Use git to restore files, then rebuild: python3 run.py rebuild AGENT_NAME",
        "target_version": target_version
    }


def _init_schema():
    """Ensure file_manifests table exists."""
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS file_manifests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_id INTEGER,
            agent_name TEXT NOT NULL,
            version TEXT NOT NULL,
            file_path TEXT NOT NULL,
            content_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    _init_schema()
    
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 processors/version_control.py versions AGENT_NAME")
        print("  python3 processors/version_control.py diff AGENT_NAME v1.0 v1.1")
        print("  python3 processors/version_control.py rollback AGENT_NAME v1.0")
        print("  python3 processors/version_control.py record AGENT_NAME [version]")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    agent = sys.argv[2]
    
    if cmd == "versions":
        versions = list_versions(agent)
        if not versions:
            print(f"No versions found for {agent}")
        else:
            print(f"Versions for {agent}:")
            for v in versions:
                print(f"  {v['version']} — {v['created_at']} — {v['changelog'] or 'no changelog'}")
    
    elif cmd == "diff":
        if len(sys.argv) < 5:
            print("Usage: diff AGENT_NAME v1.0 v1.1")
            sys.exit(1)
        result = diff_versions(agent, sys.argv[3], sys.argv[4])
        print(f"Diff {result['agent']}: {result['from']} → {result['to']}")
        print(f"Summary: {result['summary']}")
        if result['added']: print(f"  Added: {result['added']}")
        if result['removed']: print(f"  Removed: {result['removed']}")
        if result['changed']: print(f"  Changed: {result['changed']}")
    
    elif cmd == "rollback":
        result = rollback(agent, sys.argv[3] if len(sys.argv) > 3 else "v1.0")
        print(f"[*] {result['message']}")
        print(f"    Recommendation: {result['recommendation']}")
    
    elif cmd == "record":
        version = sys.argv[3] if len(sys.argv) > 3 else None
        result = record_version(agent, version=version)
        if result["success"]:
            print(f"[+] Recorded {result['version']} — {result['manifest_size']} files")
        else:
            print(f"[-] Error: {result['error']}")
    
    else:
        print(f"Unknown command: {cmd}")
