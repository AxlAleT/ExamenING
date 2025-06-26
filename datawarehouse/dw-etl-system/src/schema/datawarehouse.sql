-- filepath: /dw-etl-system/dw-etl-system/src/schema/datawarehouse.sql
DROP TABLE IF EXISTS fact_orders;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_restaurant;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_location;
DROP TABLE IF EXISTS dim_timeslot;
DROP TABLE IF EXISTS dim_deliveryperson;

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