from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import connection
import sys
import os


class Command(BaseCommand):
    help = 'Setup the complete ETL system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--demo-data',
            action='store_true',
            help='Load demo data after setup',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up Data Warehouse ETL System...'))
        
        try:
            # Step 1: Run migrations
            self.stdout.write('1. Running database migrations...')
            call_command('migrate', verbosity=0)
            call_command('migrate', '--database=olapdb', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✓ Migrations completed'))
            
            # Step 2: Create admin user
            self.stdout.write('2. Creating/verifying admin user...')
            call_command('create_admin', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✓ Admin user ready'))
            
            # Step 3: Load demo data if requested
            if options['demo_data']:
                self.stdout.write('3. Loading demo data...')
                call_command('test_etl', '--sample')
                self.stdout.write('4. Running warehouse ETL...')
                call_command('run_warehouse_etl')
                self.stdout.write(self.style.SUCCESS('✓ Demo data loaded'))
            
            # Step 4: Show completion message
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('🎉 ETL System Setup Complete!'))
            self.stdout.write('='*60)
            self.stdout.write('Next steps:')
            self.stdout.write('1. Start the development server:')
            self.stdout.write('   python manage.py runserver')
            self.stdout.write('2. Access the system at: http://localhost:8000/etl/')
            self.stdout.write('3. Login with: admin/admin')
            self.stdout.write('4. Upload CSV files or view analytics')
            self.stdout.write('\nFor scheduled ETL, run:')
            self.stdout.write('   python manage.py schedule_etl')
            self.stdout.write('='*60)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Setup failed: {str(e)}')
            )
            sys.exit(1)
