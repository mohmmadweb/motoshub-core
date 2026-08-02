# Motoshub Core — Architecture & Engineering Guide

> Living document. Section 9 tracks per-module implementation status.

## 1. Product in one paragraph

Motoshub is a **multi-tenant enterprise platform** that combines a communications
layer (messenger, channels, groups, feed, notifications), a content layer (news,
blog, knowledge, media, forum, polls), and a process layer (projects, contracts &
e-signature, the innovation-fund workflow, tickets, training, awards, evaluation).
It is sold module-by-module to organizations; each customer is a **tenant** with
its own users, branding, roles, and — internally — a **holding → company** tree.
The reference UX is the prototype served at **demo.shub.ir**.

## 2. Where `motoshub-core` sits

The broader ecosystem is a **strangler-fig migration**: a Kong gateway routes
`/api/v1/*` to either the legacy PHP/Oxwall backend or new Django services, all
sharing one contract. `motoshub-core` is the **greenfield, clean-schema** Django
+ Next implementation of the whole product. It owns its **own PostgreSQL schema**
(managed models, no legacy-table coupling) yet stays **drop-in compatible** with
the ecosystem so it can serve as the `api2` / `motonextapi` backend behind the
gateway.

Domain / environment map:

| Domain | Component | Role |
|--------|-----------|------|
| `demo.shub.ir` | `motoshub-prototype` (React) | UX reference / acceptance benchmark |
| `motonext.shub.ir` | `motoshub-web` (PHP/Oxwall) | Current production API |
| `motonextapi.shub.ir` (api2) | **`motoshub-core` backend** | New Django API |
| `motonextfront.shub.ir` | **`motoshub-core` frontend** | New Next.js client |
| `api.shub.ir` | `motoshub-gateway` (Kong) | Gateway / mobile + unified entry |
| `docs.shub.ir` | `motoshub-docs` | Docs (GitHub Pages) |

## 3. Contract compatibility (non-negotiable)

Three contracts let core coexist with the PHP backend behind one gateway:

1. **Response envelope.** Every success body is `{data, links, meta}`. Lists fill
   `links` (first/last/next/prev) and `meta` (count/page/pages/page_size);
   detail/action responses use empty `links`/`meta`.
   → `apps/core/renderers.py`, `apps/core/pagination.py`.
2. **Uniform errors.** `{error: {code, type, message, details?}}` for
   401/403/404/422/… — DRF `ValidationError` is remapped to **422**.
   → `apps/core/exceptions.py`.
3. **Unified JWT.** HS256 signed with the shared `OW_PASSWORD_PEPPER`; claims
   `{iat, exp, sub, iss, typ, tid}`. A token minted by either backend validates
   on the other. → `apps/accounts/tokens.py`, `apps/accounts/authentication.py`.

## 4. Backend architecture

- **Layout:** `config/` (project: split settings `base`/`development`/`production`,
  `urls`, `celery`, `wsgi`, `asgi`) + `apps/<bounded-context>/`. Each domain app
  follows the same split: `models.py`, `serializers.py`, `views.py`, `urls.py`,
  `permissions`-map on the ViewSet, `tests/`.
- **Model bases** (`apps/core/models.py`): `TimeStampedModel` (UUID pk +
  timestamps), `TenantScopedModel` (adds `tenant` FK for row-level isolation),
  and the shared `Visibility` / `ContentScope` choice enums.
- **Multi-tenancy:** shared-DB, row-level. `CurrentTenantMiddleware` resolves the
  active tenant per request (X-Tenant header → JWT `tid` → user's home tenant) and
  exposes `request.tenant`. Tenant-scoped querysets filter by it.
- **RBAC:** the permission catalog (`apps/rbac/catalog.py`, ~99 ids across 20
  groups, `"<group>.<action>"`) is the single source of truth, in code. `Role`
  holds a permission-id set + scope (platform/tenant/group); preset roles are
  seeded (`seed_rbac`) and non-deletable, custom roles are per-tenant and CRUD-able.
  `RoleAssignment` binds user↔role within a tenant (optionally narrowed to a
  holding/company). `HasPerm` (`apps/core/permissions.py`) gates each ViewSet
  action via a `required_perms` map; effective permissions are cached per
  (user, tenant).
- **Async & realtime:** Celery (Redis broker) runs the prototype's workflow rules
  — report reminders (`reportReminderDays`), 15-day review escalation, dormant-
  project detection (`dormantProjectDays`), whole-team payment notifications,
  green-path fast-tracking, auto-apply of approved out-of-contract requests.
  Django Channels (Redis layer) backs realtime chat.
- **Config:** all secrets/toggles via `django-environ` (`.env`); nothing hard-coded.

## 5. Two visibility axes (both modeled)

1. `Visibility` = public/private — on news, blog, events, media, knowledge, forum
   (groups use the same values as `privacy`). Public items surface on the
   unauthenticated showcase.
2. `ContentScope` = global/holding/company — on scoped content (e.g. scoped news):
   global → everyone in tenant; holding → same holding; company → same company.
   Publishing beyond your company is gated by `companies.publish-holding` /
   `companies.publish-global`.

## 6. The Innovation Fund (richest aggregate)

`NfProject` is a dossier with child tables (guarantees, gantt rows, reports +
approval-chain steps, payments, timeline, out-of-contract requests) and a
**two-level state machine**: `stage` (7 stages) × `subStatus` (per-stage list).
Evaluation gates: screening (22 criteria / 200, threshold 80) and jury (5
dimensions / 100, threshold 50). The seven `nfWorkflowRules` become Celery
jobs/signals. This app is modeled after the funds sections of the prototype and is
the reference for how other stateful modules (contracts, RFP, tenders, seed
investments, sabbaticals, e-sign, research, award) encode their own stage enums +
transition rules.

## 7. Frontend architecture (Next.js)

- App Router with **route-group-per-subapp** (`(auth)`, `(workspace)`, `(social)`)
  sharing one prop-driven `MainLayout`; `dir="rtl"`, local Persian font, `fa-IR`
  formatters.
- **Server state** via TanStack Query hooks (`hooks/queries/*`) that own fetching +
  toasts + navigation; **UI state** via Zustand (+persist) with a central
  `resetAllStores()`.
- One interceptor-configured Axios instance with real token-refresh; a central
  `libs/routes.ts` registry; typed `xxxApi` service objects per resource.
- The prototype's **design tokens** (brand/navy/ink scales, 6 accent presets, dark
  mode via CSS-variable inversion, font-scale) are ported into `tailwind.config`
  so the client matches demo.shub.ir pixel-for-pixel.
- `NEXT_PUBLIC_API_BASE_URL` (or a Next rewrite of `/api/v1`) points at the gateway.

> **Note (see §10):** §7 describes the original Next.js client, which has been
> replaced by the Vite prototype SPA. The delivery/infra notes below are updated
> for that reality: the `web` container builds the SPA and serves it via nginx,
> which reverse-proxies `/api`, `/ws`, `/static`, `/media` to the Django `api`
> container — a single browser origin. CI runs backend (check + migration-drift +
> pytest) and frontend (oxlint + `tsc`/vite build) jobs.

## 8. Delivery pipeline (mirrors motoshub-docs)

DoR → `issue-N` branch → L1 unit tests (pytest / component tests + tsc + lint) →
self-review + MR checklist → L2 CI (lint, types, tests, build, **contract test vs
OpenAPI**) → peer review (≥1 approval; focus correctness/security/IDOR/envelope) →
merge → staging deploy → L3 acceptance (PO/QA) → Done. MRs < ~400 lines; issue
branches ≤ 3 days; bug fixes start with a failing test.

## 9. Implementation status

| Area | Status |
|------|--------|
| Project config, envelope, errors, pagination | ✅ done, tested |
| Unified JWT auth (login/refresh/me) | ✅ done, tested |
| accounts (custom User + presence) | ✅ done, tested |
| tenancy (tenant/holding/company + middleware) | ✅ done, tested |
| rbac (catalog, roles, assignments, HasPerm, seed) | ✅ done, tested |
| content: news/blog/events/media/knowledge | ✅ done, tested |
| social: groups (+membership, IDOR-safe) / forum | ✅ done, tested |
| projects + Kanban task board | ✅ done, tested |
| contracts (stage machine, payments, approval chain) | ✅ done, tested |
| innovation fund (7-stage machine, eval gates, Celery job) | ✅ done, tested |
| **Next.js frontend** (auth, RTL shell, 11 module pages) | ✅ done, builds green, e2e-tested |
| infra (docker-compose + Dockerfiles + seed_demo) | ✅ done, compose validated |
| research / training / awards / tickets / polls | ✅ done, tested |
| chat + realtime (Channels WebSocket) | ✅ done, live-tested |
| notifications (per-user) + header bell | ✅ done, tested |
| admin (workflow settings + branding) + reports summary | ✅ done, tested |
| nginx reverse proxy (REST + WS upgrade) | ✅ done, compose-validated |
| CI pipeline (GitHub Actions) + pytest L1 suite | ✅ done (5 tests green) |

**All prototype modules are now implemented end-to-end (backend + frontend).**
Remaining work is depth per module (richer detail views, more L1 tests, the
remaining SettingsContext wiring to live theming) rather than new modules.

### Depth completion (all P1/P2/P3 done)
- Full CRUD from the UI for every module (create/edit/delete/search + pagination)
- Forum & ticket thread views (view + reply); chat realtime
- File upload (media, knowledge) via multipart
- Runtime notifications (ticket reply, task assignment) + Celery beat (fund
  escalation, report reminders); DRF rate-limiting (anon/user/login scopes)
- User & role administration UI (invite users, custom roles from the 99-permission
  catalog, system-role protection)
- Public unauthenticated showcase (/ + /api/v1/public/feed)
- Live theming: dark mode + font scale (a11y) + 4 accent presets, all persisted
- Custom 404, loading skeletons, richer dashboard
- Tests: 13 pytest (backend) + 5 Vitest (frontend), all green in CI

### Known limitations (deliberate / future)
- Cross-tenant workspace switching needs multi-tenant user membership (users have
  one home tenant today) — a data-model extension, not wired.
- Auth extras (password reset, OTP, SSO/LDAP) are not implemented (username/password).
- Chat is channel-based (no DMs/reactions/threads yet).

## 10. Frontend = the prototype UI on the real backend (current reality)

The single `frontend/` is the **exact demo.shub.ir prototype UI** (Vite + React 19
+ Tailwind v4), served as a static SPA, talking to the real Django API. There is
no separate Next client and no `frontend-demo/` — those were consolidated away.

**Wiring pattern (mock → real without rewriting pages):**
- `src/lib/http.ts` — fetch client (JWT, refresh, envelope unwrap, FormData).
- `src/lib/auth.ts` — real login/guard.
- `src/lib/adapters.ts` — map backend shapes ↔ prototype shapes (Jalali dates,
  Persian enums, money formatting).
- `src/context/ContentContext.tsx` + `src/lib/useApiCollection.ts` — load a
  collection from the API and turn the prototype's local `set*` CRUD into
  create/update/delete API calls by **diffing** old vs new arrays. This makes
  pages real without editing them.

**Real on the backend (18 modules):** auth, news, blog, events, media, knowledge,
forum, groups, projects, research, training, tickets, polls, notifications,
contracts (core + tech-transfer portfolio, tenders/commission, e-sign flow),
roles (RBAC/admin), funds (simple + full innovation-fund dossier: NfProject with
finance/gantt/timeline + guarantees/reports/payments/requests, addressable by
NF code), chat (channels+messages),
friends/profile (Friendship + Follow graph + user org/skills/presence).

The innovation-fund dossier persists top-level fields + finance/gantt/timeline
JSON via the diff-persist `useApiCollection` setter (NfProjectViewSet uses
`lookup_field="code"` so the prototype's code-as-id maps straight to the URL).
Nested guarantees/reports/payments/requests are served real (read) and remain
first-class models with their own workflow actions (advance/score/request).

**Partly real:**
- reports: KPI cards + the report-builder (projects/contracts/funds/research
  grouped by status) run off live `/reports/summary` aggregates. The decorative
  charts (by-department, monthly trend, holding funnel, cross-tab) stay
  illustrative — they need dimensions the schema doesn't model yet (a
  `department` field, a time-series aggregation).

**Still on mock — demo-only (no backend planned yet):**
- chat threads / voice / typing indicators (inherently client-side polish).
  Channels **and DMs** are realtime over WebSocket (`ws/chat/<id>`, `ws/dm/`);
  channel-message **reactions persist** and broadcast live.
- a few illustrative widgets (report decorative charts, pending-review queue).

Once a module's backend exists, wiring is a small adapter + a `useApiCollection`
swap (or a `ContentContext` entry), following the established pattern.
