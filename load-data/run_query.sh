#!/bin/bash

# Script to run queries against the database
# Usage: ./run_query.sh "SELECT * FROM orders LIMIT 10;"

if [ -z "$1" ]; then
    echo "Usage: ./run_query.sh \"YOUR SQL QUERY HERE\""
    echo "Example: ./run_query.sh \"SELECT * FROM orders LIMIT 10;\""
    exit 1
fi

# Run the query
docker exec -it examen-db-1 mysql -uroot -pexample -e "USE ordersdb; $1"
