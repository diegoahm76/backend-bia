from django.urls import path
from conservacion.views import despachos_views as views

urlpatterns = [
    # Recepción y Distribución
    path('guardar/<str:id_despacho_entrante>/', views.GuardarDistribucionBienes.as_view(), name='guardar-distribucion'),
    path('get-list/', views.GetDespachosEntrantes.as_view(), name='get-list-despachos'),
    path('items-despacho/get-by-id/<str:pk>/', views.GetItemsDespachosEntrantes.as_view(), name='get-items-despachos'),
    path('confirmar-distribucion/<str:id_despacho_entrante>/',views.ConfirmarDistribucion.as_view(),name='confirmar-distribucion'),
    path('get-obtener-items-predistribuidos/<str:pk>/',views.GetItemsPredistribuidos.as_view(),name='get-obtener-items-predistribuidos'),
    
    # Despachos de viveros
    path('registrar-despacho-viveros/', views.CreateDespacho.as_view(), name='registrar-despacho-viveros'),
    path('update-despacho-viveros/', views.UpdatePreparacionMezclas.as_view(), name='update-despacho-viveros'),
    path('anular-despacho-viveros/<str:id_despacho_anular>/', views.AnularPreparacionMezclas.as_view(), name='anular-despacho-viveros'),
    path('get-solicitudes-por-nro-despacho-y-id-vivero/',views.GetSolicitudesVivero.as_view(),name='get-solicitudes-por-id-vivero'),
    path('get-ultimo-nro-despacho-viveros/',views.GetNroDespachoViveros.as_view(),name='get-ultimo-nro-despacho-viveros'),
    path('get-items_solicitud/<str:id_solicitud_viveros>/',views.GetItemsSolicitud.as_view(),name='get-items_solicitud'),
    path('get-insumo/<str:id_vivero>/<str:codigo_insumo>/',views.GetInsumo.as_view(),name='get-insumo'),
    path('get-planta/',views.GetPlanta.as_view(),name='get-planta'),
    path('get-despachos/',views.GetDespachosVivero.as_view(),name='get-despachos'),
    path('get-items-despacho/<str:id_despacho_vivero>/',views.GetItemsDespacho.as_view(),name='get-items-despacho'),
]