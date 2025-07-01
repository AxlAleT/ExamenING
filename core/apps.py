from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Called when the app is ready.
        Import signals here to ensure they're connected.
        """
        import core.signals
