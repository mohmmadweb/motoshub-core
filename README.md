# Motoshub Core

[![CI](https://github.com/mohmmadweb/motoshub-core/actions/workflows/ci.yml/badge.svg)](https://github.com/mohmmadweb/motoshub-core/actions/workflows/ci.yml)

A clean, modular, production-grade implementation of the **Motoshub** platform —
a multi-tenant enterprise "communications + organizational processes" product.
It brings the reference prototype at **demo.shub.ir** fully to life: a Django REST
+ Channels backend and the **exact prototype UI** (a Vite/React SPA) wired to it,
so every screen works for real — no mock data.

> **Standalone repo.** This project does not depend on or modify the other
> Motoshub repositories — they are references only. Architecture is in
> [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md); coding rules in
> [CONVENTIONS.md](CONVENTIONS.md).

## Monorepo layout

```
motoshub-core/
├── backend/     Django 5 + DRF + PostgreSQL + Redis + Celery + Channels  (the API)
├── frontend/    Vite + React 19 + Tailwind v4, RTL/Persian — the demo.shub.ir UI, wired to the API
├── infra/       docker-compose + nginx  (run the whole stack behind one origin)
├── docs/        architecture & engineering docs
├── README.md
└── CONVENTIONS.md
```

There is **one** frontend: `frontend/` is the pixel-for-pixel prototype UI served
as a static SPA. In production nginx serves it and reverse-proxies `/api`, `/ws`,
`/static`, `/media` to the Django container, so the browser talks to a single origin.

## Tech stack

| Layer | Choice | Why |
|-------|--------|-----|
| API | Django 5 + Django REST Framework | Batteries-included, great admin, mature RBAC/ORM |
| DB | PostgreSQL (sqlite for local dev) | Clean normalized schema, JSON fields, strong integrity |
| Cache/queue/realtime | Redis + Celery + Channels | Scheduled workflow rules + realtime chat (channels + DMs) |
| ASGI server | daphne | Serves REST **and** WebSockets in one process |
| Auth | Unified HS256 JWT (shared pepper) | Interops with the gateway ecosystem |
| Web | Vite + React + Tailwind (RTL) | The prototype's own stack; pixel-matches demo.shub.ir |

## Run it live (Docker — recommended)

The whole stack (Postgres, Redis, API, Celery worker, web) comes up with one
command; the API auto-migrates and seeds demo data on first boot.

```bash
docker compose -f infra/docker-compose.yml up --build
```

Then open:

| What | URL |
|------|-----|
| Web app (SPA + proxied API) | http://localhost |
| API — Swagger UI | http://localhost/api/v1/docs/ |
| API — health | http://localhost/api/v1/health |

**Demo login** (seeded automatically): `admin` / `demo1234` (full access) or
`member` / `demo1234` (regular member).

## Run locally without Docker

**Backend** (REST + WebSockets on :8000):

```bash
cd backend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                        # DATABASE_URL=sqlite:///dev.db for a quick spin
python manage.py migrate
python manage.py seed_rbac                  # preset roles from the permission catalog
python manage.py seed_demo                  # demo tenant + users + sample content
python manage.py runserver 0.0.0.0:8000     # daphne-backed → serves WS too
```

**Frontend** (Vite dev server, needs Node 20):

```bash
cd frontend
npm install
# For a direct dev spin against the backend on :8000:
VITE_API_BASE=http://localhost:8000/api/v1 VITE_WS_BASE=ws://localhost:8000 npm run dev
```

Production build: `npm run build` → static files in `frontend/dist/` (serve with
any static host, or the `frontend/docker` nginx image which also proxies the API).

## How to test

- **Interactively:** open Swagger at `/api/v1/docs/`, call `POST /api/v1/auth/login`
  with the demo credentials, copy the `access` token into "Authorize", then
  exercise any endpoint.
- **Automated:** `cd backend && pytest` (L1 suite) · `cd frontend && npm run lint && npm run build`.

Every list response is `{data, links, meta}`; errors are
`{error: {code, type, message, details?}}`.

## API surface (current)

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| `POST` | `/api/v1/auth/login` · `/auth/refresh` · `GET /auth/me` | —/✔ | unified JWT |
| `GET` | `/api/v1/health` | — | liveness (pings DB) |
| CRUD | content: `/news` `/blogs` `/events` `/media` `/knowledge` | ✔ + RBAC | tenant-scoped |
| CRUD | social: `/groups` (+join/leave) `/forum/topics` (+reply) · `/social/friends` | ✔ | IDOR-safe; friend graph |
| CRUD | process: `/projects` `/tasks` `/contracts` (+tech-transfer/tenders/esign) | ✔ + RBAC | stage machines |
| CRUD | `/funds/records` · `/funds/projects` (innovation-fund dossier, by NF code) | ✔ + RBAC | eval gates + workflow |
| CRUD | `/training/courses` `/tickets` `/polls` `/research` `/awards/*` | ✔ + RBAC | |
| CRUD | `/competitions` (+vote) · `/challenges` (+join) | ✔ | participatory |
| REST+WS | `/chat/channels` (+messages) · `/chat/dms` · `ws/chat/<id>/` · `ws/dm/` | ✔ | realtime |
| — | `/notifications` `/reports/summary` `/assistant/{ask,suggestions}` `/settings/workflow` `/roles` `/users` | ✔ + RBAC | assistant answers from live data |

The full module map + honest per-feature status is in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) (§9–§10).

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system design, contracts, module map, status
- [CONVENTIONS.md](CONVENTIONS.md) — coding rules for backend & frontend
