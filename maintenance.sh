#!/bin/bash
# Innovator VPS Maintenance Script

set -e

echo "Starting Innovator Maintenance..."

# Check Docker Compose version
if docker compose version > /dev/null 2>&1; then
  DOCKER_CMD="docker compose"
  echo "Using Docker Compose V2"
else
  DOCKER_CMD="docker-compose"
  echo "Using Docker Compose V1"
fi

# 1. Cleanup orphaned containers and networks
echo "Cleaning up orphans..."
$DOCKER_CMD -f docker-compose.prod.yml down --remove-orphans || true

# 2. Prune unused images and volumes (safety check)
echo "Pruning unused resources..."
docker image prune -f
docker network prune -f

# 3. Verify Environment Files
SERVICES=("auth" "kms" "elearning" "ecommerce" "social_media")
for svc in "${SERVICES[@]}"; do
  if [ ! -f "${svc}_service/.env.prod" ]; then
    echo "WARNING: ${svc}_service/.env.prod is MISSING!"
  fi
done

# 4. Check Container Health
echo "Current Container Status:"
$DOCKER_CMD -f docker-compose.prod.yml ps

echo "Maintenance Complete."
