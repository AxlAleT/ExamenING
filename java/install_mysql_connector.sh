#!/bin/bash

# This script checks if the MySQL connector is available, and if not, downloads it

MYSQL_CONNECTOR_JAR="$HADOOP_HOME/share/hadoop/common/lib/mysql-connector-java-8.0.28.jar"
MYSQL_CONNECTOR_URL="https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.28/mysql-connector-java-8.0.28.jar"

if [ ! -f "$MYSQL_CONNECTOR_JAR" ]; then
    echo "MySQL connector JAR not found at $MYSQL_CONNECTOR_JAR"
    echo "Downloading MySQL connector..."
    
    # Try wget first, then curl if wget is not available
    if command -v wget >/dev/null 2>&1; then
        wget "$MYSQL_CONNECTOR_URL" -O "$MYSQL_CONNECTOR_JAR"
    elif command -v curl >/dev/null 2>&1; then
        curl -o "$MYSQL_CONNECTOR_JAR" "$MYSQL_CONNECTOR_URL"
    else
        echo "ERROR: Neither wget nor curl is available to download the MySQL connector."
        exit 1
    fi
    
    if [ $? -eq 0 ]; then
        echo "MySQL connector downloaded successfully."
    else
        echo "ERROR: Failed to download MySQL connector."
        exit 1
    fi
else
    echo "MySQL connector already exists at $MYSQL_CONNECTOR_JAR"
fi
