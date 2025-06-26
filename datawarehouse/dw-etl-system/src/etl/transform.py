import pandas as pd
import numpy as np
from utils.logging import logger
from config.settings import PROCESSED_DATA_PATH
import os
import datetime
from tqdm import tqdm

class DataTransformer:
    def __init__(self):
        """Initialize the data transformer."""
        # Ensure processed data directory exists
        os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
        
    def transform_customers(self, df):
        """Transform customer data.
        
        Args:
            df (DataFrame): Raw customer data
            
        Returns:
            DataFrame: Transformed customer data
        """
        logger.info("Transforming customer data")
        
        # Copy to avoid modifying the original
        result = df.copy()
        
        # Handle missing values
        result['customer_name'] = result['customer_name'].fillna('Unknown Customer')
        result['segment'] = result['segment'].fillna('Unknown')
        
        # Clean and validate data
        result = result.drop_duplicates(subset=['customer_id'])
        
        # Save to processed folder
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = os.path.join(PROCESSED_DATA_PATH, f"dim_customer_{timestamp}.csv")
        result.to_csv(output_path, index=False)
        logger.info(f"Saved transformed customer data to {output_path}")
        
        return result
        
    def transform_restaurants(self, df):
        """Transform restaurant data.
        
        Args:
            df (DataFrame): Raw restaurant data
            
        Returns:
            DataFrame: Transformed restaurant data
        """
        logger.info("Transforming restaurant data")
        
        # Copy to avoid modifying the original
        result = df.copy()
        
        # Handle missing values
        result['restaurant_name'] = result['restaurant_name'].fillna('Unknown Restaurant')
        result['cuisine_type'] = result['cuisine_type'].fillna('Other')
        result['rating_avg'] = result['rating_avg'].fillna(0)
        
        # Clean and validate data
        result = result.drop_duplicates(subset=['restaurant_id'])
        
        # Save to processed folder
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = os.path.join(PROCESSED_DATA_PATH, f"dim_restaurant_{timestamp}.csv")
        result.to_csv(output_path, index=False)
        logger.info(f"Saved transformed restaurant data to {output_path}")
        
        return result
        
    def transform_days_to_dates(self, df):
        """Transform day data into date dimension.
        
        Args:
            df (DataFrame): Raw day data
            
        Returns:
            DataFrame: Transformed date dimension data
        """
        logger.info("Transforming day data to date dimension")
        
        # Create date dimension with dates for the last 3 years
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(days=365*3)
        
        dates = []
        current_date = start_date
        
        # Map day names to dates
        day_name_map = {
            'Monday': 0,
            'Tuesday': 1,
            'Wednesday': 2,
            'Thursday': 3,
            'Friday': 4,
            'Saturday': 5,
            'Sunday': 6
        }
        
        # Reverse map from day index to name
        day_index_to_name = {v: k for k, v in day_name_map.items()}
        
        # Create date records
        while current_date <= end_date:
            date_id = int(current_date.strftime('%Y%m%d'))
            day_of_week = day_index_to_name[current_date.weekday()]
            month_name = current_date.strftime('%B')
            quarter = (current_date.month - 1) // 3 + 1
            year = current_date.year
            
            # Get weekend status from source data if available
            is_weekend = current_date.weekday() >= 5  # Default assumption
            is_holiday = False  # Default assumption
            
            # Try to get from source data
            day_row = df[df['day_name'] == day_of_week]
            if not day_row.empty:
                is_weekend = day_row.iloc[0]['is_weekend']
                is_holiday = day_row.iloc[0]['is_holiday']
            
            dates.append({
                'date_id': date_id,
                'full_date': current_date,
                'day_of_week': day_of_week,
                'month_name': month_name,
                'quarter': quarter,
                'year': year,
                'is_weekend': is_weekend,
                'is_holiday': is_holiday
            })
            
            current_date += datetime.timedelta(days=1)
        
        result = pd.DataFrame(dates)
        
        # Save to processed folder
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = os.path.join(PROCESSED_DATA_PATH, f"dim_date_{timestamp}.csv")
        result.to_csv(output_path, index=False)
        logger.info(f"Saved transformed date data to {output_path}")
        
        return result
        
    def create_location_dimension(self):
        """Create a location dimension.
        
        Returns:
            DataFrame: Location dimension data
        """
        logger.info("Creating location dimension")
        
        # Create a basic location dimension
        locations = [
            {
                'location_id': 1,
                'neighborhood': 'Downtown',
                'postal_code': '10001',
                'city': 'New York',
                'region': 'Northeast'
            },
            {
                'location_id': 2,
                'neighborhood': 'Midtown',
                'postal_code': '10002',
                'city': 'New York',
                'region': 'Northeast'
            },
            {
                'location_id': 3,
                'neighborhood': 'Financial District',
                'postal_code': '10003',
                'city': 'New York',
                'region': 'Northeast'
            }
        ]
        
        result = pd.DataFrame(locations)
        
        # Save to processed folder
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = os.path.join(PROCESSED_DATA_PATH, f"dim_location_{timestamp}.csv")
        result.to_csv(output_path, index=False)
        logger.info(f"Saved location dimension data to {output_path}")
        
        return result
        
    def create_timeslot_dimension(self):
        """Create a time slot dimension.
        
        Returns:
            DataFrame: Time slot dimension data
        """
        logger.info("Creating time slot dimension")
        
        # Create time slots for every hour
        timeslots = []
        
        for hour in range(24):
            start_time = datetime.time(hour, 0)
            end_time = datetime.time((hour + 1) % 24, 0)
            
            # Determine slot name
            if 6 <= hour < 11:
                slot_name = 'Breakfast'
            elif 11 <= hour < 15:
                slot_name = 'Lunch'
            elif 15 <= hour < 18:
                slot_name = 'Afternoon'
            elif 18 <= hour < 22:
                slot_name = 'Dinner'
            else:
                slot_name = 'Late Night'
                
            timeslots.append({
                'time_slot_id': hour + 1,
                'slot_name': slot_name,
                'start_time': start_time,
                'end_time': end_time
            })
            
        result = pd.DataFrame(timeslots)
        
        # Save to processed folder
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = os.path.join(PROCESSED_DATA_PATH, f"dim_timeslot_{timestamp}.csv")
        result.to_csv(output_path, index=False)
        logger.info(f"Saved time slot dimension data to {output_path}")
        
        return result
        
    def transform_delivery_persons(self, df):
        """Transform delivery person data.
        
        Args:
            df (DataFrame): Raw delivery person data
            
        Returns:
            DataFrame: Transformed delivery person data
        """
        logger.info("Transforming delivery person data")
        
        # Copy to avoid modifying the original
        result = df.copy()
        
        # Handle missing values
        result['delivery_person_name'] = result['delivery_person_name'].fillna('Unknown Driver')
        result['operation_zone'] = result['operation_zone'].fillna('General')
        result['tenure_months'] = result['tenure_months'].fillna(0)
        
        # Clean and validate data
        result = result.drop_duplicates(subset=['delivery_person_id'])
        
        # Save to processed folder
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = os.path.join(PROCESSED_DATA_PATH, f"dim_deliveryperson_{timestamp}.csv")
        result.to_csv(output_path, index=False)
        logger.info(f"Saved transformed delivery person data to {output_path}")
        
        return result
        
    def transform_orders(self, df, date_df):
        """Transform order data.
        
        Args:
            df (DataFrame): Raw order data
            date_df (DataFrame): Date dimension for mapping
            
        Returns:
            DataFrame: Transformed order data
        """
        logger.info("Transforming order data")
        
        # Copy to avoid modifying the original
        result = df.copy()
        
        # Handle missing values
        result['order_cost'] = result['order_cost'].fillna(0)
        result['rating'] = result['rating'].fillna(None)
        result['food_preparation_time'] = result['food_preparation_time'].fillna(0)
        result['delivery_time'] = result['delivery_time'].fillna(0)
        result['total_time'] = result['total_time'].fillna(0)
        
        # Map day_id to date_id using current date
        today = datetime.datetime.now().date()
        today_str = today.strftime('%Y%m%d')
        date_id = int(today_str)
        
        # Set default date_id for all orders (can be improved with actual date logic)
        result['date_id'] = date_id
        
        # Fill in random time slots
        result['time_slot_id'] = np.random.randint(1, 25, size=len(result))
        
        # Clean and validate data
        result = result.drop_duplicates(subset=['order_id'])
        
        # Ensure data types
        result['order_cost'] = result['order_cost'].astype(float)
        result['food_preparation_time'] = result['food_preparation_time'].astype(int)
        result['delivery_time'] = result['delivery_time'].astype(int)
        result['total_time'] = result['total_time'].astype(int)
        
        # Save to processed folder
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = os.path.join(PROCESSED_DATA_PATH, f"fact_orders_{timestamp}.csv")
        result.to_csv(output_path, index=False)
        logger.info(f"Saved transformed order data to {output_path}")
        
        return result
    
    def transform_all(self, extracted_data):
        """Transform all extracted data.
        
        Args:
            extracted_data (dict): Dictionary with all extracted DataFrames
            
        Returns:
            dict: Dictionary with all transformed DataFrames
        """
        # Transform dimensions
        dim_customer = self.transform_customers(extracted_data['customers'])
        dim_restaurant = self.transform_restaurants(extracted_data['restaurants'])
        dim_date = self.transform_days_to_dates(extracted_data['days'])
        dim_location = self.create_location_dimension()
        dim_timeslot = self.create_timeslot_dimension()
        dim_deliveryperson = self.transform_delivery_persons(extracted_data['delivery_persons'])
        
        # Transform facts
        fact_orders = self.transform_orders(extracted_data['orders'], dim_date)
        
        return {
            'dim_customer': dim_customer,
            'dim_restaurant': dim_restaurant,
            'dim_date': dim_date,
            'dim_location': dim_location,
            'dim_timeslot': dim_timeslot,
            'dim_deliveryperson': dim_deliveryperson,
            'fact_orders': fact_orders
        }