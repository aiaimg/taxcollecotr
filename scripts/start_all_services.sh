#!/bin/bash

# Script to start all Docker services (including Redis)
# This script will start all services defined in docker-compose.yml

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Starting Docker..."
    open -a Docker
    # Wait for Docker to start
    echo "Waiting for Docker to start..."
    timeout=60
    elapsed=0
    while ! docker info > /dev/null 2>&1; do
        if [ $elapsed -ge $timeout ]; then
            echo "Error: Docker failed to start within $timeout seconds"
            exit 1
        fi
        sleep 2
        elapsed=$((elapsed + 2))
    done
    echo "Docker is now running"
fi

# Detect docker-compose command (support both docker-compose and docker compose)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "Error: docker-compose or docker compose not found"
    exit 1
fi

# Start all services
echo "Starting all Docker services..."
$DOCKER_COMPOSE up -d

# Wait a moment for services to start
sleep 5

# Check service status
echo "Service status:"
$DOCKER_COMPOSE ps

