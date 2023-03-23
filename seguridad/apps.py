from django.apps import AppConfig


class SeguridadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'seguridad'
    
    def ready(self):
        import seguridad.signals.personas_signals
        import seguridad.signals.roles_signals