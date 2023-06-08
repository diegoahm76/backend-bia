from django.urls import path
from almacen.views import despachos_viveros_views as views

urlpatterns = [
    path('crear-despacho-bienes-de-consumo/', views.CreateDespachoMaestroVivero.as_view(), name='crear-despacho-bienes-de-consumo'),
    path('actualizar-despacho-bienes-de-consumo/', views.ActualizarDespachoConsumo.as_view(), name='actualizar-despacho-bienes-de-consumo'),
    # path('eliminar-items-despacho-bienes-de-consumo/<str:id_despacho_consumo>/', views.EliminarItemsDespachoVivero.as_view(), name='actualizar-despacho-bienes-de-consumo'),
    path('anular-despacho-bienes-de-consumo/<str:despacho_a_anular>/', views.AnularDespachoConsumoVivero.as_view(), name='anular-despacho-bienes-de-consumo')
]
