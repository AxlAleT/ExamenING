def load_data_to_warehouse(transformed_data, db_connection):
    """
    Load transformed data into the data warehouse.
    
    Parameters:
    transformed_data (list of dict): The data to be loaded into the warehouse.
    db_connection: The database connection object.
    """
    try:
        with db_connection.cursor() as cursor:
            for record in transformed_data:
                # Assuming record is a dictionary with keys matching the fact table columns
                cursor.execute("""
                    INSERT INTO fact_orders (order_id, customer_id, restaurant_id, delivery_person_id, date_id, location_id, time_slot_id, order_date, order_time, order_cost, rating, food_preparation_time, delivery_time, total_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    record['order_id'],
                    record['customer_id'],
                    record['restaurant_id'],
                    record['delivery_person_id'],
                    record['date_id'],
                    record['location_id'],
                    record['time_slot_id'],
                    record['order_date'],
                    record['order_time'],
                    record['order_cost'],
                    record['rating'],
                    record['food_preparation_time'],
                    record['delivery_time'],
                    record['total_time']
                ))
            db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        print(f"Error loading data: {e}")