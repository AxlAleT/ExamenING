import csv
import random
import os
import datetime
import mysql.connector
from collections import defaultdict
from faker import Faker

# Initialize faker for generating realistic data
fake = Faker()

# Database connection function
def connect_to_db(host='localhost', user='root', password='password', database='ordersdb'):
    """Connect to the MySQL database"""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        print(f"Successfully connected to {database}")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# Function to enrich customers table
def enrich_customers(connection):
    """Add additional fields to customers table and populate with realistic data"""
    if not connection:
        print("No database connection available")
        return False
    
    cursor = connection.cursor()
    
    # First, check if the columns already exist
    cursor.execute("DESCRIBE customers")
    columns = [column[0] for column in cursor.fetchall()]
    
    # Add new columns if they don't exist
    new_columns = {
        "first_name": "VARCHAR(100)",
        "last_name": "VARCHAR(100)",
        "email": "VARCHAR(255)",
        "phone": "VARCHAR(12)",
        "address": "VARCHAR(255)",
        "city": "VARCHAR(100)",
        "registration_date": "DATE"
    }
    
    for col_name, col_type in new_columns.items():
        if col_name not in columns:
            try:
                cursor.execute(f"ALTER TABLE customers ADD COLUMN {col_name} {col_type}")
                print(f"Added column {col_name} to customers table")
            except mysql.connector.Error as err:
                print(f"Error adding column {col_name}: {err}")
                return False
    
    # Get all customer IDs
    cursor.execute("SELECT customer_id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    # Update each customer with realistic data
    for customer_id in customer_ids:
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        # Ensure phone number fits within VARCHAR(20) by truncating or simplifying
        phone = fake.phone_number()[:11]  # Limit to 19 chars to fit in VARCHAR(20)
        address = fake.street_address()
        city = fake.city()
        registration_date = fake.date_between(start_date='-5y', end_date='today')
        
        update_query = """
        UPDATE customers
        SET first_name = %s, last_name = %s, email = %s, phone = %s, 
            address = %s, city = %s, registration_date = %s
        WHERE customer_id = %s AND (first_name IS NULL OR first_name = '')
        """
        
        try:
            cursor.execute(update_query, (
                first_name, last_name, email, phone, 
                address, city, registration_date, customer_id
            ))
        except mysql.connector.Error as err:
            print(f"Error updating customer {customer_id}: {err}")
            continue
    
    connection.commit()
    print(f"Updated {len(customer_ids)} customers with realistic data")
    return True

# Function to enrich restaurants table
def enrich_restaurants(connection):
    """Add additional fields to restaurants table and populate with realistic data"""
    if not connection:
        print("No database connection available")
        return False
    
    cursor = connection.cursor()
    
    # First, check if the columns already exist
    cursor.execute("DESCRIBE restaurants")
    columns = [column[0] for column in cursor.fetchall()]
    
    # Add new columns if they don't exist
    new_columns = {
        "address": "VARCHAR(255)",
        "city": "VARCHAR(100)",
        "phone": "VARCHAR(20)",
        "website": "VARCHAR(255)",
        "price_range": "VARCHAR(10)",
        "rating_avg": "DECIMAL(3,2)",
        "opening_hour": "TIME",
        "closing_hour": "TIME",
        "established_date": "DATE"
    }
    
    for col_name, col_type in new_columns.items():
        if col_name not in columns:
            try:
                cursor.execute(f"ALTER TABLE restaurants ADD COLUMN {col_name} {col_type}")
                print(f"Added column {col_name} to restaurants table")
            except mysql.connector.Error as err:
                print(f"Error adding column {col_name}: {err}")
                return False
    
    # Get all restaurant IDs and cuisine types
    cursor.execute("SELECT restaurant_id, restaurant_name, cuisine_type FROM restaurants")
    restaurants = cursor.fetchall()
    
    # Price ranges by cuisine type (more expensive cuisines tend to have higher ranges)
    cuisine_price_ranges = {
        "American": ["$", "$$", "$$$"],
        "Italian": ["$$", "$$$"],
        "Japanese": ["$$", "$$$", "$$$$"],
        "Chinese": ["$", "$$"],
        "Indian": ["$$", "$$$"],
        "Mexican": ["$", "$$"],
        "Thai": ["$$", "$$$"],
        "Mediterranean": ["$$", "$$$"],
        "Middle Eastern": ["$$", "$$$"],
        "Korean": ["$$", "$$$"],
        "French": ["$$$", "$$$$"],
        "Spanish": ["$$", "$$$"],
        "Southern": ["$$", "$$$"]
    }
    
    # Default price range if cuisine not in mapping
    default_price_range = ["$", "$$", "$$$"]
    
    # Update each restaurant with realistic data
    for restaurant_id, restaurant_name, cuisine_type in restaurants:
        address = fake.street_address()
        city = fake.city()
        # Ensure phone number fits within VARCHAR(20)
        phone = fake.phone_number()[:19]
        website = f"www.{restaurant_name.lower().replace(' ', '')}.com"
        
        # Assign price range based on cuisine type
        price_range = random.choice(cuisine_price_ranges.get(cuisine_type, default_price_range))
        
        # Generate realistic ratings (higher for more expensive places)
        base_rating = 3.0
        if price_range == "$":
            rating_avg = round(random.uniform(3.0, 4.2), 2)
        elif price_range == "$$":
            rating_avg = round(random.uniform(3.5, 4.5), 2)
        elif price_range == "$$$":
            rating_avg = round(random.uniform(3.8, 4.7), 2)
        else:  # $$$$
            rating_avg = round(random.uniform(4.0, 4.9), 2)
        
        # Generate business hours (vary by cuisine and price)
        if price_range in ["$$$", "$$$$"]:
            # Upscale restaurants often open later and close later
            opening_hour = f"{random.randint(11, 16)}:00:00"
            closing_hour = f"{random.randint(20, 23)}:00:00"
        else:
            # Casual restaurants tend to have longer hours
            opening_hour = f"{random.randint(7, 12)}:00:00"
            closing_hour = f"{random.randint(20, 22)}:30:00"
        
        # Established date (older for higher rated restaurants)
        years_ago = int((5 - (rating_avg - 3)) * 3)  # Higher rated places tend to be more established
        established_date = fake.date_between(start_date=f'-{years_ago}y', end_date='-1y')
        
        update_query = """
        UPDATE restaurants
        SET address = %s, city = %s, phone = %s, website = %s, 
            price_range = %s, rating_avg = %s, opening_hour = %s, 
            closing_hour = %s, established_date = %s
        WHERE restaurant_id = %s AND (address IS NULL OR address = '')
        """
        
        try:
            cursor.execute(update_query, (
                address, city, phone, website, price_range, 
                rating_avg, opening_hour, closing_hour, 
                established_date, restaurant_id
            ))
        except mysql.connector.Error as err:
            print(f"Error updating restaurant {restaurant_id}: {err}")
            continue
    
    connection.commit()
    print(f"Updated {len(restaurants)} restaurants with realistic data")
    return True

# Function to enhance days table
def enrich_days(connection):
    """Add additional fields to days table with realistic data"""
    if not connection:
        print("No database connection available")
        return False
    
    cursor = connection.cursor()
    
    # First, check if the columns already exist
    cursor.execute("DESCRIBE days")
    columns = [column[0] for column in cursor.fetchall()]
    
    # Add new columns if they don't exist
    new_columns = {
        "is_weekend": "BOOLEAN",
        "is_holiday": "BOOLEAN"
    }
    
    for col_name, col_type in new_columns.items():
        if col_name not in columns:
            try:
                cursor.execute(f"ALTER TABLE days ADD COLUMN {col_name} {col_type}")
                print(f"Added column {col_name} to days table")
            except mysql.connector.Error as err:
                print(f"Error adding column {col_name}: {err}")
                return False
    
    # Get all days
    cursor.execute("SELECT day_id, day_name FROM days")
    days = cursor.fetchall()
    
    # Update each day with additional data
    for day_id, day_name in days:
        is_weekend = 1 if day_name == "Weekend" else 0
        
        # Randomly assign some days as holidays (10% chance)
        is_holiday = 1 if random.random() < 0.1 else 0
        
        update_query = """
        UPDATE days
        SET is_weekend = %s, is_holiday = %s
        WHERE day_id = %s
        """
        
        try:
            cursor.execute(update_query, (is_weekend, is_holiday, day_id))
        except mysql.connector.Error as err:
            print(f"Error updating day {day_id}: {err}")
            continue
    
    connection.commit()
    print(f"Updated {len(days)} days with additional data")
    return True

# Function to add delivery person dimension
def create_delivery_person_table(connection):
    """Create and populate a delivery_person dimension table"""
    if not connection:
        print("No database connection available")
        return False
    
    cursor = connection.cursor()
    
    # Create delivery_person table if it doesn't exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS delivery_person (
        delivery_person_id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        phone VARCHAR(20),
        email VARCHAR(255),
        vehicle_type ENUM('car', 'motorcycle', 'bicycle', 'scooter', 'on foot'),
        hire_date DATE,
        rating DECIMAL(3,2)
    )
    """
    
    try:
        cursor.execute(create_table_query)
        print("Created delivery_person table")
    except mysql.connector.Error as err:
        print(f"Error creating delivery_person table: {err}")
        return False
    
    # Check if table is empty
    cursor.execute("SELECT COUNT(*) FROM delivery_person")
    count = cursor.fetchone()[0]
    
    # Only populate if table is empty
    if count == 0:
        # Generate 50 delivery persons
        for _ in range(50):
            first_name = fake.first_name()
            last_name = fake.last_name()
            # Ensure phone number fits within VARCHAR(20)
            phone = fake.phone_number()[:19]
            email = fake.email()
            vehicle_type = random.choice(['car', 'motorcycle', 'bicycle', 'scooter', 'on foot'])
            hire_date = fake.date_between(start_date='-3y', end_date='today')
            rating = round(random.uniform(3.0, 5.0), 2)
            
            insert_query = """
            INSERT INTO delivery_person 
                (first_name, last_name, phone, email, vehicle_type, hire_date, rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            try:
                cursor.execute(insert_query, (
                    first_name, last_name, phone, email, 
                    vehicle_type, hire_date, rating
                ))
            except mysql.connector.Error as err:
                print(f"Error inserting delivery person: {err}")
                continue
        
        connection.commit()
        print("Added 50 delivery persons to the table")
    else:
        print(f"Delivery person table already contains {count} records")
    
    return True

# Function to modify orders table to include delivery_person_id
def add_delivery_person_to_orders(connection):
    """Add delivery_person_id to orders table and assign values"""
    if not connection:
        print("No database connection available")
        return False
    
    cursor = connection.cursor()
    
    # Check if column already exists
    cursor.execute("DESCRIBE orders")
    columns = [column[0] for column in cursor.fetchall()]
    
    # Add new column if it doesn't exist
    if "delivery_person_id" not in columns:
        try:
            cursor.execute("ALTER TABLE orders ADD COLUMN delivery_person_id INT")
            print("Added delivery_person_id column to orders table")
            
            # Add foreign key constraint
            cursor.execute("""
                ALTER TABLE orders 
                ADD CONSTRAINT fk_delivery_person 
                FOREIGN KEY (delivery_person_id) 
                REFERENCES delivery_person(delivery_person_id)
            """)
            print("Added foreign key constraint for delivery_person_id")
        except mysql.connector.Error as err:
            print(f"Error modifying orders table: {err}")
            return False
    
    # Get all order IDs
    cursor.execute("SELECT order_id FROM orders WHERE delivery_person_id IS NULL")
    orders = cursor.fetchall()
    
    # Get all delivery person IDs
    cursor.execute("SELECT delivery_person_id FROM delivery_person")
    delivery_persons = [row[0] for row in cursor.fetchall()]
    
    if not delivery_persons:
        print("No delivery persons found in the database")
        return False
    
    # Assign delivery persons to orders
    for order_id, in orders:
        delivery_person_id = random.choice(delivery_persons)
        
        update_query = """
        UPDATE orders
        SET delivery_person_id = %s
        WHERE order_id = %s
        """
        
        try:
            cursor.execute(update_query, (delivery_person_id, order_id))
        except mysql.connector.Error as err:
            print(f"Error updating order {order_id}: {err}")
            continue
    
    connection.commit()
    print(f"Assigned delivery persons to {len(orders)} orders")
    return True

# Function to add tip amount to orders
def add_tip_to_orders(connection):
    """Add tip amount to orders table and populate with realistic values"""
    if not connection:
        print("No database connection available")
        return False
    
    cursor = connection.cursor()
    
    # Check if column already exists
    cursor.execute("DESCRIBE orders")
    columns = [column[0] for column in cursor.fetchall()]
    
    # Add new column if it doesn't exist
    if "tip_amount" not in columns:
        try:
            cursor.execute("ALTER TABLE orders ADD COLUMN tip_amount DECIMAL(5,2)")
            print("Added tip_amount column to orders table")
        except mysql.connector.Error as err:
            print(f"Error adding tip_amount column: {err}")
            return False
    
    # Get all orders with their cost
    cursor.execute("SELECT order_id, cost_of_the_order, rating FROM orders WHERE tip_amount IS NULL")
    orders = cursor.fetchall()
    
    # Assign realistic tips based on order cost and rating
    for order_id, cost, rating in orders:
        # Convert Decimal to float for calculations
        if isinstance(cost, object) and hasattr(cost, 'to_float'):  # Some MySQL connector versions use Decimal
            cost_float = float(cost)
        else:
            cost_float = float(cost) if cost is not None else 0.0
            
        # Higher tips for higher ratings and expensive orders
        if rating is None:
            # No rating often means no tip or minimal tip
            base_tip_percentage = random.uniform(0, 0.10)
        elif rating >= 4:
            # Good ratings get good tips
            base_tip_percentage = random.uniform(0.15, 0.25)
        else:
            # Lower ratings get lower tips
            base_tip_percentage = random.uniform(0.05, 0.15)
        
        # Sometimes people don't tip
        if random.random() < 0.05:  # 5% chance of no tip
            tip_amount = 0
        else:
            # Calculate tip with some randomness
            tip_amount = round(cost_float * base_tip_percentage, 2)
            
            # Round tips to common values
            if tip_amount > 0 and tip_amount < 1:
                tip_amount = round(tip_amount * 2) / 2  # Round to nearest 0.50
            elif tip_amount >= 1 and tip_amount < 5:
                tip_amount = round(tip_amount)  # Round to nearest dollar
            elif tip_amount >= 5:
                tip_amount = round(tip_amount / 5) * 5  # Round to nearest $5 for larger tips
        
        update_query = """
        UPDATE orders
        SET tip_amount = %s
        WHERE order_id = %s
        """
        
        try:
            cursor.execute(update_query, (tip_amount, order_id))
        except mysql.connector.Error as err:
            print(f"Error updating order {order_id} with tip: {err}")
            continue
    
    connection.commit()
    print(f"Added tips to {len(orders)} orders")
    return True

# Main function to run all enrichment operations
def enrich_database(host='localhost', user='root', password='password', database='ordersdb'):
    """Run all database enrichment operations"""
    print("Starting database enrichment process...")
    
    # Connect to the database
    connection = connect_to_db(host, user, password, database)
    if not connection:
        return False
    
    try:
        # Create and populate delivery person table
        create_delivery_person_table(connection)
        
        # Enrich existing tables
        enrich_customers(connection)
        enrich_restaurants(connection)
        enrich_days(connection)
        
        # Add delivery person to orders
        add_delivery_person_to_orders(connection)
        
        # Add tip information
        add_tip_to_orders(connection)
        
        print("Database enrichment completed successfully!")
        return True
    
    except Exception as e:
        print(f"Error during database enrichment: {e}")
        return False
    
    finally:
        if connection.is_connected():
            connection.close()
            print("Database connection closed")

# Run the script if executed directly
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Enrich food order database with realistic data')
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--user', default='root', help='Database user')
    parser.add_argument('--password', default='password', help='Database password')
    parser.add_argument('--database', default='ordersdb', help='Database name')
    
    args = parser.parse_args()
    
    print("Database Enrichment Tool")
    print("------------------------")
    print("This script adds realistic data to your food ordering database tables.")
    print("Requirements: mysql-connector-python, faker")
    print("You may need to install these packages: pip install mysql-connector-python faker")
    print()
    
    enrich_database(args.host, args.user, args.password, args.database)
