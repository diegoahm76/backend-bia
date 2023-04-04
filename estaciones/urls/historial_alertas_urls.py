from django.urls import path
from estaciones.views import historial_alertas_views as views

urlpatterns = [
    # Historial Alertas
    path('consultar-historial-alertas/<str:pk>/<str:mes>/',
         views.ConsultarDatosAlertas.as_view(), name='consultar-historial-alertas'),
    path('consultar-historial-equipo/<str:pk>/<str:mes>/',
         views.ConsultarDatosEquipos.as_view(), name='consultar-historial-equipo'),
]
