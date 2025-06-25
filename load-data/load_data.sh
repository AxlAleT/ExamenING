#!/bin/bash

# Stop and remove containers
docker compose down

# Rebuild and start containers
docker compose up --build -d

# Wait for MySQL to be ready
echo "Waiting for MySQL to start..."
sleep 15

# Check if the data was loaded
docker exec -it examen-db-1 mysql -uroot -pexample -e "USE ordersdb; SHOW TABLES; SELECT COUNT(*) FROM stagingOrders;"

# If the staging table is empty, manually load the data
docker exec -it examen-db-1 mysql -uroot -pexample -e "USE ordersdb; 
SET GLOBAL local_infile=1; 
SHOW VARIABLES LIKE 'local_infile'; 
SHOW VARIABLES LIKE 'secure_file_priv';"

# Copy the CSV file to the container
docker cp ./utils-python/unnormalized.csv examen-db-1:/tmp/

# Load the data directly
docker exec -it examen-db-1 mysql -uroot -pexample --local-infile=1 -e "USE ordersdb; 
LOAD DATA LOCAL INFILE '/tmp/unnormalized.csv' 
INTO TABLE stagingOrders 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '\"' 
LINES TERMINATED BY '\n' 
IGNORE 1 LINES;"

# Check if the data was loaded now
docker exec -it examen-db-1 mysql -uroot -pexample -e "USE ordersdb; 
SELECT COUNT(*) FROM stagingOrders; 
INSERT IGNORE INTO customers (customer_id) SELECT DISTINCT so.customer_id FROM stagingOrders so;
INSERT IGNORE INTO days (day_name) SELECT DISTINCT so.day_of_the_week FROM stagingOrders so;
INSERT IGNORE INTO restaurants (restaurant_name, cuisine_type) SELECT DISTINCT so.restaurant_name, so.cuisine_type FROM stagingOrders so;
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM days;
SELECT COUNT(*) FROM restaurants;"
