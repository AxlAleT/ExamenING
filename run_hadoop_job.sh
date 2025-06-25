#!/bin/bash

# Script to build and run the containerized Hadoop job

# Set directory paths
JAVA_DIR="$(pwd)/java"
LOAD_DATA_DIR="$(pwd)/load-data"

# Check if Maven is installed
if ! command -v mvn &> /dev/null; then
    echo "Maven is not installed. Please install Maven first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Step 1: Build the Maven project
echo "Building the Maven project..."
cd $JAVA_DIR
mvn clean package dependency:copy-dependencies

# Step 2: Create directory for Hadoop configuration files
mkdir -p hadoop-config

# Step 3: Build and start the containers
echo "Building and starting the containers..."
docker-compose build
docker-compose up -d

# Step 4: Wait for the Hadoop job to complete
echo "The Hadoop job is running in the background..."
echo "You can check the logs with: docker-compose logs -f hadoop"

# Step 5: Show instructions for viewing the results
echo ""
echo "To check if the data was exported to MySQL, you can run:"
echo "docker exec -it java_db_1 mysql -u root -pexample -e 'USE datawarehouse; SHOW TABLES;'"
echo ""
echo "To query the star schema, you can run:"
echo "docker exec -it java_db_1 mysql -u root -pexample -e 'USE datawarehouse; SELECT * FROM fact_orders LIMIT 10;'"
echo ""
echo "To access the Hadoop web interfaces:"
echo "- NameNode: http://localhost:9870"
echo "- ResourceManager: http://localhost:8088"
echo ""
echo "To stop the containers, run: docker-compose down"
