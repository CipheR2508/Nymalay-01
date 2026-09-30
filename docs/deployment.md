# Deployment

The `deploy` job in `.github/workflows/ci-cd.yml` is intentionally inert. This
document is the checklist to fill in before it is enabled.

## What CI does today

| Job | Trigger | Does |
|-----|---------|------|
| `frontend` | push/PR | `npm ci`, `npm run lint`, `npm run build`, audit |
| `backend` | push/PR | `pip install -r requirements.txt -r requirements-dev.txt`, `pytest`, `bandit` |
| `build-and-push` | push to `main` | builds and pushes both images to the registry |
| `deploy` | push to `main` | prints a placeholder |

## Required repository variables and secrets

| Name | Kind | Purpose |
|------|------|---------|
| `DOCKER_USERNAME` | secret | registry account, e.g. a GitHub org name |
| `DOCKER_PASSWORD` | secret | registry token with push scope |
| `PUBLIC_API_URL` | variable | browser-visible backend URL, e.g. `https://api.nymalay.clinic`. Passed as a build arg, because `NEXT_PUBLIC_*` values are inlined at build time and cannot be changed at runtime. |

## Backend environment

Set these in the target platform, not in the repository:

- `SECRET_KEY` — **required in production.** Generate with `openssl rand -hex 32`.
  Startup fails if it is missing, under 32 characters, or equal to a known
  placeholder including the one that used to be committed in `auth.py`.
- `ENVIRONMENT=production` — activates the `SECRET_KEY` check.
- `DATABASE_URL=postgresql://nymalaya:<password>@<host>:5432/nymalaya`
- `CORS_ORIGINS` — comma-separated, exact browser origins. No wildcards.
- `ADMIN_USERNAME` / `ADMIN_EMAIL` / `ADMIN_PASSWORD` — seeds one admin account on
  first boot. Clear `ADMIN_PASSWORD` once the account exists.

### Schema management

`init_db()` calls `Base.metadata.create_all()`. That creates missing tables but
does **not** alter existing ones, so it is fine for a fresh database and unsafe
as an upgrade path. Before the first schema change lands in production, add
Alembic and switch startup to `alembic upgrade head`.

## Database

Postgres 15, matching `docker-compose.yml`. Take a dump before each release:

```bash
pg_dump "$DATABASE_URL" > backup-$(date +%F).sql
```

The database holds patient names, contact details, dates of birth, medical
history and consultation notes. Treat backups as clinical records: encrypt at
rest, restrict access, and set a retention period.

## Before enabling the deploy job

1. Add the SSH key or cloud credential secret and the actual deploy commands.
2. Set the environment variables above on the target.
3. Run the deploy job on a branch and confirm the site loads.
4. Verify the booking form end to end against the deployed backend.
5. Confirm `GET /patients/` still returns 401 without a token.

## Health check

    GET /health

Returns 200 with a status and the configured environment. It touches no patient
data and is safe to leave public.
