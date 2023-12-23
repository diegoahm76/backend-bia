#urls
#BandejaTareasPersonaCreate

from django.urls import path
from gestion_documental.views import bandeja_tareas_views as views

urlpatterns = [

    path('create/', views.BandejaTareasPersonaCreate.as_view(),name='crear-bandeja-tareas'),
    #TareasAsignadasCreate
    path('tareas-asignadas/create/', views.TareasAsignadasCreate.as_view(),name='crear-tareas-asignadas'),
    #TareaBandejaTareasPersonaCreate
    path('tarea-bandeja-tareas-persona/create/', views.TareaBandejaTareasPersonaCreate.as_view(),name='crear-tarea-bandeja-tareas-persona'),

]
