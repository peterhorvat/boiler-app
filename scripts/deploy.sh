#!/bin/bash

# Boiler App Deployment Script
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

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found. Please run ./scripts/setup.sh first"
    exit 1
fi

# Load environment variables
source .env

print_status "🚀 Deploying Boiler App..."

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Remove old images (optional)
read -p "Do you want to remove old Docker images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Removing old Docker images..."
    docker image prune -f
    docker system prune -f
fi

# Build and start services
print_status "Building and starting services..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check if services are running
print_status "Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# Run Django migrations
print_status "Running Django migrations..."
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Collect static files
print_status "Collecting static files..."
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Create superuser (optional)
read -p "Do you want to create a Django superuser? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Creating Django superuser..."
    docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
fi

# Show final status
print_status "✅ Deployment completed successfully!"
print_status "Services running:"
docker-compose -f docker-compose.prod.yml ps

print_status "🌐 Your application should be available at:"
echo "   Frontend: https://${DOMAIN:-localhost}"
echo "   API: https://${DOMAIN:-localhost}/api/"
echo "   Admin: https://${DOMAIN:-localhost}/admin/"

print_warning "Don't forget to:"
echo "1. Set up SSL certificates in nginx/ssl/"
echo "2. Configure your domain DNS to point to this server"
echo "3. Set up automated backups using ./scripts/backup.sh"