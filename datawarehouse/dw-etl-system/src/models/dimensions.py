class Dimension:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class DimCustomer(Dimension):
    def __init__(self, customer_id, customer_name, segment, registration_date):
        super().__init__(customer_id, customer_name)
        self.segment = segment
        self.registration_date = registration_date

class DimRestaurant(Dimension):
    def __init__(self, restaurant_id, restaurant_name, cuisine_type, rating_avg):
        super().__init__(restaurant_id, restaurant_name)
        self.cuisine_type = cuisine_type
        self.rating_avg = rating_avg

class DimDate(Dimension):
    def __init__(self, date_id, full_date, day_of_week, month_name, quarter, year):
        super().__init__(date_id, full_date)
        self.day_of_week = day_of_week
        self.month_name = month_name
        self.quarter = quarter
        self.year = year

class DimLocation(Dimension):
    def __init__(self, location_id, neighborhood, postal_code, city, region):
        super().__init__(location_id, neighborhood)
        self.postal_code = postal_code
        self.city = city
        self.region = region

class DimTimeslot(Dimension):
    def __init__(self, time_slot_id, slot_name, start_time, end_time):
        super().__init__(time_slot_id, slot_name)
        self.start_time = start_time
        self.end_time = end_time

class DimDeliveryPerson(Dimension):
    def __init__(self, delivery_person_id, delivery_person_name, operation_zone, tenure_months):
        super().__init__(delivery_person_id, delivery_person_name)
        self.operation_zone = operation_zone
        self.tenure_months = tenure_months