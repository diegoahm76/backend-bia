from django.urls import path
from estaciones.views import configuracion_alertas_views as views

urlpatterns=[
    #Configuracion Alertas
    path('consultar-configuracion-alerta/',views.ConsultarAlertaEstacion.as_view(),name='consultarconfalertaestacion'),
    path('crear-configuracion-alerta/',views.CrearAlertaEstacion.as_view(),name='crearconfalertaestacion'),
    path('actualizar-configuracion-alerta/<str:pk>/',views.ActualizarAlertaEstacion.as_view(),name='actualizarconfalertaestacion'),
    path('eliminar-configuracion-alerta/<str:pk>/',views.EliminarAlertaEstacion.as_view(),name='eliminarconfalertaestacion'),
    path('consultar-configuracion-alerta-id/<str:pk>/',views.ConsultarAlertaEstacionId.as_view(),name='consultarconfalertaidestacion'),

]