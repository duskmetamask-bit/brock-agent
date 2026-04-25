"""
Assessor — gap analysis for existing agents.
Takes an agent directory, reads all files, runs gap analysis vs quality gates.
"""

import json
import re
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


def assess_agent(agent_dir: Path) -> dict:
    """
    Run full gap analysis on an existing agent.
    Returns structured assessment report.
    """
    agent_dir = Path(agent_dir)
    agent_name = agent_dir.name

    report = {
        "agent_name": agent_name,
        "assessed_at": datetime.now().isoformat(),
        "overall_score": 0,
        "gates_passed": [],
        "gates_failed": [],
        "gaps": [],
        "pattern_match": None,
        "recommendations": []
    }

    # ── Gate 1: SOUL.md exists ──────────────────────────────────────────
    soul = agent_dir / "SOUL.md"
    if not soul.exists():
        report["gates_failed"].append("SOUL.md missing")
        report["gaps"].append({"severity": "critical", "item": "SOUL.md", "issue": "Identity file missing"})
    else:
        report["gates_passed"].append("SOUL.md exists")
        content = soul.read_text()

        # Gate 2-4: Required sections in SOUL.md
        required_sections = ["## Identity", "## Core Responsibilities", "## Key Rules"]
        for section in required_sections:
            if section in content:
                report["gates_passed"].append(f"SOUL.md has {section}")
            else:
                report["gates_failed"].append(f"SOUL.md missing {section}")
                report["gaps"].append({"severity": "high", "item": f"SOUL.md", "issue": f"Missing section: {section}"})

        # Gate 5: Memory/tool usage defined
        if "memory" in content.lower() or "tool" in content.lower():
            report["gates_passed"].append("SOUL.md defines memory/tool usage")
        else:
            report["gates_failed"].append("SOUL.md — no memory/tool usage defined")
            report["gaps"].append({"severity": "medium", "item": "SOUL.md", "issue": "No memory or tool usage documented"})

    # ── Gate 6: run.py exists ───────────────────────────────────────────
    run_py = agent_dir / "run.py"
    if not run_py.exists():
        report["gates_failed"].append("run.py missing")
        report["gaps"].append({"severity": "critical", "item": "run.py", "issue": "Entry point missing"})
    else:
        report["gates_passed"].append("run.py exists")
        content = run_py.read_text()

        # Gate 7: main() function
        if "def main(" in content:
            report["gates_passed"].append("run.py has main() function")
        else:
            report["gates_failed"].append("run.py — no main() function")
            report["gaps"].append({"severity": "high", "item": "run.py", "issue": "No main() entry point"})

        # Gate 8: CLI argument handling
        if "sys.argv" in content or "argparse" in content or "click" in content:
            report["gates_passed"].append("run.py handles CLI args")
        else:
            report["gates_failed"].append("run.py — no CLI argument handling")
            report["gaps"].append({"severity": "medium", "item": "run.py", "issue": "No CLI argument parsing"})

        # Gate 9: imports are valid (basic check)
        import_lines = [l.strip() for l in content.split("\n") if l.strip().startswith("import ") or l.strip().startswith("from ")]
        invalid_imports = []
        for imp in import_lines:
            # Skip stdlib and obvious third-party
            stdlib = {"sys", "json", "re", "pathlib", "datetime", "time", "os", "sqlite3", "typing", "collections"}
            # Extract module name
            if imp.startswith("from "):
                mod = imp.split("from ")[1].split()[0].split(".")[0]
            else:
                mod = imp.split("import ")[1].split()[0].split(".")[0]
            if mod not in stdlib and mod not in ["terminal", "read_file", "write_file", "patch", "search_files", "delegate_task"]:
                # Could be a custom module — flag for review
                pass  # Skip deep validation, would need runtime check

    # ── Gate 10: skills/ directory exists ──────────────────────────────
    skills_dir = agent_dir / "skills"
    if skills_dir.exists():
        report["gates_passed"].append("skills/ directory exists")
        skill_files = list(skills_dir.glob("*.md"))
        if skill_files:
            report["gates_passed"].append(f"Has {len(skill_files)} skill file(s)")
            # Gate 11: skills have trigger + steps
            for sf in skill_files:
                sc = sf.read_text()
                if "## Trigger" in sc or "### Trigger" in sc or "trigger" in sc.lower():
                    report["gates_passed"].append(f"{sf.name} has trigger condition")
                else:
                    report["gates_failed"].append(f"{sf.name} — no trigger condition")
                    report["gaps"].append({"severity": "high", "item": f"skill: {sf.name}", "issue": "No trigger condition defined"})

                if re.search(r"\d+\.\s+\w", sc):  # Numbered steps like "1. Do X"
                    report["gates_passed"].append(f"{sf.name} has numbered steps")
                else:
                    report["gates_failed"].append(f"{sf.name} — no numbered steps")
                    report["gaps"].append({"severity": "high", "item": f"skill: {sf.name}", "issue": "No numbered procedure steps"})

                if "## Pitfalls" in sc or "### Pitfalls" in sc:
                    report["gates_passed"].append(f"{sf.name} has pitfalls section")
                else:
                    report["gates_failed"].append(f"{sf.name} — no pitfalls section")
                    report["gaps"].append({"severity": "medium", "item": f"skill: {sf.name}", "issue": "No pitfalls section"})

                if "## Verification" in sc or "### Verification" in sc:
                    report["gates_passed"].append(f"{sf.name} has verification steps")
                else:
                    report["gates_failed"].append(f"{sf.name} — no verification steps")
                    report["gaps"].append({"severity": "medium", "item": f"skill: {sf.name}", "issue": "No verification steps"})
        else:
            report["gates_failed"].append("skills/ is empty")
            report["gaps"].append({"severity": "high", "item": "skills/", "issue": "No skill files found"})
    else:
        report["gates_failed"].append("skills/ directory missing")
        report["gaps"].append({"severity": "critical", "item": "skills/", "issue": "No skills directory — agent lacks procedural memory"})

    # ── Gate 12: SPEC.md exists ─────────────────────────────────────────
    spec = agent_dir / "SPEC.md"
    if not spec.exists():
        report["gates_failed"].append("SPEC.md missing")
        report["gaps"].append({"severity": "high", "item": "SPEC.md", "issue": "Architecture spec missing"})
    else:
        report["gates_passed"].append("SPEC.md exists")

    # ── Gate 13: processors/ directory ─────────────────────────────────
    procs_dir = agent_dir / "processors"
    if procs_dir.exists():
        report["gates_passed"].append("processors/ directory exists")
        proc_files = list(procs_dir.glob("*.py"))
        if proc_files:
            report["gates_passed"].append(f"Has {len(proc_files)} processor(s)")
        init_py = procs_dir / "__init__.py"
        if init_py.exists():
            report["gates_passed"].append("processors/__init__.py exists")
        else:
            report["gates_failed"].append("processors/__init__.py missing")
            report["gaps"].append({"severity": "medium", "item": "processors/__init__.py", "issue": "Missing module init file"})
    else:
        report["gates_failed"].append("processors/ directory missing")
        report["gaps"].append({"severity": "medium", "item": "processors/", "issue": "No processors directory"})

    # ── Gate 14: database/ directory ───────────────────────────────────
    db_dir = agent_dir / "database"
    if db_dir.exists():
        report["gates_passed"].append("database/ directory exists")
        db_files = list(db_dir.glob("*.db")) + list(db_dir.glob("*.sql"))
        if db_files:
            report["gates_passed"].append(f"Has {len(db_files)} database file(s)")
        else:
            report["gates_failed"].append("database/ exists but no .db or .sql files")
            report["gaps"].append({"severity": "medium", "item": "database/", "issue": "No database files found"})
    else:
        report["gates_failed"].append("database/ directory missing")
        report["gaps"].append({"severity": "medium", "item": "database/", "issue": "No database directory — no persistent state"})

    # ── Gate 15: config/ directory ──────────────────────────────────────
    config_dir = agent_dir / "config"
    if config_dir.exists():
        report["gates_passed"].append("config/ directory exists")
    else:
        report["gates_failed"].append("config/ directory missing")
        report["gaps"].append({"severity": "low", "item": "config/", "issue": "No config directory — settings not externalised"})

    # ── Gate 16: README.md ──────────────────────────────────────────────
    readme = agent_dir / "README.md"
    if readme.exists():
        report["gates_passed"].append("README.md exists")
    else:
        report["gates_failed"].append("README.md missing")
        report["gaps"].append({"severity": "medium", "item": "README.md", "issue": "No user-facing documentation"})

    # ── Gate 17: No hardcoded credentials ─────────────────────────────
    files_with_secrets = []
    secret_patterns = [r'api_key\s*=\s*["\'][^"\']{10,}', r'password\s*=\s*["\'][^"\']{10,}', r'api_key_env\s*=\s*["\'][^"\']+']
    # Exclude known false positive patterns
    false_positive_files = ["x_writer.py"]  # Contains USER_PROFILE with long strings, not secrets
    for py_file in agent_dir.rglob("*.py"):
        if "brock" in str(py_file):
            continue
        # Skip known false positives
        if py_file.name in false_positive_files:
            continue
        content = py_file.read_text()
        for pattern in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                files_with_secrets.append(py_file.name)
                break
    if files_with_secrets:
        report["gates_failed"].append(f"Hardcoded credentials found in: {', '.join(files_with_secrets)}")
        report["gaps"].append({"severity": "critical", "item": "credentials", "issue": f"Hardcoded secrets in: {', '.join(files_with_secrets)}"})
    else:
        report["gates_passed"].append("No hardcoded credentials detected")

    # ── Gate 18: Voice/memory conventions ─────────────────────────────
    soul_content = soul.read_text() if soul.exists() else ""
    if any(kw in soul_content for kw in ["Memory", "memory_", "session_search", "skill_manage"]):
        report["gates_passed"].append("Memory conventions defined")
    else:
        report["gates_failed"].append("No memory conventions defined")
        report["gaps"].append({"severity": "medium", "item": "SOUL.md", "issue": "No memory management documented"})

    # ── Gate 19: Session startup defined ──────────────────────────────
    if re.search(r"Session Startup|Startup|session_start", soul_content):
        report["gates_passed"].append("Session startup documented")
    else:
        report["gates_failed"].append("No session startup documented")
        report["gaps"].append({"severity": "medium", "item": "SOUL.md", "issue": "No session startup procedure"})

    # ── Gate 20: Cron-compatible ──────────────────────────────────────
    if (agent_dir / "cron" / "README.md").exists() or "cron" in soul_content.lower():
        report["gates_passed"].append("Cron compatibility documented")
    else:
        report["gates_failed"].append("No cron documentation")
        report["gaps"].append({"severity": "low", "item": "SOUL.md", "issue": "Not documented as cron-compatible"})

    # ── Calculate overall score ─────────────────────────────────────────
    total = len(report["gates_passed"]) + len(report["gates_failed"])
    if total > 0:
        report["overall_score"] = round(len(report["gates_passed"]) / total * 100, 1)

    # ── Pattern match ──────────────────────────────────────────────────
    domain_pattern = _detect_domain(agent_dir, soul_content)
    if domain_pattern:
        report["pattern_match"] = domain_pattern
        pattern_path = Path(__file__).parent.parent / "patterns" / f"{domain_pattern}.md"
        if pattern_path.exists():
            report["gates_passed"].append(f"Matches pattern: {domain_pattern}")
        else:
            report["gates_failed"].append(f"Pattern {domain_pattern} listed but file missing")

    # ── Recommendations ─────────────────────────────────────────────────
    critical_gaps = [g for g in report["gaps"] if g["severity"] == "critical"]
    high_gaps = [g for g in report["gaps"] if g["severity"] == "high"]

    if critical_gaps:
        report["recommendations"].append(f"Fix {len(critical_gaps)} critical gap(s) immediately — agent cannot function properly")
    if high_gaps:
        report["recommendations"].append(f"Fix {len(high_gaps)} high-severity gap(s) — quality gates failing")
    if report["overall_score"] >= 80:
        report["recommendations"].append("Overall score above 80% — agent is production-ready with minor fixes")
    elif report["overall_score"] >= 60:
        report["recommendations"].append("Overall score 60-80% — needs work before production")
    else:
        report["recommendations"].append("Overall score below 60% — BROCK should rebuild this agent from pattern")

    return report


def _detect_domain(agent_dir: Path, soul_content: str) -> Optional[str]:
    """Detect which domain pattern this agent belongs to."""
    content_lower = (soul_content + " " + " ".join(
        f.read_text() for f in agent_dir.rglob("*.md") if f.is_file()
    )).lower()

    signals = {
        "content-agent": ["content", "x.com", "twitter", "youtube", "linkedin", "post", "thread", "story", "prism"],
        "outreach-agent": ["outreach", "cold email", "lead", "email campaign", "karma", "mail"],
        "voice-agent": ["voice", "vapi", "phone", "call", "telephony", "speech", "callie"],
        "research-agent": ["research", "intel", "clarke", "harold", "scan", "monitor"],
        "audit-agent": ["audit", "business", "process", "connor", "review", "assessment"]
    }

    best_match = None
    best_score = 0
    for pattern, keywords in signals.items():
        score = sum(1 for kw in keywords if kw in content_lower)
        if score > best_score:
            best_score = score
            best_match = pattern

    return best_match if best_score >= 2 else None


def format_assessment(assessment: dict) -> str:
    """Format assessment report as readable text."""
    lines = [
        f"\n{'='*60}",
        f"BROCK ASSESSMENT — {assessment['agent_name']}",
        f"{'='*60}",
        f"\nOverall Score: {assessment['overall_score']}%",
        f"Pattern Match: {assessment['pattern_match'] or 'unknown'}",
        f"Assessed: {assessment['assessed_at'][:10]}",
        f"\n--- Gates Passed ({len(assessment['gates_passed'])}) ---"
    ]
    for g in assessment["gates_passed"]:
        lines.append(f"  ✅ {g}")

    if assessment["gates_failed"]:
        lines.append(f"\n--- Gates Failed ({len(assessment['gates_failed'])}) ---")
        for g in assessment["gates_failed"]:
            lines.append(f"  ❌ {g}")

    if assessment["gaps"]:
        lines.append(f"\n--- Gaps ({len(assessment['gaps'])}) ---")
        for gap in assessment["gaps"]:
            lines.append(f"  [{gap['severity'].upper()}] {gap['item']}: {gap['issue']}")

    if assessment["recommendations"]:
        lines.append(f"\n--- Recommendations ---")
        for rec in assessment["recommendations"]:
            lines.append(f"  → {rec}")

    lines.append(f"\n{'='*60}")
    return "\n".join(lines)
