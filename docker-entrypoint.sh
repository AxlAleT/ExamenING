#!/bin/bash

# Exit on any error
set -e

# Function to wait for database
wait_for_db() {
    echo "Waiting for database..."
    while ! nc -z $DB_HOST $DB_PORT; do
        echo "Database is unavailable - sleeping"
        sleep 1
    done
    echo "Database is up - continuing..."
}

# Function to wait for Redis
wait_for_redis() {
    echo "Waiting for Redis..."
    while ! nc -z redis 6379; do
        echo "Redis is unavailable - sleeping"
        sleep 1
    done
    echo "Redis is up - continuing..."
}

# Wait for services
if [ "$1" = "web" ] || [ "$1" = "celery_worker" ] || [ "$1" = "celery_beat" ]; then
    wait_for_db
    wait_for_redis
fi

# Run migrations for web service
if [ "$1" = "web" ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
    python manage.py migrate --database=olapdb --noinput
    
    echo "Collecting static files..."
    python manage.py collectstatic --noinput --clear
    
    echo "Creating default admin user if not exists..."
    python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Created default admin user: admin/admin123')
else:
    print('Admin user already exists')
"
fi

# Execute the command
exec "$@"
