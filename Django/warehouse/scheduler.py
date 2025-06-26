from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore, register_events
import logging

logger = logging.getLogger(__name__)

def populate_datawarehouse_job():
    """
    Job function to call the populate_datawarehouse management command.
    """
    try:
        call_command('populate_datawarehouse')
        logger.info("Successfully executed populate_datawarehouse job.")
    except Exception as e:
        logger.error(f"Error running populate_datawarehouse job: {e}", exc_info=True)

def start():
    """
    Starts the APScheduler.
    Adds the populate_datawarehouse_job to run daily at midnight.
    """
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Schedule job to run daily at midnight
    # Use 'cron' trigger for precise scheduling
    # id is important to prevent duplicate jobs if server restarts/reloads code
    # replace_existing=True ensures that if a job with the same ID exists, it's updated
    scheduler.add_job(
        populate_datawarehouse_job,
        trigger='cron',
        hour='0',  # Midnight
        minute='0',
        id='populate_datawarehouse_daily',  # Unique ID for this job
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added daily job: 'populate_datawarehouse_daily'.")

    try:
        logger.info("Starting scheduler...")
        register_events(scheduler) # Needed for DjangoJobStore to work properly with Django signals
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully!")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}", exc_info=True)
