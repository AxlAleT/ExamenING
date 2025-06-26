#!/usr/bin/env bash

# This script initializes the Airflow environment

# Set up Airflow home
export AIRFLOW_HOME=${AIRFLOW_HOME:-~/airflow}
echo "Airflow home set to: $AIRFLOW_HOME"

# Initialize Airflow database
echo "Initializing Airflow database..."
airflow db init

# Create Airflow admin user if it doesn't exist
if ! airflow users list | grep -q "admin"; then
    echo "Creating Airflow admin user..."
    airflow users create \
      --username admin \
      --firstname Admin \
      --lastname User \
      --role Admin \
      --email admin@example.com \
      --password admin
fi

# Create symbolic link to DAGs directory if it doesn't exist
if [ ! -L "$AIRFLOW_HOME/dags/etl_order_datawarehouse.py" ]; then
    echo "Creating symbolic link to DAGs..."
    mkdir -p "$AIRFLOW_HOME/dags"
    ln -sf "$(pwd)/dags/etl_order_datawarehouse.py" "$AIRFLOW_HOME/dags/etl_order_datawarehouse.py"
fi

echo "Airflow initialization complete!"
echo "To start Airflow webserver: airflow webserver -p 8080"
echo "To start Airflow scheduler: airflow scheduler"
