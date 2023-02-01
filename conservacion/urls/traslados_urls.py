from django.urls import path
from conservacion.views import traslados_views as views


urlpatterns = [
    path('traslados/',views.TrasladosCreate.as_view(),name='traslados-viveros'),
    path('traslados/get-inventario-viveros/<str:codigo_bien_entrante>/<str:id_vivero_entrante>/',views.GetItemsInventarioVivero.as_view(),name='get-inventario-viveros'),
]