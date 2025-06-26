from django.db import models

# Dimension tables
class DimCustomer(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    customer_name = models.CharField(max_length=255)
    segment = models.CharField(max_length=50)
    registration_date = models.DateField()

    def __str__(self):
        return self.customer_name

    class Meta:
        db_table = 'dim_customer'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'


class DimRestaurant(models.Model):
    restaurant_id = models.IntegerField(primary_key=True)
    restaurant_name = models.CharField(max_length=255)
    cuisine_type = models.CharField(max_length=100)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return self.restaurant_name

    class Meta:
        db_table = 'dim_restaurant'
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'


class DimDate(models.Model):
    date_id = models.IntegerField(primary_key=True)
    full_date = models.DateField()
    day_of_week = models.CharField(max_length=20)
    month_name = models.CharField(max_length=20)
    quarter = models.IntegerField()
    year = models.IntegerField()

    def __str__(self):
        return str(self.full_date)

    class Meta:
        db_table = 'dim_date'
        verbose_name = 'Date'
        verbose_name_plural = 'Dates'


class DimLocation(models.Model):
    location_id = models.IntegerField(primary_key=True)
    neighborhood = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.neighborhood}, {self.city}"

    class Meta:
        db_table = 'dim_location'
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'


class DimTimeslot(models.Model):
    time_slot_id = models.IntegerField(primary_key=True)
    slot_name = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.slot_name

    class Meta:
        db_table = 'dim_timeslot'
        verbose_name = 'Time Slot'
        verbose_name_plural = 'Time Slots'


class DimDeliveryPerson(models.Model):
    delivery_person_id = models.IntegerField(primary_key=True)
    delivery_person_name = models.CharField(max_length=255)
    operation_zone = models.CharField(max_length=100)
    tenure_months = models.IntegerField()

    def __str__(self):
        return self.delivery_person_name

    class Meta:
        db_table = 'dim_deliveryperson'
        verbose_name = 'Delivery Person'
        verbose_name_plural = 'Delivery People'


# Fact table
class FactOrders(models.Model):
    order_id = models.IntegerField(primary_key=True)
    customer = models.ForeignKey(DimCustomer, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(DimRestaurant, on_delete=models.CASCADE, related_name='orders')
    delivery_person = models.ForeignKey(DimDeliveryPerson, on_delete=models.CASCADE, related_name='deliveries')
    date = models.ForeignKey(DimDate, on_delete=models.CASCADE, related_name='orders')
    location = models.ForeignKey(DimLocation, on_delete=models.CASCADE, related_name='orders')
    time_slot = models.ForeignKey(DimTimeslot, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateField()
    order_time = models.TimeField()
    order_cost = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.IntegerField()
    food_preparation_time = models.IntegerField()
    delivery_time = models.IntegerField()
    total_time = models.IntegerField()

    def __str__(self):
        return f"Order {self.order_id}"

    class Meta:
        db_table = 'fact_orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
