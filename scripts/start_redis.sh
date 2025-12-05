#!/bin/bash

# Script to start Redis using Docker Compose
# This script will start only the Redis service

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

# Check if Redis container already exists and is running
if docker ps --format '{{.Names}}' | grep -q "^redis-taxcollector$"; then
    echo "✓ Redis container is already running"
    docker ps | grep redis-taxcollector
    exit 0
fi

# Detect docker-compose command (support both docker-compose and docker compose)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE=""
fi

# Try to start Redis using docker-compose first (if .env file exists)
if [ -n "$DOCKER_COMPOSE" ] && [ -f "$PROJECT_DIR/.env" ]; then
    echo "Starting Redis service using docker-compose..."
    if $DOCKER_COMPOSE up -d redis 2>/dev/null; then
        sleep 3
        if $DOCKER_COMPOSE ps redis 2>/dev/null | grep -q "Up"; then
            echo "✓ Redis is running successfully (via docker-compose)"
            $DOCKER_COMPOSE ps redis
            exit 0
        fi
    fi
    echo "docker-compose failed, trying direct docker run..."
fi

# Fallback: Start Redis directly with docker run
echo "Starting Redis service directly with Docker..."
if docker ps -a --format '{{.Names}}' | grep -q "^redis-taxcollector$"; then
    echo "Starting existing Redis container..."
    docker start redis-taxcollector
else
    echo "Creating new Redis container..."
    docker run -d --name redis-taxcollector -p 6379:6379 -v redis_data:/data redis:7-alpine
fi

# Wait a moment for Redis to start
sleep 3

# Check if Redis is running
if docker ps --format '{{.Names}}' | grep -q "^redis-taxcollector$"; then
    echo "✓ Redis is running successfully"
    docker ps | grep redis-taxcollector
    
    # Test Redis connection
    if docker exec redis-taxcollector redis-cli ping 2>/dev/null | grep -q "PONG"; then
        echo "✓ Redis is responding to ping"
    else
        echo "⚠ Redis container is running but not responding to ping yet"
    fi
else
    echo "✗ Failed to start Redis"
    docker logs redis-taxcollector 2>/dev/null || echo "Could not retrieve logs"
    exit 1
fi

