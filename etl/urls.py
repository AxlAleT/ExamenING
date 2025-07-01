from django.urls import path
from . import views

app_name = 'etl'

urlpatterns = [
    path('', views.etl_dashboard, name='dashboard'),
    path('upload/', views.upload_file, name='upload_file'),
    path('process-csv/', views.process_csv_data, name='process_csv_data'),
    path('job/<int:job_id>/status/', views.job_status, name='job_status'),
    path('upload/<int:upload_id>/process/', views.trigger_manual_processing, name='trigger_manual_processing'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('export/', views.export_data, name='export_data'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
