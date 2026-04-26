# BROCK Pattern Library

Reusable architecture patterns for all build types. BROCK loads these during Phase 1 to speed up builds and apply proven patterns.

## Agent Patterns (Type 1)

| Pattern | File | When to Use |
|---------|------|------------|
| Content Intelligence | `content-agent.md` | PRISM, Maya, any content generation agent |
| Outreach & Campaigns | `outreach-agent.md` | Karma, cold email, lead follow-up agents |
| Voice / Telephony | `voice-agent.md` | CALLIE, any VAPI or phone integration agent |
| Research & Intelligence | `research-agent.md` | CLARKE, Harold, market research agents |
| Business Audit | `audit-agent.md` | CONN, any business assessment agent |

## Build Type Patterns (Universal)

| Pattern | File | When to Use |
|---------|------|------------|
| Web App (Next.js) | `webapp-pattern.md` | Type 2 — landing pages, dashboards, client portals |
| Automation | `automation-pattern.md` | Type 3 — Python scripts, n8n, data pipelines, webhooks |
| System | `system-pattern.md` | Type 4 — schemas, Chrome extensions, infrastructure |

---

*To add a new pattern: create `patterns/[name].md` following the template structure, then add it to this index.*
