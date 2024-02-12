#urls
#BandejaTareasPersonaCreate

from django.urls import path
from gestion_documental.views import bandeja_tareas_views as views
from gestion_documental.views import bandeja_tareas_otros_views as views_otros

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
]