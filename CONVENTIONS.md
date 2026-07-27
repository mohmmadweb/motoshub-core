# Motoshub Core — Coding Conventions & Rules

Every change (backend or frontend) must follow these rules. They exist so the
codebase stays modular, stable, and easy to maintain and extend. This is the
contract for humans and AI agents working in this repo.

---

## 0. Golden rules (apply everywhere)

1. **Small, focused changes.** One concern per commit/MR; keep MRs under ~400
   lines. An issue branch lives ≤ 3 days.
2. **Never break the API contract.** The `{data, links, meta}` envelope, the
   uniform error body, and the unified JWT are load-bearing — other services and
   the frontend depend on them. Contract changes are a deliberate, reviewed act.
3. **Tenant isolation is sacred.** No query may return another tenant's rows. New
   models are `TenantScopedModel`; new viewsets extend `TenantScopedModelViewSet`.
4. **Everything gated by RBAC.** Every write action maps to a permission id from
   the catalog. No endpoint ships "open by default".
5. **No secrets in code.** Config comes from the environment (`.env`), never
   hard-coded. Never commit `.env`, tokens, or credentials.
6. **Tests before green.** A bug fix starts with a failing test. A new endpoint
   ships with success + `401/403/422` + one edge-case test.
7. **Match the prototype.** `demo.shub.ir` is the acceptance benchmark; behavior
   and (for the frontend) pixels must match it.
8. **Keep the repos separate.** This repo does not import from or write to
   `motoshub-web`, `-web-client`, `-new-api`, `-gateway`, `-docs`, or
   `-prototype`. They are references only.

---

## 1. Backend (Django + DRF)

### 1.1 Structure
- One Django app per **bounded context** under `backend/apps/<name>/`.
- Each app is split: `models.py`, `serializers.py`, `views.py`, `urls.py`,
  `filters.py` (optional), `tasks.py` (Celery, optional), `tests/`.
- Cross-cutting helpers live in `apps/core/` (model bases, envelope renderer,
  pagination, exception handler, `HasPerm`, `TenantScopedModelViewSet`).
- Register a new app in `config/settings/base.py::LOCAL_APPS` and mount its
  router in `config/urls.py`.

### 1.2 Models
- Inherit `TimeStampedModel` (UUID pk + timestamps) or `TenantScopedModel`
  (adds `tenant` FK) — never a bare `models.Model` for domain data.
- Set an explicit `db_table` (`<app>_<name>`), `ordering`, and `indexes` for
  common query paths (`tenant` + hot filter/sort columns).
- Money → `DecimalField` (+ a currency), never a formatted string. Dates →
  real `DateTimeField` (store Gregorian/UTC; Jalali is a display concern).
- Choice sets → `models.TextChoices` with Persian labels.
- Author/owner references → real FK to `accounts.User` (`on_delete=SET_NULL`,
  `null=True` for content that outlives its author).

### 1.3 API
- ViewSets extend `TenantScopedModelViewSet`; declare a full `required_perms`
  map (`list/retrieve/create/update/partial_update/destroy` + custom actions).
- Routes are **slash-less** (`DefaultRouter(trailing_slash=False)`), mounted
  under `/api/v1`.
- Serializers are explicit: list `fields` and `read_only_fields`; never
  `fields = "__all__"`. Server-owned fields (`tenant`, `author`, counters,
  timestamps) are read-only and set server-side.
- Filtering/search/ordering via `filterset_fields` / `search_fields` /
  `ordering_fields` — do not hand-roll query parsing.
- Return the raw payload from a view; the renderer adds the envelope. Errors go
  through `raise ValidationError(...)` / DRF exceptions, not manual JSON (except
  the two hand-built auth 401s, which already match the error shape).

### 1.4 Async / realtime
- Long or scheduled work (reminders, escalations, notifications, exports) →
  Celery tasks in `apps/<name>/tasks.py`. Views never block on them.
- Realtime → Django Channels consumers; the channel layer is Redis.

### 1.5 Style & quality
- `ruff` is the formatter/linter (run `ruff check` + `ruff format`). 4-space
  indent, double quotes, ≤ 100 cols.
- Type-hint public functions. Docstrings explain **why**, not what.
- `pytest` for tests (`apps/<name>/tests/`); use `model_bakery` for fixtures.
  Never hit external services in tests.
- Migrations are committed with their model change and never edited after merge.

---

## 2. Frontend (Next.js + TypeScript)

### 2.1 Structure
- App Router with a **route group per sub-app** (`(auth)`, `(workspace)`,
  `(social)`) sharing one prop-driven `MainLayout`.
- `components/ui` (primitives) → `components/common` (shared blocks) →
  `components/<feature>` (feature components mirroring routes).
- `@/*` path alias for imports; **PascalCase** component filenames (be
  consistent — no mixed casing).

### 2.2 Data & state
- **Server state**: TanStack Query only, via hooks in `hooks/queries/<domain>.ts`.
  Hooks own fetching, cache keys, toasts, and navigation; components stay dumb.
  No side effects during render — use effects/handlers.
- **UI/local state**: Zustand (+`persist`) with a central `resetAllStores()`
  for logout. One source of truth per datum (don't duplicate the token across
  store + localStorage).
- **HTTP**: one interceptor-configured Axios instance (`libs/axios.ts`) with
  real token refresh. Typed `xxxApi` service objects per resource. All URLs come
  from the central `libs/routes.ts` registry — no hard-coded paths.
- Unwrap the `{data, links, meta}` envelope in the query `select`.

### 2.3 Forms & validation
- `react-hook-form` + `zod` resolvers for every form — no hand-rolled `useState`
  validation.

### 2.4 Styling & i18n
- Tailwind with the **prototype design tokens** (brand/navy/ink scales, 6 accent
  presets) defined in `tailwind.config`. Dark mode is real (class-based, CSS-var
  inversion) — no dangling `dark:`/`bg-theme`.
- RTL everywhere: `dir="rtl"`, local Persian font via `next/font/local`, `fa-IR`
  number/date formatting. All user-facing strings are Persian.
- Accessibility: label every control, `aria-*` on interactive widgets, visible
  focus, contrast that passes in both themes.

### 2.5 Quality
- `strict: true` TS; no `any` without a written reason. `tsc` + ESLint must pass.
- Component tests for shared UI; each PR includes before/after screenshots
  (light + dark, desktop + 375px).

---

## 3. Git & delivery

- Branch `issue-<N>` off `main`; commit messages `type(scope): summary`
  (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`) with `#<N>` when tied to
  an issue. Direct commits to `main` are avoided.
- MR description: **what / why / how tested**. Backend adds curl samples; frontend
  adds screenshots. ≥ 1 non-author approval.
- CI (Layer-2) must be green: lint + type-check + tests + build + contract test
  against the OpenAPI schema.
- Definition of Done: merged + all test layers pass + PO-accepted + no
  `TODO`/`console.log`/`print` left + documented in Swagger/README.
