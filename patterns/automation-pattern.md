# Automation Pattern
**Type:** Type 3 — Automation (Python, n8n, workflows)
**For:** Headless automations, data pipelines, scheduled scripts, webhook processors
**Last updated:** 2026-04-26

---

## When to Use This Pattern

Use this pattern when the build is:
- A Python script that runs on a schedule or trigger
- An API-to-API integration
- A data pipeline or ETL process
- A webhook processor
- An n8n or Zapier workflow (documented as JSON/config)
- Any headless, event-driven piece of logic

---

## Standard Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Language | Python 3.11+ | venv isolation |
| Scheduling | cron or APScheduler | For recurring tasks |
| Logging | Python logging | Structured, file output |
| Config | environment variables | No hardcoded credentials |
| Storage | SQLite or Supabase | Depends on data needs |

---

## Directory Structure

```
automation/[name]/
├── run.py                 ← Entry point
├── requirements.txt       ← Dependencies
├── .env                   ← Environment (gitignored)
├── src/
│   ├── __init__.py
│   ├── main.py            ← Core logic
│   ├── [processor].py     ← Specific processors
│   └── [utils].py         ← Utility functions
├── config/
│   └── config.yaml        ← Configuration (optional)
└── README.md              ← What it does, how to run
```

---

## Required Components

Every automation must have:

1. **Clear trigger** — cron expression, webhook URL, or manual invocation documented
2. **Defined inputs** — where data comes from, expected format
3. **Defined outputs** — where data goes, what format
4. **Error handling** — try/except with logging, dead letter queue if critical
5. **No hardcoded credentials** — all secrets via environment variables
6. **Logging** — structured logging to file and/or stdout
7. **Idempotency** — safe to run multiple times without side effects

---

## Trigger Patterns

### Cron (recurring)
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(run_main, 'cron', hour=6, minute=0)
scheduler.start()
```

### Webhook (event-driven)
```python
from flask import Flask, request
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    payload = request.json
    process(payload)
    return {'status': 'ok'}
```

### Manual / CLI
```python
if __name__ == '__main__':
    run_main()
```

---

## Error Handling Pattern

```python
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_main():
    try:
        logger.info("Starting automation")
        # ... main logic
        logger.info("Completed successfully")
    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)
        raise  # or retry logic
```

---

## Quality Checklist

Before delivery, verify:
- [ ] Runs end-to-end without error (test with mock data)
- [ ] Error handling catches and logs all exceptions
- [ ] No hardcoded credentials
- [ ] Trigger mechanism documented and tested
- [ ] Logging is clear and useful
- [ ] README documents how to run
- [ ] requirements.txt is complete
- [ ] Idempotent (safe to re-run)

---

## Common Failure Modes

1. **No error handling** — script dies silently on first exception
2. **Hardcoded credentials** — API keys in source code instead of env vars
3. **Not idempotent** — running twice creates duplicate records
4. **No logging** — no way to debug when it fails in production
5. **Wrong working directory** — relative paths break when run from cron

---

*Update this pattern when automation tooling or patterns change.*
