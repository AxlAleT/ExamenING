#!/bin/bash

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
until mysql -h db -u root -pexample -e "SELECT 1"; do
  echo "Waiting for MySQL to be available..."
  sleep 5
done

# Create the datawarehouse database if it doesn't exist
echo "Setting up database..."
mysql -h db -u root -pexample -e "CREATE DATABASE IF NOT EXISTS datawarehouse;"

# Run the complete ETL process as a standalone Java application
echo "Running the ETL process..."
java -cp "/app/target/fooddelivery-dw-1.0-SNAPSHOT.jar:/app/target/dependency/*:/app/mysql-connector-java-8.0.28.jar" com.hadoop.aggregation.StandaloneETL

# Keep container running for debugging if needed
if [ "$1" = "keep-alive" ]; then
  echo "Container will stay running for debugging..."
  tail -f /dev/null
fi
