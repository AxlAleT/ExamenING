from django.db import models

# OLTP Models (ordersdb - default database)
class Customer(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    registration_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'customers'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Restaurant(models.Model):
    restaurant_id = models.AutoField(primary_key=True)
    restaurant_name = models.CharField(max_length=255, null=True, blank=True)
    cuisine_type = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    website = models.URLField(max_length=255, null=True, blank=True)
    price_range = models.CharField(max_length=10, null=True, blank=True)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    opening_hour = models.TimeField(null=True, blank=True)
    closing_hour = models.TimeField(null=True, blank=True)
    established_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'restaurants'

    def __str__(self):
        return self.restaurant_name

class Day(models.Model):
    day_id = models.AutoField(primary_key=True)
    day_name = models.CharField(max_length=50, null=True, blank=True)
    is_weekend = models.BooleanField(null=True, blank=True)
    is_holiday = models.BooleanField(null=True, blank=True)

    class Meta:
        db_table = 'days'

    def __str__(self):
        return self.day_name

class DeliveryPerson(models.Model):
    VEHICLE_CHOICES = [
        ('car', 'Car'),
        ('motorcycle', 'Motorcycle'),
        ('bicycle', 'Bicycle'),
        ('scooter', 'Scooter'),
        ('on foot', 'On Foot'),
    ]
    
    delivery_person_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES, null=True, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'delivery_person'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Order(models.Model):
    order_id = models.IntegerField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, db_column='restaurant_id')
    day = models.ForeignKey(Day, on_delete=models.CASCADE, db_column='day_id')
    cost_of_the_order = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    food_preparation_time = models.IntegerField(null=True, blank=True)
    delivery_time = models.IntegerField(null=True, blank=True)
    delivery_person = models.ForeignKey(DeliveryPerson, on_delete=models.SET_NULL, null=True, blank=True, db_column='delivery_person_id')
    tip_amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return f"Order {self.order_id}"


# Data Warehouse Models (olapdb database)
class DimCustomer(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    segment = models.CharField(max_length=50, null=True, blank=True)
    registration_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'dim_customer'
        app_label = 'core'

    def __str__(self):
        return self.customer_name


class DimRestaurant(models.Model):
    restaurant_id = models.IntegerField(primary_key=True)
    restaurant_name = models.CharField(max_length=255, null=True, blank=True)
    cuisine_type = models.CharField(max_length=100, null=True, blank=True)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'dim_restaurant'
        app_label = 'core'

    def __str__(self):
        return self.restaurant_name


class DimDate(models.Model):
    date_id = models.IntegerField(primary_key=True)
    full_date = models.DateField(null=True, blank=True)
    day_of_week = models.CharField(max_length=20, null=True, blank=True)
    month_name = models.CharField(max_length=20, null=True, blank=True)
    quarter = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'dim_date'
        app_label = 'core'

    def __str__(self):
        return str(self.full_date)


class DimLocation(models.Model):
    location_id = models.IntegerField(primary_key=True)
    neighborhood = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'dim_location'
        app_label = 'core'

    def __str__(self):
        return f"{self.neighborhood}, {self.city}"


class DimTimeslot(models.Model):
    time_slot_id = models.IntegerField(primary_key=True)
    slot_name = models.CharField(max_length=50, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = 'dim_timeslot'
        app_label = 'core'

    def __str__(self):
        return self.slot_name


class DimDeliveryPerson(models.Model):
    delivery_person_id = models.IntegerField(primary_key=True)
    delivery_person_name = models.CharField(max_length=255, null=True, blank=True)
    operation_zone = models.CharField(max_length=100, null=True, blank=True)
    tenure_months = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'dim_deliveryperson'
        app_label = 'core'

    def __str__(self):
        return self.delivery_person_name


class FactOrders(models.Model):
    order_id = models.IntegerField(primary_key=True)
    customer = models.ForeignKey(DimCustomer, on_delete=models.CASCADE, db_column='customer_id')
    restaurant = models.ForeignKey(DimRestaurant, on_delete=models.CASCADE, db_column='restaurant_id')
    delivery_person = models.ForeignKey(DimDeliveryPerson, on_delete=models.CASCADE, db_column='delivery_person_id')
    date = models.ForeignKey(DimDate, on_delete=models.CASCADE, db_column='date_id')
    location = models.ForeignKey(DimLocation, on_delete=models.CASCADE, db_column='location_id')
    time_slot = models.ForeignKey(DimTimeslot, on_delete=models.CASCADE, db_column='time_slot_id')
    order_date = models.DateField(null=True, blank=True)
    order_time = models.TimeField(null=True, blank=True)
    order_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    food_preparation_time = models.IntegerField(null=True, blank=True)
    delivery_time = models.IntegerField(null=True, blank=True)
    total_time = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'fact_orders'
        app_label = 'core'

    def __str__(self):
        return f"Fact Order {self.order_id}"
