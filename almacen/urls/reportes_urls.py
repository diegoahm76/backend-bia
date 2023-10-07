from django.urls import path
from almacen.views import reportes_views as views

urlpatterns = [
    path('entradas-inventario/get-list/', views.EntradasInventarioGetView.as_view(), name='entradas-inventario-get-list'),
    path('movimientos-incautados/get-list/', views.MovimientosIncautadosGetView.as_view(), name='movimientos-incautados-get-list'),
    # path('mantenimientos-realizados/get-list/', views.MantenimientosRealizadosGetView.as_view(), name='mantenimientos-realizados-get-list'),
]