import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Source database configuration
SOURCE_DB_URL = os.getenv("SOURCE_DB_URL", "mysql://root:password@localhost:3306/ordersdb")
SOURCE_DB_NAME = os.getenv("SOURCE_DB_NAME", "ordersdb")
SOURCE_DB_USER = os.getenv("SOURCE_DB_USER", "root")
SOURCE_DB_PASSWORD = os.getenv("SOURCE_DB_PASSWORD", "password")
SOURCE_DB_HOST = os.getenv("SOURCE_DB_HOST", "localhost")
SOURCE_DB_PORT = os.getenv("SOURCE_DB_PORT", "3306")

# Target datawarehouse configuration
DW_DB_URL = os.getenv("DW_DB_URL", "mysql://root:password@localhost:3306/datawarehouse")
DW_DB_NAME = os.getenv("DW_DB_NAME", "datawarehouse")
DW_DB_USER = os.getenv("DW_DB_USER", "root")
DW_DB_PASSWORD = os.getenv("DW_DB_PASSWORD", "password")
DW_DB_HOST = os.getenv("DW_DB_HOST", "localhost")
DW_DB_PORT = os.getenv("DW_DB_PORT", "3306")

# Airflow settings
AIRFLOW_HOME = os.getenv("AIRFLOW_HOME", os.path.expanduser("~/airflow"))

# ETL settings
ETL_BATCH_SIZE = int(os.getenv("ETL_BATCH_SIZE", "1000"))
ETL_RETRY_COUNT = int(os.getenv("ETL_RETRY_COUNT", "3"))

# Logging configuration
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
LOGGING_FORMAT = os.getenv("LOGGING_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "etl.log")

# Data paths
RAW_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "raw")
PROCESSED_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "processed")