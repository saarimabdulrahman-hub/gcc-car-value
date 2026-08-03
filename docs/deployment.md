# Deployment Guide

## Architecture

| Component | Platform | URL |
|-----------|----------|-----|
| Frontend | Vercel (static) | https://gcc-car-value.vercel.app |
| API | Render (Docker) | https://gcc-car-value.onrender.com |
| Database | Neon (serverless PostgreSQL) | Via DATABASE_URL |
| Object storage | AWS S3 | gcc-car-value-raw |

## Render Tier

**Production requires `plan: starter` ($7/mo).** The free tier sleeps containers after 15 minutes of inactivity and cold starts take 30+ seconds, causing timeouts for the first user after an idle period.

The `keep-alive.yml` workflow pings `/v1/health/live` every 10 minutes to prevent sleep on the free tier, but this is a workaround — the `starter` plan is the correct fix.

## Environment Variables (Render)

| Variable | Source | Notes |
|----------|--------|-------|
| `DATABASE_URL` | Neon dashboard | asyncpg connection string |
| `DATABASE_URL_SYNC` | Neon dashboard | psycopg2 connection string (for Alembic) |
| `JWT_SECRET` | Render auto-generated | `generateValue: true` in render.yaml |
| `SECRET_PROVIDER` | `environment` | Reads from Render env vars |
| `API_CORS_ORIGINS` | Vercel domain | `https://gcc-car-value.vercel.app` |
| `S3_ACCESS_KEY` | AWS IAM | Scraper raw data storage |
| `S3_SECRET_KEY` | AWS IAM | |
| `S3_REGION` | `me-central-1` | GCC region |
| `ENVIRONMENT` | `production` | Enables HSTS, startup validation |

## Deploying

```bash
# Render auto-deploys on push to master
git push origin master

# Vercel auto-deploys on push to master (serves ui/ directory)
# Manual deploy:
vercel --prod
```

## Database Migrations

Migrations run automatically at container start via:
```dockerfile
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn ..."]
```

A failed migration prevents the container from starting (fail-fast).

## Rollback

See `docs/rollback.md` for detailed rollback procedures.
