from django.db import transaction, connections
from django.utils import timezone
from datetime import datetime, date, time
from decimal import Decimal
from typing import Dict, List, Any
import logging
import threading
import concurrent.futures
import time as time_module

from core.models import (
    # OLTP Models
    Customer, Restaurant, Day, DeliveryPerson, Order,
    # OLAP Models 
    DimCustomer, DimRestaurant, DimDate, DimLocation, 
    DimTimeslot, DimDeliveryPerson, FactOrders
)

logger = logging.getLogger(__name__)


class DataWarehouseETL:
    """
    ETL service for extracting data from OLTP (ordersdb) and loading into OLAP (olapdb).
    Thread-safe implementation for parallel dimension extraction.
    """
    
    def __init__(self):
        # Initialize stats dictionary
        self.stats = {
            'dim_customer': {'processed': 0, 'inserted': 0, 'updated': 0, 'errors': 0},
            'dim_restaurant': {'processed': 0, 'inserted': 0, 'updated': 0, 'errors': 0},
            'dim_date': {'processed': 0, 'inserted': 0, 'updated': 0, 'errors': 0},
            'dim_location': {'processed': 0, 'inserted': 0, 'updated': 0, 'errors': 0},
            'dim_timeslot': {'processed': 0, 'inserted': 0, 'updated': 0, 'errors': 0},
            'dim_deliveryperson': {'processed': 0, 'inserted': 0, 'updated': 0, 'errors': 0},
            'fact_orders': {'processed': 0, 'inserted': 0, 'updated': 0, 'errors': 0}
        }
        
        # Create locks for thread-safe stats updates
        self._stats_lock = threading.Lock()
        
    def _update_stats(self, dimension: str, stat_type: str, value: int = 1):
        """
        Thread-safe method to update stats.
        
        Args:
            dimension: The dimension name (e.g., 'dim_customer')
            stat_type: The stat type (e.g., 'processed', 'inserted')
            value: Value to increment by (default: 1)
        """
        with self._stats_lock:
            self.stats[dimension][stat_type] += value
    
    def run_full_etl(self) -> Dict[str, Any]:
        """
        Run the complete ETL process for the data warehouse.
        Uses parallel processing for dimension extraction.
        """
        logger.info("Starting full data warehouse ETL process with parallel dimension extraction")
        start_time = time_module.time()
        
        try:
            # Extract and load dimensions in parallel using thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                # Submit all dimension extraction tasks to the executor
                dim_tasks = {
                    'customer': executor.submit(self.extract_dim_customer),
                    'restaurant': executor.submit(self.extract_dim_restaurant),
                    'date': executor.submit(self.extract_dim_date),
                    'location': executor.submit(self.extract_dim_location),
                    'timeslot': executor.submit(self.extract_dim_timeslot),
                    'deliveryperson': executor.submit(self.extract_dim_deliveryperson)
                }
                
                # Wait for all tasks to complete and log results
                for dim_name, task in dim_tasks.items():
                    try:
                        # This will block until the task is complete
                        task.result()
                        logger.info(f"Dimension extraction for {dim_name} completed successfully")
                    except Exception as e:
                        logger.error(f"Error extracting dimension {dim_name}: {str(e)}")
                        raise
            
            # Then extract and load facts (this must run after all dimensions are loaded)
            self.extract_fact_orders()
            
            end_time = time_module.time()
            total_time = end_time - start_time
            logger.info(f"Data warehouse ETL completed in {total_time:.2f} seconds")
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Error in data warehouse ETL process: {str(e)}")
            raise
            self.extract_fact_orders()
            
            logger.info("Data warehouse ETL process completed successfully")
            return self.stats
            
        except Exception as e:
            logger.error(f"Data warehouse ETL process failed: {str(e)}")
            raise
    
    def extract_dim_customer(self):
        """Extract customer dimension from OLTP."""
        logger.info("Extracting customer dimension")
        start_time = time_module.time()
        
        customers = Customer.objects.using('default').all()
        
        for customer in customers:
            self._update_stats('dim_customer', 'processed')
            try:
                # Determine customer segment based on registration date
                segment = self._determine_customer_segment(customer.registration_date)
                
                dim_customer, created = DimCustomer.objects.using('olapdb').get_or_create(
                    customer_id=customer.customer_id,
                    defaults={
                        'customer_name': f"{customer.first_name or ''} {customer.last_name or ''}".strip(),
                        'segment': segment,
                        'registration_date': customer.registration_date
                    }
                )
                
                if created:
                    self._update_stats('dim_customer', 'inserted')
                else:
                    # Update if needed
                    updated = False
                    new_name = f"{customer.first_name or ''} {customer.last_name or ''}".strip()
                    if dim_customer.customer_name != new_name:
                        dim_customer.customer_name = new_name
                        updated = True
                    if dim_customer.segment != segment:
                        dim_customer.segment = segment
                        updated = True
                    if updated:
                        dim_customer.save(using='olapdb')
                        self._update_stats('dim_customer', 'updated')
                        
            except Exception as e:
                self._update_stats('dim_customer', 'errors')
                logger.error(f"Error processing customer {customer.customer_id}: {str(e)}")
        
        end_time = time_module.time()
        elapsed = end_time - start_time
        logger.info(f"Customer dimension extraction completed in {elapsed:.2f} seconds")
    
    def extract_dim_restaurant(self):
        """Extract restaurant dimension from OLTP."""
        logger.info("Extracting restaurant dimension")
        start_time = time_module.time()
        
        restaurants = Restaurant.objects.using('default').all()
        
        for restaurant in restaurants:
            self._update_stats('dim_restaurant', 'processed')
            try:
                dim_restaurant, created = DimRestaurant.objects.using('olapdb').get_or_create(
                    restaurant_id=restaurant.restaurant_id,
                    defaults={
                        'restaurant_name': restaurant.restaurant_name,
                        'cuisine_type': restaurant.cuisine_type,
                        'rating_avg': restaurant.rating_avg
                    }
                )
                
                if created:
                    self._update_stats('dim_restaurant', 'inserted')
                else:
                    # Update if needed
                    updated = False
                    if dim_restaurant.restaurant_name != restaurant.restaurant_name:
                        dim_restaurant.restaurant_name = restaurant.restaurant_name
                        updated = True
                    if dim_restaurant.cuisine_type != restaurant.cuisine_type:
                        dim_restaurant.cuisine_type = restaurant.cuisine_type
                        updated = True
                    if dim_restaurant.rating_avg != restaurant.rating_avg:
                        dim_restaurant.rating_avg = restaurant.rating_avg
                        updated = True
                    if updated:
                        dim_restaurant.save(using='olapdb')
                        self._update_stats('dim_restaurant', 'updated')
                        
            except Exception as e:
                self._update_stats('dim_restaurant', 'errors')
                logger.error(f"Error processing restaurant {restaurant.restaurant_id}: {str(e)}")
        
        end_time = time_module.time()
        elapsed = end_time - start_time
        logger.info(f"Restaurant dimension extraction completed in {elapsed:.2f} seconds")
    
    def extract_dim_date(self):
        """Extract date dimension - create date entries for order dates."""
        logger.info("Extracting date dimension")
        start_time = time_module.time()
        
        # Get unique order dates from orders
        order_dates = Order.objects.using('default').values_list(
            'customer__registration_date', flat=True
        ).distinct()
        
        # Also include restaurant establishment dates
        restaurant_dates = Restaurant.objects.using('default').values_list(
            'established_date', flat=True
        ).distinct()
        
        # Combine and filter out None values
        all_dates = set()
        for date_val in order_dates:
            if date_val:
                all_dates.add(date_val)
        for date_val in restaurant_dates:
            if date_val:
                all_dates.add(date_val)
        
        for date_val in all_dates:
            self._update_stats('dim_date', 'processed')
            try:
                # Generate date_id as YYYYMMDD
                date_id = int(date_val.strftime('%Y%m%d'))
                
                dim_date, created = DimDate.objects.using('olapdb').get_or_create(
                    date_id=date_id,
                    defaults={
                        'full_date': date_val,
                        'day_of_week': date_val.strftime('%A'),
                        'month_name': date_val.strftime('%B'),
                        'quarter': (date_val.month - 1) // 3 + 1,
                        'year': date_val.year
                    }
                )
                
                if created:
                    self._update_stats('dim_date', 'inserted')
                    
            except Exception as e:
                self._update_stats('dim_date', 'errors')
                logger.error(f"Error processing date {date_val}: {str(e)}")
        
        end_time = time_module.time()
        elapsed = end_time - start_time
        logger.info(f"Date dimension extraction completed in {elapsed:.2f} seconds")
    
    def extract_dim_location(self):
        """Extract location dimension from customer and restaurant addresses."""
        logger.info("Extracting location dimension")
        start_time = time_module.time()
        
        # Get unique locations from customers
        customer_locations = Customer.objects.using('default').values(
            'city', 'address'
        ).distinct()
        
        # Get unique locations from restaurants  
        restaurant_locations = Restaurant.objects.using('default').values(
            'city', 'address'
        ).distinct()
        
        location_id = 1
        processed_locations = set()
        
        # Process customer locations
        for loc in customer_locations:
            if loc['city'] and loc['city'] not in processed_locations:
                self._update_stats('dim_location', 'processed')
                try:
                    dim_location, created = DimLocation.objects.using('olapdb').get_or_create(
                        location_id=location_id,
                        defaults={
                            'neighborhood': self._extract_neighborhood(loc['address']),
                            'postal_code': self._extract_postal_code(loc['address']),
                            'city': loc['city'],
                            'region': self._determine_region(loc['city'])
                        }
                    )
                    
                    if created:
                        self._update_stats('dim_location', 'inserted')
                        location_id += 1
                    
                    processed_locations.add(loc['city'])
                    
                except Exception as e:
                    self._update_stats('dim_location', 'errors')
                    logger.error(f"Error processing location {loc}: {str(e)}")
        
        # Process restaurant locations
        for loc in restaurant_locations:
            if loc['city'] and loc['city'] not in processed_locations:
                self._update_stats('dim_location', 'processed')
                try:
                    dim_location, created = DimLocation.objects.using('olapdb').get_or_create(
                        location_id=location_id,
                        defaults={
                            'neighborhood': self._extract_neighborhood(loc['address']),
                            'postal_code': self._extract_postal_code(loc['address']),
                            'city': loc['city'],
                            'region': self._determine_region(loc['city'])
                        }
                    )
                    
                    if created:
                        self.stats['dim_location']['inserted'] += 1
                        location_id += 1
                    
                    processed_locations.add(loc['city'])
                    
                except Exception as e:
                    self.stats['dim_location']['errors'] += 1
                    logger.error(f"Error processing location {loc}: {str(e)}")
    
    def extract_dim_timeslot(self):
        """Extract time slot dimension."""
        logger.info("Extracting time slot dimension")
        
        # Define standard time slots
        time_slots = [
            {'slot_name': 'Early Morning', 'start_time': time(6, 0), 'end_time': time(9, 0)},
            {'slot_name': 'Morning', 'start_time': time(9, 0), 'end_time': time(12, 0)},
            {'slot_name': 'Lunch', 'start_time': time(12, 0), 'end_time': time(15, 0)},
            {'slot_name': 'Afternoon', 'start_time': time(15, 0), 'end_time': time(18, 0)},
            {'slot_name': 'Dinner', 'start_time': time(18, 0), 'end_time': time(22, 0)},
            {'slot_name': 'Late Night', 'start_time': time(22, 0), 'end_time': time(6, 0)},
        ]
        
        for i, slot_data in enumerate(time_slots, 1):
            self.stats['dim_timeslot']['processed'] += 1
            try:
                dim_timeslot, created = DimTimeslot.objects.using('olapdb').get_or_create(
                    time_slot_id=i,
                    defaults=slot_data
                )
                
                if created:
                    self.stats['dim_timeslot']['inserted'] += 1
                    
            except Exception as e:
                self.stats['dim_timeslot']['errors'] += 1
                logger.error(f"Error processing time slot {slot_data}: {str(e)}")
    
    def extract_dim_deliveryperson(self):
        """Extract delivery person dimension from OLTP."""
        logger.info("Extracting delivery person dimension")
        
        delivery_persons = DeliveryPerson.objects.using('default').all()
        
        for dp in delivery_persons:
            self.stats['dim_deliveryperson']['processed'] += 1
            try:
                # Calculate tenure in months
                tenure_months = self._calculate_tenure_months(dp.hire_date)
                
                dim_dp, created = DimDeliveryPerson.objects.using('olapdb').get_or_create(
                    delivery_person_id=dp.delivery_person_id,
                    defaults={
                        'delivery_person_name': f"{dp.first_name or ''} {dp.last_name or ''}".strip(),
                        'operation_zone': self._determine_operation_zone(dp),
                        'tenure_months': tenure_months
                    }
                )
                
                if created:
                    self.stats['dim_deliveryperson']['inserted'] += 1
                else:
                    # Update tenure months
                    new_tenure = self._calculate_tenure_months(dp.hire_date)
                    if dim_dp.tenure_months != new_tenure:
                        dim_dp.tenure_months = new_tenure
                        dim_dp.save(using='olapdb')
                        self.stats['dim_deliveryperson']['updated'] += 1
                        
            except Exception as e:
                self.stats['dim_deliveryperson']['errors'] += 1
                logger.error(f"Error processing delivery person {dp.delivery_person_id}: {str(e)}")
    
    def extract_fact_orders(self):
        """
        Extract fact orders from OLTP.
        Implements a robust upsert (update or insert) strategy for fact table records.
        """
        logger.info("Extracting fact orders")
        start_time = time_module.time()
        
        orders = Order.objects.using('default').select_related(
            'customer', 'restaurant', 'day', 'delivery_person'
        ).all()
        
        for order in orders:
            self._update_stats('fact_orders', 'processed')
            try:
                # Get dimension keys
                customer_dim = DimCustomer.objects.using('olapdb').filter(
                    customer_id=order.customer.customer_id
                ).first()
                
                restaurant_dim = DimRestaurant.objects.using('olapdb').filter(
                    restaurant_id=order.restaurant.restaurant_id
                ).first()
                
                delivery_person_dim = DimDeliveryPerson.objects.using('olapdb').filter(
                    delivery_person_id=order.delivery_person.delivery_person_id if order.delivery_person else None
                ).first()
                
                # Create synthetic date and time for the order
                order_date = self._generate_order_date(order)
                date_id = int(order_date.strftime('%Y%m%d'))
                date_dim = DimDate.objects.using('olapdb').filter(date_id=date_id).first()
                
                # Get location and time slot
                location_dim = self._get_location_for_order(order)
                time_slot_dim = self._get_timeslot_for_order(order)
                
                if not all([customer_dim, restaurant_dim, date_dim, location_dim, time_slot_dim, delivery_person_dim]):
                    logger.warning(f"Missing dimension data for order {order.order_id}")
                    continue
                
                # Calculate total time
                total_time = (order.food_preparation_time or 0) + (order.delivery_time or 0)
                
                # Prepare order data
                order_data = {
                    'customer': customer_dim,
                    'restaurant': restaurant_dim,
                    'delivery_person': delivery_person_dim,
                    'date': date_dim,
                    'location': location_dim,
                    'time_slot': time_slot_dim,
                    'order_date': order_date,
                    'order_time': self._generate_order_time(order),
                    'order_cost': order.cost_of_the_order,
                    'rating': order.rating,
                    'food_preparation_time': order.food_preparation_time,
                    'delivery_time': order.delivery_time,
                    'total_time': total_time
                }
                
                # Try to get the existing fact record
                try:
                    fact_order = FactOrders.objects.using('olapdb').get(order_id=order.order_id)
                    
                    # Update with new values if record exists
                    updated = False
                    for field, value in order_data.items():
                        if getattr(fact_order, field) != value:
                            setattr(fact_order, field, value)
                            updated = True
                    
                    if updated:
                        fact_order.save(using='olapdb')
                        self._update_stats('fact_orders', 'updated')
                    
                except FactOrders.DoesNotExist:
                    # Create new record if it doesn't exist
                    fact_order = FactOrders.objects.using('olapdb').create(
                        order_id=order.order_id,
                        **order_data
                    )
                    self._update_stats('fact_orders', 'inserted')
                    
            except Exception as e:
                self._update_stats('fact_orders', 'errors')
                logger.error(f"Error processing order {order.order_id}: {str(e)}")
        
        end_time = time_module.time()
        elapsed = end_time - start_time
        logger.info(f"Fact orders extraction completed in {elapsed:.2f} seconds")
    
    # Helper methods
    def _determine_customer_segment(self, registration_date):
        """Determine customer segment based on registration date."""
        if not registration_date:
            return 'Unknown'
        
        years_ago = (timezone.now().date() - registration_date).days / 365.25
        
        if years_ago < 1:
            return 'New'
        elif years_ago < 3:
            return 'Regular'
        else:
            return 'Loyal'
    
    def _extract_neighborhood(self, address):
        """Extract neighborhood from address."""
        if not address:
            return 'Unknown'
        # Simple heuristic - take the first part before comma
        parts = address.split(',')
        return parts[0].strip() if parts else 'Unknown'
    
    def _extract_postal_code(self, address):
        """Extract postal code from address."""
        if not address:
            return '00000'
        # Simple heuristic - look for numbers
        import re
        postal_codes = re.findall(r'\b\d{5}\b', address)
        return postal_codes[0] if postal_codes else '00000'
    
    def _determine_region(self, city):
        """Determine region based on city."""
        if not city:
            return 'Unknown'
        
        # Simple mapping - you can enhance this
        east_cities = ['New York', 'Boston', 'Philadelphia', 'Miami']
        west_cities = ['Los Angeles', 'San Francisco', 'Seattle', 'Portland']
        south_cities = ['Houston', 'Dallas', 'Atlanta', 'New Orleans']
        
        city_lower = city.lower()
        for east_city in east_cities:
            if east_city.lower() in city_lower:
                return 'East'
        for west_city in west_cities:
            if west_city.lower() in city_lower:
                return 'West'
        for south_city in south_cities:
            if south_city.lower() in city_lower:
                return 'South'
        
        return 'Central'
    
    def _calculate_tenure_months(self, hire_date):
        """Calculate tenure in months."""
        if not hire_date:
            return 0
        
        today = timezone.now().date()
        months = (today.year - hire_date.year) * 12 + (today.month - hire_date.month)
        return max(0, months)
    
    def _determine_operation_zone(self, delivery_person):
        """Determine operation zone for delivery person."""
        # Simple heuristic based on vehicle type
        if delivery_person.vehicle_type in ['car', 'motorcycle']:
            return 'Wide Range'
        elif delivery_person.vehicle_type in ['bicycle', 'scooter']:
            return 'Local'
        else:
            return 'Neighborhood'
    
    def _generate_order_date(self, order):
        """Generate a synthetic order date."""
        # Use customer registration date as base and add some days
        base_date = order.customer.registration_date or timezone.now().date()
        import random
        days_offset = random.randint(0, 365)
        return base_date + timezone.timedelta(days=days_offset)
    
    def _generate_order_time(self, order):
        """Generate a synthetic order time."""
        import random
        hour = random.randint(8, 23)
        minute = random.randint(0, 59)
        return time(hour, minute)
    
    def _get_location_for_order(self, order):
        """Get location dimension for order."""
        # Use customer city
        location = DimLocation.objects.using('olapdb').filter(
            city=order.customer.city
        ).first()
        
        if not location:
            # Create a default location
            location, created = DimLocation.objects.using('olapdb').get_or_create(
                location_id=999999,
                defaults={
                    'neighborhood': 'Unknown',
                    'postal_code': '00000',
                    'city': order.customer.city or 'Unknown',
                    'region': 'Unknown'
                }
            )
        
        return location
    
    def _get_timeslot_for_order(self, order):
        """Get time slot dimension for order."""
        # Simple heuristic - use food preparation time to determine slot
        prep_time = order.food_preparation_time or 30
        
        if prep_time < 20:
            return DimTimeslot.objects.using('olapdb').filter(time_slot_id=1).first()  # Early Morning
        elif prep_time < 30:
            return DimTimeslot.objects.using('olapdb').filter(time_slot_id=3).first()  # Lunch
        else:
            return DimTimeslot.objects.using('olapdb').filter(time_slot_id=5).first()  # Dinner
