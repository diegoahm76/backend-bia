from django.urls import path
from almacen.views import reportes_views as views

urlpatterns = [
    path('entradas-inventario/get-list/', views.EntradasInventarioGetView.as_view(), name='entradas-inventario-get-list'),
    path('movimientos-incautados/get-list/', views.MovimientosIncautadosGetView.as_view(), name='movimientos-incautados-get-list'),
    path('mantenimientos-realizados/get-list/', views.MantenimientosRealizadosGetView.as_view(), name='mantenimientos-realizados-get-list'),


    #Reportes-Movimientos-Inventarios
    path('reporte-movimientos-inventario/get-list/', views.BusquedaGeneralInventario.as_view(), name='reporte-inventario-list'),
    path('busqueda-vehiculos-reporte/get-list/', views.BusquedaVehiculos.as_view(), name='reporte-vehiculos-list'),
    path('busqueda-viajes-agendados/<int:id_hoja_vida_vehiculo>/', views.BusquedaViajesAgendados.as_view(), name='busqueda-viajes-agendados-list'),
    path('historico-viajes-agendados/get-list/', views.HistoricoTodosViajesAgendados.as_view(), name='historico-viajes-agendados-list'),


    
]