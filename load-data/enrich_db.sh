#!/bin/bash

# Script to enrich the food order database with realistic data

# Define default values
DB_HOST="localhost"
DB_USER="root"
DB_PASSWORD="example"
DB_NAME="ordersdb"

# Display a welcome message
echo "==============================================="
echo "Food Order Database Enrichment Tool"
echo "==============================================="
echo "This script will add realistic customer, restaurant,"
echo "delivery person data, and more to your database."
echo

# Install required Python packages if not already installed
echo "Installing required Python packages..."
pip install -r requirements.txt

# Run the Python enrichment script
echo
echo "Starting database enrichment process..."
python utils-python/table_enricher.py --host "$DB_HOST" --user "$DB_USER" --password "$DB_PASSWORD" --database "$DB_NAME"

echo
echo "Enrichment process completed."
echo "Check your database to see the new realistic data!"
echo "==============================================="
