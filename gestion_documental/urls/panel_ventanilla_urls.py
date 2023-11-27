#PQRSDFGet
from django.urls import path

from gestion_documental.views import panel_ventanilla_views as views

urlpatterns = [
    path('estados_solicitudes/get/', views.EstadosSolicitudesGet.as_view(),name='listar-estados_solicitud'),
    path('pqrsdf/get/', views.PQRSDFGet.as_view(),name='listar-pqrs'),
    path('complementos/get/<str:pqr>/', views.PQRSDFGetDetalle.as_view(),name='listar-complementos-pqrs'),

    #SOLICITUD DE DIGITALIZACION
    path('pqrsdf/solicitudd_digitalizacion/create/', views.SolicitudDeDigitalizacionCreate.as_view(),name='crear-solicitud-digitalizacion'),
    path('estado/create/',views.Estados_PQRCreate.as_view(),name='crear-estado-pqrsdf'),

    #COMPLEMENTOS
    path('complementos/digitalizacion/create/',views.SolicitudDeDigitalizacionComplementoCreate.as_view(),name='crear-solicitud-complemento-pqrsdf'),
    path('complementos/anexos/get/<str:pk>/',views.ComplementoPQRSDFInfoAnexosGet.as_view(),name='listar-complemento-anexo'),
    #HISTORICO DE SOLICITUDES 
    path('historico/get/',views.CabezerasPQRSDFGet.as_view(),name='listar-historico-pqrsdf'),
    #Historico_Solicitud_PQRSDFGet,
    path('historico/get/<str:pqr>/',views.Historico_Solicitud_PQRSDFGet.as_view(),name='listar-historico-pqrsdf-detalle'),

    #Informacion de pqrsdf
    path('pqrsdf/anexo/get/<str:pqr>/',views.PQRSDFInfoGet.as_view(),name='get-pqrsdf-id'),
    path('pqrsdf/anexo-documento/get/<str:pk>/',views.PQRSDFAnexoDocumentoDigitalGet.as_view(),name='get-pqrsdf-id'),
    path('pqrsdf/anexo-documento/meta-data/get/<str:pk>/',views.PQRSDFAnexoMetaDataGet.as_view(),name='get-pqrsdf-id'),
    path('complemento-pqrsdf/anexo-documento/get/<str:pk>/',views.ComplementoPQRSDFAnexoDocumentoDigitalGet.as_view(),name='get-dcumento-complemento-id'),
    path('complemento-pqrsdf/anexo-documento/meta-data/get/<str:pk>/',views.ComplementoPQRSDFAnexoMetaDataGet.as_view(),name='get-pqrsdf-id'),

    #ENTREGA 102 ASIGNACION DE PQR
    path('unidades/agrupacion/get/',views.SeccionSubseccionVentanillaGet.as_view(),name='listar-unidades'),
    path('subseccion-grupo/get/<str:uni>/',views.SubseccionGrupoVentanillaGet.as_view(),name='listar-subseccion'),
    path('persona-lider/get/<str:uni>/',views.PersonaLiderUnidadGet.as_view(),name='listar-persona-lider'),
    #AsignacionPQRCreate
    path('asignar-pqrsdf/create/',views.AsignacionPQRCreate.as_view(),name='crear-asignacion-grupo')
    ,

]