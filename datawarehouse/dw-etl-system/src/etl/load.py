import pandas as pd
from sqlalchemy import create_engine, text
from utils.logging import logger
from utils.database import db_connection, execute_query
from config.settings import DW_DB_URL, ETL_BATCH_SIZE
from tqdm import tqdm
import time

class DataLoader:
    def __init__(self, engine=None):
        """Initialize the data loader.
        
        Args:
            engine: SQLAlchemy engine for data warehouse connection
        """
        if engine is None:
            self.engine = create_engine(DW_DB_URL)
        else:
            self.engine = engine
    
    def load_dimension_table(self, df, table_name, if_exists='replace'):
        """Load data into a dimension table.
        
        Args:
            df (DataFrame): Data to load
            table_name (str): Target table name
            if_exists (str): How to handle existing data ('replace', 'append', 'fail')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Loading {len(df)} rows into {table_name}")
            
            # Load data in batches to avoid memory issues
            batch_size = ETL_BATCH_SIZE
            num_batches = (len(df) + batch_size - 1) // batch_size
            
            for i in tqdm(range(num_batches), desc=f"Loading {table_name}"):
                start_idx = i * batch_size
                end_idx = min((i + 1) * batch_size, len(df))
                batch = df.iloc[start_idx:end_idx]
                
                batch.to_sql(
                    table_name, 
                    self.engine, 
                    if_exists='append' if i > 0 else if_exists, 
                    index=False,
                    chunksize=1000
                )
                
                # Small delay to prevent overwhelming the database
                time.sleep(0.1)
                
            logger.info(f"Successfully loaded data into {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data into {table_name}: {str(e)}")
            return False
    
    def load_fact_table(self, df, table_name='fact_orders', if_exists='replace'):
        """Load data into the fact table.
        
        Args:
            df (DataFrame): Data to load
            table_name (str): Target table name
            if_exists (str): How to handle existing data ('replace', 'append', 'fail')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Loading {len(df)} rows into {table_name}")
            
            # Load data in batches to avoid memory issues
            batch_size = ETL_BATCH_SIZE
            num_batches = (len(df) + batch_size - 1) // batch_size
            
            for i in tqdm(range(num_batches), desc=f"Loading {table_name}"):
                start_idx = i * batch_size
                end_idx = min((i + 1) * batch_size, len(df))
                batch = df.iloc[start_idx:end_idx]
                
                batch.to_sql(
                    table_name, 
                    self.engine, 
                    if_exists='append' if i > 0 else if_exists, 
                    index=False,
                    chunksize=1000
                )
                
                # Small delay to prevent overwhelming the database
                time.sleep(0.1)
                
            logger.info(f"Successfully loaded data into {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data into {table_name}: {str(e)}")
            return False
    
    def create_schema(self, schema_file='/home/axltorres/Repo/Examen/datawarehouse/dw-etl-system/src/schema/datawarehouse.sql'):
        """Create the data warehouse schema using the SQL file.
        
        Args:
            schema_file (str): Path to the SQL schema file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Creating schema from {schema_file}")
            
            # Read the SQL file
            with open(schema_file, 'r') as f:
                sql = f.read()
                
            # Split the SQL statements
            statements = sql.split(';')
            
            # Execute each statement
            with db_connection(self.engine) as conn:
                for statement in statements:
                    if statement.strip():
                        execute_query(conn, statement)
                        
            logger.info("Successfully created schema")
            return True
            
        except Exception as e:
            logger.error(f"Error creating schema: {str(e)}")
            return False
    
    def load_all_dimensions(self, transformed_data):
        """Load all dimension tables.
        
        Args:
            transformed_data (dict): Dictionary with all transformed DataFrames
            
        Returns:
            bool: True if all successful, False otherwise
        """
        success = True
        
        # Load dimensions
        success &= self.load_dimension_table(transformed_data['dim_customer'], 'dim_customer')
        success &= self.load_dimension_table(transformed_data['dim_restaurant'], 'dim_restaurant')
        success &= self.load_dimension_table(transformed_data['dim_date'], 'dim_date')
        success &= self.load_dimension_table(transformed_data['dim_location'], 'dim_location')
        success &= self.load_dimension_table(transformed_data['dim_timeslot'], 'dim_timeslot')
        success &= self.load_dimension_table(transformed_data['dim_deliveryperson'], 'dim_deliveryperson')
        
        return success
    
    def load_all(self, transformed_data):
        """Load all tables.
        
        Args:
            transformed_data (dict): Dictionary with all transformed DataFrames
            
        Returns:
            bool: True if all successful, False otherwise
        """
        # Create schema
        schema_success = self.create_schema()
        if not schema_success:
            logger.error("Failed to create schema, aborting load")
            return False
        
        # Load dimensions
        dim_success = self.load_all_dimensions(transformed_data)
        if not dim_success:
            logger.error("Failed to load some dimensions, continuing with fact table")
        
        # Load fact table
        fact_success = self.load_fact_table(transformed_data['fact_orders'], 'fact_orders')
        
        return fact_success