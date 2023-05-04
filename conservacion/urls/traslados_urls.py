from django.urls import path
from conservacion.views import traslados_views as views


urlpatterns = [
    path('create-traslados/',views.TrasladosCreate.as_view(),name='crear-traslados-viveros'),
    path('actualizar-traslados/',views.TrasladosActualizar.as_view(),name='actualizar-traslados-viveros'),
    path('anular-traslados/<str:id_traslado_a_anular>/',views.TrasladosAnular.as_view(),name='anular-traslados-viveros'),
    path('get-inventario-viveros/<str:codigo_bien_entrante>/<str:id_vivero_entrante>/',views.GetItemsInventarioVivero.as_view(),name='get-inventario-viveros'),
    path('filter-inventario-viveros/<str:id_vivero_entrante>/',views.FilterInventarioVivero.as_view(),name='filter-inventario-viveros'),
    path('get-traslados-por-nro-traslado/<str:nro_traslado_entrante>/',views.GetTrasladosByIdTraslados.as_view(),name='get-traslado-por-nro-traslado'),
    path('busqueda-avanzada-traslados/',views.GetAvanzadoTraslados.as_view(),name='get-avanzado-traslados'),
    path('get-items-traslado/<str:id_traslado_entrante>/',views.GetItemsTrasladoByIdTraslado.as_view(),name='get-items-traslado'),
]