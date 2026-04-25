# BROCK — Agent Builder

**What it does:** Builds AI agents end-to-end from a brief. Assesses existing agents. Self-improves daily.

**Owner:** MEWY  
**Platform:** Hermes CLI  
**Location:** `~/.hermes/agents/brock/`

---

## Commands

```bash
cd ~/.hermes/agents/brock
python3 run.py build [name] [brief-json]   # Build an agent from brief
python3 run.py assess [agent-dir]          # Gap analysis on existing agent
python3 run.py research [domain]            # Phase 0 research
python3 run.py docs [agent-name]            # Generate README/API/USAGE
python3 run.py monitor                      # Build stats dashboard
python3 run.py intel                        # Intelligence summary
python3 run.py selfreview [force]           # Self-improvement check
python3 run.py versions [name]              # List agent versions
python3 run.py rollback [name] [version]    # Roll back to version
python3 run.py template [type] [name]       # Instantiate from template
```

---

## Architecture

```
brock/
├── SOUL.md               ← Identity
├── SPEC.md               ← Technical spec
├── run.py                ← CLI entry (9 commands)
├── skills/
│   └── build-agent-skill.md
├── processors/           ← 13 processors
├── agents/
│   └── judge.py          ← 20 quality gates
├── patterns/             ← 5 domain patterns
├── templates/            ← 4 agent templates
└── database/
    └── brock.db          ← Build registry + history
```

---

## Quality Gates

Every build must pass 20 quality gates before delivery. Run `python3 run.py assess [agent-dir]` to audit an existing agent.

---

## Daily Crons

- **6 AM** — Market Intelligence → updates patterns, briefs MEWY on Telegram
- **7 AM** — Self-Review → checks brock.db, patches methodology, briefs MEWY on Telegram
