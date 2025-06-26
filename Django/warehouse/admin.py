from django.contrib import admin
from .models import (
    DimCustomer, DimRestaurant, DimDate, DimLocation,
    DimTimeSlot, DimDeliveryPerson, FactOrders
)

@admin.register(DimCustomer)
class DimCustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'customer_name', 'segment', 'registration_date')
    search_fields = ('customer_name', 'segment')
    list_filter = ('segment',)


@admin.register(DimRestaurant)
class DimRestaurantAdmin(admin.ModelAdmin):
    list_display = ('restaurant_id', 'restaurant_name', 'cuisine_type', 'rating_avg')
    search_fields = ('restaurant_name', 'cuisine_type')
    list_filter = ('cuisine_type',)


@admin.register(DimDate)
class DimDateAdmin(admin.ModelAdmin):
    list_display = ('date_id', 'full_date', 'day_of_week', 'month_name', 'quarter', 'year')
    search_fields = ('day_of_week', 'month_name')
    list_filter = ('year', 'quarter', 'day_of_week')


@admin.register(DimLocation)
class DimLocationAdmin(admin.ModelAdmin):
    list_display = ('location_id', 'neighborhood', 'postal_code', 'city', 'region')
    search_fields = ('neighborhood', 'city', 'region')
    list_filter = ('city', 'region')


@admin.register(DimTimeSlot)
class DimTimeSlotAdmin(admin.ModelAdmin):
    list_display = ('time_slot_id', 'slot_name', 'start_time', 'end_time')
    search_fields = ('slot_name',)


@admin.register(DimDeliveryPerson)
class DimDeliveryPersonAdmin(admin.ModelAdmin):
    list_display = ('delivery_person_id', 'delivery_person_name', 'operation_zone', 'tenure_months')
    search_fields = ('delivery_person_name', 'operation_zone')
    list_filter = ('operation_zone',)


@admin.register(FactOrders)
class FactOrdersAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'restaurant', 'order_date', 'order_cost', 'rating')
    search_fields = ('order_id', 'customer__customer_name', 'restaurant__restaurant_name')
    list_filter = ('order_date', 'rating')
    date_hierarchy = 'order_date'
