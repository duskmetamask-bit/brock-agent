# System Pattern
**Type:** Type 4 — System (Infrastructure, multi-component, Chrome extensions)
**For:** Supabase schemas, infrastructure setups, Chrome extensions, complex multi-service architectures
**Last updated:** 2026-04-26

---

## When to Use This Pattern

Use this pattern when the build is:
- A Supabase database schema (with migrations)
- A Chrome extension
- A multi-component system (frontend + backend + database + external APIs)
- An infrastructure setup (VPS, Cloudflare Tunnel, Docker)
- A complex integration spanning multiple services

---

## Chrome Extension Structure

```
extension/[name]/
├── manifest.json           ← Extension manifest v3
├── background.js           ← Service worker
├── content.js             ← Content script (runs on page)
├── popup/
│   ├── popup.html
│   └── popup.js
├── options/
│   ├── options.html
│   └── options.js
├── src/
│   └── [feature].js       ← Feature modules
└── README.md
```

**Key rules:**
- Manifest v3 (Manifest v2 deprecated)
- Service worker instead of background pages
- No remote code — all bundled
- Content script communicates via `chrome.runtime.sendMessage`

---

## Supabase Schema Pattern

```
database/[name]/
├── schema.sql              ← Full schema (CREATE TABLE, RLS policies)
├── migrations/
│   └── [version]_[name].sql  ← Incremental migrations
├── seed.sql                ← Seed data (dev only)
├── supabase/
│   └── config.toml         ← Supabase CLI config
└── README.md
```

**Required for every schema:**
- RLS (Row Level Security) policies on all tables
- Indexes on all foreign keys and frequently queried columns
- Created_at / updated_at timestamps on all tables
- UUID primary keys
- Migration history (don't overwrite schema.sql)

---

## Infrastructure Pattern (VPS)

```
infrastructure/[name]/
├── docker-compose.yml      ← All services
├── Dockerfile
├── .env.example           ← Template (no real secrets)
├── nginx/
│   └── nginx.conf
├── cloudflared/
│   └── config.yml         ← Cloudflare Tunnel config
├── pm2.config.js           ← PM2 process management
└── README.md
```

**Required for every VPS setup:**
- cloudflared tunnel for public access (no open ports)
- PM2 for process management
- nginx reverse proxy
- Environment variables via .env (not hardcoded)
- Log rotation configured
- Backup strategy documented

---

## System Architecture Documentation

Every system must have an architecture diagram in SPEC.md:

```
┌─────────────────────────────────────────────────────────┐
│  Architecture: [System Name]                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Component A]  ──── API ────►  [Component B]          │
│        │                              │                 │
│        ▼                              ▼                 │
│  [Database]                   [External Service]        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Migration Pattern

For any database change:

1. Create new migration file: `migrations/YYYYMMDDHHMMSS_name.sql`
2. Never modify existing migration files
3. Test migration on dev before shipping
4. Document rollback step

```sql
-- migrations/YYYYMMDDHHMMSS_add_users_table.sql
BEGIN;

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Rollback:
-- DROP TABLE users;

COMMIT;
```

---

## Quality Checklist

Before delivery, verify:
- [ ] Architecture diagram in SPEC.md
- [ ] All API connections documented and tested
- [ ] Migration steps documented (up and down)
- [ ] Deployment process documented step-by-step
- [ ] Environment variables listed in .env.example
- [ ] No secrets in any committed files
- [ ] Chrome extension loads without errors (if applicable)
- [ ] Supabase schema passes `supabase db diff` check (if applicable)
- [ ] Docker compose runs without errors (if applicable)
- [ ] Log locations documented

---

## Common Failure Modes

1. **No rollback plan** — can't undo a bad migration
2. **Secrets in git** — API keys committed to repo
3. **No migration history** — schema.sql overwritten, no way to reconstruct
4. **Extension rejected** — using Manifest v2 or remote code
5. **Port conflicts on VPS** — not checking what's already running

---

*Update this pattern when infrastructure or extension guidelines change.*
