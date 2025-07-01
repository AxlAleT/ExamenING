#!/usr/bin/env python
"""
Health check script for the Django application.
This script can be used by Docker health checks or monitoring systems.
"""

import sys
import os
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Add the project directory to the Python path
sys.path.append('/app')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dataWarehouse.settings')

# Setup Django
django.setup()

def check_database():
    """Check database connectivity."""
    try:
        from django.db import connections
        from django.db.utils import OperationalError
        
        # Check default database
        db_conn = connections['default']
        db_conn.cursor()
        
        # Check OLAP database
        olap_conn = connections['olapdb']
        olap_conn.cursor()
        
        print("✓ Database connections are healthy")
        return True
    except OperationalError as e:
        print(f"✗ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Database check failed: {e}")
        return False

def check_redis():
    """Check Redis connectivity."""
    try:
        import redis
        from django.core.cache import cache
        
        # Test cache connection
        cache.set('health_check', 'ok', 30)
        value = cache.get('health_check')
        
        if value != 'ok':
            print("✗ Redis cache test failed")
            return False
            
        print("✓ Redis connection is healthy")
        return True
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return False

def check_celery():
    """Check Celery worker connectivity."""
    try:
        from celery import current_app
        
        # Get active workers
        inspect = current_app.control.inspect()
        stats = inspect.stats()
        
        if not stats:
            print("✗ No Celery workers found")
            return False
            
        print(f"✓ Celery workers are healthy ({len(stats)} workers)")
        return True
    except Exception as e:
        print(f"✗ Celery check failed: {e}")
        return False

def check_disk_space():
    """Check available disk space."""
    try:
        import shutil
        
        # Check disk space for media directory
        media_usage = shutil.disk_usage('/app/media')
        media_free_gb = media_usage.free / (1024**3)
        
        # Check disk space for logs directory
        logs_usage = shutil.disk_usage('/app/logs')
        logs_free_gb = logs_usage.free / (1024**3)
        
        min_free_gb = 1.0  # Minimum 1GB free space
        
        if media_free_gb < min_free_gb or logs_free_gb < min_free_gb:
            print(f"✗ Low disk space: media={media_free_gb:.1f}GB, logs={logs_free_gb:.1f}GB")
            return False
            
        print(f"✓ Disk space is healthy: media={media_free_gb:.1f}GB, logs={logs_free_gb:.1f}GB")
        return True
    except Exception as e:
        print(f"✗ Disk space check failed: {e}")
        return False

def main():
    """Run all health checks."""
    print("Starting health checks...")
    
    checks = [
        ("Database", check_database),
        ("Redis", check_redis),
        ("Disk Space", check_disk_space),
    ]
    
    # Only check Celery if we're not in the web container
    container_name = os.environ.get('HOSTNAME', '')
    if 'web' not in container_name:
        checks.append(("Celery", check_celery))
    
    all_healthy = True
    
    for check_name, check_func in checks:
        print(f"\nChecking {check_name}...")
        try:
            if not check_func():
                all_healthy = False
        except Exception as e:
            print(f"✗ {check_name} check failed with exception: {e}")
            all_healthy = False
    
    print(f"\nHealth check summary: {'✓ ALL HEALTHY' if all_healthy else '✗ SOME CHECKS FAILED'}")
    
    # Exit with appropriate code
    sys.exit(0 if all_healthy else 1)

if __name__ == '__main__':
    main()
