from django.apps import AppConfig


class EcomApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ecom_api'

    def ready(self):                        
        import ecom_api.signals


