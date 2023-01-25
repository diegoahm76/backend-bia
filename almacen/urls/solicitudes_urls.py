from django.urls import path
from almacen.views import solicitudes_views as views

urlpatterns = [
    path('crear-solicitud-bienes-de-consumo/', views.CreateSolicitud.as_view(), name='crear-solicitud-bienes-de-consumo'),
    path('filtro-bienes-solicitud/', views.FiltroVisibleBySolicitud.as_view(), name='filtro-bienes-solicitud'),
    path('filtro-bienes-solicitable-vivero/', views.FiltroBienSolicitableVivero.as_view(), name='search-viveros'),
    path('get-bien-solicitable-vivero/', views.GetBienSolicitableVivero.as_view(), name='search-viveros'),
    path('get-bienes-solicitud/', views.GetVisibleBySolicitud.as_view(), name='search-viveros'),
    path('get-orgchart-tree/<str:pk>/', views.get_orgchart_tree, name='get-orgchart-tree'),
    path('get-solicitudes-pendientes-por-aprobar/<str:tipodocumento>/<str:numerodocumento>/', views.GetSolicitudesPendentesPorAprobar.as_view(), name='get-solicitudes-pendientes-por-aprobar'),
    path('get-solicitud-by-id/<str:id_solicitud>/', views.GetSolicitudesById_Solicitudes.as_view(), name='get-solicitudes-pendientes-por-aprobar'),
    path('get-nro-documento-solicitudes-bienes-consumo/', views.GetNroDocumentoSolicitudesBienesConsumo.as_view(), name='get-solicitudes-pendientes-por-aprobar'),
    path('SearchViveros', views.GetNroDocumentoSolicitudesBienesConsumo.as_view(), name='get-solicitudes-pendientes-por-aprobar'),
    path('aprobacion-solicitudes-pendientes/<str:id_solicitud>/', views.RevisionSolicitudBienConsumosPorSupervisor.as_view(), name='aprobacion-solicitudes-pendientes-por-aprobar'),
    path('solicitudes-pendientes-por-despachar/', views.SolicitudesPendientesDespachar.as_view(), name='solicitudes-pendientes-por-despachar'),
    path('rechazo-solicitudes-bienes-desde-almacen/<str:id_solicitud>/', views.RechazoSolicitudesBienesAlmacen.as_view(), name='rechazo-solicitudes-bienes-desde-almacen'),
    path('anular-solicitudes-bienes/<str:id_solicitud>/', views.AnularSolicitudesBienesConsumo.as_view(), name='anular-solicitudes-bienes'),
    path('search-funcionario/', views.SearchFuncionarioResponsable.as_view(), name='search-funcionario-responsable')
]