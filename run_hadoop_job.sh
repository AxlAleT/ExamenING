#!/bin/bash

# Script to build and run the containerized Hadoop job

# Set directory paths
JAVA_DIR="$(pwd)/java"
LOAD_DATA_DIR="$(pwd)/load-data"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose - could be standalone or plugin
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

# Step 1: Build and start the containers using the official Apache Hadoop image
echo "Building and starting the containers..."
cd $JAVA_DIR
$DOCKER_COMPOSE_CMD build
$DOCKER_COMPOSE_CMD up -d

# Step 2: Wait for the Hadoop job to complete
echo "The Hadoop job is running in the background..."
echo "You can check the logs with: $DOCKER_COMPOSE_CMD logs -f hadoop"

# Step 3: Show instructions for viewing the results
echo ""
echo "To check if the data was exported to MySQL, you can run:"
echo "docker exec -it java-db-1 mysql -u root -pexample -e 'USE datawarehouse; SHOW TABLES;'"
echo ""
echo "To query the star schema, you can run:"
echo "docker exec -it java-db-1 mysql -u root -pexample -e 'USE datawarehouse; SELECT * FROM fact_orders LIMIT 10;'"
echo ""
echo "To access the Hadoop web interfaces:"
echo "- NameNode: http://localhost:9870"
echo "- ResourceManager: http://localhost:8088"
echo ""
echo "To stop the containers, run: $DOCKER_COMPOSE_CMD down"
