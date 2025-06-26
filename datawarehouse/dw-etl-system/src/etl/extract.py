from typing import List
import pandas as pd

def extract_from_csv(file_path: str) -> pd.DataFrame:
    """Extract data from a CSV file."""
    return pd.read_csv(file_path)

def extract_from_database(query: str, connection) -> pd.DataFrame:
    """Extract data from a database using a SQL query."""
    return pd.read_sql(query, connection)

def extract_from_api(api_url: str) -> List[dict]:
    """Extract data from an API endpoint."""
    import requests
    response = requests.get(api_url)
    response.raise_for_status()
    return response.json()