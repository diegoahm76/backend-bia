from django.apps import AppConfig


class AlmacenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'almacen'

    def ready(self):
        import almacen.signals.bienes_signals
        import almacen.signals.inventario_signals
        import almacen.signals.solicitudes_signals
