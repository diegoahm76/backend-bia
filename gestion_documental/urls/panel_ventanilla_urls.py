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
    path('asignar-pqrsdf/create/',views.AsignacionPQRCreate.as_view(),name='crear-asignacion-grupo'),

    path('asignar-pqrsdf/update/<str:pk>/',views.AsignacionPQRUpdate.as_view(),name='actualizar-asignacion-grupo'),
    path('asignar-pqrsdf/get/<str:pqr>/',views.AsignacionPQRGet.as_view(),name='listar-asignacion-grupo'),
    path('asignacion-opas/get/<str:tra>/',views.AsignacionOPASGet.as_view(),name='listar-asignacion-otros'),
    
    #ENTREGA 99 
    path('pqrsdf/titular/get/<str:pqr>/',views.PQRSDFPersonaTitularGet.as_view(),name='listar-persona-titular-pqrsdf'),

    path('pqrsdf/solicita/get/',views.PQRSDFPersonaSolicitaGet.as_view(),name='listar-persona-solicita-pqrsdf'),
    path('pqrsdf/detalle-solicitud/get/<str:pqr>/',views.PQRSDFDetalleSolicitudGet.as_view(),name='listar-detalle-pqrsdf'),
    path('pqrsdf/solicitud-al-usuario/create/',views.SolicitudAlUsuarioSobrePQRSDFCreate.as_view(),name='crear-solicitud-al-usuario-pqrsdf'),
    path('pqrsdf/anexo/meta-data/create/',views.MetadatosAnexosTmpCreate.as_view(),name='crear-metadatos-anexos-tmp'),
    path('pqrsdf/anexo/create/',views.AnexosCreate.as_view(),name='crear-anexos'),
    path('pqrsdf/solicitud-usuario/get/<str:pqr>/',views.SolicitudAlUsuarioSobrePQRSDFGetByPQRS.as_view(),name='listar-solicitud-al-usuario-pqrsdf'),
    path('pqrsdf/solicitud/anexos/get/<str:soli>/',views.SolicitudAlUsuarioSobrePQRSDAnexosFGetByPQRS.as_view(),name='listar-anexos-solicitud'),
    path('pqrsdf/solicitud/get/id/<str:pk>/',views.SolicitudAlUsuarioSobrePQRSDFGetById.as_view(),name='listar-solicitud-id'),
    #MetadatosAnexosTmpFGetByIdAnexo
    path('pqrsdf/solicitud/anexos/meta-data/get/<str:pk>/',views.MetadatosAnexosTmpFGetByIdAnexo.as_view(),name='listar-meta-data_anexo'),
    
    path('pqrsdf/archivo/create/',views.VistaCreadoraArchivo3.as_view(),name='crear-archivo'),

    #ARREGLOS ENTREGA 107
    path('pqrsdf/denuncias/get/<str:pqr>/',views.InfoDenuncias_PQRSDFGetByPQRSDF.as_view(),name='listar-denuncias-pqrsdf'),
    path('opas/tramite/get/',views.TramiteListOpasGetView.as_view(),name='listar-tramite-opas'),
    path('pqrsdf/asignacion/grupo/update/<str:pk>/',views.ComplementosUsu_PQRPut.as_view(),name='actualizar-asignacion-grupo'),
    #OPAS
    #SolicitudDeDigitalizacionOPACreate
    path('opas/solicitud_digitalizacion/create/',views.SolicitudDeDigitalizacionOPACreate.as_view(),name='crear-solicitud-opas'),
    path('opas/historico/get/',views.OPAFGetHitorico.as_view(),name='listar-historico-opas'),
    #AsignacionOPACreate
    path('opas/asignacion/create/',views.AsignacionOPACreate.as_view(),name='crear-asignacion-opas'),

    
    # OTROS
    path('otros/get/', views.OtrosGet.as_view(),name='listar-otros'),
    path('otros/estados_solicitudes/get/', views.OtrosEstadosSolicitudesGet.as_view(),name='listar-estados-solicitud-otros'),
    path('otros/solicitudd_digitalizacion/create/', views.OtrosSolicitudDeDigitalizacionCreate.as_view(),name='crear-solicitud-digitalizacion-otros'),
    path('otros/anexo/get/<str:id_otros>/',views.OtrosInfoGet.as_view(),name='get-otros-anexo'),
    path('asignar-otros/create/',views.AsignacionOtrosCreate.as_view(),name='crear-asignacion-grupo-otros'),
    path('asignar-otros/get/<str:id_otros>/',views.AsignacionOtrosGet.as_view(),name='listar-asignacion-grupo-otros'),
    path('otros/historico/get/',views.OtrosGetHistorico.as_view(),name='listar-historico-opas'),

]