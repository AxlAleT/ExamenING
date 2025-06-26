#!/usr/bin/env bash

# Stop and remove the Airflow webserver container
echo "Stopping Airflow webserver..."
docker stop etl-webserver || true
docker rm etl-webserver || true

# Stop and remove the Airflow scheduler container
echo "Stopping Airflow scheduler..."
docker stop etl-scheduler || true
docker rm etl-scheduler || true

echo "Containers stopped and removed!"
