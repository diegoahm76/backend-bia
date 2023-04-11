from django.urls import path
from estaciones.views import migracion_estaciones_view as views

urlpatterns = [
    # Historial Alertas
    path('consultar-migracion-estaciones/',
         views.ConsultarMigracion.as_view(), name='consultar-migracion-estaciones'),
    path('consultar-migracion-estaciones-id/<str:pk>/',
         views.ConsultarMigracionId.as_view(), name='consultar-migracion-estaciones-id'),
]