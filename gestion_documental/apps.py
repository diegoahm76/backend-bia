from django.apps import AppConfig


class GestionDocumentalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion_documental'

    def ready(self):
        import gestion_documental.signals.trd_signals
        import gestion_documental.signals.tca_signals