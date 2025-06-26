import pandas as pd
from sqlalchemy import create_engine, text
from contextlib import contextmanager
from utils.logging import logger

def get_database_engine(db_url):
    """Create and return a SQLAlchemy engine.
    
    Args:
        db_url (str): Database connection URL
        
    Returns:
        Engine: SQLAlchemy engine object
    """
    try:
        engine = create_engine(db_url)
        logger.info(f"Successfully created database engine for {db_url.split('@')[-1]}")
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {str(e)}")
        raise

@contextmanager
def db_connection(engine):
    """Context manager for database connections.
    
    Args:
        engine (Engine): SQLAlchemy engine
        
    Yields:
        Connection: SQLAlchemy connection object
    """
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()

def execute_query(connection, query, params=None):
    """Execute a SQL query.
    
    Args:
        connection (Connection): SQLAlchemy connection
        query (str): SQL query to execute
        params (dict, optional): Parameters for the query
        
    Returns:
        Result: Query execution result
    """
    try:
        if params:
            result = connection.execute(text(query), params)
        else:
            result = connection.execute(text(query))
        return result
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        logger.error(f"Query: {query}")
        if params:
            logger.error(f"Params: {params}")
        raise

def fetch_data_as_df(connection, query, params=None):
    """Execute a query and return results as a pandas DataFrame.
    
    Args:
        connection (Connection): SQLAlchemy connection
        query (str): SQL query to execute
        params (dict, optional): Parameters for the query
        
    Returns:
        DataFrame: Query results as pandas DataFrame
    """
    try:
        result = execute_query(connection, query, params)
        df = pd.DataFrame(result.fetchall())
        if not df.empty:
            df.columns = result.keys()
        return df
    except Exception as e:
        logger.error(f"Failed to fetch data as DataFrame: {str(e)}")
        raise