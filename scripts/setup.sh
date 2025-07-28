#!/bin/bash

# Boiler App Setup Script for Linux Production Environment
set -e

echo "🚀 Setting up Boiler App for production..."

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_status "Docker installed successfully"
else
    print_status "Docker is already installed"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed successfully"
else
    print_status "Docker Compose is already installed"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file..."
    cp .env.example .env
    print_warning "Please edit .env file with your production settings"
else
    print_status ".env file already exists"
fi

# Create SSL directory
if [ ! -d "nginx/ssl" ]; then
    print_status "Creating SSL directory..."
    mkdir -p nginx/ssl
    print_warning "Please add your SSL certificates to nginx/ssl/"
fi

# Set proper permissions
print_status "Setting proper permissions..."
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p backups

print_status "✅ Setup completed successfully!"
print_warning "Next steps:"
echo "1. Edit .env file with your production settings"
echo "2. Add SSL certificates to nginx/ssl/"
echo "3. Update DOMAIN in .env file"
echo "4. Run: ./scripts/deploy.sh"