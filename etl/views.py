from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.utils import timezone
from .models import ETLJob, DataUpload
from .services import ETLService
from .signals import process_etl_file_sync
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncMonth, TruncDate
from core.models import FactOrders, DimCustomer, DimRestaurant, DimDate
import json
import logging

logger = logging.getLogger(__name__)


@login_required
def etl_dashboard(request):
    """Dashboard view to show ETL jobs and upload interface."""
    jobs = ETLJob.objects.all()[:20]  # Show last 20 jobs
    uploads = DataUpload.objects.all()[:10]  # Show last 10 uploads
    
    context = {
        'jobs': jobs,
        'uploads': uploads
    }
    return render(request, 'etl/dashboard.html', context)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def upload_file(request):
    """Handle file upload for ETL processing."""
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)
    
    uploaded_file = request.FILES['file']
    
    # Validate file type
    if not uploaded_file.name.lower().endswith('.csv'):
        return JsonResponse({'error': 'Only CSV files are supported'}, status=400)
    
    try:
        # Create upload record
        data_upload = DataUpload.objects.create(
            file=uploaded_file,
            original_filename=uploaded_file.name
        )
        
        return JsonResponse({
            'success': True,
            'upload_id': data_upload.id,
            'message': 'File uploaded successfully. Processing will begin shortly.'
        })
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return JsonResponse({'error': f'Upload failed: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def process_csv_data(request):
    """Process CSV data directly from POST request."""
    try:
        data = json.loads(request.body)
        csv_data = data.get('csv_data', '')
        
        if not csv_data:
            return JsonResponse({'error': 'No CSV data provided'}, status=400)
        
        # Create ETL job
        etl_job = ETLJob.objects.create(
            name=f"Direct CSV Processing - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}",
            status='running',
            started_at=timezone.now()
        )
        
        # Process data
        etl_service = ETLService()
        result = etl_service.process_csv_data_with_warehouse_etl(csv_data)
        stats = result['etl_stats']
        
        # Update job with results
        etl_job.records_processed = stats['processed']
        etl_job.records_inserted = stats['inserted']
        etl_job.records_updated = stats['updated']
        etl_job.records_skipped = stats['skipped']
        etl_job.records_errored = stats['errors']
        etl_job.status = 'completed'
        etl_job.completed_at = timezone.now()
        
        # Include warehouse ETL results if triggered
        if result['warehouse_etl_triggered']:
            if result['warehouse_etl_error']:
                etl_job.notes = f"Warehouse ETL triggered but failed: {result['warehouse_etl_error']}"
            else:
                etl_job.notes = f"Warehouse ETL triggered and completed successfully. Job ID: {result.get('job_id')}"
        
        etl_job.save()
        
        return JsonResponse({
            'success': True,
            'job_id': etl_job.id,
            'processed': stats['processed'],
            'inserted': stats['inserted'],
            'updated': stats['updated'],
            'skipped': stats['skipped'],
            'errors': stats['errors'],
            'warehouse_etl_triggered': result['warehouse_etl_triggered']
        })
        
    except Exception as e:
        logger.error(f"Error processing CSV data: {str(e)}")
        
        # Update job status if it exists
        if 'etl_job' in locals():
            etl_job.status = 'failed'
            etl_job.error_message = str(e)
            etl_job.completed_at = timezone.now()
            etl_job.save()
        
        return JsonResponse({'error': f'Processing failed: {str(e)}'}, status=500)


@login_required
def job_status(request, job_id):
    """Get status of an ETL job."""
    try:
        job = ETLJob.objects.get(id=job_id)
        
        return JsonResponse({
            'id': job.id,
            'name': job.name,
            'status': job.status,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'records_processed': job.records_processed,
            'records_inserted': job.records_inserted,
            'records_updated': job.records_updated,
            'records_skipped': job.records_skipped,
            'records_errored': job.records_errored,
            'error_message': job.error_message
        })
        
    except ETLJob.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def trigger_manual_processing(request, upload_id):
    """Manually trigger processing for an upload."""
    try:
        upload = DataUpload.objects.get(id=upload_id)
        
        if upload.processed:
            return JsonResponse({'error': 'Upload already processed'}, status=400)
        
        # Create ETL job if not exists
        if not upload.etl_job:
            etl_job = ETLJob.objects.create(
                name=f"Manual Process {upload.original_filename}",
                file_path=upload.get_file_path(),
                status='pending'
            )
            upload.etl_job = etl_job
            upload.save()
        
        # Trigger processing
        process_etl_file_sync(upload.etl_job.id)
        
        return JsonResponse({
            'success': True,
            'job_id': upload.etl_job.id,
            'message': 'Processing triggered successfully'
        })
        
    except DataUpload.DoesNotExist:
        return JsonResponse({'error': 'Upload not found'}, status=404)
    except Exception as e:
        logger.error(f"Error triggering manual processing: {str(e)}")
        return JsonResponse({'error': f'Processing failed: {str(e)}'}, status=500)


@login_required  
def analytics_dashboard(request):
    """Analytics dashboard with data visualizations."""
    try:
        # Get summary statistics
        total_orders = FactOrders.objects.using('olapdb').count()
        total_revenue = FactOrders.objects.using('olapdb').aggregate(
            total=Sum('order_cost')
        )['total'] or 0
        avg_order_value = FactOrders.objects.using('olapdb').aggregate(
            avg=Avg('order_cost')
        )['avg'] or 0
        avg_delivery_time = FactOrders.objects.using('olapdb').aggregate(
            avg=Avg('delivery_time')
        )['avg'] or 0
        
        # Orders by month
        orders_by_month = FactOrders.objects.using('olapdb').annotate(
            month=TruncMonth('order_date')
        ).values('month').annotate(
            count=Count('order_id'),
            revenue=Sum('order_cost')
        ).order_by('month')[:12]
        
        # Top restaurants by revenue
        top_restaurants = FactOrders.objects.using('olapdb').values(
            'restaurant__restaurant_name'
        ).annotate(
            revenue=Sum('order_cost'),
            order_count=Count('order_id')
        ).order_by('-revenue')[:10]
        
        # Orders by cuisine type
        cuisine_stats = FactOrders.objects.using('olapdb').values(
            'restaurant__cuisine_type'
        ).annotate(
            count=Count('order_id'),
            revenue=Sum('order_cost')
        ).order_by('-count')[:10]
        
        # Customer segments
        customer_segments = DimCustomer.objects.using('olapdb').values(
            'segment'
        ).annotate(
            count=Count('customer_id')
        ).order_by('-count')
        
        context = {
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'avg_order_value': float(avg_order_value),
            'avg_delivery_time': float(avg_delivery_time),
            'orders_by_month': list(orders_by_month),
            'top_restaurants': list(top_restaurants),
            'cuisine_stats': list(cuisine_stats),
            'customer_segments': list(customer_segments),
        }
        
        return render(request, 'etl/analytics.html', context)
        
    except Exception as e:
        logger.error(f"Error loading analytics dashboard: {str(e)}")
        messages.error(request, "Error loading analytics data. Please ensure the data warehouse has been populated.")
        return render(request, 'etl/analytics.html', {'error': True})


@login_required
def export_data(request):
    """Export data as CSV."""
    from django.http import HttpResponse
    import csv
    
    export_type = request.GET.get('type', 'orders')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{export_type}_export.csv"'
    
    writer = csv.writer(response)
    
    try:
        if export_type == 'orders':
            # Export fact orders
            writer.writerow([
                'Order ID', 'Customer Name', 'Restaurant Name', 'Order Date', 
                'Order Cost', 'Rating', 'Delivery Time', 'Total Time'
            ])
            
            orders = FactOrders.objects.using('olapdb').select_related(
                'customer', 'restaurant'
            ).all()[:1000]  # Limit to 1000 records
            
            for order in orders:
                writer.writerow([
                    order.order_id,
                    order.customer.customer_name,
                    order.restaurant.restaurant_name,
                    order.order_date,
                    order.order_cost,
                    order.rating,
                    order.delivery_time,
                    order.total_time
                ])
                
        elif export_type == 'restaurants':
            # Export restaurant performance
            writer.writerow([
                'Restaurant Name', 'Cuisine Type', 'Total Orders', 
                'Total Revenue', 'Average Rating'
            ])
            
            restaurant_stats = FactOrders.objects.using('olapdb').values(
                'restaurant__restaurant_name',
                'restaurant__cuisine_type'
            ).annotate(
                order_count=Count('order_id'),
                total_revenue=Sum('order_cost'),
                avg_rating=Avg('rating')
            )
            
            for stat in restaurant_stats:
                writer.writerow([
                    stat['restaurant__restaurant_name'],
                    stat['restaurant__cuisine_type'],
                    stat['order_count'],
                    stat['total_revenue'],
                    stat['avg_rating']
                ])
                
        return response
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        response = JsonResponse({'error': f'Export failed: {str(e)}'}, status=500)
        return response


def login_view(request):
    """Custom login view."""
    if request.user.is_authenticated:
        return redirect('etl:dashboard')
    return auth_views.LoginView.as_view(template_name='registration/login.html')(request)


def logout_view(request):
    """Custom logout view."""
    return auth_views.LogoutView.as_view(next_page='etl:login')(request)
