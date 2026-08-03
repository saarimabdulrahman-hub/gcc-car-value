# Rollback Procedures

> Maintained by: GCC Car Value Dev & Claude

## Frontend (Vercel)

**Revert to previous deployment:**
1. Go to Vercel Dashboard → gcc-car-value → Deployments
2. Find the last healthy deployment (green checkmark)
3. Click "..." → "Promote to Production"
4. Verify: `curl -sI https://gcc-car-value.vercel.app | grep x-vercel`

**Manual rollback via CLI:**
```bash
vercel rollback --prod --scope gcc-car-value
```

## API (Render)

**Revert to previous Docker image:**
1. Go to Render Dashboard → gcc-car-value-api → Deploys
2. Find the last healthy deploy → "Rollback to this deploy"
3. Wait for health check to pass: `curl https://gcc-car-value.onrender.com/v1/health/live`

**Manual rollback via commit revert:**
```bash
git revert HEAD --no-edit
git push origin main  # Render auto-deploys from main
```

## Database (Neon)

**Rollback a migration:**
```bash
# Get current revision
alembic -c src/db/migrations/alembic.ini current

# Roll back one migration
alembic -c src/db/migrations/alembic.ini downgrade -1

# Verify
alembic -c src/db/migrations/alembic.ini current
```

**Restore from backup:**
1. Download latest backup from S3
2. Create a new Neon branch from backup
3. Update `DATABASE_URL`/`DATABASE_URL_SYNC` in Render to point at restored branch
4. Redeploy

## Verification After Rollback

```bash
# Health check
curl -s https://gcc-car-value.onrender.com/v1/health/live

# Smoke test valuation
curl -s -X POST https://gcc-car-value.onrender.com/v1/valuate \
  -H "Content-Type: application/json" \
  -d '{"make":"Toyota","model":"Land Cruiser","year":2022,"mileage_km":50000}' \
  | jq .estimate

# Frontend loads
curl -sI https://gcc-car-value.vercel.app | head -1  # 200 OK
```
