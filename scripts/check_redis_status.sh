#!/bin/bash

# Script to check Redis status

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

echo "Checking Redis Status"
echo "===================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "✗ Docker is not running"
    echo "  Run: open -a Docker"
    exit 1
else
    echo "✓ Docker is running"
fi

# Check if Redis container exists
if docker ps -a | grep -q "redis"; then
    echo "✓ Redis container exists"
    
    # Check if Redis is running
    if docker ps | grep -q "redis"; then
        echo "✓ Redis container is running"
        
        # Detect docker-compose command
        if command -v docker-compose &> /dev/null; then
            DOCKER_COMPOSE="docker-compose"
        elif docker compose version &> /dev/null; then
            DOCKER_COMPOSE="docker compose"
        else
            DOCKER_COMPOSE=""
        fi
        
        # Check Redis health
        if [ -n "$DOCKER_COMPOSE" ] && $DOCKER_COMPOSE ps redis 2>/dev/null | grep -q "Up"; then
            echo "✓ Redis service is healthy"
        else
            echo "⚠ Redis container is running but service health check unavailable"
        fi
        
        # Test Redis connection
        if docker exec $(docker ps -q -f name=redis) redis-cli ping 2>/dev/null | grep -q "PONG"; then
            echo "✓ Redis is responding to ping"
        else
            echo "⚠ Redis is running but not responding to ping"
        fi
    else
        echo "✗ Redis container exists but is not running"
        if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
            echo "  Run: docker-compose up -d redis (or: docker compose up -d redis)"
        else
            echo "  Run: docker start redis"
        fi
    fi
else
    echo "✗ Redis container does not exist"
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        echo "  Run: docker-compose up -d redis (or: docker compose up -d redis)"
    else
        echo "  Run: docker run -d --name redis -p 6379:6379 redis:7-alpine"
    fi
fi

echo ""
echo "Container details:"
if [ -n "$DOCKER_COMPOSE" ]; then
    $DOCKER_COMPOSE ps redis 2>/dev/null || docker ps -a | grep redis
else
    docker ps -a | grep redis
fi

echo ""
echo "To start Redis, run:"
echo "  $PROJECT_DIR/scripts/start_redis.sh"

