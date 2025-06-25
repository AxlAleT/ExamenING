#!/bin/bash

# Script to rebuild and initialize the database
# Usage: ./reset_db.sh

echo "Stopping any running containers..."
docker compose down

# If you want to completely wipe the volume data, uncomment the next line
# docker volume rm examen_mysql_data

echo "Rebuilding and starting containers..."
docker compose up --build -d

# Wait for MySQL to start (adjust timeout as needed)
echo "Waiting for MySQL to start... (30 seconds)"
sleep 30

# Check if MySQL is responsive
echo "Checking MySQL connection..."
docker exec -it examen-db-1 mysqladmin -uroot -pexample ping

if [ $? -eq 0 ]; then
    echo "MySQL is running. Checking data..."
    
    # Check if data was loaded properly
    docker exec -it examen-db-1 mysql -uroot -pexample -e "
    USE ordersdb;
    SELECT 'Customers' as 'Table', COUNT(*) as 'Count' FROM customers
    UNION
    SELECT 'Days', COUNT(*) FROM days
    UNION
    SELECT 'Restaurants', COUNT(*) FROM restaurants
    UNION
    SELECT 'Orders', COUNT(*) FROM orders;
    "
    
    echo "Database initialization complete!"
else
    echo "Error: MySQL is not responding. You may need to check the logs:"
    docker logs examen-db-1
fi

# Optional: Display sample data from each table
echo "Displaying sample data from tables..."
docker exec -it examen-db-1 mysql -uroot -pexample -e "
USE ordersdb;
SELECT 'Days' as 'Table';
SELECT * FROM days;
SELECT 'Sample Restaurants' as 'Table';
SELECT * FROM restaurants LIMIT 5;
SELECT 'Sample Orders' as 'Table';
SELECT * FROM orders LIMIT 5;
"
