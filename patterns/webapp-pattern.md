# Web App Pattern
**Type:** Type 2 — Web App (Next.js)
**For:** EMVY web properties (dashboards, landing pages, client portals)
**Last updated:** 2026-04-26

---

## When to Use This Pattern

Use this pattern when the build is:
- A Next.js application (App Router)
- A landing page or marketing site
- A client dashboard or admin panel
- Any web UI that connects to Supabase

---

## Standard Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Framework | Next.js 14+ App Router | TypeScript, Server Components |
| Database | Supabase | PostgreSQL + Auth + Storage |
| Styling | Tailwind CSS | Dark mode support |
| Deployment | Vercel or VPS | Documented in SPEC |
| State | React hooks + Server Actions | No heavy state libraries |

---

## Directory Structure

```
app/
├── layout.tsx              ← Root layout with providers
├── page.tsx               ← Home/landing page
├── [feature]/
│   ├── page.tsx           ← Feature page
│   └── actions.ts        ← Server actions
├── api/
│   └── [route]/
│       └── route.ts       ← API routes
components/
├── ui/                    ← Reusable UI components
│   ├── button.tsx
│   ├── card.tsx
│   └── input.tsx
├── [feature]/             ← Feature-specific components
│   └── [component].tsx
lib/
├── supabase/
│   ├── client.ts          ← Browser client
│   └── server.ts          ← Server client
├── utils.ts               ← Utility functions
└── [integrations]/        ← Third-party integrations
├── .env.local             ← Environment variables (gitignored)
├── tailwind.config.ts
├── next.config.js
└── package.json
```

---

## Required Components

Every EMVY web app must have:

1. **Supabase integration** — client.ts + server.ts wired correctly
2. **Auth flow** — login/logout/signup pages wired to Supabase Auth
3. **Environment setup** — all secrets in .env.local, documented in SPEC.md
4. **Error boundaries** — React error boundaries on all major pages
5. **Loading states** — skeleton loaders for async content
6. **Responsive design** — mobile-first, Tailwind breakpoints

---

## API Route Patterns

```typescript
// app/api/[resource]/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

export async function POST(req: NextRequest) {
  const { data } = await createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  ).auth.getServiceRole();

  const body = await req.json();
  // Process...
  return NextResponse.json({ success: true, data });
}
```

---

## Supabase Client Patterns

**Browser client (client.ts):**
```typescript
import { createBrowserClient } from '@supabase/ssr';
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
```

**Server client (server.ts):**
```typescript
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';
export async function createClient() {
  const cookieStore = await cookies();
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: { getAll: () => cookieStore.getAll() }
    }
  );
}
```

---

## Quality Checklist

Before delivery, verify:
- [ ] `npm run build` passes without errors
- [ ] All pages render without console errors
- [ ] API routes respond correctly to test requests
- [ ] Supabase connection works in both browser and server contexts
- [ ] Auth flow works end-to-end
- [ ] Environment variables documented in SPEC.md
- [ ] No hardcoded credentials or secrets
- [ ] Mobile responsive on all pages
- [ ] Loading states on all async operations
- [ ] Error states handled gracefully

---

## Common Failure Modes

1. **Supabase client initialized twice** — server client and browser client fighting over cookies
2. **Service role key exposed** — never put SERVICE_ROLE_KEY in NEXT_PUBLIC_ vars
3. **Build fails on VPS** — always test `npm run build` locally before deploy
4. **Missing middleware** — Supabase Auth needs middleware.ts for route protection
5. **No error boundaries** — crashes on edge cases bring down whole pages

---

*Update this pattern when Next.js or Supabase patterns change.*
