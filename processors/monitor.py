"""
BROCK Monitoring Dashboard
Build stats and health metrics.

Usage:
    python3 processors/monitor.py              — print dashboard to stdout
    python3 processors/monitor.py --format json  — JSON output
    python3 processors/monitor.py dashboard.md  — write to file
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

BROCK_DIR = Path.home() / ".hermes" / "agents" / "brock"
DB_PATH = BROCK_DIR / "database" / "brock.db"


def get_stats() -> dict:
    """Query BROCK database and return stats."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    def one(query):
        cur.execute(query)
        r = cur.fetchone()
        return r[0] if r else 0

    def all_rows(query):
        cur.execute(query)
        return cur.fetchall()

    stats = {}

    # Basic counts
    stats["total_agents"] = one("SELECT COUNT(*) FROM agents")
    stats["total_builds"] = one("SELECT COUNT(*) FROM builds")
    stats["total_versions"] = one("SELECT COUNT(*) FROM versions")
    stats["open_issues"] = one("SELECT COUNT(*) FROM issues WHERE resolved = 0")
    stats["resolved_issues"] = one("SELECT COUNT(*) FROM issues WHERE resolved = 1")
    stats["self_reviews"] = one("SELECT COUNT(*) FROM self_reviews")

    # Build success rate
    stats["successful_builds"] = one("SELECT COUNT(*) FROM builds WHERE status = 'success'")
    if stats["total_builds"] > 0:
        stats["success_rate"] = round(100 * stats["successful_builds"] / stats["total_builds"], 1)
    else:
        stats["success_rate"] = 0

    # Average gates
    stats["avg_gates"] = round(one("SELECT AVG(gates_passed) FROM builds WHERE gates_passed IS NOT NULL") or 0, 1)
    stats["avg_build_time"] = round(one("SELECT AVG(build_time_seconds) FROM builds WHERE build_time_seconds IS NOT NULL") or 0, 1)

    # This week
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    stats["builds_this_week"] = one(f"SELECT COUNT(*) FROM builds WHERE built_at >= '{week_ago}'")
    stats["agents_this_week"] = one(f"SELECT COUNT(*) FROM agents WHERE first_built >= '{week_ago}'")

    # Top issues by severity
    stats["critical_issues"] = one("SELECT COUNT(*) FROM issues WHERE severity = 'critical' AND resolved = 0")
    stats["high_issues"] = one("SELECT COUNT(*) FROM issues WHERE severity = 'high' AND resolved = 0")

    # Recent builds
    cur.execute("""
        SELECT agent_name, version, gates_passed, gates_total, build_time_seconds, status, built_at
        FROM builds ORDER BY built_at DESC LIMIT 10
    """)
    stats["recent_builds"] = [
        {"agent": r[0], "version": r[1], "gates": f"{r[2]}/{r[3]}", "time_s": r[4], "status": r[5], "when": r[6]}
        for r in cur.fetchall()
    ]

    # Top patterns
    cur.execute("SELECT pattern_name, COUNT(*) FROM pattern_usage GROUP BY pattern_name ORDER BY COUNT(*) DESC LIMIT 5")
    stats["top_patterns"] = [{"pattern": r[0], "uses": r[1]} for r in cur.fetchall()]

    # Agents list
    cur.execute("SELECT agent_name, current_version, status, total_builds, last_updated FROM agents ORDER BY last_updated DESC LIMIT 20")
    stats["agents"] = [
        {"name": r[0], "version": r[1], "status": r[2], "builds": r[3], "last": r[4]}
        for r in cur.fetchall()
    ]

    # Top issues
    cur.execute("""
        SELECT agent_name, issue_description, severity, source, created_at
        FROM issues WHERE resolved = 0 ORDER BY severity DESC, created_at DESC LIMIT 10
    """)
    stats["top_issues"] = [
        {"agent": r[0], "description": r[1][:80], "severity": r[2], "source": r[3], "when": r[4]}
        for r in cur.fetchall()
    ]

    conn.close()
    return stats


def format_dashboard(stats: dict) -> str:
    """Format stats as a markdown dashboard."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# BROCK Dashboard",
        f"**Updated:** {now}",
        "",
        "## Health Overview",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Agents | {stats['total_agents']} |",
        f"| Total Builds | {stats['total_builds']} |",
        f"| Build Success Rate | {stats['success_rate']}% |",
        f"| Avg Gates Passed | {stats['avg_gates']}/20 |",
        f"| Avg Build Time | {stats['avg_build_time']}s |",
        f"| Builds This Week | {stats['builds_this_week']} |",
        "",
        "## Issues",
        "",
        f"| Severity | Count |",
        f"|----------|-------|",
        f"| Critical | {stats['critical_issues']} |",
        f"| High | {stats['high_issues']} |",
        f"| Open Total | {stats['open_issues']} |",
        f"| Resolved Total | {stats['resolved_issues']} |",
        "",
    ]

    if stats["recent_builds"]:
        lines.append("## Recent Builds")
        lines.append("")
        lines.append(f"| Agent | Version | Gates | Time | Status | When |")
        lines.append(f"|-------|---------|-------|------|--------|------|")
        for b in stats["recent_builds"]:
            time_str = f"{b['time_s']:.1f}s" if b['time_s'] else "-"
            lines.append(f"| {b['agent']} | {b['version']} | {b['gates']} | {time_str} | {b['status']} | {b['when'][:10]} |")
        lines.append("")

    if stats["top_patterns"]:
        lines.append("## Top Patterns")
        lines.append("")
        for p in stats["top_patterns"]:
            lines.append(f"- **{p['pattern']}** — {p['uses']} uses")
        lines.append("")

    if stats["top_issues"]:
        lines.append("## Open Issues")
        lines.append("")
        for i in stats["top_issues"][:5]:
            lines.append(f"- `[{i['severity']}]` {i['agent']}: {i['description']}")
        lines.append("")

    if stats["agents"]:
        lines.append("## Agents")
        lines.append("")
        lines.append(f"| Name | Version | Status | Builds |")
        lines.append(f"|------|---------|--------|-------|")
        for a in stats["agents"][:10]:
            lines.append(f"| {a['name']} | {a['version']} | {a['status']} | {a['builds']} |")
        lines.append("")

    lines.append(f"\n*BROCK has conducted {stats['self_reviews']} self-reviews.*")
    return "\n".join(lines)


if __name__ == "__main__":
    import json

    stats = get_stats()

    fmt = "markdown"
    if "--format" in sys.argv:
        idx = sys.argv.index("--format")
        fmt = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "json"
        sys.argv.pop(idx)
        sys.argv.pop(idx)

    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        output_path = Path(sys.argv[1])
        output_path.write_text(format_dashboard(stats))
        print(f"[+] Dashboard written to: {output_path}")
    elif fmt == "json":
        print(json.dumps(stats, indent=2, default=str))
    else:
        print(format_dashboard(stats))
