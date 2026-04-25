"""
Fixer — patches gaps found by the assessor.
Takes an assessment dict and applies all recommended fixes to the agent directory.
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def fix_agent(agent_dir: Path, assessment: dict) -> dict:
    """
    Apply all patchable gaps from an assessment to an agent directory.
    Returns a report of what was fixed.
    """
    agent_dir = Path(agent_dir)
    agent_name = agent_dir.name
    report = {
        "agent_name": agent_name,
        "fixed": [],
        "skipped": [],
        "errors": []
    }

    # ── Categorise gaps by fix type ────────────────────────────────────
    gaps = assessment.get("gaps", [])

    for gap in gaps:
        item = gap["item"]
        issue = gap["issue"]
        severity = gap["severity"]

        try:
            # SOUL.md fixes
            if "SOUL.md" in item:
                _fix_soul(agent_dir, gap, report)

            # Skill file fixes
            elif item.startswith("skill:"):
                skill_name = item.split("skill: ")[1]
                _fix_skill(agent_dir, skill_name, gap, report)

            # run.py missing
            elif "run.py" in item and "missing" in issue.lower():
                _fix_runpy(agent_dir, agent_name, report)

            # README.md missing
            elif "README.md" in item and "missing" in issue.lower():
                _fix_readme(agent_dir, agent_name, report)

            # processors/ missing
            elif ("processors/" in item or "processors" in item) and "missing" in issue.lower():
                _fix_processors(agent_dir, report)

            # Hardcoded credentials
            elif "credentials" in issue.lower() or "hardcoded" in issue.lower():
                # Credentials need manual review — flag but don't auto-fix
                report["skipped"].append(f"{item}: Credentials issue — requires manual review")

            # Cron docs
            elif "cron" in issue.lower():
                _fix_cron_doc(agent_dir, agent_name, report)

            else:
                report["skipped"].append(f"{item}: {issue} — no auto-fix available")

        except Exception as e:
            report["errors"].append(f"{item}: {e}")

    return report


def _fix_soul(agent_dir: Path, gap: dict, report: dict):
    """Patch SOUL.md with missing sections."""
    soul = agent_dir / "SOUL.md"
    if not soul.exists():
        report["errors"].append("SOUL.md does not exist — cannot patch")
        return

    content = soul.read_text()
    issue = gap["issue"]
    agent_name = agent_dir.name

    if "## Identity" in issue and "## Identity" not in content:
        identity = f"""
## Identity

**Name:** {agent_name.upper()}
**Role:** [describe what this agent does]
**Owner:** MEWY
**Platform:** Hermes CLI
**Status:** [status]

---

"""
        content = identity + content
        report["fixed"].append("SOUL.md: Added ## Identity section")

    if "Missing section: ## Core Responsibilities" in issue and "## Core Responsibilities" not in content:
        core_resp = """

## Core Responsibilities

1. [Primary responsibility]
2. [Secondary responsibility]
3. [Tertiary responsibility]

---

"""
        # Insert after ## Identity if present, else at top
        if "## Identity" in content:
            content = content.replace("## Identity\n", "## Identity\n" + core_resp, 1)
        else:
            content = core_resp + content
        report["fixed"].append("SOUL.md: Added ## Core Responsibilities section")

    if "Missing section: ## Key Rules" in issue and "## Key Rules" not in content:
        key_rules = """

## Key Rules

1. [Non-negotiable rule]
2. [Non-negotiable rule]
3. [Non-negotiable rule]

---

"""
        content += key_rules
        report["fixed"].append("SOUL.md: Added ## Key Rules section")

    if "memory" in issue.lower() and "Memory" not in content:
        mem_section = """

## Memory & Tool Conventions

**Session memory:** [how this agent stores session state]
**Persistent memory:** [how this agent uses brock.db or other persistence]
**Tool usage:** [which Hermes tools this agent uses]

---

"""
        content += mem_section
        report["fixed"].append("SOUL.md: Added ## Memory & Tool Conventions section")

    if "session startup" in issue.lower() and "Session Startup" not in content:
        startup = """

## Session Startup

1. [Startup step 1]
2. [Startup step 2]
3. [Startup step 3]

---

"""
        content += startup
        report["fixed"].append("SOUL.md: Added ## Session Startup section")

    if "cron" in issue.lower() and "Cron" not in content:
        cron = """

## Cron Compatibility

This agent [can/cannot] run as a cron job. If cron-compatible:
- Schedule: [how often]
- Trigger: [what starts it]
- Delivery: [where output goes]

---

"""
        content += cron
        report["fixed"].append("SOUL.md: Added ## Cron Compatibility section")

    soul.write_text(content)


def _fix_skill(agent_dir: Path, skill_name: str, gap: dict, report: dict):
    """Patch a skill file with missing sections."""
    skills_dir = agent_dir / "skills"
    if not skills_dir.exists():
        report["errors"].append(f"skills/ directory missing — cannot fix skill {skill_name}")
        return

    # Find matching skill file
    skill_files = list(skills_dir.glob("*.md"))
    skill_file = None
    for sf in skill_files:
        if skill_name.lower() in sf.name.lower():
            skill_file = sf
            break

    if not skill_file:
        report["errors"].append(f"Skill file not found for: {skill_name}")
        return

    content = skill_file.read_text()
    issue = gap["issue"]

    if "no numbered steps" in issue.lower() and not re.search(r"\d+\.\s+\w", content):
        # Add a basic steps section if none exists
        if "## Steps" not in content and "### Steps" not in content:
            steps = """

## Steps

1. [Step 1]
2. [Step 2]
3. [Step 3]

---

"""
            content += steps
            report["fixed"].append(f"{skill_file.name}: Added ## Steps section")
        else:
            report["skipped"].append(f"{skill_file.name}: Steps section exists but content may be incomplete")

    if "no pitfalls" in issue.lower() and "## Pitfalls" not in content:
        pitfalls = """

## Pitfalls

1. [Common mistake to avoid]
2. [Common mistake to avoid]

---

"""
        content += pitfalls
        report["fixed"].append(f"{skill_file.name}: Added ## Pitfalls section")

    if "no verification" in issue.lower() and "## Verification" not in content:
        verification = """

## Verification

To verify this skill is working correctly:
1. [Check 1]
2. [Check 2]

---

"""
        content += verification
        report["fixed"].append(f"{skill_file.name}: Added ## Verification section")

    skill_file.write_text(content)


def _fix_runpy(agent_dir: Path, agent_name: str, report: dict):
    """Create a run.py entry point."""
    run_py = agent_dir / "run.py"
    if run_py.exists():
        report["skipped"].append("run.py already exists")
        return

    template = f'''"""
{agent_name} — Entry Point
Built by BROCK on {datetime.now().strftime("%Y-%m-%d")}
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """{agent_name} main loop."""
    print(f"Running {agent_name}...")
    # TODO: Implement core logic
    print(f"{{agent_name}} complete.")


if __name__ == "__main__":
    main()
'''
    run_py.write_text(template)
    report["fixed"].append("run.py: Created entry point")


def _fix_readme(agent_dir: Path, agent_name: str, report: dict):
    """Create a README.md."""
    readme = agent_dir / "README.md"
    if readme.exists():
        report["skipped"].append("README.md already exists")
        return

    template = f"""# {agent_name}

**What it does:** [description]
**Owner:** MEWY
**Platform:** Hermes CLI

---

## Commands

```bash
cd ~/.hermes/agents/{agent_name.lower()}
python3 run.py
```

---

## Architecture

```
{agent_name.lower()}/
├── SOUL.md
├── SPEC.md
├── run.py
├── skills/
├── processors/
├── database/
└── config/
```

---

## Status

[BUILDING / LIVE / PAUSED]
"""
    readme.write_text(template)
    report["fixed"].append("README.md: Created README")


def _fix_processors(agent_dir: Path, report: dict):
    """Create processors/ directory with __init__.py and core.py."""
    procs_dir = agent_dir / "processors"
    if procs_dir.exists():
        report["skipped"].append("processors/ already exists")
        return

    procs_dir.mkdir(exist_ok=True)
    (procs_dir / "__init__.py").write_text(
        '"""Processors for this agent."""\nfrom .core import main\n__all__ = ["main"]\n'
    )
    (procs_dir / "core.py").write_text(
        '"""Core processor."""\ndef main():\n    print("Running...")\nif __name__ == "__main__":\n    main()\n'
    )
    report["fixed"].append("processors/: Created directory + __init__.py + core.py")


def _fix_cron_doc(agent_dir: Path, agent_name: str, report: dict):
    """Add cron documentation to SOUL.md or create a cron/README.md."""
    soul = agent_dir / "SOUL.md"
    if soul.exists():
        content = soul.read_text()
        if "## Cron" not in content:
            cron_section = """

## Cron Compatibility

This agent can run on a schedule. To set up a cron:
1. Identify the trigger (daily, weekly, on-event)
2. Create a cron job pointing to `python3 run.py`
3. Set delivery destination (telegram, local, origin)

---

"""
            content += cron_section
            soul.write_text(content)
            report["fixed"].append("SOUL.md: Added ## Cron Compatibility section")
    else:
        report["skipped"].append("SOUL.md missing — cannot add cron section")


def format_fix_report(report: dict) -> str:
    """Format fix report as readable text."""
    lines = [
        f"\n{'='*60}",
        f"BROCK FIX REPORT — {report['agent_name']}",
        f"{'='*60}",
        f"\n--- Fixed ({len(report['fixed'])}) ---"
    ]
    for f in report["fixed"]:
        lines.append(f"  ✅ {f}")

    if report["skipped"]:
        lines.append(f"\n--- Skipped ({len(report['skipped'])}) ---")
        for s in report["skipped"]:
            lines.append(f"  ⏭ {s}")

    if report["errors"]:
        lines.append(f"\n--- Errors ({len(report['errors'])}) ---")
        for e in report["errors"]:
            lines.append(f"  ❌ {e}")

    lines.append(f"\n{'='*60}")
    return "\n".join(lines)
