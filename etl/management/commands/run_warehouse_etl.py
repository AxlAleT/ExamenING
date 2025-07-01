from django.core.management.base import BaseCommand
from etl.warehouse_etl import DataWarehouseETL
from etl.models import ETLJob
from django.utils import timezone
import sys


class Command(BaseCommand):
    help = 'Run data warehouse ETL process to extract from OLTP and load into OLAP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force run even if recent job exists',
        )

    def handle(self, *args, **options):
        # Check for recent ETL jobs unless forced
        if not options['force']:
            recent_job = ETLJob.objects.filter(
                name__contains='Data Warehouse ETL',
                status='completed',
                completed_at__gte=timezone.now() - timezone.timedelta(hours=1)
            ).first()
            
            if recent_job:
                self.stdout.write(
                    self.style.WARNING(
                        'Recent data warehouse ETL job found. Use --force to override.'
                    )
                )
                return
        
        # Create ETL job record
        etl_job = ETLJob.objects.create(
            name=f"Data Warehouse ETL - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}",
            status='running',
            started_at=timezone.now()
        )
        
        self.stdout.write("Starting data warehouse ETL process...")
        
        try:
            warehouse_etl = DataWarehouseETL()
            stats = warehouse_etl.run_full_etl()
            
            # Update job with results
            total_processed = sum(table_stats['processed'] for table_stats in stats.values())
            total_inserted = sum(table_stats['inserted'] for table_stats in stats.values())
            total_updated = sum(table_stats['updated'] for table_stats in stats.values())
            total_errors = sum(table_stats['errors'] for table_stats in stats.values())
            
            etl_job.records_processed = total_processed
            etl_job.records_inserted = total_inserted
            etl_job.records_updated = total_updated
            etl_job.records_errored = total_errors
            etl_job.status = 'completed'
            etl_job.completed_at = timezone.now()
            etl_job.save()
            
            self.display_detailed_stats(stats)
            self.stdout.write(
                self.style.SUCCESS('Data warehouse ETL process completed successfully!')
            )
            
        except Exception as e:
            # Update job status
            etl_job.status = 'failed'
            etl_job.error_message = str(e)
            etl_job.completed_at = timezone.now()
            etl_job.save()
            
            self.stdout.write(
                self.style.ERROR(f'Data warehouse ETL process failed: {str(e)}')
            )
            sys.exit(1)

    def display_detailed_stats(self, stats):
        """Display detailed statistics for each table."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("DATA WAREHOUSE ETL STATISTICS")
        self.stdout.write("="*60)
        
        for table_name, table_stats in stats.items():
            self.stdout.write(f"\n{table_name.upper()}:")
            self.stdout.write(f"  Processed: {table_stats['processed']}")
            self.stdout.write(f"  Inserted:  {table_stats['inserted']}")
            self.stdout.write(f"  Updated:   {table_stats['updated']}")
            self.stdout.write(f"  Errors:    {table_stats['errors']}")
        
        # Calculate totals
        total_processed = sum(table_stats['processed'] for table_stats in stats.values())
        total_inserted = sum(table_stats['inserted'] for table_stats in stats.values())
        total_updated = sum(table_stats['updated'] for table_stats in stats.values())
        total_errors = sum(table_stats['errors'] for table_stats in stats.values())
        
        self.stdout.write("\n" + "-"*60)
        self.stdout.write("TOTALS:")
        self.stdout.write(f"  Total Processed: {total_processed}")
        self.stdout.write(f"  Total Inserted:  {total_inserted}")
        self.stdout.write(f"  Total Updated:   {total_updated}")
        self.stdout.write(f"  Total Errors:    {total_errors}")
        self.stdout.write("="*60)
