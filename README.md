# Data Warehouse ETL System

A comprehensive Django-based ETL (Extract, Transform, Load) system for processing order data and creating a data warehouse with analytics capabilities.

## Features

- **CSV Data Upload & Processing**: Upload CSV files containing unnormalized order data
- **Automated ETL Pipeline**: Extract data from OLTP database and load into OLAP warehouse
- **Parallel Processing**: Multi-threaded dimension extraction for faster ETL
- **Robust Upsert Strategy**: Fact table records are properly updated when source data changes
- **Scheduled Processing**: Automatic nightly ETL runs
- **Analytics Dashboard**: Rich visualizations and insights
- **Data Export**: Export processed data in CSV format
- **User Authentication**: Secure access with Django auth
- **Real-time Monitoring**: Track ETL job progress and statistics

## System Architecture

### OLTP Database (ordersdb)
- **Customer**: Customer information
- **Restaurant**: Restaurant details
- **Day**: Day information (weekend/holiday flags)
- **DeliveryPerson**: Delivery personnel data
- **Order**: Order transactions

### OLAP Database (olapdb)
- **Dimension Tables**: DimCustomer, DimRestaurant, DimDate, DimLocation, DimTimeslot, DimDeliveryPerson
- **Fact Table**: FactOrders (star schema)

## Installation & Setup

### 1. Prerequisites
```bash
# Install Python 3.8+
# Install MySQL/MariaDB
# Install pip and virtualenv
```

### 2. Database Setup
```bash
# Create databases
CREATE DATABASE ordersdb;
CREATE DATABASE olapdb;

# Create user (optional)
CREATE USER 'etl_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL ON ordersdb.* TO 'etl_user'@'localhost';
GRANT ALL ON olapdb.* TO 'etl_user'@'localhost';
```

### 3. Project Setup
```bash
# Clone repository
git clone <repository_url>
cd staging

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure settings
cp dataWarehouse/settings.py.example dataWarehouse/settings.py
# Edit database settings in settings.py
```

### 4. Django Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --database=olapdb

# Create superuser
python manage.py createsuperuser

# Collect static files (if in production)
python manage.py collectstatic
```

### 5. Run the Application
```bash
# Development server
python manage.py runserver

# Access the application
# http://localhost:8000/etl/
```

## Usage

### 1. Data Upload
1. Login to the system
2. Navigate to ETL Dashboard
3. Upload CSV files with the following format:

```csv
order_id,customer_id,restaurant_name,cuisine_type,cost_of_the_order,day_of_the_week,rating,food_preparation_time,delivery_time,cust_first_name,cust_last_name,cust_email,cust_phone,cust_address,cust_city,cust_registration_date,rest_address,rest_city,rest_phone,rest_website,rest_price_range,rest_rating_avg,rest_opening_hour,rest_closing_hour,rest_established_date,is_weekend,is_holiday,del_first_name,del_last_name,del_phone,del_email,del_vehicle,del_hire_date,del_rating,delivery_person_id,tip_amount
```

### 2. ETL Processing

#### Manual Processing
```bash
# Test ETL with sample data
python manage.py test_etl --sample

# Process CSV file
python manage.py test_etl --file path/to/your/file.csv

# Run data warehouse ETL
python manage.py run_warehouse_etl

# Run data warehouse ETL with stats output
python manage.py run_warehouse_etl --stats
```

#### Scheduled Processing
```bash
# Start ETL scheduler (runs at midnight daily)
python manage.py schedule_etl

# Run as daemon
python manage.py schedule_etl --daemon

# Test run
python manage.py schedule_etl --test
```

### 3. Analytics & Reporting
1. Navigate to Analytics Dashboard
2. View key metrics:
   - Total orders and revenue
   - Average order value
   - Delivery performance
   - Restaurant rankings
   - Customer segments
3. Export data in CSV format

## Management Commands

```bash
# ETL Commands
python manage.py test_etl --sample              # Test with sample data
python manage.py test_etl --file <path>         # Process specific file
python manage.py run_warehouse_etl              # Run warehouse ETL
python manage.py run_warehouse_etl --stats      # Show detailed ETL statistics
python manage.py run_warehouse_etl --force      # Force run even if recent job exists
python manage.py schedule_etl                   # Start scheduler
python manage.py schedule_etl --daemon          # Run as daemon
python manage.py schedule_etl --test            # Test run

# Django Commands
python manage.py migrate                        # Run migrations
python manage.py createsuperuser               # Create admin user
python manage.py collectstatic                 # Collect static files
python manage.py runserver                     # Start development server
```

## API Endpoints

### ETL Endpoints
- `POST /etl/upload/` - Upload CSV file
- `POST /etl/process-csv/` - Process CSV data directly
- `GET /etl/job/<id>/status/` - Get job status
- `POST /etl/upload/<id>/process/` - Trigger manual processing

### Analytics Endpoints
- `GET /etl/analytics/` - Analytics dashboard
- `GET /etl/export/?type=orders` - Export orders
- `GET /etl/export/?type=restaurants` - Export restaurant data

### Authentication
- `GET /etl/login/` - Login page
- `POST /etl/logout/` - Logout

## Configuration

### Database Settings
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ordersdb',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
    'olapdb': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'olapdb',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

### Logging
Logs are written to `etl.log` in the project root. Configure logging in settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'etl.log',
        },
    },
    'loggers': {
        'etl': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database credentials in settings.py
   - Ensure MySQL service is running
   - Verify database exists

2. **Migration Errors**
   - Run migrations for both databases
   - Check database user permissions

3. **File Upload Issues**
   - Ensure MEDIA_ROOT directory exists
   - Check file permissions
   - Verify CSV format matches expected structure

4. **ETL Processing Errors**
   - Check logs in etl.log
   - Verify data format and encoding
   - Ensure all required fields are present

### Debug Mode
Enable debug logging by setting `DEBUG = True` in settings.py and adding console handler:

```python
'handlers': {
    'console': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
    },
}
```

## Performance Optimization

### For Large Datasets
1. Parallel dimension extraction using ThreadPoolExecutor
2. Robust upsert strategy for fact tables with field-by-field comparison
3. Use bulk operations in ETL services
4. Process data in chunks
5. Celery for async processing
6. Data pagination
7. Database indexing

### Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_customer_id ON orders(customer_id);
CREATE INDEX idx_restaurant_id ON orders(restaurant_id);
CREATE INDEX idx_order_date ON fact_orders(order_date);
```

## Security Considerations

1. **Authentication**: All views require login
2. **File Uploads**: Validate file types and sizes
3. **Database**: Use separate credentials for OLTP/OLAP
4. **Production**: Set `DEBUG = False` and configure ALLOWED_HOSTS

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

## License

This project is licensed under the MIT License.
