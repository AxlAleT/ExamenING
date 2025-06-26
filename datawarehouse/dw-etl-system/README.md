# Order Data Warehouse ETL System with Apache Airflow

This project is an ETL (Extract, Transform, Load) system designed for processing food delivery order data into a data warehouse. It uses Apache Airflow for orchestration and MySQL for both source and target databases.

## Project Overview

The system extracts data from a source database containing food delivery order information, transforms it into a star schema, and loads it into a data warehouse for analysis. The data warehouse is designed to facilitate analytics on restaurant performance, delivery efficiency, customer behavior, and more.

## Project Structure

```
dw-etl-system/
├── dags/                # Airflow DAG definitions
├── data/
│   ├── processed/       # Transformed data ready for loading
│   └── raw/             # Raw extracted data
├── logs/                # Log files
├── src/
│   ├── config/          # Configuration files
│   │   ├── database.py  # Database connection settings
│   │   ├── settings.py  # Application settings
│   ├── etl/             # ETL process modules
│   │   ├── extract.py   # Data extraction
│   │   ├── transform.py # Data transformation
│   │   ├── load.py      # Data loading
│   ├── models/          # Data models
│   │   ├── dimensions.py # Dimension table models
│   │   ├── facts.py     # Fact table models
│   ├── schema/          # Database schema definitions
│   │   ├── datawarehouse.sql # Star schema definition
│   ├── utils/           # Utility functions
│   │   ├── database.py  # Database utilities
│   │   ├── logging.py   # Logging utilities
│   ├── main.py          # Command-line entry point
├── tests/               # Unit tests
├── Dockerfile           # Docker configuration
├── run_containers.sh    # Script to run Docker containers
├── stop_containers.sh   # Script to stop Docker containers
├── run_etl.sh           # Script to run ETL process in Docker
├── .env                 # Environment variables
├── requirements.txt     # Project dependencies
├── setup.py             # Package installation
└── README.md            # Project documentation
```

## Prerequisites

- Python 3.8+ (for local development)
- MySQL 8.0+
- Docker (for containerized deployment)
- Apache Airflow 2.7+ (installed automatically in container)

## Installation

### Option 1: Local Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd dw-etl-system
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment variables in the `.env` file.

5. Install and initialize Airflow:
   ```bash
   export AIRFLOW_HOME=~/airflow
   airflow db init
   airflow users create \
     --username admin \
     --firstname Admin \
     --lastname User \
     --role Admin \
     --email admin@example.com \
     --password admin
   ```

6. Create a symbolic link to the DAGs folder:
   ```bash
   ln -s $(pwd)/dags $AIRFLOW_HOME/dags
   ```

### Option 2: Docker Installation

1. Make sure Docker is installed on your system

2. Update the `.env` file to point to the correct database host:
   - Update `SOURCE_DB_HOST` and `DW_DB_HOST` to point to your MySQL server
   - By default, they're set to `host.docker.internal` to access a MySQL server running on the host machine

3. Build the Docker image:
   ```bash
   docker build -t etl-app .
   ```

## Database Setup

Ensure you have MySQL running with the required databases:

1. Source database (ordersdb): Contains the raw order data
2. Target database (datawarehouse): Will store the star schema

You can initialize the source database using the SQL scripts in the `/load-data` directory.

## Usage

### Running with Docker

#### Option 1: Using the provided scripts

1. Run the ETL process once:
   ```bash
   ./run_etl.sh
   ```

2. Start Airflow (both webserver and scheduler):
   ```bash
   ./run_containers.sh
   ```

3. Access the Airflow web UI at http://localhost:8080 with:
   - Username: admin
   - Password: admin

4. Stop Airflow containers when done:
   ```bash
   ./stop_containers.sh
   ```

#### Option 2: Manual Docker commands

1. Run the ETL process once:
   ```bash
   docker run --name etl-run --rm etl-app etl
   ```

2. Run the Airflow webserver:
   ```bash
   docker run -d --name etl-webserver -p 8080:8080 etl-app webserver
   ```

3. Run the Airflow scheduler:
   ```bash
   docker run -d --name etl-scheduler etl-app scheduler
   ```

4. Stop and remove containers when done:
   ```bash
   docker stop etl-webserver etl-scheduler
   docker rm etl-webserver etl-scheduler
   ```

### Running Locally (without Docker)

#### Running the ETL Process directly

To run the ETL process directly (without Airflow):

```bash
python -m src.main
```

Optional arguments:
- `--extract-only`: Only perform data extraction
- `--schema-only`: Only create the schema in the data warehouse

#### Running with Airflow

1. Start the Airflow webserver:
   ```bash
   airflow webserver --port 8080
   ```

2. In another terminal, start the Airflow scheduler:
   ```bash
   airflow scheduler
   ```

3. Access the Airflow web UI at http://localhost:8080 and trigger the `etl_order_datawarehouse` DAG.

## Data Model

The data warehouse uses a star schema with the following structure:

- **Fact Table**: `fact_orders` - Contains order metrics
- **Dimension Tables**:
  - `dim_customer` - Customer information
  - `dim_restaurant` - Restaurant information
  - `dim_date` - Date information
  - `dim_location` - Location information
  - `dim_timeslot` - Time slot information
  - `dim_deliveryperson` - Delivery person information

## Analytics Views

The data warehouse includes these pre-built views:

1. `restaurant_performance` - Overall restaurant metrics
2. `customer_order_patterns` - Customer behavior analysis
3. `delivery_performance_by_zone` - Delivery performance metrics
4. `time_order_patterns` - Order patterns by time
5. `cuisine_by_location` - Cuisine popularity by location

## Testing

To run the tests:

```bash
pytest tests/
```

## Maintenance

- Logs are stored in the `logs/` directory
- Intermediate data files are stored in `data/raw/` and `data/processed/`

## License

This project is licensed under the MIT License.