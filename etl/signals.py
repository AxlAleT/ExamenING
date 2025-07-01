from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from .models import DataUpload, ETLJob
from .services import ETLService
from .tasks import process_etl_file_async
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DataUpload)
def trigger_etl_processing(sender, instance, created, **kwargs):
    """
    Signal handler to automatically trigger ETL processing when a file is uploaded.
    """
    if created and not instance.processed:
        logger.info(f"New file uploaded: {instance.original_filename}. Triggering ETL processing.")
        
        # Create ETL job
        etl_job = ETLJob.objects.create(
            name=f"Process {instance.original_filename}",
            file_path=instance.get_file_path(),
            status='pending'
        )
        
        # Link upload to job
        instance.etl_job = etl_job
        instance.save(update_fields=['etl_job'])
        
        # Trigger async processing (if Celery is available)
        try:
            process_etl_file_async.delay(etl_job.id)
        except Exception as e:
            logger.warning(f"Celery not available, processing synchronously: {e}")
            # Process synchronously as fallback
            process_etl_file_sync(etl_job.id)


def process_etl_file_sync(etl_job_id):
    """
    Process ETL file synchronously.
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
