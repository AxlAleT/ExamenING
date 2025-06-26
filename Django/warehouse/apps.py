from django.apps import AppConfig
import os
import sys # Import sys to check arguments

class WarehouseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'warehouse'

    def ready(self):
        """
        Starts the scheduler when the Django app is ready, specifically for the 'runserver' command.
        This helps prevent the scheduler from running multiple times or during other management commands.
        """
        # Check if 'runserver' is in sys.argv and if RUN_MAIN is set (for the main thread of runserver)
        # This is a common pattern for development.
        # For production, especially with multiple workers (Gunicorn/uWSGI),
        # running APScheduler might be handled by a single dedicated worker/process or a different mechanism.

        command = sys.argv[1] if len(sys.argv) > 1 else None

        # Only start scheduler if running `runserver` and in the main process (not reloader)
        if command == 'runserver' and os.environ.get('RUN_MAIN') == 'true':
            from . import scheduler
            scheduler.start()
        # If you need to run with `runserver --noreload`, RUN_MAIN is not set.
        # You might add another condition for that specific case if necessary:
        # elif command == 'runserver' and '--noreload' in sys.argv and not os.environ.get('RUN_MAIN'):
        #     from . import scheduler
        #     scheduler.start()
        # However, the above can lead to multiple schedulers if not careful.
        # The RUN_MAIN check is generally the safest for the auto-reloading runserver.
