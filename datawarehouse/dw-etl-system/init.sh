#!/usr/bin/env bash

# This script initializes the environment for the ETL system

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -e .

# Create necessary directories if they don't exist
mkdir -p data/raw
mkdir -p data/processed
mkdir -p logs
mkdir -p dags

# Set up Airflow home
export AIRFLOW_HOME=${AIRFLOW_HOME:-~/airflow}
echo "Airflow home set to: $AIRFLOW_HOME"

# Create symbolic link to DAGs directory if it doesn't exist
if [ ! -L "$AIRFLOW_HOME/dags/etl_order_datawarehouse.py" ]; then
    echo "Creating symbolic link to DAGs..."
    mkdir -p "$AIRFLOW_HOME/dags"
    ln -sf "$(pwd)/dags/etl_order_datawarehouse.py" "$AIRFLOW_HOME/dags/etl_order_datawarehouse.py"
fi

echo "Initialization complete! You can now start using the ETL system."
echo "To run the ETL process directly: python -m src.main"
echo "To start Airflow: airflow webserver -p 8080 & airflow scheduler"
