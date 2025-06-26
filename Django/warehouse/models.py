from django.db import models
from django.utils import timezone

# Dimension tables
class DimCustomer(models.Model):
    customer_id = models.IntegerField(primary_key=True)  # From CSV
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    segment = models.CharField(max_length=50, null=True, blank=True)
    registration_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.customer_id)

    class Meta:
        db_table = 'dim_customer'
        verbose_name = 'Dimension Customer'
        verbose_name_plural = 'Dimension Customers'


class DimRestaurant(models.Model):
    restaurant_id = models.AutoField(primary_key=True) # Auto-generated
    restaurant_name = models.CharField(max_length=255)
    cuisine_type = models.CharField(max_length=100)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.restaurant_name

    class Meta:
        db_table = 'dim_restaurant'
        verbose_name = 'Dimension Restaurant'
        verbose_name_plural = 'Dimension Restaurants'
        unique_together = ('restaurant_name', 'cuisine_type')


class DimDate(models.Model):
    date_id = models.AutoField(primary_key=True)
    full_date = models.DateField(unique=True)
    day_of_week = models.CharField(max_length=20)
    month_name = models.CharField(max_length=20)
    quarter = models.IntegerField()
    year = models.IntegerField()

    def __str__(self):
        return str(self.full_date)

    class Meta:
        db_table = 'dim_date'
        verbose_name = 'Dimension Date'
        verbose_name_plural = 'Dimension Dates'


class DimLocation(models.Model):
    location_id = models.AutoField(primary_key=True)
    neighborhood = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.location_id) if not self.city else self.city

    class Meta:
        db_table = 'dim_location'
        verbose_name = 'Dimension Location'
        verbose_name_plural = 'Dimension Locations'


class DimTimeSlot(models.Model):
    time_slot_id = models.AutoField(primary_key=True)
    slot_name = models.CharField(max_length=50, null=True, blank=True) # e.g., "Morning", "Afternoon", "Evening"
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return str(self.time_slot_id) if not self.slot_name else self.slot_name

    class Meta:
        db_table = 'dim_timeslot'
        verbose_name = 'Dimension Time Slot'
        verbose_name_plural = 'Dimension Time Slots'


class DimDeliveryPerson(models.Model):
    delivery_person_id = models.AutoField(primary_key=True)
    delivery_person_name = models.CharField(max_length=255, null=True, blank=True)
    operation_zone = models.CharField(max_length=100, null=True, blank=True)
    tenure_months = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.delivery_person_id) if not self.delivery_person_name else self.delivery_person_name

    class Meta:
        db_table = 'dim_deliveryperson'
        verbose_name = 'Dimension Delivery Person'
        verbose_name_plural = 'Dimension Delivery People'


# Fact table
class FactOrders(models.Model):
    order_id = models.IntegerField(primary_key=True) # From CSV
    customer = models.ForeignKey(DimCustomer, on_delete=models.CASCADE, db_column='customer_id', related_name='orders')
    restaurant = models.ForeignKey(DimRestaurant, on_delete=models.CASCADE, db_column='restaurant_id', related_name='orders')
    delivery_person = models.ForeignKey(DimDeliveryPerson, on_delete=models.CASCADE, null=True, blank=True, db_column='delivery_person_id', related_name='deliveries')
    date = models.ForeignKey(DimDate, on_delete=models.CASCADE, db_column='date_id', related_name='orders')
    location = models.ForeignKey(DimLocation, on_delete=models.CASCADE, null=True, blank=True, db_column='location_id', related_name='orders')
    time_slot = models.ForeignKey(DimTimeSlot, on_delete=models.CASCADE, null=True, blank=True, db_column='time_slot_id', related_name='orders')

    order_date = models.DateField(null=True, blank=True) # Derived from DimDate.full_date
    order_time = models.TimeField(null=True, blank=True) # Not available in CSV, will be null

    order_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    food_preparation_time = models.IntegerField(null=True, blank=True)
    delivery_time = models.IntegerField(null=True, blank=True)
    total_time = models.IntegerField(null=True, blank=True) # Calculated: food_preparation_time + delivery_time

    def __str__(self):
        return f"Order {self.order_id}"

    class Meta:
        db_table = 'fact_orders'
        verbose_name = 'Fact Order'
        verbose_name_plural = 'Fact Orders'

    def save(self, *args, **kwargs):
        if self.food_preparation_time is not None and self.delivery_time is not None:
            self.total_time = self.food_preparation_time + self.delivery_time
        if self.date:
            self.order_date = self.date.full_date
        super().save(*args, **kwargs)
