#urls
#BandejaTareasPersonaCreate

from django.urls import path
from gestion_documental.views import bandeja_tareas_views as views

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
    #ENTREGA 103 REQUERIMIENTO SOBRE PQRSDF
    path('pqrsdf/titular/get/<str:pqr>/',views.PQRSDFPersonaTitularGet.as_view(),name='get-pqrsdf-titular-by-pqr'),
    path('pqrsdf/persona/requerimiento/get/',views.PQRSDFPersonaRequerimientoGet.as_view(),name='get-pqrsdf-requerimiento-by-pqr'),
    path('pqrsdf/detalle-requerimiento/get/<str:pqr>/',views.PQRSDFDetalleRequerimientoGet.as_view(),name='get-pqrsdf-detalle-requerimiento-by-pqr'),
    #RequerimientosPQRSDFGetByPQRSDF
    path('pqrsdf/requerimiento/get/<str:pqr>/',views.RequerimientosPQRSDFGetByPQRSDF.as_view(),name='get-requerimientos-by-pqr')
    #Reasignacion de tarea 
    ]
