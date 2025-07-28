#!/bin/bash

# Boiler App Backup Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Load environment variables
if [ -f .env ]; then
    source .env
else
    print_error ".env file not found"
    exit 1
fi

# Create backup directory
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="boiler_backup_$TIMESTAMP"

mkdir -p $BACKUP_DIR

print_status "🗄️ Starting backup process..."

# Database backup
print_status "Backing up PostgreSQL database..."
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U $DB_USER $DB_NAME > "$BACKUP_DIR/${BACKUP_NAME}_db.sql"

# Media files backup
print_status "Backing up media files..."
docker cp $(docker-compose -f docker-compose.prod.yml ps -q backend):/app/media "$BACKUP_DIR/${BACKUP_NAME}_media"

# Create compressed archive
print_status "Creating compressed archive..."
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" -C $BACKUP_DIR "${BACKUP_NAME}_db.sql" "${BACKUP_NAME}_media"

# Clean up temporary files
rm -f "$BACKUP_DIR/${BACKUP_NAME}_db.sql"
rm -rf "$BACKUP_DIR/${BACKUP_NAME}_media"

# Remove old backups (keep last 7 days)
print_status "Cleaning up old backups..."
find $BACKUP_DIR -name "boiler_backup_*.tar.gz" -mtime +7 -delete

print_status "✅ Backup completed successfully!"
print_status "Backup saved as: $BACKUP_DIR/$BACKUP_NAME.tar.gz"

# Upload to cloud storage (optional)
# Uncomment and configure for your cloud provider
# print_status "Uploading to cloud storage..."
# aws s3 cp "$BACKUP_DIR/$BACKUP_NAME.tar.gz" s3://your-backup-bucket/
# gsutil cp "$BACKUP_DIR/$BACKUP_NAME.tar.gz" gs://your-backup-bucket/