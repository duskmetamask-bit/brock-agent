# Build Agent Skill — BROCK's Methodology
**For:** BROCK
**Purpose:** Encodes how to build an agent end-to-end
**Last updated:** 2026-04-25

---

## The Golden Rule

Every agent is only as good as its SOUL. Build the identity first. Everything else follows.

---

## The 5-Question Brief

Before building, confirm you have:
1. **Agent name** — what do we call it?
2. **Domain** — what does it own?
3. **Voice/personality** — how does it sound?
4. **Trigger** — what makes it run?
5. **Skills** — what domain knowledge does it need?

If any are missing, ask MEWY before proceeding.

---

## Directory Structure (The Standard Layout)

```
~/.hermes/agents/[agent-name]/
├── SOUL.md               ← Identity, voice, rules
├── SPEC.md               ← Architecture, data flow
├── config/
│   └── agent.yaml        ← Runtime config
├── database/
│   ├── schema.sql        ← SQLite schema
│   └── [agent].db        ← Initialized on first run
├── skills/               ← Domain knowledge files
│   ├── [skill-1].md
│   └── [skill-2].md
├── processors/           ← Core logic modules
│   ├── __init__.py
│   ├── core.py           ← Main agent loop
│   └── [processor].py
├── agents/               ← Sub-agents (if needed)
│   └── judge.py
├── engine/               ← Shared logic (optional)
│   └── [shared].py
└── run.py                ← Entry point
```

---

## SOUL.md — What It Must Contain

```
# [AGENT NAME] — SOUL.md

## Identity
- Name + Role tagline
- Owner (MEWY / project)
- Platform (Hermes CLI)

## What It Does
- One sentence: what it owns end-to-end

## How It Works
- Trigger (cron / on-demand / event)
- Inputs (what it reads)
- Outputs (what it produces)
- Delivery (where results go)

## Voice & Style
- Tone: [direct / warm / technical / etc.]
- What it sounds like
- What it never sounds like

## Rules (Non-Negotiable)
- Vault is source of truth
- Log every session
- [Agent-specific rules]

## Key Files
- File tree showing structure

## [Optional] Skills It Loads
- List of skills + when loaded
```

---

## SPEC.md — What It Must Contain

```
# [AGENT NAME] — SPEC.md

## What It Is
- Description + purpose

## Architecture
- File tree with descriptions
- Component responsibilities

## Data Flow
- Input → Processing → Output
- Database schema (SQL)
- External API calls

## Skills Architecture
- List of skills
- When each is loaded
- What domain it encodes

## Build Phases
- Table: Phase → What → Done When

## Quality Gates
- Checklist from Evaluation Rubric
- How to verify each gate

## Research Summary
- From Step 0: what similar agents exist
- What patterns to follow
- What failure modes to avoid
```

---

## Skill File Format

Every skill follows this format:

```markdown
# [Skill Name]
**For:** [Agent Name]
**Purpose:** [What this encodes]
**Last updated:** [YYYY-MM-DD]

---

[Rules / patterns / knowledge]

---

*Update this skill when [domain] changes.*
```

---

## The Build Sequence

**NEVER skip steps. This order matters.**

1. **Acknowledge brief** → confirm name + domain
2. **Deep research** → 3-5 similar agents → patterns + failures
3. **SOUL.md** → write first, identity drives everything
4. **SPEC.md** → architecture from identity
5. **Directory structure** → create all folders
6. **Database schema** → schema.sql + init
7. **Config files** → agent.yaml
8. **Skills** → write all skill files
9. **Processors** → core.py + sub-processors
10. **run.py** → entry point
11. **Quality gates** → run judge.py against agent
12. **Deliver** → report to MEWY

---

## Quality Gate Checklist (Before Delivery)

Run this mentally or via judge.py:

- [ ] SOUL.md exists and has: name, domain, voice, rules, key files
- [ ] SPEC.md exists and has: architecture, data flow, skills list, build phases
- [ ] All directories created
- [ ] schema.sql is valid SQL
- [ ] All skill files created and loadable
- [ ] run.py exists and `python run.py` at least imports without error
- [ ] `from processors import core` works
- [ ] `from agents import judge` works (if agents/ exists)
- [ ] Config files are valid YAML

Any gate failing → fix before delivery.

---

## Common Failure Modes

**Skipping deep research:** You'll miss patterns that already work. Always research first.

**Building processors before SOUL:** You'll build the wrong processors. Identity drives architecture.

**Hardcoding domain knowledge:** Put it in a skill file. Never in code.

**Delivering without testing imports:** If it can't import, it's not done.

**Forgetting the trigger:** Every agent needs a trigger. If you don't know when it runs, the agent isn't defined.

---

## Self-Improvement Triggers

After every build, ask:
1. What took longer than expected?
2. What did I have to redo?
3. What pattern can I save for next time?

Update this skill with improvements after each build.

---

## Pitfalls

1. **Deep research is skipped under time pressure** — always do it. Skipping research means copying bad patterns.
2. **Processor files grow too large** — if a processor is >300 lines, split it. Each processor does one thing.
3. **Skills are an afterthought** — write skills first, processors second. Domain knowledge drives the architecture.
4. **run.py is written last** — it's the entry point but it should be designed alongside the SOUL, not bolted on.
5. **judge.py gates are relaxed to pass a failing build** — if it fails, fix the agent, don't lower the bar.
6. **Pattern mismatch** — forcing a content-agent pattern onto an audit-agent because it's faster. Patterns exist to enforce quality, not convenience.
7. **Testing with only happy paths** — judge.py must test both valid and invalid inputs.

---

## Verification

To verify a build was done correctly:

1. **Import chain:** `cd ~/.hermes/agents/[agent] && python3 -c "from processors import *; from agents import *"` — must not error
2. **run.py --help:** `python3 run.py` with no args should print the docstring help
3. **Skills exist and are non-empty:** `ls skills/*.md` should return 1+ files, each >200 chars
4. **SOUL.md has all required sections:** grep for Identity, Core Responsibilities, Key Rules, Memory & Tool Conventions, Session Startup
5. **SPEC.md exists:** `test -f SPEC.md && echo "exists"`
6. **judge.py runs clean:** `python3 agents/judge.py [agent-name]` — 18/20 minimum, 20/20 target
7. **Database initialises:** `sqlite3 database/[agent].db < database/schema.sql && echo "schema valid"`
8. **Config is valid YAML:** `python3 -c "import yaml; yaml.safe_load(open('config/agent.yaml'))"`

If any verification step fails, fix the agent before delivery.

---

*BROCK loads this skill at startup. Update when build methodology evolves.*
