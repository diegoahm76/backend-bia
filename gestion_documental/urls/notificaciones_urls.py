from django.urls import path
from gestion_documental.views import notificaciones_views as views

urlpatterns = [
    # Notificaciones
    path('get-notificaciones/', views.ListaNotificacionesCorrespondencia.as_view(),name='get-notificaiones'),
]