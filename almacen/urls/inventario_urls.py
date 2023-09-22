from django.urls import path
from almacen.views import inventario_views as views

urlpatterns = [
    # BUSQUEDA BIENES
    path('control/activos-fijos/get-bienes/', views.BusquedaBienesView.as_view(), name='control-activos-fijos-get-bienes'),
    
    # ACTIVOS FIJOS
    path('control/activos-fijos/get-list/', views.ControlActivosFijosGetListView.as_view(), name='control-activos-fijos-get-list'),
    path('control/activos-fijos/get-by-id-bien/<str:id_bien>/', views.ControlActivosFijosGetByIdBienView.as_view(), name='control-activos-fijos-get-by-id-bien'),
]