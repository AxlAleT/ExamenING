import csv
import os
from datetime import date, datetime
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone

# Assuming models are in ..models relative to this file's eventual location
# For initial creation, use absolute path based on typical Django structure
# This will be Django.warehouse.models after full setup
from warehouse.models import (
    DimCustomer, DimRestaurant, DimDate, DimLocation,
    DimTimeSlot, DimDeliveryPerson, FactOrders
)

class Command(BaseCommand):
    help = 'Populates the data warehouse from the unnormalized.csv file and updates DimDate.'

    def get_or_create_date(self, date_obj):
        """
        Gets or creates a DimDate record for the given date object.
        Populates day_of_week, month_name, quarter, year.
        """
        try:
            dt_obj = timezone.make_aware(datetime.combine(date_obj, datetime.min.time())) if not timezone.is_aware(datetime.combine(date_obj, datetime.min.time())) else datetime.combine(date_obj, datetime.min.time())
        except AttributeError: # date_obj might already be a datetime
             dt_obj = timezone.make_aware(date_obj) if not timezone.is_aware(date_obj) else date_obj


        dim_date, created = DimDate.objects.get_or_create(
            full_date=date_obj,
            defaults={
                'day_of_week': dt_obj.strftime('%A'),
                'month_name': dt_obj.strftime('%B'),
                'quarter': (dt_obj.month - 1) // 3 + 1,
                'year': dt_obj.year
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created DimDate for {date_obj}"))
        return dim_date

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting data warehouse population..."))

        # Clear existing data from DWH models
        self.stdout.write("Clearing existing data...")
        FactOrders.objects.all().delete()
        DimDeliveryPerson.objects.all().delete()
        DimTimeSlot.objects.all().delete()
        DimLocation.objects.all().delete()
        DimDate.objects.all().delete() # Clear dates; they will be repopulated
        DimRestaurant.objects.all().delete()
        DimCustomer.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Existing data cleared."))

        # --- Populate DimDate with today's date ---
        today = timezone.now().date()
        self.get_or_create_date(today)
        # For CSV processing, we'll use this 'today' as the default order date
        # as unnormalized.csv doesn't have date information for orders.
        default_order_date_dim = self.get_or_create_date(today)


        # --- Create default dimension records ---
        self.stdout.write("Creating default dimension records...")
        default_location, _ = DimLocation.objects.get_or_create(
            location_id=1, # Explicitly set an ID for the unknown/default record
            defaults={'city': 'Unknown', 'region': 'Unknown'}
        )
        default_timeslot, _ = DimTimeSlot.objects.get_or_create(
            time_slot_id=1, # Explicitly set an ID
            defaults={'slot_name': 'Unknown'}
        )
        default_delivery_person, _ = DimDeliveryPerson.objects.get_or_create(
            delivery_person_id=1, # Explicitly set an ID
            defaults={'delivery_person_name': 'Unknown'}
        )
        self.stdout.write(self.style.SUCCESS("Default dimension records created/ensured."))

        # --- Process unnormalized.csv ---
        # Construct path to CSV file, assuming it's in warehouse/data/
        csv_file_path = os.path.join(settings.BASE_DIR, 'warehouse', 'data', 'unnormalized.csv')

        if not os.path.exists(csv_file_path):
            raise CommandError(f"File not found: {csv_file_path}. Please create it and populate it with data.")

        self.stdout.write(f"Processing {csv_file_path}...")

        processed_orders = 0
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row_num, row in enumerate(reader):
                    try:
                        # Validate required fields
                        required_fields = ['order_id', 'customer_id', 'restaurant_name', 'cuisine_type',
                                           'cost_of_the_order', 'day_of_the_week', 'rating',
                                           'food_preparation_time', 'delivery_time']
                        for field in required_fields:
                            if field not in row or not row[field]:
                                self.stdout.write(self.style.WARNING(f"Skipping row {row_num + 2} due to missing required field: {field}"))
                                continue

                        # Customer
                        customer, _ = DimCustomer.objects.get_or_create(
                            customer_id=int(row['customer_id'])
                        )

                        # Restaurant
                        # Using name and cuisine as a composite key for uniqueness
                        restaurant, _ = DimRestaurant.objects.get_or_create(
                            restaurant_name=row['restaurant_name'],
                            cuisine_type=row['cuisine_type']
                        )

                        # Use the default date created earlier for all orders from CSV
                        order_dim_date = default_order_date_dim

                        # Convert rating
                        rating_val = None
                        if row['rating'] and row['rating'].lower() != 'not given':
                            try:
                                rating_val = int(row['rating'])
                            except ValueError:
                                self.stdout.write(self.style.WARNING(f"Invalid rating value '{row['rating']}' for order_id {row['order_id']}. Setting to NULL."))

                        # Convert cost, prep time, delivery time
                        try:
                            cost = Decimal(row['cost_of_the_order'])
                            prep_time = int(row['food_preparation_time'])
                            delivery_time_val = int(row['delivery_time'])
                        except ValueError as e:
                            self.stdout.write(self.style.WARNING(f"Skipping order_id {row['order_id']} due to data conversion error: {e}"))
                            continue

                        # Create FactOrder
                        FactOrders.objects.create(
                            order_id=int(row['order_id']),
                            customer=customer,
                            restaurant=restaurant,
                            delivery_person=default_delivery_person, # Default
                            date=order_dim_date, # Default date from CSV
                            location=default_location, # Default
                            time_slot=default_timeslot, # Default
                            order_cost=cost,
                            rating=rating_val,
                            food_preparation_time=prep_time,
                            delivery_time=delivery_time_val
                            # total_time and order_date are handled by the model's save() method
                        )
                        processed_orders += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error processing row {row_num + 2} (Order ID: {row.get('order_id', 'N/A')}): {e}"))
                        self.stdout.write(self.style.WARNING(f"Problematic row data: {row}"))


        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_file_path}")
        except Exception as e:
            raise CommandError(f"An error occurred: {e}")

        self.stdout.write(self.style.SUCCESS(f"Successfully processed {processed_orders} orders from CSV."))
        self.stdout.write(self.style.SUCCESS("Data warehouse population complete."))
