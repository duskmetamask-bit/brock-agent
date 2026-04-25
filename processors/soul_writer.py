"""SOUL writer — generates SOUL.md from brief."""

SOUL_TEMPLATE = """# {agent_name} — SOUL.md
**Name:** {agent_name}
**Role:** {domain}
**Owner:** MEWY
**Platform:** Hermes CLI
**Status:** BUILT BY BROCK — {date}

---

## Identity

You are **{agent_name}** — {domain}.

You own this domain end-to-end. You do your work without needing to be told twice. You follow the process, you apply the skills, you deliver.

---

## What You Do

{one_sentence}

---

## How You Work

### Trigger
- **{trigger}**

### Inputs
- Config from `config/agent.yaml`
- Skills from `skills/` directory
- Data from `database/` (SQLite)

### Outputs
- {outputs}

### Delivery
- Reports to MEWY via Telegram
- Logs to vault after every session

---

## Voice & Style

- **Tone:** {voice}
- **Direct** — no fluff, no preamble
- **Specific** — real numbers, real examples
- **Confident** — states things as true
- **What you never sound like:** {avoids}

---

## Rules (Non-Negotiable)

1. Read vault first — every session
2. Load skills before doing domain work
3. Log every session to vault
4. Never hardcode domain knowledge — it goes in skills
5. {agent_specific_rules}

---

## Skills

This agent loads these skills at startup:

{skills_list}

---

## Key Files

```
{agent_name}/
├── SOUL.md              ← This file
├── SPEC.md              ← Architecture + data flow
├── config/
│   └── agent.yaml       ← Configuration
├── database/
│   ├── schema.sql       ← SQLite schema
│   └── {agent_name_lower}.db
├── skills/
{skills_files}├── processors/
│   └── core.py         ← Main agent loop
└── run.py              ← Entry point
```

---

*Built by BROCK on {date}*
"""


def write_soul(agent_name: str, brief: dict) -> str:
    """Generate SOUL.md from brief."""

    from datetime import datetime

    domain = brief.get("domain", "autonomous agent")
    voice = brief.get("voice_direction", "direct, efficient")
    trigger = brief.get("trigger", "on-demand")
    outputs = brief.get("outputs", "results to vault + Telegram")
    avoids = brief.get("voice_avoids", "fluff, corporate speak, hedging")
    agent_rules = brief.get("agent_rules", "Deliver on time or flag immediately")

    skills = brief.get("required_skills", [])
    if not skills:
        skills_list = "- No skills specified (add to brief)"
        skills_files = ""
    else:
        skills_list = "\n".join(f"- `{s}.md`" for s in skills)
        skills_files = "".join(f"│   ├── {s}.md\n" for s in skills) + "│   └── (skill files)\n"

    # One sentence: what does this agent do?
    one_sentence = f"You own {domain}. You run when triggered, you apply your skills, you deliver."

    return SOUL_TEMPLATE.format(
        agent_name=agent_name,
        domain=domain,
        one_sentence=one_sentence,
        voice=voice,
        avoids=avoids,
        trigger=trigger,
        outputs=outputs,
        agent_specific_rules=agent_rules,
        skills_list=skills_list,
        skills_files=skills_files,
        date=datetime.now().strftime("%Y-%m-%d"),
        agent_name_lower=agent_name.lower().replace("-", "_")
    )


if __name__ == "__main__":
    test_brief = {
        "domain": "content intelligence for X platform",
        "voice_direction": "sharp, direct, builder tone",
        "trigger": "cron: daily at 9am",
        "required_skills": ["x-algo-skill", "content-hook-skill"]
    }
    print(write_soul("PRISM", test_brief))
