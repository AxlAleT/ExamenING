#!/bin/bash

# This script helps troubleshoot connection issues between the Hadoop and MySQL containers

# Determine Docker Compose command
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "==== Database Connection Troubleshooter ===="
echo "Testing connection to MySQL from Hadoop container..."

# Check if containers are running
echo "Checking containers..."
HADOOP_RUNNING=$(docker ps | grep java-hadoop-1 | wc -l)
MYSQL_RUNNING=$(docker ps | grep java-db-1 | wc -l)

if [ "$HADOOP_RUNNING" -eq "0" ]; then
  echo "ERROR: Hadoop container is not running!"
  exit 1
fi

if [ "$MYSQL_RUNNING" -eq "0" ]; then
  echo "ERROR: MySQL container is not running!"
  exit 1
fi

echo "Both containers are running."

# Check network connectivity
echo "Testing network connectivity..."
docker exec java-hadoop-1 ping -c 2 db
if [ $? -ne 0 ]; then
  echo "ERROR: Hadoop container cannot reach MySQL container!"
  echo "Checking Docker network..."
  docker network inspect java_default
  exit 1
fi

echo "Network connectivity OK."

# Check MySQL accessibility
echo "Testing MySQL connection..."
docker exec java-hadoop-1 mysql -h db -u root -pexample -e "SHOW DATABASES;"
if [ $? -ne 0 ]; then
  echo "ERROR: Cannot connect to MySQL from Hadoop container!"
  echo "Checking MySQL status..."
  docker exec java-db-1 mysqladmin -u root -pexample status
  
  echo "Ensuring MySQL is configured to accept remote connections..."
  docker exec java-db-1 mysql -u root -pexample -e "CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'example'; GRANT ALL PRIVILEGES ON *.* TO 'root'@'%'; FLUSH PRIVILEGES;"
  
  echo "Retrying connection..."
  docker exec java-hadoop-1 mysql -h db -u root -pexample -e "SHOW DATABASES;"
  if [ $? -ne 0 ]; then
    echo "Still cannot connect. Please check MySQL configuration."
    exit 1
  fi
fi

echo "MySQL connection OK."

# Check Java installation and MySQL connector
echo "Checking Java and MySQL connector..."
docker exec java-hadoop-1 java -version
if [ $? -ne 0 ]; then
  echo "ERROR: Java not properly installed in Hadoop container!"
  exit 1
fi

# Check if the MySQL connector is available
docker exec java-hadoop-1 ls -l /opt/hadoop/share/hadoop/common/lib/mysql-connector-java-8.0.28.jar
if [ $? -ne 0 ]; then
  echo "ERROR: MySQL connector not found in Hadoop container!"
  exit 1
fi

echo "Java and MySQL connector OK."

# Check Hadoop services
echo "Checking Hadoop services..."
docker exec java-hadoop-1 jps
if [ $? -ne 0 ]; then
  echo "ERROR: Hadoop services not running properly!"
  exit 1
fi

echo "Hadoop services OK."

echo "All checks passed! The containers should be able to communicate properly."
echo "If you're still experiencing issues, check the application logs:"
echo "$DOCKER_COMPOSE_CMD logs -f hadoop"
