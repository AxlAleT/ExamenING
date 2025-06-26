#!/bin/bash

# Script to clean up Docker containers and start fresh

# Determine Docker Compose command
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
echo "Using Docker Compose command: $DOCKER_COMPOSE_CMD"

# Stop and remove existing containers
echo "Stopping and removing existing containers..."
cd /home/axltorres/Repo/Examen/java
$DOCKER_COMPOSE_CMD down

# Remove any existing volumes
echo "Removing existing volumes..."
docker volume rm java_mysql_data java_hadoop_data 2>/dev/null || true

# Build and start containers
echo "Building and starting containers from scratch..."
cd /home/axltorres/Repo/Examen
./run_hadoop_job.sh
