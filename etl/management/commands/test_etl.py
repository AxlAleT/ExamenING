from django.core.management.base import BaseCommand
from etl.services import ETLService
import sys


class Command(BaseCommand):
    help = 'Test ETL processing with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to CSV file to process',
        )
        parser.add_argument(
            '--sample',
            action='store_true',
            help='Use sample data for testing',
        )

    def handle(self, *args, **options):
        etl_service = ETLService()
        
        if options['file']:
            self.stdout.write(f"Processing file: {options['file']}")
            try:
                result = etl_service.process_csv_file_with_warehouse_etl(options['file'])
                stats = result['etl_stats']
                self.display_stats(stats)
                
                # Display warehouse ETL results if triggered
                if result['warehouse_etl_triggered']:
                    self.stdout.write("\n" + "="*50)
                    if result['warehouse_etl_error']:
                        self.stdout.write(
                            self.style.ERROR(f"Warehouse ETL triggered but failed: {result['warehouse_etl_error']}")
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS("Warehouse ETL triggered and completed successfully")
                        )
                        self.stdout.write(f"Warehouse ETL Job ID: {result.get('job_id')}")
                    self.stdout.write("="*50)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing file: {str(e)}')
                )
                sys.exit(1)
                
        elif options['sample']:
            self.stdout.write("Processing sample data...")
            sample_data = self.get_sample_data()
            try:
                result = etl_service.process_csv_data_with_warehouse_etl(sample_data)
                stats = result['etl_stats']
                self.display_stats(stats)
                
                # Display warehouse ETL results if triggered
                if result['warehouse_etl_triggered']:
                    self.stdout.write("\n" + "="*50)
                    if result['warehouse_etl_error']:
                        self.stdout.write(
                            self.style.ERROR(f"Warehouse ETL triggered but failed: {result['warehouse_etl_error']}")
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS("Warehouse ETL triggered and completed successfully")
                        )
                        self.stdout.write(f"Warehouse ETL Job ID: {result.get('job_id')}")
                    self.stdout.write("="*50)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing sample data: {str(e)}')
                )
                sys.exit(1)
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --file or --sample')
            )
            sys.exit(1)

    def display_stats(self, stats):
        self.stdout.write(
            self.style.SUCCESS('ETL Processing completed!')
        )
        self.stdout.write(f"Records processed: {stats['processed']}")
        self.stdout.write(f"Records inserted: {stats['inserted']}")
        self.stdout.write(f"Records updated: {stats['updated']}")
        self.stdout.write(f"Records skipped: {stats['skipped']}")
        self.stdout.write(f"Records with errors: {stats['errors']}")

    def get_sample_data(self):
        return """order_id,customer_id,restaurant_name,cuisine_type,cost_of_the_order,day_of_the_week,rating,food_preparation_time,delivery_time,cust_first_name,cust_last_name,cust_email,cust_phone,cust_address,cust_city,cust_registration_date,rest_address,rest_city,rest_phone,rest_website,rest_price_range,rest_rating_avg,rest_opening_hour,rest_closing_hour,rest_established_date,is_weekend,is_holiday,del_first_name,del_last_name,del_phone,del_email,del_vehicle,del_hire_date,del_rating,delivery_person_id,tip_amount
1477147,337525,Hangawi,Korean,30.75,Weekend,5,25,20,Kyle,White,hamiltonnicole@example.com,(687)256-0554x974,7620 Morris Curve,North Amanda,2022-11-27,969 Adkins Neck Apt. 368,Port Nicole,523-433-6080,www.hangawi.com,$$,3.27,9:00,22:00,2017-06-10,True,False,Sandra,Simmons,(276)857-0126,johnpace@example.com,scooter,2024-02-14,4.44,13,1.94
1477685,358141,Blue Ribbon Sushi Izakaya,Japanese,12.08,Weekend,4,25,23,Justin,Rodgers,patricia27@example.net,+1-850-777-7203,18692 Nelson Prairie Suite 367,Smithhaven,2023-05-24,96632 Sloan Throughway,West Austinport,001-371-553-3197x59394,www.blueribbonsushiizakaya.com,$$,4.17,9:00,21:00,2021-11-21,True,False,Christopher,Clark,(732)707-2310x226,randy82@example.com,car,2025-01-27,4.98,44,0.4
1477070,66393,Cafe Habana,Mexican,12.23,Weekday,5,23,28,Andrew,Oliver,matthewbaker@example.org,875.996.7988x622,13916 Young Via Suite 741,South Alan,2024-02-16,497 Hannah Wells Apt. 510,Debraport,(779)600-8693x128,www.cafehabana.com,$$,4.1,8:00,23:00,2017-08-28,False,False,Luke,Rivas,878.524.8479x535,weekstara@example.com,scooter,2023-04-02,3.55,39,2.73"""
