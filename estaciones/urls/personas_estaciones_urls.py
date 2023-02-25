from django.urls import path
from estaciones.views import personas_estaciones_views as views

urlpatterns=[
    #PersonasEstaciones
    path('consultar-persona/',views.ConsultarPersonaEstacion.as_view(),name='consultarpersonaestacion'),
    path('crear-persona/',views.CrearPersonaEstacion.as_view(),name='crearpersonaestacion'),
    path('actualizar-persona/<str:pk>/',views.ActualizarPersonaEstacion.as_view(),name='actualizarpersonaestacion'),
    path('eliminar-persona/<str:pk>/',views.EliminarPersonaEstacion.as_view(),name='eliminarpersonaestacion'),
    path('consultar-persona-id/<str:pk>/',views.ConsultarPersonaEstacionId.as_view(),name='consultarpersonaidestacion'),

]