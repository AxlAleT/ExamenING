from celery import shared_task
from django.utils import timezone
from .models import ETLJob
from .services import ETLService
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_etl_file_async(etl_job_id):
    """
    Celery task to process ETL file asynchronously.
    """
    try:
        etl_job = ETLJob.objects.get(id=etl_job_id)
        etl_job.status = 'running'
        etl_job.started_at = timezone.now()
        etl_job.save()
        
        etl_service = ETLService()
        result = etl_service.process_csv_file_with_warehouse_etl(etl_job.file_path)
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
        
        # Mark upload as processed
        if hasattr(etl_job, 'dataupload_set'):
            etl_job.dataupload_set.update(processed=True)
        
        logger.info(f"ETL job {etl_job_id} completed successfully. Stats: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"ETL job {etl_job_id} failed: {str(e)}")
        try:
            etl_job = ETLJob.objects.get(id=etl_job_id)
            etl_job.status = 'failed'
            etl_job.error_message = str(e)
            etl_job.completed_at = timezone.now()
            etl_job.save()
        except:
            pass
        raise


@shared_task
def scheduled_etl_processing():
    """
    Scheduled task to process pending ETL jobs.
    This can be used with Celery Beat for periodic processing.
    """
    pending_jobs = ETLJob.objects.filter(status='pending')
    
    for job in pending_jobs:
        process_etl_file_async.delay(job.id)
    
    return f"Triggered processing for {pending_jobs.count()} pending jobs"
