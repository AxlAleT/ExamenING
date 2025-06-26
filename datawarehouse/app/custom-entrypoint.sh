#!/bin/bash

# If the ETL command is used, run our ETL script
if [ "$1" = "etl" ]; then
    cd /app && python -m src.main
else
    # Otherwise use the default Airflow entrypoint
    exec /entrypoint.sh "$@"
fi
