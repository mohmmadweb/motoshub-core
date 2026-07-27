# Contributing

Read **[CONVENTIONS.md](CONVENTIONS.md)** first — it is the binding coding contract.

Quick loop:
1. Branch `issue-<N>` off `main`.
2. Backend: `cd backend && pytest` must pass. Frontend: `cd frontend && npm run build` must pass.
3. Open a PR using the template; ≥1 approval; CI green.

Run locally: `docker compose -f infra/docker-compose.yml up --build` (see README).
