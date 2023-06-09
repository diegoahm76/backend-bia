from django.urls import path
from transversal.views import notificaciones_views as views

urlpatterns = [
    path('datos-remitente/<int:id>/', views.DatosRemitenteView.as_view(), name='datos-remitente'),
    path('medio-notificacion/', views.MedioNotificacionView.as_view(), name='medio-notificacion/')
    




]