# Redis Auto-Start Setup for macOS

This guide explains how to set up Redis to start automatically on your Mac using Docker.

## Quick Setup

1. **Run the setup script:**
   ```bash
   cd /Users/samoela/Projet/taxcollecotr
   ./scripts/setup_redis_autostart.sh
   ```

2. **Verify Redis is running:**
   ```bash
   ./scripts/check_redis_status.sh
   ```

## Manual Setup

If you prefer to set up manually:

1. **Make sure Docker Desktop is installed and running:**
   - Download from: https://www.docker.com/products/docker-desktop
   - Start Docker Desktop application

2. **Install the LaunchAgent:**
   ```bash
   # Copy the plist file to LaunchAgents directory
   cp scripts/com.taxcollector.redis.plist ~/Library/LaunchAgents/
   
   # Update the paths in the plist file (replace /Users/samoela/Projet/taxcollecotr with your actual path)
   # Edit ~/Library/LaunchAgents/com.taxcollector.redis.plist
   
   # Load the LaunchAgent
   launchctl load ~/Library/LaunchAgents/com.taxcollector.redis.plist
   ```

## Scripts

### `start_redis.sh`
Starts Redis service using Docker Compose. This script:
- Checks if Docker is running and starts it if needed
- Starts the Redis container
- Verifies Redis is running

### `start_all_services.sh`
Starts all Docker services (Redis, PostgreSQL, Web, Celery, etc.)

### `check_redis_status.sh`
Checks the current status of Redis and Docker

### `setup_redis_autostart.sh`
Sets up the LaunchAgent for auto-start on login

## Managing the Auto-Start

### Check if auto-start is enabled:
```bash
launchctl list | grep com.taxcollector.redis
```

### Unload (disable) auto-start:
```bash
launchctl unload ~/Library/LaunchAgents/com.taxcollector.redis.plist
```

### Reload (re-enable) auto-start:
```bash
launchctl load ~/Library/LaunchAgents/com.taxcollector.redis.plist
```

### Remove auto-start completely:
```bash
launchctl unload ~/Library/LaunchAgents/com.taxcollector.redis.plist
rm ~/Library/LaunchAgents/com.taxcollector.redis.plist
```

## Logs

Auto-start logs are written to:
- `logs/redis_startup.log` - Standard output
- `logs/redis_startup.error.log` - Error output

View logs:
```bash
tail -f logs/redis_startup.log
tail -f logs/redis_startup.error.log
```

## Troubleshooting

### Docker is not starting
- Make sure Docker Desktop is installed
- Try starting Docker manually: `open -a Docker`
- Check Docker preferences to ensure it starts on login

### Redis is not starting
- Check Docker logs: `docker-compose logs redis`
- Verify Docker is running: `docker info`
- Check if port 6379 is already in use: `lsof -i :6379`

### LaunchAgent is not working
- Check if it's loaded: `launchctl list | grep com.taxcollector.redis`
- Check logs in `logs/redis_startup.log`
- Verify paths in the plist file are correct
- Try reloading: `launchctl unload ~/Library/LaunchAgents/com.taxcollector.redis.plist && launchctl load ~/Library/LaunchAgents/com.taxcollector.redis.plist`

## Testing Redis Connection

Test Redis connection using the provided test script:
```bash
python test_redis_connection.py
```

Or test directly:
```bash
docker exec $(docker ps -q -f name=redis) redis-cli ping
```

Expected output: `PONG`









