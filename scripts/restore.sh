#!/bin/bash

# Boiler App Restore Script
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

# Check if backup file is provided
if [ $# -eq 0 ]; then
    print_error "Usage: $0 <backup_file.tar.gz>"
    print_status "Available backups:"
    ls -la backups/*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE=$1

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    print_error "Backup file $BACKUP_FILE not found"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    source .env
else
    print_error ".env file not found"
    exit 1
fi

print_warning "⚠️  This will replace existing data with backup data."
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Restore cancelled"
    exit 0
fi

print_status "🔄 Starting restore process..."

# Create temporary directory
TEMP_DIR=$(mktemp -d)
BACKUP_NAME=$(basename "$BACKUP_FILE" .tar.gz)

# Extract backup
print_status "Extracting backup..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Stop services
print_status "Stopping services..."
docker-compose -f docker-compose.prod.yml down

# Start database only
print_status "Starting database..."
docker-compose -f docker-compose.prod.yml up -d db

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 10

# Restore database
print_status "Restoring database..."
docker-compose -f docker-compose.prod.yml exec -T db dropdb -U $DB_USER $DB_NAME || true
docker-compose -f docker-compose.prod.yml exec -T db createdb -U $DB_USER $DB_NAME
docker-compose -f docker-compose.prod.yml exec -T db psql -U $DB_USER $DB_NAME < "$TEMP_DIR/${BACKUP_NAME}_db.sql"

# Start all services
print_status "Starting all services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for backend to be ready
print_status "Waiting for backend to be ready..."
sleep 30

# Restore media files
if [ -d "$TEMP_DIR/${BACKUP_NAME}_media" ]; then
    print_status "Restoring media files..."
    docker cp "$TEMP_DIR/${BACKUP_NAME}_media/." $(docker-compose -f docker-compose.prod.yml ps -q backend):/app/media/
fi

# Run migrations (in case of version differences)
print_status "Running migrations..."
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Collect static files
print_status "Collecting static files..."
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Clean up
rm -rf "$TEMP_DIR"

print_status "✅ Restore completed successfully!"
print_status "Services status:"
docker-compose -f docker-compose.prod.yml ps