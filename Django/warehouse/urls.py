from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('restaurant-performance/', views.RestaurantPerformanceView.as_view(), name='restaurant_performance'),
    path('customer-patterns/', views.CustomerOrderPatternsView.as_view(), name='customer_patterns'),
    path('delivery-performance/', views.DeliveryPerformanceView.as_view(), name='delivery_performance'),
    path('order-patterns-time/', views.OrderPatternsByTimeView.as_view(), name='order_patterns_time'),
    path('cuisine-popularity/', views.CuisinePopularityView.as_view(), name='cuisine_popularity'),
]
