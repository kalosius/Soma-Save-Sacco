from django.apps import AppConfig

class ClientsPortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clients_portal'

    def ready(self):
        # Ensure models.py (with signals) is loaded
        import clients_portal.signals 