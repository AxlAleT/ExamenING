from django.shortcuts import render
from django.db.models import Count, Avg, Sum
from django.views.generic import TemplateView, ListView
from .models import (
    FactOrders, DimCustomer, DimRestaurant,
    DimDeliveryPerson, DimDate, DimTimeslot, DimLocation
)

class DashboardView(TemplateView):
    """Main dashboard view displaying overview statistics"""
    template_name = 'warehouse/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Count of total orders
        context['total_orders'] = FactOrders.objects.count()

        # Average order cost
        context['avg_order_cost'] = FactOrders.objects.aggregate(avg=Avg('order_cost'))['avg'] or 0

        # Average delivery time
        context['avg_delivery_time'] = FactOrders.objects.aggregate(avg=Avg('delivery_time'))['avg'] or 0

        # Average rating
        context['avg_rating'] = FactOrders.objects.aggregate(avg=Avg('rating'))['avg'] or 0

        # Top 5 restaurants by order count
        context['top_restaurants'] = DimRestaurant.objects.annotate(
            order_count=Count('orders')
        ).order_by('-order_count')[:5]

        # Top 5 customers by order count
        context['top_customers'] = DimCustomer.objects.annotate(
            order_count=Count('orders')
        ).order_by('-order_count')[:5]

        return context

class RestaurantPerformanceView(ListView):
    """View for displaying restaurant performance metrics"""
    template_name = 'warehouse/restaurant_performance.html'
    context_object_name = 'restaurants'

    def get_queryset(self):
        return DimRestaurant.objects.annotate(
            total_orders=Count('orders'),
            avg_preparation_time=Avg('orders__food_preparation_time'),
            avg_delivery_time=Avg('orders__delivery_time'),
            avg_rating=Avg('orders__rating'),
            total_revenue=Sum('orders__order_cost')
        ).order_by('-total_orders')

class CustomerOrderPatternsView(ListView):
    """View for displaying customer order patterns"""
    template_name = 'warehouse/customer_patterns.html'
    context_object_name = 'customers'

    def get_queryset(self):
        return DimCustomer.objects.annotate(
            total_orders=Count('orders'),
            total_spent=Sum('orders__order_cost'),
            avg_order_value=Avg('orders__order_cost'),
            avg_rating_given=Avg('orders__rating')
        ).order_by('-total_orders')

class DeliveryPerformanceView(TemplateView):
    """View for displaying delivery performance by zone"""
    template_name = 'warehouse/delivery_performance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Group by operation zone
        zones = DimDeliveryPerson.objects.values('operation_zone').annotate(
            total_deliveries=Count('deliveries'),
            avg_delivery_time=Avg('deliveries__delivery_time'),
            avg_rating=Avg('deliveries__rating')
        ).order_by('operation_zone')

        context['zones'] = zones
        return context

class OrderPatternsByTimeView(TemplateView):
    """View for displaying order patterns by time"""
    template_name = 'warehouse/order_patterns_time.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get orders by time slot and day of week
        time_patterns = (
            FactOrders.objects
            .values('time_slot__slot_name', 'date__day_of_week')
            .annotate(
                total_orders=Count('order_id'),
                total_revenue=Sum('order_cost'),
                avg_total_time=Avg('total_time')
            )
            .order_by('date__day_of_week', 'time_slot__slot_name')
        )

        context['time_patterns'] = time_patterns
        return context

class CuisinePopularityView(TemplateView):
    """View for displaying cuisine popularity by location"""
    template_name = 'warehouse/cuisine_popularity.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get cuisine popularity by location
        cuisine_location = (
            FactOrders.objects
            .values('location__region', 'location__city', 'restaurant__cuisine_type')
            .annotate(
                order_count=Count('order_id'),
                total_revenue=Sum('order_cost')
            )
            .order_by('location__region', 'location__city', '-order_count')
        )

        context['cuisine_location'] = cuisine_location
        return context
