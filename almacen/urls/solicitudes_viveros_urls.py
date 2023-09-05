from django.urls import path
from almacen.views import solicitudes_viveros_views as views

urlpatterns = [
    path('crear-solicitud/', views.CreateSolicitudViveros.as_view(), name='crear-solicitud-viveros'),
    path('search-coordinador-viveros/get/', views.SearchCoordinadorViveros.as_view(), name='search-coordinador-viveros'),
    path('get-nro-documento-solicitudes-bienes-consumo-vivero/', views.GetNroDocumentoSolicitudesBienesConsumoVivero.as_view(), name='crear-solicitud-viveros'),
    path('aprobacion-solicitudes-pendientes-vivero/<str:id_solicitud>/', views.RevisionSolicitudBienConsumosViveroPorSupervisor.as_view(), name='aprobacion-solicitudes-pendientes-por-aprobar-vivero'),
]