class FactOrders:
    def __init__(self, order_id, customer_id, restaurant_id, delivery_person_id, date_id, location_id, time_slot_id, order_date, order_time, order_cost, rating, food_preparation_time, delivery_time, total_time):
        self.order_id = order_id
        self.customer_id = customer_id
        self.restaurant_id = restaurant_id
        self.delivery_person_id = delivery_person_id
        self.date_id = date_id
        self.location_id = location_id
        self.time_slot_id = time_slot_id
        self.order_date = order_date
        self.order_time = order_time
        self.order_cost = order_cost
        self.rating = rating
        self.food_preparation_time = food_preparation_time
        self.delivery_time = delivery_time
        self.total_time = total_time

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "restaurant_id": self.restaurant_id,
            "delivery_person_id": self.delivery_person_id,
            "date_id": self.date_id,
            "location_id": self.location_id,
            "time_slot_id": self.time_slot_id,
            "order_date": self.order_date,
            "order_time": self.order_time,
            "order_cost": self.order_cost,
            "rating": self.rating,
            "food_preparation_time": self.food_preparation_time,
            "delivery_time": self.delivery_time,
            "total_time": self.total_time,
        }