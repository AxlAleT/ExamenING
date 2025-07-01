from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction


class Command(BaseCommand):
    help = 'Create a default admin user if it does not exist'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Admin username (default: admin)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin',
            help='Admin password (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@example.com',
            help='Admin email (default: admin@example.com)'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Admin',
            help='Admin first name (default: Admin)'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='User',
            help='Admin last name (default: User)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update if user already exists'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        first_name = options['first_name']
        last_name = options['last_name']
        force = options['force']

        try:
            # Check if user already exists
            user = User.objects.get(username=username)
            
            if force:
                # Update existing user
                user.set_password(password)
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated admin user: {username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Admin user "{username}" already exists. Use --force to update.')
                )
                
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created admin user: {username}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating/updating admin user: {str(e)}')
            )
            raise

        # Display user info
        self.stdout.write(f'Admin user details:')
        self.stdout.write(f'  Username: {user.username}')
        self.stdout.write(f'  Email: {user.email}')
        self.stdout.write(f'  Full name: {user.first_name} {user.last_name}')
        self.stdout.write(f'  Is staff: {user.is_staff}')
        self.stdout.write(f'  Is superuser: {user.is_superuser}')
        self.stdout.write(f'  Is active: {user.is_active}')
