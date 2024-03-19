from django.urls import path
from gestion_documental.views import notificaciones_views as views

urlpatterns = [
    # Notificaciones
    path('get-notificaciones/', views.ListaNotificacionesCorrespondencia.as_view(),name='get-notificaiones'),
    path('get-asignaciones/', views.GetAsignacionesCorrespondencia.as_view(),name='get-asignaciones'),
    path('create-asignacion/', views.CrearAsignacionNotificacion.as_view(),name='create-asignacion'),
]