# Containerized Hadoop ETL Pipeline

This project contains a containerized Hadoop-based ETL pipeline that extracts data from a MySQL database, transforms it into a star schema, and loads it back into a different database in the same MySQL server.

## Architecture

The system consists of two main containers:

1. **MySQL Container**: Hosts the source database (`ordersdb`) and the target data warehouse database (`datawarehouse`)
2. **Hadoop Container**: Runs the Hadoop cluster and the ETL jobs

## Prerequisites

- Docker
- Docker Compose
- Maven (for building the Java application)

## Directory Structure

```
Examen/
├── java/
│   ├── Dockerfile          # Hadoop container configuration
│   ├── docker-compose.yml  # Docker Compose file for the Hadoop container
│   ├── entrypoint.sh       # Startup script for the Hadoop container
│   ├── hadoop-config/      # Hadoop configuration files
│   ├── src/                # Java source code
│   ├── target/             # Compiled Java code
│   └── ...
├── load-data/
│   ├── Dockerfile          # MySQL container configuration
│   ├── docker-compose.yml  # Docker Compose file for the MySQL container
│   ├── db.sql              # Database schema and initial data
│   └── ...
├── run_hadoop_job.sh       # Script to build and run the containerized job
└── ...
```

## How to Run

1. Make sure Docker and Docker Compose are running
2. Execute the script to build and run the containerized job:

```bash
./run_hadoop_job.sh
```

The script will:
1. Build the Java application with Maven
2. Build the Docker images for both containers
3. Start the containers
4. Run the Hadoop ETL job
5. Export the results to the MySQL database

## Monitoring and Debugging

- **Hadoop Web Interfaces**:
  - NameNode: http://localhost:9870
  - ResourceManager: http://localhost:8088
  - DataNode: http://localhost:9864

- **MySQL Database**:
  To connect to the MySQL database:
  ```bash
  docker exec -it java_db_1 mysql -u root -pexample
  ```

- **Container Logs**:
  ```bash
  docker-compose logs -f hadoop
  ```

## Stopping the Containers

To stop the containers:
```bash
cd java
docker-compose down
```

## Data Flow

1. **Extract**: Data is extracted from the `ordersdb` database in MySQL
2. **Transform**: Hadoop MapReduce jobs transform the data into a star schema model
3. **Load**: The transformed data is exported to the `datawarehouse` database in MySQL

## Star Schema Design

The star schema includes:

- **Fact Table**: `fact_orders` with metrics like order cost, preparation time, delivery time, and ratings
- **Dimension Tables**: Customer, Restaurant, DeliveryPerson, Date, Location, TimeSlot

See the `STAR_SCHEMA_DESCRIPTION.md` file for more details on the schema design.
