"""SPEC writer — generates SPEC.md from brief."""

SPEC_TEMPLATE = """# {agent_name} — SPEC.md
**Agent:** {agent_name}
**Built by:** BROCK
**Date:** {date}
**Status:** BUILT — Phase 1

---

## What It Is

{one_sentence}

**Built from brief:** {domain}

---

## Architecture

```
{agent_name}/
{file_tree}
```

---

## Data Flow

### Input
{inputs}

### Processing
{processing}

### Output
{outputs}

---

## Database Schema

```sql
-- {agent_name} SQLite Schema
{schema}
```

---

## API Dependencies

{api_list}

---

## Skills Architecture

Domain knowledge lives in skill files. Never hardcoded.

| Skill | Purpose | When Loaded |
|-------|---------|-------------|
{skills_table}

---

## Build Phases

| Phase | What | Status |
|-------|------|--------|
| 1 | SOUL + SPEC | ✅ Complete |
| 2 | Directory structure | ✅ Complete |
| 3 | Database schema | ✅ Complete |
| 4 | Skills | ✅ Complete |
| 5 | Processors | ⬜ Pending (implement core logic) |
| 6 | Integration | ⬜ Pending |
| 7 | Quality Gates | ⬜ Pending |

---

## Research Summary

_Research phase (Step 0 of checklist) was completed during build._

---

## Quality Gates

- [ ] SOUL.md complete
- [ ] SPEC.md complete
- [ ] All skills created
- [ ] Database schema valid
- [ ] run.py executes without import errors
- [ ] Processors importable

---

*Built by BROCK on {date}*
"""


def write_spec(agent_name: str, brief: dict) -> str:
    """Generate SPEC.md from brief."""

    from datetime import datetime

    domain = brief.get("domain", "")
    trigger = brief.get("trigger", "on-demand")

    # Build file tree
    skills = brief.get("required_skills", [])
    processors = brief.get("required_processors", [])

    file_tree = f"""├── SOUL.md              ← Identity + voice
├── SPEC.md              ← This file
├── config/
│   └── agent.yaml       ← Configuration
├── database/
│   ├── schema.sql       ← SQLite schema
│   └── {agent_name.lower().replace("-","_")}.db
├── skills/
"""
    for s in skills:
        file_tree += f"│   └── {s}.md\n"
    if not skills:
        file_tree += "│   └── (no skills defined)\n"

    file_tree += "├── processors/\n"
    for p in processors:
        file_tree += f"│   └── {p}.py\n"
    file_tree += "│   └── core.py       ← Main agent loop\n"
    file_tree += "└── run.py              ← Entry point\n"

    # Build skills table
    skills_table = "| Skill | Purpose | When Loaded |\n|-------|---------|-------------|\n"
    for s in skills:
        skills_table += f"| `{s}.md` | (define in brief) | At startup |\n"
    if not skills:
        skills_table += "| (none) | — | — |\n"

    # Schema placeholder
    schema = f"""CREATE TABLE IF NOT EXISTS {agent_name.lower().replace("-","_")}_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);
"""

    api_list = brief.get("apis", [])
    if not api_list:
        api_list = ["(define APIs in brief)"]
    api_str = "\n".join(f"- {a}" for a in api_list)

    inputs = f"- Config: `config/agent.yaml`\n- Trigger: {trigger}\n- Skills: {len(skills)} skill files"
    processing = "- Skills loaded at startup\n- Core loop executes on trigger\n- Results persisted to database"
    outputs = brief.get("outputs", "Reports to MEWY via Telegram, logs to vault")

    one_sentence = f"{agent_name} is an autonomous agent that handles {domain}."

    return SPEC_TEMPLATE.format(
        agent_name=agent_name,
        one_sentence=one_sentence,
        domain=domain,
        file_tree=file_tree,
        schema=schema,
        skills_table=skills_table,
        api_list=api_str,
        inputs=inputs,
        processing=processing,
        outputs=outputs,
        date=datetime.now().strftime("%Y-%m-%d")
    )


if __name__ == "__main__":
    test = {"domain": "cold email outreach", "required_skills": ["cold-email-skill"]}
    print(write_spec("OUTREACH", test))
