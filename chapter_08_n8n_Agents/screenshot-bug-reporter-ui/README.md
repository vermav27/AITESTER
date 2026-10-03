# Screenshot Bug Reporter UI

Vercel-ready UI for the screenshot bug reporter.

The browser submits only to first-party routes:

- `/api/report-bug`
- `/api/report-status`

The production automation endpoint is stored server-side in `N8N_BUG_REPORTER_URL`.

## Local

```bash
npm run dev
```

Open <http://127.0.0.1:4173/>.

## Vercel

1. Use this folder as the Vercel project root.
2. Add `N8N_BUG_REPORTER_URL`.
3. Add `STATUS_TOKEN_SECRET`.
4. Deploy.

## Scripts

- `npm run dev` starts the local UI and API proxy.
- `npm run build` validates deploy readiness.
