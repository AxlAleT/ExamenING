def transform_data(extracted_data):
    transformed_data = []

    for record in extracted_data:
        transformed_record = {
            'customer_id': record['customer_id'],
            'restaurant_id': record['restaurant_id'],
            'delivery_person_id': record['delivery_person_id'],
            'date_id': record['date_id'],
            'location_id': record['location_id'],
            'time_slot_id': record['time_slot_id'],
            'order_date': record['order_date'],
            'order_time': record['order_time'],
            'order_cost': float(record['order_cost']),
            'rating': int(record['rating']),
            'food_preparation_time': int(record['food_preparation_time']),
            'delivery_time': int(record['delivery_time']),
            'total_time': int(record['food_preparation_time']) + int(record['delivery_time']),
        }
        transformed_data.append(transformed_record)

    return transformed_data