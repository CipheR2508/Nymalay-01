# Cloudflare Pages deployment

The public website is a Next.js static export. It does not call the FastAPI
backend and does not need a running server, API URL, or frontend environment
variables. Keep the backend available separately for future use; it is not part
of this Pages deployment.

## Cloudflare Pages settings

Connect the repository to Cloudflare Pages and use:

| Setting | Value |
|---------|-------|
| Framework preset | Next.js (Static HTML Export) |
| Root directory | `frontend` |
| Build command | `npx next build` |
| Build output directory | `out` |
| Environment variables | None required |

`frontend/next.config.js` enables `output: 'export'`; `next build` writes the
complete site to `frontend/out/`. Do not use `next start` or configure a
Functions/Workers backend for this static site.

## Verify locally

From `frontend/`:

```bash
npm install
npm run build
```

Confirm `out/index.html`, the exported route directories, `_next/` assets, and
the copied `images/` directory exist. The backend can be stopped while serving
this output from any static HTTP server.

Clinic contact links open `https://wa.me/<clinic-number>` directly, without a
message or form data. The site does not collect or submit consultation details.

## Backend files

Cloudflare Pages does not host the existing FastAPI backend. Its source remains
under `backend/` and is not removed by this deployment configuration. Keep
`backend/.env` and `backend/clinic.db` out of version control.
