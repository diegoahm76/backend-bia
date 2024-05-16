#urls
#BandejaTareasPersonaCreate

from django.urls import path
from gestion_documental.views import bandeja_tareas_views as views
from gestion_documental.views import bandeja_tareas_otros_views as views_otros
from gestion_documental.views import bandeja_tareas_tramites_views as views_tramites
from gestion_documental.views import bandeja_tareas_opas_views as views_opas
from gestion_documental.views import bandeja_tareas_documentos_views as views_docs
from pathlib import Path

urlpatterns = [

    path('create/', views.BandejaTareasPersonaCreate.as_view(),name='crear-bandeja-tareas'),
    path('tareas-asignadas/create/', views.TareasAsignadasCreate.as_view(),name='crear-tareas-asignadas'),
    path('tarea-bandeja-tareas-persona/create/', views.TareaBandejaTareasPersonaCreate.as_view(),name='crear-tarea-bandeja-tareas-persona'),
    path('tareas-asignadas/get-by-persona/<str:id>/', views.TareasAsignadasGetByPersona.as_view(),name='get-tareas-asignadas-by-persona'),
    path('pqrsdf/detalle/get-by-id/<str:id>/', views.PQRSDFDetalleGetById.as_view(),name='get-pqrsdf-detalle-by-id'),
    path('tareas-asignada-rechazar/update/<str:pk>/',views.TareasAsignadasRechazarUpdate.as_view(),name='update-tareas-asignadas'),
    path('tareas-asignada-aceptar/update/<str:pk>/',views.TareasAsignadasAceptarUpdate.as_view(),name='update-tareas-asignadas'),
    path('tarea-bandeja-asignacion/update/<str:tarea>/',views.TareaBandejaTareasPersonaUpdate.as_view(),name='update-tarea-bandeja-tareas-persona'),
    path('tareas-asignadas-jus-rechazo/get/<str:id>/',views.TareasAsignadasJusTarea.as_view(),name='update-tareas-asignadas-jus-tarea'),
    path('complemento-tarea/get-by-tarea/<str:tarea>/',views.ComplementoTareaGetByTarea.as_view(),name='get-complemento-tarea-by-tarea'),
    path('complemento/get-detalle-by-id/<str:pk>/',views.ComplementosUsu_PQRGetDetalleById.as_view(),name='get-complemento-tarea-detalle-by-id'),
    path('complemento/get-anexos-by-id/<str:pk>/',views.ComplementoPQRSDFInfoAnexosGet.as_view(),name='get-complemento-tarea-anexos-by-id'),
    path('complemento/get-metadatos-by-anexo/<str:pk>/',views.ComplementoMetaDataGetByIdAnexo.as_view(),name='get-complemento-tarea-metadatos-by-id'),
    path('complemento/get-documento-digital-by-id/<str:pk>/',views.DocumentoDigitalAnexoGet.as_view(),name='get-complemento-tarea-documento-digital-by-id'),
    #ENTREGA 103 REQUERIMIENTO SOBRE PQRSDF
    path('pqrsdf/titular/get/<str:pqr>/',views.PQRSDFPersonaTitularGet.as_view(),name='get-pqrsdf-titular-by-pqr'),
    path('pqrsdf/persona/requerimiento/get/',views.PQRSDFPersonaRequerimientoGet.as_view(),name='get-pqrsdf-requerimiento-by-pqr'),
    path('pqrsdf/detalle-requerimiento/get/<str:pk>/',views.PQRSDFDetalleRequerimientoGet.as_view(),name='get-pqrsdf-detalle-requerimiento-by-pqr'),
    path('pqrsdf/requerimiento/get/<str:pqr>/',views.RequerimientosPQRSDFGetByPQRSDF.as_view(),name='get-requerimientos-by-pqr'),
    path('pqrsdf/requerimiento/create/',views.RequerimientoSobrePQRSDFCreate.as_view(),name='crear-requerimientos-pqrsdf'),
    path('pqrsdf/requerimientos/anexos/get/<str:re>/',views.AnexosFGetByRequerimiento.as_view(),name='listar-anexos-requerimiento'),
    #MetadatosAnexosRequerimientoGetByIdAnexo
    path('pqrsdf/requerimientos/anexos/metadatos/get/<str:pk>/',views.MetadatosAnexosRequerimientoGetByIdAnexo.as_view(),name='listar-metadatos-anexos-requer'),
    #REASIGNACION
    path('unidad-organizacional/persona/get/<str:pk>/',views.UnidadOrganizacionalUsuarioBandeja.as_view(),name='listar-unidad-organizacional-usuario'),
    path('unidad-organizacional/hijas/get/<str:pk>/',views.UnidadOrganizacionalHijasByUnidadId.as_view(),name='listar-unidad-organizacional-hijas'),
    path('unidad-organizacional/persona-lider/get/<str:uni>/',views.PersonaLiderUnidadGetByUnidad.as_view(),name='listar-persona-lider-unidad'),
    path('unidad-organizacional/personas/get/<str:uni>/',views.PersonasUnidadGetByUnidad.as_view(),name='listar-personas-unidad'),
    path('reasignaciones/tareas/create/',views.ReasignacionesTareasCreate.as_view(),name='crear-reasignaciones-tareas'),
    path('reasignaciones/tareas/get/<str:pk>/',views.ReasignacionesTareasgetById.as_view(),name='listar-reasignaciones-tareas'),
    path('reasignaciones/tareas/jus/get/<str:pk>/',views.ReasignacionTareasAsignadasJusTarea.as_view(),name='listar-reasignaciones-tareas-jus'),
    path('seguimiento-tarea/tareas/get/<str:pk>/',views.ReasignacionTareasGetByIdTarea.as_view(),name='listar-reasignaciones-tareas-id'),
    path('seguimiento-tarea/respuesta/pqrsdf/get/<str:pqr>/',views.RespuestaPQRSDFByPQR.as_view(),name='listar-respuesta-pqrsdf'),
    #OTROS
    path('tareas-asignadas/get-otros-by-persona/<str:id>/', views_otros.TareasAsignadasGetOtrosByPersona.as_view(), name='get-tareas-asignadas-otros-by-person'),
    path('detalle-otros/get/<str:id>/', views_otros.DetalleOtrosGet.as_view(), name='get-detalle-otros-by-id'),
    path('otros/anexo/get/<str:pk>/',views_otros.OtrosInfoAnexosGet.as_view(),name='get-otros-anexo'),
    path('otros/anexo/metadatos/get/<str:pk>/', views_otros.OtrosAnexoMetaDataGet.as_view(), name='get-otros-anexo-metadatos'),
    path('tareas-asignadas/otros/rechazar/update/<str:pk>/', views_otros.TareasAsignadasOtrosRechazarUpdate.as_view(), name='update-tareas-asignadas-otros'),
    path('tareas-asignadas/otros/aceptar/update/<str:pk>/', views_otros.TareasAsignadasAceptarOtroUpdate.as_view(), name='update-tareas-asignadas-otros'),
    path('tareas-asignadas/otros/jus/tarea/get/<str:pk>/', views_otros.TareasAsignadasOtroJusTarea.as_view(), name='update-tareas-asignadas-otros'),
    #ReasignacionesTareasOtroCreate
    path('reasignaciones/otros/tareas/create/', views_otros.ReasignacionesTareasOtroCreate.as_view(), name='crear-reasignaciones-tareas-otros'),
    path('reasignaciones/otros/tareas/get/<str:pk>/', views_otros.ReasignacionesOtrosTareasgetById.as_view(), name='listar-reasignaciones-tareas-otros'),
    #TRAMITES
    path('tareas-asignadas/tramites/get-by-persona/<str:id>/', views_tramites.TareasAsignadasGetTramitesByPersona.as_view(), name='get-tareas-asignadas-tr'),
    path('detalle-tramites/get/<str:id>/', views_tramites.DetalleSolicitudesTramitesGet.as_view(), name='get-detalle-tramites-by-id'),
    path('tramites/anexo/get/<str:pk>/', views_tramites.TramitesInfoAnexosGet.as_view(), name='get-tramites-anexo'),
    path('tareas-asignadas/tramites/rechazar/update/<str:pk>/', views_tramites.TareasAsignadasTramitesRechazarUpdate.as_view(), name='update-tareas-asignadas-tram'),
    path('tareas-asignadas/tramites/aceptar/update/<str:pk>/', views_tramites.TareasAsignadasAceptarTramiteUpdate.as_view(), name='update-tareas-asignadas-tram'),
    path('reasignaciones/tramites/tareas/create/',views_tramites.ReasignacionesTareasTramitesCreate.as_view(),name='crear-reasignaciones-tareas-tramites'),
    path('reasignaciones/tramites/tareas/get/<str:pk>/', views_tramites.ReasignacionesTramitesTareasgetById.as_view(), name='listar-reasignaciones-tareas-tramites'),
    path('tramites/anexo/metadatos/get/<str:pk>/', views_tramites.TramitesAnexoMetaDataGet.as_view(), name='get-tramites-anexo-metadatos'),
    path('tareas-asignadas/tramites/jus/tarea/get/<str:pk>/', views_tramites.TareasAsignadasTramitesJusTarea.as_view(), name='update-tareas-asignadas-tr'),
    path('tareas-asignadas/tramites/respuesta/requerimientos/<str:pk>/',views_tramites.RequerimientosTramite.as_view(),name='listar-respuesta-requerimientos'),
    path('tareas-asignadas/tramites/respuesta/anexo/get/<str:pk>/', views_tramites.RespuestaTramitesInfoAnexosGet.as_view(), name='get-respuesta-tramites-anexo'),
    path('tareas-asignadas/tramites/complemento/documento/digital/get/<str:pk>/', views_tramites.ComplementoTramitesAnexoDocumentoDigitalGet.as_view(), name='get-archivo-complemento'),
    path('tareas-asignadas/tramites/respuesta/detalle/get/<str:pk>/', views_tramites.DetalleRespuestaTramitesByIdGet.as_view(), name='get-detalle-respuesta-tramites-by-id'),

    #BANDEJA DE TAREAS DE OPAS
    path('tareas-asignadas/opas/get-by-persona/<str:id>/', views_opas.TareasAsignadasGetOpasByPersona.as_view(), name='get-tareas-asignadas-opas-by-persona'),
    path('detalle-opas/get/<str:id>/', views_opas.DetalleOpaGetbyId.as_view(), name='get-detalle-opas-by-id'),
    path('tareas-asignadas/opas/aceptar/update/<str:pk>/', views_opas.TareasAsignadasAceptarOpaUpdate.as_view(), name='update-tareas-asignadas-opas'),
    path('tareas-asignadas/opas/rechazar/update/<str:pk>/', views_opas.TareasAsignadasOpasRechazarUpdate.as_view(), name='update-tareas-asignadas-opas'),
    path('tareas-asignadas/opas/complemento/tarea/get/<str:tarea>/', views_opas.ComplementoTareaOPAGetByTarea.as_view(), name='get-complemento-tarea-opa'),
    #RespuestaTramitesInfoAnexosGet
    path('tareas-asignadas/opas/respuesta/anexo/get/<str:pk>/', views_opas.RespuestaTramitesOpasInfoAnexosGet.as_view(), name='get-respuesta-opa-anexo'),
    #REQUERIMIENTO A LA OPA
    path('opa/persona/titular/get/<str:tra>/', views_opas.OpaPersonaTitularGet.as_view(), name='get-opa-persona-titular'),
    path('opa/tramite/detalle/get/<str:tra>/', views_opas.OpaTramiteDetalleGet.as_view(), name='get-opa-tramite-detalle'),
    #path('opa/requerimiento/create/', views_opas.RequerimientoSobreOPACreate.as_view(), name='crear-requerimiento-opa'),
    path('opa/requerimiento/tramite/create/', views_opas.RequerimienntoSobreOpaTramiteCreate.as_view(), name='crear-requerimiento-opa-tramite'),
    path('opa/requerimiento/get/<str:tra>/', views_opas.RequerimientosPQRSDFGetByTramiteOPA.as_view(), name='get-requerimiento-opa'),
    path('opa/requerimiento/tramite/get/<str:tra>/', views_opas.RequerimientosTramiteGetByTramiteOPA.as_view(), name='get-requerimiento-opa-tramite'),
    path('opa/requerimiento/anexo/get/<str:re>/', views_opas.AnexosRequerimientoGetByRequerimiento.as_view(), name='get-anexos-requerimiento'),
    
    path('opa/expediente/create/', views_opas.CrearExpedienteOPA.as_view(), name='crear-expediente-opa'),

    path('opa/respuesta/create/', views_opas.RespuestaOpaTramiteCreate.as_view(), name='crear-respuesta-opa-tramite'),
    path('opa/respuesta/get/<str:tra>/', views_opas.RespuestaOpaGet.as_view(), name='get-respuesta-opa-tramite'),
    path('opa/respuesta/anexo/get/<str:pk>/', views_opas.RespestaOpasInfoAnexosGet.as_view(), name='get-anexos-respuesta'),
    
    #RespuestaPQRSDFByTra
    path('opa/respuesta/detalle/get/<str:tra>/', views_opas.RespuestaPQRSDFByTra.as_view(), name='get-respuesta-pqrsdf'),

    #Archivar Otros

    path('archivar/otros/create/', views.ArchiarSolicitudOtros.as_view(), name='crear-archivar-otros'),


    #acta_inicio
    path('4 ', views_opas.ActaInicioCreate.as_view(), name='crear-acta-inicio'),

    #Generador de Documentos
    path('tareas-asignadas/docs/get-by-persona/<str:id>/', views_docs.TareasAsignadasDocsGet.as_view(), name='get-tareas-asignadas-docs-by-persona'),


    
]