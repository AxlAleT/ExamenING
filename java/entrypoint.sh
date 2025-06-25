#!/bin/bash

# Start SSH service
service ssh start

# Format namenode (only the first time)
if [ ! -d "/opt/hadoop/data/namenode" ]; then
  mkdir -p /opt/hadoop/data/namenode
  $HADOOP_HOME/bin/hdfs namenode -format
fi

# Start Hadoop services
$HADOOP_HOME/sbin/start-dfs.sh
$HADOOP_HOME/sbin/start-yarn.sh

# Create HDFS directories if they don't exist
$HADOOP_HOME/bin/hdfs dfs -mkdir -p /warehouse/fooddelivery
$HADOOP_HOME/bin/hdfs dfs -mkdir -p /warehouse/fooddelivery/results
$HADOOP_HOME/bin/hdfs dfs -chmod -R 777 /warehouse

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
until mysql -h db -u root -pexample -e "SELECT 1"; do
  sleep 1
done

# Create the datawarehouse database if it doesn't exist
mysql -h db -u root -pexample -e "CREATE DATABASE IF NOT EXISTS datawarehouse;"

# Run the complete ETL process
echo "Running the complete ETL process..."
java -cp "/app/fooddelivery-dw-1.0-SNAPSHOT.jar:/app/dependency/*" com.hadoop.aggregation.AggregationDriver run-complete-etl

# Keep container running for debugging if needed
if [ "$1" = "keep-alive" ]; then
  tail -f /dev/null
fi
