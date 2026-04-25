# {{AGENT_NAME}} — SPEC.md

**Type:** Content Intelligence Agent
**Pattern:** content-agent
**Built by:** BROCK

---

## What It Is

Automated content generation and scheduling agent. Generates platform-optimized content, applies algorithms, schedules posts, tracks engagement.

---

## Architecture

```
{{AGENT_NAME}}/
├── SOUL.md
├── SPEC.md
├── run.py
├── processors/
│   ├── __init__.py
│   ├── core.py           ← main loop
│   ├── topic_picker.py   ← selects next topic
│   ├── content_generator.py ← generates post
│   ├── platform_optimizer.py ← applies algo
│   └── scheduler.py      ← optimal timing
├── skills/
│   ├── x-algo-skill.md
│   └── topic-selection-skill.md
├── database/
│   └── schema.sql
└── config/
    └── agent.yaml
```

---

## Trigger

- On-demand via `python3 run.py`
- Or via cron (configurable)

---

## Data Flow

1. topic_picker -> selects weighted topic from content_brain
2. content_generator -> generates draft
3. platform_optimizer -> applies X/LinkedIn algo rules
4. scheduler -> determines optimal post time
5. queue -> stores pending posts
6. (future: post executor)

---

## API Dependencies

- MiniMax API (content generation)
- Platform APIs (X, LinkedIn) — via skills

---

## Success Metrics

- Posts pass platform algo checks
- Zero flooding violations
- Topic diversity maintained
- Engagement tracked per post
