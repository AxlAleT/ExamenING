#!/usr/bin/env bash

# Build the Docker image if it doesn't exist
if [[ "$(docker images -q etl-app 2> /dev/null)" == "" ]]; then
  echo "Building Docker image..."
  docker build -t etl-app .
fi

# Run the ETL process once
echo "Running ETL process..."
docker run --name etl-run --rm etl-app etl

echo "ETL process completed!"
