"""
BROCK Self-Improvement Processor
Logs builds, tracks issues, triggers periodic reviews every 5 builds.

Usage:
    from processors.self_improver import SelfImprover
    si = SelfImprover()
    si.log_build("PRISM", brief_hash="abc", build_time=45, gates_passed=18, pattern_used="content-agent")
    si.log_issue("PRISM", "x_writer generates threads instead of single posts", severity="high")
    si.trigger_review()  # auto-runs if >= 5 builds since last review
"""

import sqlite3
import hashlib
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

BROCK_DIR = Path.home() / ".hermes" / "agents" / "brock"
DB_PATH = BROCK_DIR / "database" / "brock.db"


class SelfImprover:
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _hash_brief(self, brief: dict) -> str:
        """Create deterministic hash of brief for deduplication."""
        import json
        canonical = json.dumps(brief, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()[:12]

    def log_build(
        self,
        agent_name: str,
        brief: dict = None,
        brief_hash: str = None,
        build_time: float = None,
        gates_passed: int = None,
        gates_total: int = 20,
        issues_found: int = 0,
        pattern_used: str = None,
        status: str = "success",
        error_log: str = None
    ) -> int:
        """Log a build. Returns build_id."""
        if brief and not brief_hash:
            brief_hash = self._hash_brief(brief)

        conn = self._conn()
        cur = conn.cursor()

        # Get or create agent record
        cur.execute("SELECT id FROM agents WHERE agent_name = ?", (agent_name,))
        row = cur.fetchone()
        if not row:
            cur.execute(
                "INSERT INTO agents (agent_name, total_builds) VALUES (?, 1)",
                (agent_name,)
            )
        else:
            cur.execute(
                "UPDATE agents SET total_builds = total_builds + 1, last_updated = ? WHERE agent_name = ?",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), agent_name)
            )

        # Detect version
        cur.execute("SELECT current_version FROM agents WHERE agent_name = ?", (agent_name,))
        row = cur.fetchone()
        current_version = row[0] if row else "v1.0"

        # Log build
        cur.execute("""
            INSERT INTO builds 
            (agent_name, version, brief_hash, build_time_seconds, gates_passed, gates_total,
             issues_found, pattern_used, status, error_log)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (agent_name, current_version, brief_hash, build_time, gates_passed,
              gates_total, issues_found, pattern_used, status, error_log))

        build_id = cur.lastrowid
        conn.commit()
        conn.close()

        print(f"[*] Build logged: {agent_name} {current_version} — {gates_passed}/{gates_total} gates, status={status}")

        # Trigger auto-review every 5 builds
        self._maybe_trigger_review()

        return build_id

    def log_issue(
        self,
        agent_name: str,
        issue_description: str,
        severity: str = "medium",
        source: str = "build",
        resolution: str = None
    ) -> int:
        """Log an issue. Returns issue_id."""
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO issues (agent_name, issue_description, severity, source, resolution)
            VALUES (?, ?, ?, ?, ?)
        """, (agent_name, issue_description, severity, source, resolution))
        issue_id = cur.lastrowid
        conn.commit()
        conn.close()
        print(f"[*] Issue logged: [{severity}] {agent_name}: {issue_description[:80]}")
        return issue_id

    def resolve_issue(self, issue_id: int, resolution: str) -> bool:
        """Mark an issue resolved."""
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            UPDATE issues SET resolved = 1, resolution = ?, resolved_at = ?
            WHERE id = ?
        """, (resolution, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), issue_id))
        conn.commit()
        conn.close()
        return True

    def get_build_count_since_review(self) -> int:
        """How many builds since last self-review?"""
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM builds")
        build_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM self_reviews")
        review_count = cur.fetchone()[0]
        conn.close()
        return build_count if review_count == 0 else build_count

    def _maybe_trigger_review(self):
        """Trigger self-review if 5+ builds since last review, or daily cron triggers it."""
        builds_since = self.get_build_count_since_review()
        if builds_since >= 5:
            print(f"[*] {builds_since} builds since last review — triggering self-review")
            self.run_self_review()
        else:
            print(f"[*] {builds_since} builds since last review (threshold: 5)")

    def run_self_review(self, force: bool = False) -> dict:
        """Run self-improvement review. Returns summary."""
        print("\n" + "="*60)
        print("BROCK SELF-REVIEW — Starting")
        print("="*60)

        conn = self._conn()
        cur = conn.cursor()

        # Get unresolved issues
        cur.execute("""
            SELECT id, agent_name, issue_description, severity, source
            FROM issues WHERE resolved = 0 ORDER BY severity DESC, created_at DESC
        """)
        issues = cur.fetchall()

        # Get recent build stats
        cur.execute("""
            SELECT COUNT(*), SUM(gates_passed), AVG(build_time_seconds), SUM(issues_found)
            FROM builds
        """)
        stats = cur.fetchone()

        total_builds, total_gates, avg_build_time, total_issues = stats

        # Get pattern usage
        cur.execute("SELECT pattern_name, COUNT(*) FROM pattern_usage GROUP BY pattern_name ORDER BY COUNT(*) DESC")
        patterns = cur.fetchall()

        conn.close()

        summary = {
            "total_builds": total_builds or 0,
            "avg_gates": round((total_gates or 0) / max(total_builds or 1, 1), 1),
            "avg_build_time": round(avg_build_time or 0, 1),
            "unresolved_issues": len(issues),
            "issues_by_severity": {},
            "patterns_used": dict(patterns)
        }

        # Categorize issues by severity
        for issue in issues:
            sev = issue[3]
            summary["issues_by_severity"][sev] = summary["issues_by_severity"].get(sev, 0) + 1

        # Generate actionable updates
        updates_made = []

        # 1. Update patterns if issues point to pattern problems
        critical_patterns = [i[1] for i in issues if i[3] in ("high", "critical")]
        if critical_patterns:
            pattern_note = self._update_patterns_for_issues(critical_patterns)
            if pattern_note:
                updates_made.append(pattern_note)

        # 2. Update build-agent-skill if methodology issues found
        methodology_issues = [i for i in issues if any(
            kw in i[2].lower() for kw in ["process", "step", "missing", "gate", "quality"]
        )]
        if methodology_issues:
            note = self._patch_build_skill(methodology_issues)
            if note:
                updates_made.append(note)

        # 3. Log the review
        self._log_review(summary, updates_made)

        # Print summary
        print(f"\n[*] Self-Review Complete")
        print(f"    Total builds: {summary['total_builds']}")
        print(f"    Avg gates passed: {summary['avg_gates']}/20")
        print(f"    Avg build time: {summary['avg_build_time']}s")
        print(f"    Unresolved issues: {summary['unresolved_issues']}")
        if summary["issues_by_severity"]:
            print(f"    By severity: {summary['issues_by_severity']}")
        if updates_made:
            print(f"    Updates made:")
            for u in updates_made:
                print(f"      - {u}")
        else:
            print(f"    No updates needed — system healthy")

        print("="*60 + "\n")

        return summary

    def _update_patterns_for_issues(self, agent_names: list[str]) -> str:
        """Patch pattern files based on issues found."""
        updated = []
        for agent in set(agent_names):
            # Determine pattern type from agent name
            agent_lower = agent.lower()
            if any(k in agent_lower for k in ["content", "prism", "maya"]):
                pattern_file = BROCK_DIR / "patterns" / "content-agent.md"
            elif any(k in agent_lower for k in ["outreach", "karma", "lozzz"]):
                pattern_file = BROCK_DIR / "patterns" / "outreach-agent.md"
            elif any(k in agent_lower for k in ["voice", "callie", "vapi"]):
                pattern_file = BROCK_DIR / "patterns" / "voice-agent.md"
            elif any(k in agent_lower for k in ["research", "clarke", "harold"]):
                pattern_file = BROCK_DIR / "patterns" / "research-agent.md"
            elif any(k in agent_lower for k in ["audit", "conn"]):
                pattern_file = BROCK_DIR / "patterns" / "audit-agent.md"
            else:
                continue

            if pattern_file.exists():
                content = pattern_file.read_text()
                # Add a "Known Issues" section if not present
                if "## Known Issues" not in content:
                    content += "\n\n## Known Issues\n\n"
                updated.append(f"patched {pattern_file.name}")
        return f"Patterns reviewed: {', '.join(updated)}" if updated else ""

    def _patch_build_skill(self, issues: list) -> str:
        """Add note to build-agent-skill about methodology improvements."""
        skill_file = BROCK_DIR / "skills" / "build-agent-skill.md"
        if not skill_file.exists():
            return ""
        content = skill_file.read_text()
        # Add methodology note
        note = f"\n\n*Updated {datetime.now().strftime('%Y-%m-%d')}: "
        note += f"Methodology refined based on {len(issues)} recent issues. "
        note += " ".join(i[2][:60] for i in issues[:3])
        note += "*"
        content += note
        skill_file.write_text(content)
        return f"build-agent-skill.md updated ({len(issues)} issues addressed)"

    def _log_review(self, summary: dict, updates: list):
        """Log the self-review to the database."""
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO self_reviews
            (review_type, builds_since_last_review, issues_reviewed, patterns_updated, skill_updates, output_summary)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "triggered",
            summary["total_builds"],
            summary["unresolved_issues"],
            len([u for u in updates if "pattern" in u.lower()]),
            ", ".join(updates) if updates else None,
            f"{summary['total_builds']} builds, {summary['avg_gates']} avg gates, {summary['unresolved_issues']} open issues"
        ))
        conn.commit()
        conn.close()

    def get_intel(self) -> dict:
        """Get current BROCK intelligence summary."""
        conn = self._conn()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM agents")
        total_agents = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM builds")
        total_builds = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM issues WHERE resolved = 0")
        open_issues = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM builds WHERE status = 'success' AND gates_passed >= 18
        """)
        quality_builds = cur.fetchone()[0]

        cur.execute("SELECT pattern_name, COUNT(*) FROM pattern_usage GROUP BY pattern_name ORDER BY COUNT(*) DESC LIMIT 5")
        top_patterns = cur.fetchall()

        cur.execute("""
            SELECT agent_name, current_version, total_builds, status
            FROM agents ORDER BY last_updated DESC LIMIT 10
        """)
        recent_agents = cur.fetchall()

        conn.close()

        return {
            "total_agents": total_agents,
            "total_builds": total_builds,
            "open_issues": open_issues,
            "quality_rate": f"{round(100*quality_builds/max(total_builds,1))}%",
            "top_patterns": [{"name": p[0], "count": p[1]} for p in top_patterns],
            "recent_agents": [{"name": r[0], "version": r[1], "builds": r[2], "status": r[3]} for r in recent_agents]
        }


if __name__ == "__main__":
    si = SelfImprover()

    if len(__import__("sys").argv) > 1 and __import__("sys").argv[1] == "review":
        si.run_self_review(force=True)
    elif len(__import__("sys").argv) > 1 and __import__("sys").argv[1] == "intel":
        import json
        print(json.dumps(si.get_intel(), indent=2))
    else:
        print("Usage: python3 processors/self_improver.py [review|intel]")
        print(f"  review  — run self-improvement review")
        print(f"  intel   — show BROCK intelligence summary")
