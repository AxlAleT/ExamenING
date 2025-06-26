#!/bin/bash

# Start SSH service (required for Hadoop)
service ssh start

# Create data directories if they don't exist
mkdir -p /hadoop/dfs/name
mkdir -p /hadoop/dfs/data

# Format namenode if not already formatted
if [ ! -d "/hadoop/dfs/name/current" ]; then
  echo "Formatting namenode..."
  $HADOOP_HOME/bin/hdfs namenode -format
fi

# Start Hadoop services
echo "Starting Hadoop services..."
$HADOOP_HOME/sbin/start-dfs.sh
$HADOOP_HOME/sbin/start-yarn.sh
$HADOOP_HOME/sbin/mr-jobhistory-daemon.sh start historyserver

# Wait for namenode to be up
echo "Waiting for namenode to be available..."
until $HADOOP_HOME/bin/hdfs dfsadmin -safemode get | grep "Safe mode is OFF"; do
  echo "Waiting for namenode to leave safe mode..."
  sleep 5
  $HADOOP_HOME/bin/hdfs dfsadmin -safemode leave || true
done

# Create HDFS directories if they don't exist
echo "Creating HDFS directories..."
$HADOOP_HOME/bin/hdfs dfs -mkdir -p /warehouse/fooddelivery
$HADOOP_HOME/bin/hdfs dfs -mkdir -p /warehouse/fooddelivery/results
$HADOOP_HOME/bin/hdfs dfs -chmod -R 777 /warehouse

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
# Try mysql command, and if not available, try the mariadb-client command
if command -v mysql >/dev/null 2>&1; then
    until mysql -h db -u root -pexample -e "SELECT 1"; do
        echo "Waiting for MySQL to be available..."
        sleep 5
    done
else
    echo "MySQL client not found, looking for alternative clients..."
    if command -v mariadb >/dev/null 2>&1; then
        until mariadb -h db -u root -pexample -e "SELECT 1"; do
            echo "Waiting for MySQL to be available..."
            sleep 5
        done
    else
        echo "No MySQL client found. Cannot connect to database."
        exit 1
    fi
fi

# Create the datawarehouse database if it doesn't exist
echo "Setting up database..."
if command -v mysql >/dev/null 2>&1; then
    mysql -h db -u root -pexample -e "CREATE DATABASE IF NOT EXISTS datawarehouse;"
else
    mariadb -h db -u root -pexample -e "CREATE DATABASE IF NOT EXISTS datawarehouse;"
fi

# Run the complete ETL process
echo "Running the complete ETL process..."
java -cp "/app/target/fooddelivery-dw-1.0-SNAPSHOT.jar:/app/target/dependency/*" com.hadoop.aggregation.AggregationDriver run-complete-etl

# Keep container running for debugging if needed
if [ "$1" = "keep-alive" ]; then
  echo "Container will stay running for debugging..."
  tail -f /dev/null
fi
