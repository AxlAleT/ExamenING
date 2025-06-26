from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.mysql_operator import MySqlOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook

import sys
import os

# Add the project directory to the path
sys.path.append('/home/axltorres/Repo/Examen/datawarehouse/dw-etl-system')

# Import our ETL classes
from src.etl.extract import DataExtractor
from src.etl.transform import DataTransformer
from src.etl.load import DataLoader
from src.utils.logging import logger

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'etl_order_datawarehouse',
    default_args=default_args,
    description='ETL process for Orders Data Warehouse',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 6, 25),
    catchup=False,
    tags=['etl', 'datawarehouse', 'orders'],
)

# Define functions for each step of the ETL process
def extract_data(**kwargs):
    """Extract data from source database."""
    logger.info("Starting data extraction")
    extractor = DataExtractor()
    extracted_data = extractor.extract_all()
    
    # Return the file paths for the next task
    return {
        'extracted_data': extracted_data,
    }

def transform_data(**kwargs):
    """Transform the extracted data."""
    logger.info("Starting data transformation")
    ti = kwargs['ti']
    
    # Get the extracted data from the previous task
    extracted_data = ti.xcom_pull(task_ids='extract_task', key='extracted_data')
    
    # Transform the data
    transformer = DataTransformer()
    transformed_data = transformer.transform_all(extracted_data)
    
    return {
        'transformed_data': transformed_data,
    }

def load_data(**kwargs):
    """Load the transformed data into the data warehouse."""
    logger.info("Starting data loading")
    ti = kwargs['ti']
    
    # Get the transformed data from the previous task
    transformed_data = ti.xcom_pull(task_ids='transform_task', key='transformed_data')
    
    # Load the data
    loader = DataLoader()
    success = loader.load_all(transformed_data)
    
    if success:
        logger.info("Data loading completed successfully")
    else:
        logger.error("Data loading failed")
        raise Exception("Data loading failed")

def create_schema(**kwargs):
    """Create the data warehouse schema."""
    logger.info("Creating schema")
    loader = DataLoader()
    success = loader.create_schema()
    
    if not success:
        raise Exception("Schema creation failed")

# Define the tasks
create_schema_task = PythonOperator(
    task_id='create_schema_task',
    python_callable=create_schema,
    provide_context=True,
    dag=dag,
)

extract_task = PythonOperator(
    task_id='extract_task',
    python_callable=extract_data,
    provide_context=True,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_task',
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_task',
    python_callable=load_data,
    provide_context=True,
    dag=dag,
)

# Define the task dependencies
create_schema_task >> extract_task >> transform_task >> load_task
