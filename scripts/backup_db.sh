#!/bin/bash
# Database backup script — pg_dump → S3 with timestamp.
# Run: DATABASE_URL_SYNC=... S3_BUCKET=... bash scripts/backup_db.sh
set -euo pipefail

BUCKET="${S3_BUCKET:-gcc-car-value-backups}"
TIMESTAMP="$(date -u +%Y%m%d-%H%M%S)"
BACKUP_FILE="db-backup-${TIMESTAMP}.sql.gz"

echo "Backing up database to s3://${BUCKET}/${BACKUP_FILE} ..."

pg_dump "$DATABASE_URL_SYNC" --no-owner --no-acl | gzip > "$BACKUP_FILE"

# Upload to S3 (uses AWS CLI — ensure credentials are configured)
if command -v aws &> /dev/null; then
    aws s3 cp "$BACKUP_FILE" "s3://${BUCKET}/${BACKUP_FILE}" --storage-class STANDARD_IA
    echo "Backup uploaded: s3://${BUCKET}/${BACKUP_FILE}"
else
    echo "WARNING: aws CLI not found — backup written locally: ${BACKUP_FILE}"
fi

# Retain last 30 days only (if aws CLI available)
if command -v aws &> /dev/null; then
    CUTOFF="$(date -u -d '30 days ago' +%Y%m%d)"
    aws s3 ls "s3://${BUCKET}/" | while read -r _ _ _ key; do
        if [[ "$key" < "db-backup-${CUTOFF}" ]]; then
            aws s3 rm "s3://${BUCKET}/${key}"
            echo "Removed expired backup: ${key}"
        fi
    done
fi

rm -f "$BACKUP_FILE"
echo "Backup complete."
