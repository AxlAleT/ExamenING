from django.apps import AppConfig


class EtlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'etl'
    
    def ready(self):
        # Import signals to register them
        import etl.signals
