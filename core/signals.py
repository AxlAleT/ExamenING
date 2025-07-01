from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def create_default_admin_on_migrate(sender, **kwargs):
    """
    Signal receiver to create default admin user after migrations.
    Only runs for the core app to avoid duplicate creation.
    """
    if sender.name == 'core':
        try:
            # Check if admin user already exists
            if not User.objects.filter(username='admin').exists():
                # Create the admin user
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin',
                    first_name='Admin',
                    last_name='User'
                )
                logger.info(f"Created default admin user via signal: {admin_user.username}")
                print(f"✅ Created default admin user: {admin_user.username}")
            else:
                logger.info("Admin user already exists, skipping creation via signal")
                
        except Exception as e:
            logger.error(f"Error creating admin user via signal: {str(e)}")
            print(f"❌ Error creating admin user: {str(e)}")


@receiver(post_migrate)
def display_admin_info_on_migrate(sender, **kwargs):
    """
    Display admin user information after migrations.
    Only runs for the core app.
    """
    if sender.name == 'core':
        try:
            admin_user = User.objects.get(username='admin')
            print("\n" + "="*50)
            print("🔑 DEFAULT ADMIN USER INFORMATION")
            print("="*50)
            print(f"Username: {admin_user.username}")
            print(f"Email: {admin_user.email}")
            print(f"Password: admin")
            print(f"Full name: {admin_user.first_name} {admin_user.last_name}")
            print(f"Is active: {admin_user.is_active}")
            print(f"Is staff: {admin_user.is_staff}")
            print(f"Is superuser: {admin_user.is_superuser}")
            print("="*50)
            print("You can use these credentials to log in to:")
            print("- Django Admin: /admin/")
            print("- ETL Dashboard: /etl/")
            print("="*50 + "\n")
            
        except User.DoesNotExist:
            logger.warning("Admin user not found after migration")
        except Exception as e:
            logger.error(f"Error displaying admin info: {str(e)}")
