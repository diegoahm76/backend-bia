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
    #TareasAsignadasUpdate
    path('tareas-asignada-rechazar/update/<str:pk>/',views.TareasAsignadasRechazarUpdate.as_view(),name='update-tareas-asignadas'),
    path('tareas-asignada-aceptar/update/<str:pk>/',views.TareasAsignadasAceptarUpdate.as_view(),name='update-tareas-asignadas'),
    #TareaBandejaTareasPersonaUpdate
    path('tarea-bandeja-asignacion/update/<str:tarea>/',views.TareaBandejaTareasPersonaUpdate.as_view(),name='update-tarea-bandeja-tareas-persona'),
    ]
