from django.core.management.base import BaseCommand
from django.core.management import call_command
from datetime import datetime, time
import schedule
import time as time_module
import threading
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start the ETL scheduler daemon'

    def add_arguments(self, parser):
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Run as daemon process',
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Run ETL immediately for testing',
        )

    def handle(self, *args, **options):
        if options['test']:
            self.stdout.write("Running ETL for testing...")
            self.run_etl()
            return
            
        self.stdout.write("Starting ETL scheduler...")
        
        # Schedule the ETL to run daily at midnight
        schedule.every().day.at("00:00").do(self.run_etl)
        
        self.stdout.write("ETL scheduled to run daily at midnight")
        
        if options['daemon']:
            self.run_daemon()
        else:
            self.run_interactive()

    def run_etl(self):
        """Run the complete ETL process."""
        try:
            self.stdout.write(f"Starting scheduled ETL at {datetime.now()}")
            
            # Run data warehouse ETL
            call_command('run_warehouse_etl')
            
            self.stdout.write(f"ETL completed successfully at {datetime.now()}")
            logger.info("Scheduled ETL completed successfully")
            
        except Exception as e:
            error_msg = f"Scheduled ETL failed: {str(e)}"
            self.stdout.write(self.style.ERROR(error_msg))
            logger.error(error_msg)

    def run_daemon(self):
        """Run as daemon process."""
        self.stdout.write("Running as daemon process...")
        
        def scheduler_thread():
            while True:
                schedule.run_pending()
                time_module.sleep(60)  # Check every minute
        
        thread = threading.Thread(target=scheduler_thread, daemon=True)
        thread.start()
        
        try:
            # Keep the main thread alive
            while True:
                time_module.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write("\nShutting down scheduler...")

    def run_interactive(self):
        """Run in interactive mode."""
        self.stdout.write("Running in interactive mode. Press Ctrl+C to stop.")
        self.stdout.write("Next run scheduled for midnight.")
        
        try:
            while True:
                schedule.run_pending()
                time_module.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.stdout.write("\nShutting down scheduler...")
