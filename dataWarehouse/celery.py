"""
Celery configuration for dataWarehouse project.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dataWarehouse.settings')

app = Celery('dataWarehouse')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'run-etl-nightly': {
        'task': 'etl.tasks.run_nightly_etl',
        'schedule': 60.0 * 60.0 * 24.0,  # Run every 24 hours
        # 'schedule': crontab(hour=0, minute=0),  # Run at midnight
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
