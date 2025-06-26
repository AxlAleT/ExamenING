#!/usr/bin/env bash

# Build the Docker image
docker build -t etl-app .

# Run the ETL process once
echo "Running ETL process..."
docker run --name etl-run --rm etl-app etl

# Run the Airflow webserver in detached mode
echo "Starting Airflow webserver..."
docker run -d --name etl-webserver -p 8080:8080 etl-app webserver

# Run the Airflow scheduler in detached mode
echo "Starting Airflow scheduler..."
docker run -d --name etl-scheduler etl-app scheduler

echo "Containers started!"
echo "Access Airflow at http://localhost:8080"
echo "Username: admin"
echo "Password: admin"
