#!/usr/bin/env bash

# This script deploys the ETL application to a Docker container

# Exit on any error
set -e

echo "Deploying ETL Application..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t etl-app .

# Test MySQL connection
echo "Testing MySQL connection..."
# Extracting MySQL credentials from .env
source <(grep -E "SOURCE_DB_HOST|SOURCE_DB_PORT|SOURCE_DB_USER|SOURCE_DB_PASSWORD|SOURCE_DB_NAME" .env | sed 's/^/export /')

# Check if MySQL is accessible (using a temporary container)
if ! docker run --rm mysql:8.0 mysql -h "$SOURCE_DB_HOST" -P "$SOURCE_DB_PORT" -u "$SOURCE_DB_USER" -p"$SOURCE_DB_PASSWORD" "$SOURCE_DB_NAME" -e "SELECT 1;" &> /dev/null; then
    echo "Warning: Cannot connect to source MySQL database. Please check your .env configuration."
    echo "Continuing with deployment, but ETL process might fail..."
fi

# Create a Docker network if it doesn't exist
NETWORK_NAME="etl-network"
if ! docker network inspect "$NETWORK_NAME" &> /dev/null; then
    echo "Creating Docker network: $NETWORK_NAME"
    docker network create "$NETWORK_NAME"
fi

# Stop and remove existing containers if they exist
echo "Stopping existing containers..."
docker stop etl-webserver etl-scheduler 2>/dev/null || true
docker rm etl-webserver etl-scheduler 2>/dev/null || true

# Deploy the Airflow webserver
echo "Deploying Airflow webserver..."
docker run -d \
    --name etl-webserver \
    --network "$NETWORK_NAME" \
    -p 8080:8080 \
    -e AIRFLOW__CORE__LOAD_EXAMPLES=False \
    etl-app webserver

# Deploy the Airflow scheduler
echo "Deploying Airflow scheduler..."
docker run -d \
    --name etl-scheduler \
    --network "$NETWORK_NAME" \
    -e AIRFLOW__CORE__LOAD_EXAMPLES=False \
    etl-app scheduler

echo "Deployment completed successfully!"
echo "Airflow UI is available at: http://localhost:8080"
echo "Username: admin"
echo "Password: admin"
echo ""
echo "To run the ETL process manually:"
echo "  docker run --rm --network $NETWORK_NAME etl-app etl"
echo ""
echo "To stop the containers:"
echo "  docker stop etl-webserver etl-scheduler"
echo "  docker rm etl-webserver etl-scheduler"
