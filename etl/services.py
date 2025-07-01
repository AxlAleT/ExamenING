import csv
import logging
from decimal import Decimal
from datetime import datetime, time
from typing import Dict, List, Any, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from django.conf import settings
from core.models import Customer, Restaurant, Day, DeliveryPerson, Order

logger = logging.getLogger(__name__)


class ETLService:
    """
    Service class for ETL operations to load unnormalized data into OLTP tables.
    """
    
    def __init__(self):
        self.stats = {
            'processed': 0,
            'inserted': 0,
            'updated': 0,
            'errors': 0,
            'skipped': 0
        }
    
    def process_csv_file(self, file_path: str) -> Dict[str, int]:
        """
        Process a CSV file with unnormalized order data.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dictionary with processing statistics
        """
        self.stats = {'processed': 0, 'inserted': 0, 'updated': 0, 'errors': 0, 'skipped': 0}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    self.stats['processed'] += 1
                    try:
                        self._process_row(row)
                        self.stats['inserted'] += 1
                    except Exception as e:
                        self.stats['errors'] += 1
                        logger.error(f"Error processing row {self.stats['processed']}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {str(e)}")
            raise
            
        return self.stats
    
    def process_csv_data(self, csv_data: str) -> Dict[str, int]:
        """
        Process CSV data from string.
        
        Args:
            csv_data: CSV data as string
            
        Returns:
            Dictionary with processing statistics
        """
        self.stats = {'processed': 0, 'inserted': 0, 'updated': 0, 'errors': 0, 'skipped': 0}
        
        try:
            lines = csv_data.strip().split('\n')
            if not lines:
                return self.stats
                
            csv_reader = csv.DictReader(lines)
            
            for row in csv_reader:
                self.stats['processed'] += 1
                try:
                    self._process_row(row)
                    self.stats['inserted'] += 1
                except Exception as e:
                    self.stats['errors'] += 1
                    logger.error(f"Error processing row {self.stats['processed']}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error processing CSV data: {str(e)}")
            raise
            
        return self.stats
    
    @transaction.atomic
    def _process_row(self, row: Dict[str, str]) -> None:
        """
        Process a single row of unnormalized data.
        
        Args:
            row: Dictionary containing the row data
        """
        # Extract and validate data
        cleaned_row = self._clean_row_data(row)
        
        # Create or get related entities
        customer = self._get_or_create_customer(cleaned_row)
        restaurant = self._get_or_create_restaurant(cleaned_row)
        day = self._get_or_create_day(cleaned_row)
        delivery_person = self._get_or_create_delivery_person(cleaned_row)
        
        # Create order
        self._create_order(cleaned_row, customer, restaurant, day, delivery_person)
    
    def _clean_row_data(self, row: Dict[str, str]) -> Dict[str, Any]:
        """
        Clean and validate row data, converting types as needed.
        
        Args:
            row: Raw row data
            
        Returns:
            Cleaned row data
        """
        cleaned = {}
        
        # Order fields
        cleaned['order_id'] = int(row.get('order_id', 0))
        cleaned['customer_id'] = int(row.get('customer_id', 0))
        cleaned['delivery_person_id'] = int(row.get('delivery_person_id', 0))
        
        # Convert cost to Decimal
        cost_str = row.get('cost_of_the_order', '0').strip()
        cleaned['cost_of_the_order'] = Decimal(cost_str) if cost_str else Decimal('0')
        
        # Convert tip to Decimal
        tip_str = row.get('tip_amount', '0').strip()
        cleaned['tip_amount'] = Decimal(tip_str) if tip_str else Decimal('0')
        
        # Convert times to integers
        cleaned['food_preparation_time'] = self._safe_int(row.get('food_preparation_time'))
        cleaned['delivery_time'] = self._safe_int(row.get('delivery_time'))
        
        # Handle rating - convert "Not given" to None
        rating_str = row.get('rating', '').strip()
        if rating_str and rating_str.lower() != 'not given':
            cleaned['rating'] = int(rating_str)
        else:
            cleaned['rating'] = None
        
        # Day fields
        cleaned['day_of_the_week'] = row.get('day_of_the_week', '').strip()
        cleaned['is_weekend'] = row.get('is_weekend', '').strip().lower() == 'true'
        cleaned['is_holiday'] = row.get('is_holiday', '').strip().lower() == 'true'
        
        # Customer fields
        cleaned['cust_first_name'] = row.get('cust_first_name', '').strip()
        cleaned['cust_last_name'] = row.get('cust_last_name', '').strip()
        cleaned['cust_email'] = row.get('cust_email', '').strip()
        cleaned['cust_phone'] = row.get('cust_phone', '').strip()
        cleaned['cust_address'] = row.get('cust_address', '').strip()
        cleaned['cust_city'] = row.get('cust_city', '').strip()
        cleaned['cust_registration_date'] = self._parse_date(row.get('cust_registration_date'))
        
        # Restaurant fields
        cleaned['restaurant_name'] = row.get('restaurant_name', '').strip()
        cleaned['cuisine_type'] = row.get('cuisine_type', '').strip()
        cleaned['rest_address'] = row.get('rest_address', '').strip()
        cleaned['rest_city'] = row.get('rest_city', '').strip()
        cleaned['rest_phone'] = row.get('rest_phone', '').strip()
        cleaned['rest_website'] = row.get('rest_website', '').strip()
        cleaned['rest_price_range'] = row.get('rest_price_range', '').strip()
        cleaned['rest_established_date'] = self._parse_date(row.get('rest_established_date'))
        cleaned['rest_opening_hour'] = self._parse_time(row.get('rest_opening_hour'))
        cleaned['rest_closing_hour'] = self._parse_time(row.get('rest_closing_hour'))
        
        # Convert restaurant rating to Decimal
        rating_avg_str = row.get('rest_rating_avg', '0').strip()
        cleaned['rest_rating_avg'] = Decimal(rating_avg_str) if rating_avg_str else Decimal('0')
        
        # Delivery person fields
        cleaned['del_first_name'] = row.get('del_first_name', '').strip()
        cleaned['del_last_name'] = row.get('del_last_name', '').strip()
        cleaned['del_phone'] = row.get('del_phone', '').strip()
        cleaned['del_email'] = row.get('del_email', '').strip()
        cleaned['del_vehicle'] = row.get('del_vehicle', '').strip()
        cleaned['del_hire_date'] = self._parse_date(row.get('del_hire_date'))
        
        # Convert delivery person rating to Decimal
        del_rating_str = row.get('del_rating', '0').strip()
        cleaned['del_rating'] = Decimal(del_rating_str) if del_rating_str else Decimal('0')
        
        return cleaned
    
    def _get_or_create_customer(self, data: Dict[str, Any]) -> Customer:
        """Get or create customer from data."""
        customer, created = Customer.objects.get_or_create(
            customer_id=data['customer_id'],
            defaults={
                'first_name': data['cust_first_name'],
                'last_name': data['cust_last_name'],
                'email': data['cust_email'],
                'phone': data['cust_phone'],
                'address': data['cust_address'],
                'city': data['cust_city'],
                'registration_date': data['cust_registration_date'],
            }
        )
        
        # Update existing customer if needed
        if not created:
            updated = False
            if customer.first_name != data['cust_first_name']:
                customer.first_name = data['cust_first_name']
                updated = True
            if customer.last_name != data['cust_last_name']:
                customer.last_name = data['cust_last_name']
                updated = True
            if customer.email != data['cust_email']:
                customer.email = data['cust_email']
                updated = True
            if customer.phone != data['cust_phone']:
                customer.phone = data['cust_phone']
                updated = True
            if customer.address != data['cust_address']:
                customer.address = data['cust_address']
                updated = True
            if customer.city != data['cust_city']:
                customer.city = data['cust_city']
                updated = True
            if updated:
                customer.save()
                self.stats['updated'] += 1
        
        return customer
    
    def _get_or_create_restaurant(self, data: Dict[str, Any]) -> Restaurant:
        """Get or create restaurant from data."""
        restaurant, created = Restaurant.objects.get_or_create(
            restaurant_name=data['restaurant_name'],
            defaults={
                'cuisine_type': data['cuisine_type'],
                'address': data['rest_address'],
                'city': data['rest_city'],
                'phone': data['rest_phone'],
                'website': data['rest_website'],
                'price_range': data['rest_price_range'],
                'rating_avg': data['rest_rating_avg'],
                'opening_hour': data['rest_opening_hour'],
                'closing_hour': data['rest_closing_hour'],
                'established_date': data['rest_established_date'],
            }
        )
        
        return restaurant
    
    def _get_or_create_day(self, data: Dict[str, Any]) -> Day:
        """Get or create day from data."""
        day, created = Day.objects.get_or_create(
            day_name=data['day_of_the_week'],
            defaults={
                'is_weekend': data['is_weekend'],
                'is_holiday': data['is_holiday'],
            }
        )
        
        return day
    
    def _get_or_create_delivery_person(self, data: Dict[str, Any]) -> DeliveryPerson:
        """Get or create delivery person from data."""
        delivery_person, created = DeliveryPerson.objects.get_or_create(
            delivery_person_id=data['delivery_person_id'],
            defaults={
                'first_name': data['del_first_name'],
                'last_name': data['del_last_name'],
                'phone': data['del_phone'],
                'email': data['del_email'],
                'vehicle_type': data['del_vehicle'],
                'hire_date': data['del_hire_date'],
                'rating': data['del_rating'],
            }
        )
        
        return delivery_person
    
    def _create_order(self, data: Dict[str, Any], customer: Customer, 
                     restaurant: Restaurant, day: Day, delivery_person: DeliveryPerson) -> Order:
        """Create order from data."""
        order, created = Order.objects.get_or_create(
            order_id=data['order_id'],
            defaults={
                'customer': customer,
                'restaurant': restaurant,
                'day': day,
                'delivery_person': delivery_person,
                'cost_of_the_order': data['cost_of_the_order'],
                'rating': data['rating'],
                'food_preparation_time': data['food_preparation_time'],
                'delivery_time': data['delivery_time'],
                'tip_amount': data['tip_amount'],
            }
        )
        
        if not created:
            # Order already exists, skip
            self.stats['skipped'] += 1
            logger.warning(f"Order {data['order_id']} already exists, skipping")
        
        return order
    
    def _safe_int(self, value: str) -> Optional[int]:
        """Safely convert string to int."""
        if not value or value.strip() == '':
            return None
        try:
            return int(value.strip())
        except (ValueError, TypeError):
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime.date]:
        """Parse date string to date object."""
        if not date_str or date_str.strip() == '':
            return None
        
        try:
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(date_str.strip(), fmt).date()
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    def _parse_time(self, time_str: str) -> Optional[time]:
        """Parse time string to time object."""
        if not time_str or time_str.strip() == '':
            return None
        
        try:
            # Try common time formats
            for fmt in ['%H:%M', '%H:%M:%S', '%I:%M %p']:
                try:
                    return datetime.strptime(time_str.strip(), fmt).time()
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    def process_csv_file_with_warehouse_etl(self, file_path: str, auto_trigger_warehouse: bool = True) -> Dict[str, Any]:
        """
        Process CSV file and optionally trigger warehouse ETL.
        
        Args:
            file_path: Path to the CSV file
            auto_trigger_warehouse: Whether to automatically trigger warehouse ETL
            
        Returns:
            Dictionary with processing statistics including warehouse ETL results
        """
        # Process the CSV data first
        etl_stats = self.process_csv_file(file_path)
        
        result = {
            'etl_stats': etl_stats,
            'warehouse_etl_triggered': False,
            'warehouse_etl_stats': None
        }
        
        # Trigger warehouse ETL if data was successfully loaded and auto_trigger is enabled
        if auto_trigger_warehouse and etl_stats['inserted'] > 0:
            logger.info(f"Auto-triggering warehouse ETL after loading {etl_stats['inserted']} records")
            result.update(self._trigger_warehouse_etl())
        
        return result
    
    def process_csv_data_with_warehouse_etl(self, csv_data: str, auto_trigger_warehouse: bool = True) -> Dict[str, Any]:
        """
        Process CSV data and optionally trigger warehouse ETL.
        
        Args:
            csv_data: CSV data as string
            auto_trigger_warehouse: Whether to automatically trigger warehouse ETL
            
        Returns:
            Dictionary with processing statistics including warehouse ETL results
        """
        # Process the CSV data first
        etl_stats = self.process_csv_data(csv_data)
        
        result = {
            'etl_stats': etl_stats,
            'warehouse_etl_triggered': False,
            'warehouse_etl_stats': None
        }
        
        # Trigger warehouse ETL if data was successfully loaded and auto_trigger is enabled
        if auto_trigger_warehouse and etl_stats['inserted'] > 0:
            logger.info(f"Auto-triggering warehouse ETL after loading {etl_stats['inserted']} records")
            result.update(self._trigger_warehouse_etl())
        
        return result
    
    def _trigger_warehouse_etl(self) -> Dict[str, Any]:
        """
        Trigger the warehouse ETL process.
        
        Returns:
            Dictionary with warehouse ETL results
        """
        try:
            # Import here to avoid circular imports
            from etl.warehouse_etl import DataWarehouseETL
            from etl.models import ETLJob
            from django.utils import timezone
            
            logger.info("Starting automatic warehouse ETL process")
            
            # Create ETL job record
            job = ETLJob.objects.create(
                name="Auto Warehouse ETL",
                description="Automatically triggered warehouse ETL after data load",
                status="running",
                started_at=timezone.now()
            )
            
            try:
                # Run the warehouse ETL
                warehouse_etl = DataWarehouseETL()
                warehouse_stats = warehouse_etl.run_full_etl()
                
                # Update job record
                job.status = "completed"
                job.completed_at = timezone.now()
                job.result = str(warehouse_stats)
                job.save()
                
                logger.info("Automatic warehouse ETL completed successfully")
                
                return {
                    'warehouse_etl_triggered': True,
                    'warehouse_etl_stats': warehouse_stats,
                    'warehouse_etl_error': None,
                    'job_id': job.id
                }
                
            except Exception as e:
                error_msg = f"Error running warehouse ETL: {str(e)}"
                logger.error(error_msg)
                
                # Update job record with error
                job.status = "failed"
                job.completed_at = timezone.now()
                job.result = error_msg
                job.save()
                
                return {
                    'warehouse_etl_triggered': True,
                    'warehouse_etl_stats': None,
                    'warehouse_etl_error': error_msg,
                    'job_id': job.id
                }
                
        except Exception as e:
            error_msg = f"Error setting up warehouse ETL: {str(e)}"
            logger.error(error_msg)
            
            return {
                'warehouse_etl_triggered': True,
                'warehouse_etl_stats': None,
                'warehouse_etl_error': error_msg,
                'job_id': None
            }
    
    def should_trigger_warehouse_etl(self, threshold: int = 10) -> bool:
        """
        Determine if warehouse ETL should be triggered based on data changes.
        
        Args:
            threshold: Minimum number of new records to trigger warehouse ETL
            
        Returns:
            Boolean indicating if warehouse ETL should be triggered
        """
        return self.stats.get('inserted', 0) >= threshold
