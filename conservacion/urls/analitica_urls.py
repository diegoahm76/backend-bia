from django.urls import path
from conservacion.views import analitica_views as views

urlpatterns = [
    # Tablero de Control
    path('tablero-control/get/', views.TableroControlGetView.as_view(), name='tablero-control-get'),
    path('busqueda-bienes-mezclas/get/', views.BienesMezclasFilterGetView.as_view(), name='busqueda-bienes-mezclas'),
    path('historico-movimientos/get/', views.HistoricoMovimientosGetView.as_view(), name='historico-movimientos'),
]