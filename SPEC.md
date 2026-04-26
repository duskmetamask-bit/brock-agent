# BROCK — SPEC.md
**Agent:** BROCK (Universal Build Engine)
**Status:** ACTIVE — Universal Mode
**Built by:** MEWY
**Date:** 2026-04-26

---

## What It Is

BROCK is EMVY's universal build engine. It builds anything EMVY needs to deliver client work and run operations. Four build types: Agents, Web Apps, Automations, Systems.

Given a build brief, BROCK produces a fully working deliverable that passes quality gates.

---

## Architecture

```
~/.hermes/agents/brock/
├── SOUL.md                        ← Identity + process
├── SPEC.md                        ← This file
├── skills/
│   └── build-skill.md            ← Universal build methodology + checklist
├── patterns/
│   ├── agent-pattern.md          ← Type 1: Agent architecture patterns
│   ├── webapp-pattern.md         ← Type 2: Web app architecture patterns
│   ├── automation-pattern.md     ← Type 3: Automation architecture patterns
│   └── system-pattern.md         ← Type 4: System architecture patterns
├── agents/
│   └── judge.py                  ← Quality evaluation (build-type-specific gates)
├── processors/
│   ├── brief_parser.py          ← Parses build brief from MEWY
│   ├── spec_writer.py            ← Writes SPEC.md from brief + research
│   ├── file_builder.py          ← Creates directory structure + files
│   ├── agent_builder.py          ← Type 1: Agent-specific builder
│   ├── web_builder.py            ← Type 2: Web app builder (Next.js)
│   ├── automation_builder.py      ← Type 3: Automation builder
│   ├── system_builder.py         ← Type 4: System builder
│   └── db_builder.py             ← Creates database schema
├── database/
│   └── brock.db                  ← Build registry, build history
└── run.py                        ← Entry point
```

---

## Build Types

### Type 1 — Agents
**What:** Hermes agent profiles (SOUL.md, SPEC.md, processors, skills, run.py)
**Trigger:** `brock build:agent [name] --brief path/to/brief.md`
**Output:** `~/.hermes/agents/[name]/`
**Quality gates:** SOUL complete, SPEC complete, all skills loadable, run.py executes, database initializes

### Type 2 — Web Apps
**What:** Next.js full-stack apps, landing pages, dashboards
**Trigger:** `brock build:web [name] --brief path/to/brief.md`
**Output:** `~/hermes/builds/web/[name]/`
**Quality gates:** `npm run build` passes, all pages render, API routes respond, Supabase wired

### Type 3 — Automations
**What:** Python scripts, n8n workflows, API integrations, data pipelines
**Trigger:** `brock build:automation [name] --brief path/to/brief.md`
**Output:** `~/hermes/builds/automation/[name]/`
**Quality gates:** Runs without error, handles errors gracefully, no hardcoded credentials

### Type 4 — Systems
**What:** Supabase schemas, infrastructure setups, Chrome extensions, multi-component architectures
**Trigger:** `brock build:system [name] --brief path/to/brief.md`
**Output:** `~/hermes/builds/system/[name]/`
**Quality gates:** Architecture documented, all connections tested, migration path defined

---

## Build Brief Format

```yaml
build_name: "emvy-audit-report-generator"
build_type: "automation"  # agent | web | automation | system
summary: "Generates PDF audit reports from EMVY audit data"
trigger: "cron daily 6am"  # or webhook, event, manual
inputs:
  - audit_id from Supabase
outputs:
  - PDF saved to Supabase Storage
  - Link stored in audit record
required_skills:
  - supabase-client
  - pdf-generation
optional_notes: "Uses EMVY brand template"
```

---

## Deep Research Step (Step 0 — Non-Negotiable)

Before writing any code, BROCK must:

1. **Search vault for existing similar builds:** `~/.hermes/builds/*/` and `~/.hermes/agents/*/`
2. **Search web for production examples:**
   - GitHub repos with stars > 1k for the relevant build type
   - Open-source projects with documentation
   - Relevant libraries and their patterns
3. **Extract patterns:**
   - Architecture decisions that work
   - Common failure modes
   - API patterns and conventions
4. **Write Research Summary** in SPEC.md

---

## Quality Gates

### Agent Gates (Type 1)
1. SOUL.md complete — identity, voice, rules, key files documented
2. SPEC.md complete — architecture, data flow, API list, build phases
3. All skills created — skill files in skills/
4. Database schema — SQLite schema written and valid
5. run.py executes — `python run.py` at minimum imports without error
6. Processors import — `from processors import *` works
7. Skills load — `load_skill("x")` returns content

### Web App Gates (Type 2)
1. `npm run build` passes without errors
2. All pages render without errors
3. All API routes respond correctly
4. Supabase connection verified
5. Environment variables documented
6. No hardcoded credentials

### Automation Gates (Type 3)
1. Runs end-to-end without error
2. Error handling in place (try/except, logging)
3. No hardcoded credentials
4. Trigger mechanism documented and tested
5. Logging output clear

### System Gates (Type 4)
1. Architecture diagram in SPEC.md
2. All API connections documented and tested
3. Migration steps documented (if DB involved)
4. Deployment process documented
5. Monitoring/logging in place

---

## Self-Improvement Loop

1. **Track build outcomes:** When MEWY deploys a build BROCK made, log it
2. **Track issues:** When a build has problems in production, log what went wrong
3. **Periodic review:** Every 5 builds, BROCK reviews issues and updates build-skill.md
4. **Pattern library:** BROCK maintains type-specific patterns that evolve with each build

---

## Research Summary

*To be written by BROCK during Phase 0 of first build.*

---

## Build Phases

| Phase | What | Done When |
|-------|------|-----------|
| 0 — Acknowledge | Parse brief, confirm type, ask clarifying Qs | Brief understood |
| 1 — Deep Research | Find similar builds, extract patterns | Research summary in SPEC |
| 2 — Core Architecture | SPEC.md, directory structure, data flow | Architecture documented |
| 3 — Build | Write code (type-specific) | All files created |
| 4 — Quality Gates | Run appropriate gates for build type | All gates pass |
| 5 — Deliver | Report to MEWY | Files delivered |

---

## Gap Analysis

### Known Gaps (2026-04-26)

1. **Type 2-4 builders not yet built** — brief_parser, spec_writer, web_builder, automation_builder, system_builder exist only as stubs
2. **No pattern files for Type 2-4** — patterns/ directory only has agent-patterns
3. **No judge.py for Type 2-4** — quality gates are defined but not automated
4. **No build registry** — brock.db exists but schema may not cover all build types
5. **No run.py update** — current run.py only handles agent builds

### Priority Fixes

| Gap | Priority | Status |
|-----|----------|--------|
| Add Type 2-4 patterns | High | Pending |
| Update run.py for universal builds | High | Pending |
| Expand judge.py for Type 2-4 gates | Medium | Pending |
| Update brock.db schema for all build types | Medium | Pending |

---

*Last updated: 2026-04-26*
