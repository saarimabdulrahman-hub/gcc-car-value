# Frontend deployment

## Source of truth

The production frontend is the static artifact under `ui/`:

- `ui/*.html`
- `ui/*.css`
- `ui/*.js`
- `ui/img/**`

Vercel publishes this directory using the repository-root `vercel.json`.
The canonical production URL is <https://gcc-car-value.vercel.app>.

The React/Vite files under `ui/src/` and generated output under
`ui/dist/react-browse/` are experimental and are not deployed. FastAPI's
static-file mount and Python's built-in HTTP server are local fallbacks, not
additional production deployment paths.

## Local preview

From the repository root:

```powershell
python -m http.server 4173 --directory ui
```

Open <http://localhost:4173>. Pages use their `.html` names locally, such as
<http://localhost:4173/reports.html>.

## Release behavior

Vercel's Git integration deploys the complete `ui/` output directory on a
release push. There is no path-filtered frontend workflow, so changes to HTML,
CSS, JavaScript, or images are all included.

`vercel.json` enables clean production URLs (`/reports` maps to
`ui/reports.html`), disables long-lived caching for HTML, and applies security
headers. Image assets receive a separate cache policy.

After a deployment, validate the complete route manifest:

```powershell
python scripts/validate_routes.py
```

Override the target for staging or a preview deployment:

```powershell
python scripts/validate_routes.py https://preview.example
```

The API is deployed separately to Render. `render.yaml` supplies the canonical
Vercel origin through `API_CORS_ORIGINS`.
