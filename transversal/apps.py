from django.apps import AppConfig


class TransversalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transversal'
    
    def ready(self):
        import transversal.signals.organigrama_signals
        import transversal.signals.personas_signals