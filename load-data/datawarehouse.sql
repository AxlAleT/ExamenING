-- Datawarehouse schema for the star schema model
-- This file creates the structure for the data warehouse database

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS datawarehouse;
USE datawarehouse;

-- Drop tables if they exist (in reverse order of dependency)
DROP TABLE IF EXISTS fact_orders;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_restaurant;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_location;
DROP TABLE IF EXISTS dim_timeslot;
DROP TABLE IF EXISTS dim_deliveryperson;

-- Create dimension tables
CREATE TABLE dim_customer (
  customer_id INT PRIMARY KEY,
  customer_name VARCHAR(255),
  segment VARCHAR(50),
  registration_date DATE
);

CREATE TABLE dim_restaurant (
  restaurant_id INT PRIMARY KEY,
  restaurant_name VARCHAR(255),
  cuisine_type VARCHAR(100),
  rating_avg DECIMAL(3,2)
);

CREATE TABLE dim_date (
  date_id INT PRIMARY KEY,
  full_date DATE,
  day_of_week VARCHAR(20),
  month_name VARCHAR(20),
  quarter INT,
  year INT
);

CREATE TABLE dim_location (
  location_id INT PRIMARY KEY,
  neighborhood VARCHAR(100),
  postal_code VARCHAR(20),
  city VARCHAR(100),
  region VARCHAR(100)
);

CREATE TABLE dim_timeslot (
  time_slot_id INT PRIMARY KEY,
  slot_name VARCHAR(50),
  start_time TIME,
  end_time TIME
);

CREATE TABLE dim_deliveryperson (
  delivery_person_id INT PRIMARY KEY,
  delivery_person_name VARCHAR(255),
  operation_zone VARCHAR(100),
  tenure_months INT
);

-- Create fact table with foreign key relationships
CREATE TABLE fact_orders (
  order_id INT,
  customer_id INT,
  restaurant_id INT,
  delivery_person_id INT,
  date_id INT,
  location_id INT,
  time_slot_id INT,
  order_date DATE,
  order_time TIME,
  order_cost DECIMAL(10,2),
  rating INT,
  food_preparation_time INT,
  delivery_time INT,
  total_time INT,
  PRIMARY KEY (order_id),
  FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
  FOREIGN KEY (restaurant_id) REFERENCES dim_restaurant(restaurant_id),
  FOREIGN KEY (delivery_person_id) REFERENCES dim_deliveryperson(delivery_person_id),
  FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
  FOREIGN KEY (location_id) REFERENCES dim_location(location_id),
  FOREIGN KEY (time_slot_id) REFERENCES dim_timeslot(time_slot_id)
);

-- Create indexes for improved query performance
CREATE INDEX idx_fact_customer ON fact_orders(customer_id);
CREATE INDEX idx_fact_restaurant ON fact_orders(restaurant_id);
CREATE INDEX idx_fact_delivery_person ON fact_orders(delivery_person_id);
CREATE INDEX idx_fact_date ON fact_orders(date_id);
CREATE INDEX idx_fact_location ON fact_orders(location_id);
CREATE INDEX idx_fact_timeslot ON fact_orders(time_slot_id);
CREATE INDEX idx_fact_order_date ON fact_orders(order_date);

-- Create some useful views for common queries

-- View 1: Restaurant performance summary
CREATE VIEW restaurant_performance AS
SELECT 
  r.restaurant_id,
  r.restaurant_name,
  r.cuisine_type,
  COUNT(f.order_id) AS total_orders,
  AVG(f.food_preparation_time) AS avg_preparation_time,
  AVG(f.delivery_time) AS avg_delivery_time,
  AVG(f.rating) AS avg_rating,
  SUM(f.order_cost) AS total_revenue
FROM fact_orders f
JOIN dim_restaurant r ON f.restaurant_id = r.restaurant_id
GROUP BY r.restaurant_id, r.restaurant_name, r.cuisine_type;

-- View 2: Customer order patterns
CREATE VIEW customer_order_patterns AS
SELECT 
  c.customer_id,
  c.customer_name,
  c.segment,
  COUNT(f.order_id) AS total_orders,
  SUM(f.order_cost) AS total_spent,
  AVG(f.order_cost) AS avg_order_value,
  AVG(f.rating) AS avg_rating_given
FROM fact_orders f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.segment;

-- View 3: Delivery performance by zone
CREATE VIEW delivery_performance_by_zone AS
SELECT 
  d.operation_zone,
  COUNT(f.order_id) AS total_deliveries,
  AVG(f.delivery_time) AS avg_delivery_time,
  AVG(f.rating) AS avg_rating
FROM fact_orders f
JOIN dim_deliveryperson d ON f.delivery_person_id = d.delivery_person_id
GROUP BY d.operation_zone;

-- View 4: Order patterns by time
CREATE VIEW time_order_patterns AS
SELECT 
  t.slot_name AS time_period,
  d.day_of_week,
  COUNT(f.order_id) AS total_orders,
  SUM(f.order_cost) AS total_revenue,
  AVG(f.food_preparation_time + f.delivery_time) AS avg_total_time
FROM fact_orders f
JOIN dim_timeslot t ON f.time_slot_id = t.time_slot_id
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY t.slot_name, d.day_of_week
ORDER BY d.day_of_week, t.slot_name;

-- View 5: Cuisine popularity by location
CREATE VIEW cuisine_by_location AS
SELECT 
  l.region,
  l.city,
  r.cuisine_type,
  COUNT(f.order_id) AS order_count,
  SUM(f.order_cost) AS total_revenue
FROM fact_orders f
JOIN dim_location l ON f.location_id = l.location_id
JOIN dim_restaurant r ON f.restaurant_id = r.restaurant_id
GROUP BY l.region, l.city, r.cuisine_type
ORDER BY l.region, l.city, order_count DESC;
