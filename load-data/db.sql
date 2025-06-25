-- Enable error logging and secure file handling
SET GLOBAL log_error_verbosity = 3;
SET GLOBAL general_log = 'ON';
SET GLOBAL local_infile = 1;

CREATE DATABASE IF NOT EXISTS ordersdb;
USE ordersdb;

-- Drop tables if they exist (in reverse order of dependency)
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS stagingOrders;
DROP TABLE IF EXISTS delivery_person;
DROP TABLE IF EXISTS restaurants;
DROP TABLE IF EXISTS days;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
  customer_id INT PRIMARY KEY,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  email VARCHAR(255),
  phone VARCHAR(20),
  address VARCHAR(255),
  city VARCHAR(100),
  registration_date DATE
);

CREATE TABLE restaurants (
  restaurant_id INT AUTO_INCREMENT PRIMARY KEY,
  restaurant_name VARCHAR(255),
  cuisine_type VARCHAR(100),
  address VARCHAR(255),
  city VARCHAR(100),
  phone VARCHAR(20),
  website VARCHAR(255),
  price_range VARCHAR(10),
  rating_avg DECIMAL(3,2),
  opening_hour TIME,
  closing_hour TIME,
  established_date DATE
);

CREATE TABLE days (
  day_id INT AUTO_INCREMENT PRIMARY KEY,
  day_name VARCHAR(50),
  is_weekend BOOLEAN,
  is_holiday BOOLEAN
);

CREATE TABLE delivery_person (
  delivery_person_id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  phone VARCHAR(20),
  email VARCHAR(255),
  vehicle_type ENUM('car', 'motorcycle', 'bicycle', 'scooter', 'on foot'),
  hire_date DATE,
  rating DECIMAL(3,2)
);

CREATE TABLE orders (
  order_id INT,
  customer_id INT,
  restaurant_id INT,
  day_id INT,
  cost_of_the_order DECIMAL(6,2),
  rating INT,
  food_preparation_time INT,
  delivery_time INT,
  delivery_person_id INT,
  tip_amount DECIMAL(5,2),
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
  FOREIGN KEY (day_id) REFERENCES days(day_id),
  FOREIGN KEY (delivery_person_id) REFERENCES delivery_person(delivery_person_id)
);

-- Create a staging table matching the CSV structure
CREATE TABLE IF NOT EXISTS stagingOrders (
  order_id INT,
  customer_id INT,
  restaurant_name VARCHAR(255),
  cuisine_type VARCHAR(100),
  cost_of_the_order DECIMAL(10,2),
  day_of_the_week VARCHAR(50),
  rating VARCHAR(50),
  food_preparation_time INT,
  delivery_time INT
);

-- Load data into the staging table
LOAD DATA LOCAL INFILE '/docker-entrypoint-initdb.d/unnormalized.csv'
INTO TABLE stagingOrders
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

-- Insert distinct customers
INSERT IGNORE INTO customers (customer_id)
SELECT DISTINCT so.customer_id
FROM stagingOrders so;

-- Insert distinct restaurants
INSERT IGNORE INTO restaurants (restaurant_name, cuisine_type)
SELECT DISTINCT so.restaurant_name, so.cuisine_type
FROM stagingOrders so;

-- Insert distinct days
INSERT IGNORE INTO days (day_name)
SELECT DISTINCT so.day_of_the_week
FROM stagingOrders so;

-- Insert orders referencing dimension IDs
INSERT IGNORE INTO orders (
  order_id, customer_id, restaurant_id, day_id, cost_of_the_order,
  rating, food_preparation_time, delivery_time
)
SELECT
  so.order_id,
  so.customer_id,
  r.restaurant_id,
  d.day_id,
  so.cost_of_the_order,
  CASE 
    WHEN so.rating = 'Not given' THEN NULL 
    ELSE CAST(so.rating AS SIGNED) 
  END as rating,
  so.food_preparation_time,
  so.delivery_time
FROM stagingOrders so
JOIN restaurants r
  ON so.restaurant_name = r.restaurant_name
  AND so.cuisine_type = r.cuisine_type
JOIN days d
  ON so.day_of_the_week = d.day_name;

-- Optional: Drop the staging table when done
DROP TABLE stagingOrders;