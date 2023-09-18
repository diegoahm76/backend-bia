from django.urls import path
from almacen.views import inventario_views as views

urlpatterns = [
    path('control/activos-fijos/get-list/', views.ControlActivosFijosGetListView.as_view(), name='control-activos-fijos-get-list'),
]