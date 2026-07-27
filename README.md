# Motoshub Core

[![CI](https://github.com/mohmmadweb/motoshub-core/actions/workflows/ci.yml/badge.svg)](https://github.com/mohmmadweb/motoshub-core/actions/workflows/ci.yml)

A clean, modular, production-grade implementation of the **Motoshub** platform —
a multi-tenant enterprise "communications + organizational processes" product.
Its goal is to bring the reference prototype at **demo.shub.ir** fully to life:
a Django REST backend and a Next.js web client that make every screen work for real.

> **Standalone repo.** This project does not depend on or modify the other
> Motoshub repositories — they are references only. Architecture is in
> [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md); coding rules in
> [CONVENTIONS.md](CONVENTIONS.md).

## Monorepo layout

```
motoshub-core/
├── backend/     Django 5 + DRF + PostgreSQL + Redis + Celery + Channels  (the API)
├── frontend/    Next.js (App Router) + TypeScript + Tailwind, RTL/Persian (the web client)
├── infra/       docker-compose + nginx  (run the whole stack)
├── docs/        architecture & engineering docs
├── README.md
└── CONVENTIONS.md
```

## Tech stack

| Layer | Choice | Why |
|-------|--------|-----|
| API | Django 5 + Django REST Framework | Batteries-included, great admin, mature RBAC/ORM |
| DB | PostgreSQL | Clean normalized schema, JSON fields, strong integrity |
| Cache/queue/realtime | Redis + Celery + Channels | Scheduled workflow rules + realtime chat |
| Auth | Unified HS256 JWT (shared pepper) | Interops with the gateway ecosystem |
| Web | Next.js App Router + Tailwind | SSR/RTL-friendly, matches the prototype's design system |

## Run it live (Docker — recommended)

The whole stack (Postgres, Redis, API, Celery worker, web) comes up with one
command; the API auto-migrates and seeds demo data on first boot.

```bash
docker compose -f infra/docker-compose.yml up --build
```

Then open:

| What | URL |
|------|-----|
| Web client | http://localhost:3000 |
| API — Swagger UI (try endpoints) | http://localhost:8000/api/v1/docs/ |
| API — health | http://localhost:8000/api/v1/health |

**Demo login** (seeded automatically): `admin` / `demo1234` (full access) or
`member` / `demo1234` (regular member).

> While the frontend is still being built, bring up just the backend stack:
> `docker compose -f infra/docker-compose.yml up --build db redis api worker`
> and test through Swagger at http://localhost:8000/api/v1/docs/.

## Run the backend only (local, no Docker)

```bash
cd backend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                       # DATABASE_URL can be sqlite:///dev.db for a quick spin
python manage.py migrate
python manage.py seed_rbac                  # preset roles from the permission catalog
python manage.py seed_demo                  # demo tenant + users + sample content
python manage.py runserver                  # http://localhost:8000
```

## How to test

- **Interactively:** open Swagger at `/api/v1/docs/`, call `POST /api/v1/auth/login`
  with the demo credentials, copy the `access` token into the "Authorize" box,
  then exercise any endpoint.
- **From the terminal:**
  ```bash
  # login → capture the access token
  curl -s localhost:8000/api/v1/auth/login \
       -H 'Content-Type: application/json' \
       -d '{"username":"admin","password":"demo1234"}' | jq .data.access

  # use it
  curl -s localhost:8000/api/v1/news -H "Authorization: Bearer <token>" | jq
  ```
- **Automated:** `cd backend && pytest`.

Every list response is `{data, links, meta}`; errors are
`{error: {code, type, message, details?}}`.

## API surface (current)

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| `POST` | `/api/v1/auth/login` | — | returns `access` + `refresh` + `user` |
| `POST` | `/api/v1/auth/refresh` | — | new `access` |
| `GET` | `/api/v1/auth/me` | ✔ | current user + effective permissions |
| `GET` | `/api/v1/health` | — | liveness |
| CRUD | content: `/news` `/blogs` `/events` `/media` `/knowledge` | ✔ + RBAC | tenant-scoped |
| CRUD | social: `/groups` (+join/leave) `/forum/topics` (+reply/solve) | ✔ + RBAC | IDOR-safe privacy |
| CRUD | process: `/projects` `/tasks` `/contracts` `/funds/projects` | ✔ + RBAC | stage machines |
| CRUD | `/training/courses` `/tickets` `/polls` `/research` `/awards/*` | ✔ + RBAC | |
| WS | `/ws/chat/<channel_id>/?token=` + `/chat/channels` | ✔ | realtime |
| — | `/notifications` `/settings/workflow` `/reports/summary` | ✔ + RBAC | |

All prototype modules are implemented end-to-end (backend + frontend); the full
module map + status is in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system design, contracts, module map, status
- [CONVENTIONS.md](CONVENTIONS.md) — coding rules for backend & frontend
