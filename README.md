# Motoshub Core

Clean, modular reimplementation of the Motoshub platform — a multi-tenant
"organizational communications + processes" product — built to fully cover the
UX reference at **demo.shub.ir** (the `motoshub-prototype`).

Monorepo:

| Path | Stack | Role |
|------|-------|------|
| `backend/` | Django 5 + DRF + PostgreSQL + Redis + Celery + Channels | REST API (`/api/v1`), the `api2` / `motonextapi` service |
| `frontend/` | Next.js (App Router) + TypeScript + Tailwind (RTL) | Web client (`motonextfront`) |
| `infra/` | docker-compose + nginx | Local + deploy composition |
| `docs/` | Markdown | Architecture & engineering docs |

## Why this exists

The wider ecosystem is a strangler-fig migration (PHP/Oxwall → Django behind a
Kong gateway, sharing the legacy DB). `motoshub-core` is the **greenfield,
clean-schema** implementation of the same product: its own normalized
PostgreSQL schema (managed models), no legacy coupling — while staying
**contract-compatible** (`{data, links, meta}` envelope, uniform errors, unified
HS256 JWT signed with the shared `OW_PASSWORD_PEPPER`) so it plugs into the same
gateway and frontends. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Quick start (backend)

```bash
cd backend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # then edit secrets
python manage.py migrate
python manage.py seed_rbac           # preset roles from the permission catalog
python manage.py runserver
```

- Health: `GET /api/v1/health`
- Auth: `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`, `GET /api/v1/auth/me`
- API docs (Swagger): `/api/v1/docs/`

## Status

Foundation is implemented and smoke-tested end-to-end: project config,
`{data,links,meta}` envelope + uniform error handler, unified JWT auth, and the
core apps **accounts / tenancy / rbac** (99-permission catalog, preset roles,
per-tenant custom roles, tenant→holding→company isolation). Domain modules
(news, blog, events, media, groups, forum, projects, contracts, innovation fund,
research, training, …) and the Next.js frontend are being added module by
module — tracked in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
