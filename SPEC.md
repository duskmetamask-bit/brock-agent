# BROCK — SPEC.md
**Agent:** BROCK (Agent Builder)
**Status:** PHASE 0 — DESIGN
**Built by:** MEWY
**Date:** 2026-04-25

---

## What It Is

BROCK is an agent builder. Given a design brief, BROCK produces a fully working Hermes agent that passes the Agent Build Checklist v1.2. BROCK's output is sellable quality — a complete agent with SOUL, SPEC, processors, skills, database, and run.py.

---

## Architecture

```
~/.hermes/agents/brock/
├── SOUL.md                       ← Identity + process
├── SPEC.md                       ← This file
├── skills/
│   └── build-agent-skill.md     ← Build methodology + checklist
├── agents/
│   └── judge.py                 ← Quality evaluation (passes Go-Live gates?)
├── processors/
│   ├── brief_parser.py          ← Parses build brief from MEWY
│   ├── soul_writer.py           ← Writes SOUL.md from brief
│   ├── spec_writer.py           ← Writes SPEC.md from brief + research
│   ├── file_builder.py          ← Creates directory structure + files
│   ├── skill_builder.py         ← Creates skill files from skill list
│   └── db_builder.py            ← Creates database schema
├── database/
│   └── brock.db                 ← Agent registry, build history
└── run.py                       ← Entry point: build agent from brief
```

---

## How It Works

### Input: Build Brief

MEWY sends BROCK a brief containing:
```yaml
agent_name: "CALLEE"  # or PRISM, CONN, etc.
domain: "voice discovery agent for EMVY"
voice_direction: "warm, professional, curious"
pipeline_position: "after SLATE, before CONN"
trigger: "VAPI call completion"
required_skills:
  - vapi-integration-skill
  - discovery-question-skill
required_processors:
  - call_notes_processor
  - supabase_writer
optional_notes: "inherits Supabase schema from EMVY stack"
```

### Output: Complete Agent Folder

BROCK produces at `~/.hermes/agents/[agent-name]/`:
```
├── SOUL.md
├── SPEC.md
├── config/
│   └── agent.yaml
├── database/
│   ├── schema.sql
│   └── [agent].db (initialized)
├── skills/
│   ├── [skill-1].md
│   └── [skill-2].md
├── processors/
│   ├── __init__.py
│   ├── core.py
│   └── [processor-1].py
├── agents/
│   └── judge.py
└── run.py
```

---

## Deep Research Step (Checklist Step 0)

Before writing any code, BROCK must:

1. **Search vault for similar agents:** `~/.hermes/agents/*/`
2. **Search web for production agents in same space:**
   - GitHub repos with stars > 5k
   - Open-source agents with documentation
3. **Extract patterns:**
   - Architecture decisions
   - Prompt patterns that work
   - Failure modes documented
4. **Write Research Summary** in SPEC.md

---

## Skills Architecture

Every agent BROCK builds must follow Skills Architecture (Checklist Step 5b):

**Skill types to create:**
- **Platform skills** — for any platform the agent interacts with
- **Process skills** — for any repeatable workflow
- **Knowledge skills** — for domain expertise
- **Integration skills** — for API wiring

**Skill file format:**
```
# [Skill Name]
**For:** [Agent Name]
**Purpose:** [What this skill encodes]
**Last updated:** [Date]

---
[Content — rules, patterns, knowledge]
---
*Update this skill when [domain] changes.*
```

**BROCK must include skill loading in every agent it builds:**
```python
def load_skill(skill_name: str) -> str:
    """Load skill content from skills/ directory."""
    path = Path(__file__).parent / "skills" / f"{skill_name}.md"
    return path.read_text()
```

---

## Quality Gates (from Evaluation Rubric)

Before delivery, BROCK verifies:

1. **SOUL.md complete** — identity, voice, rules, key files
2. **SPEC.md complete** — architecture, data flow, API list, build phases
3. **All skills created** — skill files in skills/
4. **Database schema** — SQLite schema written and valid
5. **run.py executes** — `python run.py` at minimum imports without error
6. **Processors import** — `from processors import *` works
7. **Skills load** — `load_skill("x")` returns content

---

## BROCK Self-Improvement Loop

BROCK needs to get better over time. The self-improvement loop:

1. **Track build outcomes:** When MEWY deploys an agent BROCK built, log it
2. **Track issues:** When an agent has problems in production, log what went wrong
3. **Periodic review:** Every 5 builds, BROCK reviews issues and updates `build-agent-skill.md`
4. **Pattern library:** BROCK maintains `patterns/[domain-type].md` for common agent architectures

This means BROCK's skills evolve — the build methodology gets better with each build.

---

## Research Summary

*To be written by BROCK during Phase 0 of first build.*

---

## Build Phases

| Phase | What | Done When |
|-------|------|-----------|
| 0 — Acknowledge | Parse brief, confirm scope, ask clarifying Qs | Brief understood |
| 1 — Deep Research | Find similar agents, extract patterns | Research summary in SPEC |
| 2 — Core | SOUL + SPEC + directory structure | All three files written |
| 3 — Processors | Build all processors + skill loading | All processors import |
| 4 — Skills | Create all skill files | All skills loadable |
| 5 — Database | Schema + DB init | DB initializes without error |
| 6 — Integration | run.py + wire everything | run.py executes cleanly |
| 7 — Quality Gates | Run Go-Live checklist | All gates pass |
| 8 — Deliver | Report to MEWY | Files delivered |

---

## Gap Analysis (Internal)

*This section documents what BROCK needs but doesn't yet have built.*

### Known Gaps

1. **No self-improvement loop implemented** — agent registry + issue tracking not yet built
2. **No pattern library** — no `patterns/` directory for architecture reuse
3. **Judge (quality gates) is basic** — `agents/judge.py` exists but needs full Go-Live gate implementation
4. **No web UI interface** — BROCK is CLI-only. The web UI would let non-technical users configure agents without MEWY writing briefs.

### What's Missing for "Sellable Quality"

For BROCK to be a product that can be sold:

1. **Web UI** — Configurator that generates brief from form inputs (highest priority)
2. **Documentation generator** — Auto-generate README.md + API docs from SPEC.md
3. **Demo mode** — Show a build happening in real-time (trust builder)
4. **Template library** — Pre-built agent templates (sales agent, content agent, etc.) users can customize
5. **Version control** — Track agent versions, rollback capability
6. **Monitoring dashboard** — Show agents built, build success rate, time to build

### Gap Priority for BROCK v1

| Gap | Priority | Notes |
|-----|----------|-------|
| Web UI | High | Makes it sellable, not just usable |
| Self-improvement loop | Medium | Makes BROCK get better over time |
| Pattern library | Medium | Faster builds, better architecture |
| Documentation generator | Medium | Professional product feel |
| Template library | Low | Can ship v1 without it |

---

*Last updated: 2026-04-25*
