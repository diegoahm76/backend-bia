from django.urls import path
from almacen.views import inventario_views as views

urlpatterns = [
    # LISTAS
    path('control/activos-fijos/get-list-origen/', views.OrigenesListGetView.as_view(), name='control-activos-fijos-get-list-origen'),
    
    # BUSQUEDA BIENES
    path('control/activos-fijos/get-bienes/', views.BusquedaBienesView.as_view(), name='control-activos-fijos-get-bienes'),
    path('control/bienes-consumo/get-bienes/', views.BusquedaBienesConsumoView.as_view(), name='control-bienes-consumo-get-bienes'),
    
    # ACTIVOS FIJOS
    path('control/activos-fijos/get-list/', views.ControlActivosFijosGetListView.as_view(), name='control-activos-fijos-get-list'),
    path('control/activos-fijos/get-by-id-bien/<str:id_bien>/', views.ControlActivosFijosGetByIdBienView.as_view(), name='control-activos-fijos-get-by-id-bien'),
    path('control/activos-fijos/get-by-categoria/', views.ControlActivosFijosGetByCategoriaView.as_view(), name='control-activos-fijos-get-by-categoria'),
    path('control/activos-fijos/get-propio/', views.ControlActivosFijosGetPropioView.as_view(), name='control-activos-fijos-get-propio'),
    path('control/activos-fijos/get-by-tipo/', views.ControlActivosFijosGetByTipoView.as_view(), name='control-activos-fijos-get-by-tipo'),
    
    # BIENES DE CONSUMO
    path('control/bienes-consumo/get-list/', views.ControlBienesConsumoGetListView.as_view(), name='control-activos-bienes-consumo-get-list'),
    
    # DESPACHOS
    path('control/despachos/get-list/', views.ControlConsumoBienesGetListView.as_view(), name='control-despachos-get-list'),
]