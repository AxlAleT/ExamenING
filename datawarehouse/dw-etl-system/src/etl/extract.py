import pandas as pd
from utils.logging import logger
from utils.database import db_connection, fetch_data_as_df
from config.settings import SOURCE_DB_URL, RAW_DATA_PATH
import os
from sqlalchemy import create_engine
import datetime

class DataExtractor:
    def __init__(self, engine=None):
        """Initialize the data extractor.
        
        Args:
            engine: SQLAlchemy engine for source database connection
        """
        if engine is None:
            self.engine = create_engine(SOURCE_DB_URL)
        else:
            self.engine = engine
        
        # Ensure raw data directory exists
        os.makedirs(RAW_DATA_PATH, exist_ok=True)
        
    def extract_customers(self):
        """Extract customer data from source database.
        
        Returns:
            DataFrame: Customer data
        """
        query = """
        SELECT 
            customer_id, 
            CONCAT(first_name, ' ', last_name) as customer_name,
            CASE 
                WHEN DATEDIFF(NOW(), registration_date) > 365 THEN 'Regular'
                WHEN DATEDIFF(NOW(), registration_date) > 180 THEN 'New'
                ELSE 'Beginner'
            END as segment,
            registration_date
        FROM customers
        """
        
        with db_connection(self.engine) as conn:
            logger.info("Extracting customer data")
            df = fetch_data_as_df(conn, query)
            logger.info(f"Extracted {len(df)} customer records")
            
            # Save to CSV
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            output_path = os.path.join(RAW_DATA_PATH, f"customers_{timestamp}.csv")
            df.to_csv(output_path, index=False)
            logger.info(f"Saved customer data to {output_path}")
            
            return df
            
    def extract_restaurants(self):
        """Extract restaurant data from source database.
        
        Returns:
            DataFrame: Restaurant data
        """
        query = """
        SELECT 
            restaurant_id, 
            restaurant_name,
            cuisine_type,
            rating_avg
        FROM restaurants
        """
        
        with db_connection(self.engine) as conn:
            logger.info("Extracting restaurant data")
            df = fetch_data_as_df(conn, query)
            logger.info(f"Extracted {len(df)} restaurant records")
            
            # Save to CSV
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            output_path = os.path.join(RAW_DATA_PATH, f"restaurants_{timestamp}.csv")
            df.to_csv(output_path, index=False)
            logger.info(f"Saved restaurant data to {output_path}")
            
            return df
            
    def extract_days(self):
        """Extract day data from source database.
        
        Returns:
            DataFrame: Day data
        """
        query = """
        SELECT 
            day_id,
            day_name,
            is_weekend,
            is_holiday
        FROM days
        """
        
        with db_connection(self.engine) as conn:
            logger.info("Extracting day data")
            df = fetch_data_as_df(conn, query)
            logger.info(f"Extracted {len(df)} day records")
            
            # Save to CSV
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            output_path = os.path.join(RAW_DATA_PATH, f"days_{timestamp}.csv")
            df.to_csv(output_path, index=False)
            logger.info(f"Saved day data to {output_path}")
            
            return df
            
    def extract_delivery_persons(self):
        """Extract delivery person data from source database.
        
        Returns:
            DataFrame: Delivery person data
        """
        query = """
        SELECT 
            delivery_person_id,
            CONCAT(first_name, ' ', last_name) as delivery_person_name,
            'General' as operation_zone,
            TIMESTAMPDIFF(MONTH, hire_date, CURDATE()) as tenure_months
        FROM delivery_person
        """
        
        with db_connection(self.engine) as conn:
            logger.info("Extracting delivery person data")
            df = fetch_data_as_df(conn, query)
            logger.info(f"Extracted {len(df)} delivery person records")
            
            # Save to CSV
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            output_path = os.path.join(RAW_DATA_PATH, f"delivery_persons_{timestamp}.csv")
            df.to_csv(output_path, index=False)
            logger.info(f"Saved delivery person data to {output_path}")
            
            return df
            
    def extract_orders(self):
        """Extract order data from source database.
        
        Returns:
            DataFrame: Order data
        """
        query = """
        SELECT 
            o.order_id,
            o.customer_id,
            o.restaurant_id,
            o.delivery_person_id,
            o.day_id,
            1 as location_id,  -- Placeholder as location is not in source
            1 as time_slot_id, -- Placeholder as time_slot is not in source
            CURDATE() as order_date,
            CURTIME() as order_time,
            o.cost_of_the_order as order_cost,
            o.rating,
            o.food_preparation_time,
            o.delivery_time,
            (o.food_preparation_time + o.delivery_time) as total_time
        FROM orders o
        """
        
        with db_connection(self.engine) as conn:
            logger.info("Extracting order data")
            df = fetch_data_as_df(conn, query)
            logger.info(f"Extracted {len(df)} order records")
            
            # Save to CSV
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            output_path = os.path.join(RAW_DATA_PATH, f"orders_{timestamp}.csv")
            df.to_csv(output_path, index=False)
            logger.info(f"Saved order data to {output_path}")
            
            return df
    
    def extract_all(self):
        """Extract all data from source database.
        
        Returns:
            dict: Dictionary of all extracted DataFrames
        """
        customers_df = self.extract_customers()
        restaurants_df = self.extract_restaurants()
        days_df = self.extract_days()
        delivery_persons_df = self.extract_delivery_persons()
        orders_df = self.extract_orders()
        
        return {
            'customers': customers_df,
            'restaurants': restaurants_df,
            'days': days_df,
            'delivery_persons': delivery_persons_df,
            'orders': orders_df
        }