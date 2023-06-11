from django.urls import path
from transversal.views import notificaciones_views as views

urlpatterns = [
    path('datos-remitente/<int:id>/', views.DatosRemitenteView.as_view(), name='datos-remitente'),
    path('medio-notificacion/', views.MedioNotificacionView.as_view(), name='medio-notificacion'),
    path('crear-notificacion/', views.CrearNotificacionView.as_view(), name='crear-notificacion'),
    path('crear-despacho-notificacion/', views.CrearDespachoNotificacionView.as_view(), name='crear-despacho-notificacion'),
    path('crear-respuesta-notificacion/', views.CrearRespuestaNotificacionView.as_view(), name='crear-respuesta-notificacion'),
    


]