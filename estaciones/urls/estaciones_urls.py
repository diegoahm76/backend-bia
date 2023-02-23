from django.urls import path
from estaciones.views import estaciones_views as views

urlpatterns=[
    #Estaciones
    path('consultar-estaciones/',views.ConsultarEstacion.as_view(),name='consultarestaciones'),
    path('crear-estaciones/',views.CrearEstacion.as_view(),name='crearestaciones'),
    path('actualizar-estaciones/<str:pk>/',views.ActualizarEstacion.as_view(),name='actualizarestaciones'),
    path('eliminar-estaciones/<str:pk>/',views.EliminarEstacion.as_view(),name='eliminarestaciones'),
    path('consultar-estaciones-id/<str:pk>/',views.ConsultarEstacionId.as_view(),name='consultarestacionesid'),
]