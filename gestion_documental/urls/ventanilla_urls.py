from django.urls import path
from gestion_documental.views import ventanilla_views as views

urlpatterns = [
     path('personas/autorizacion-notificaciones/<str:id_persona>/', views.AutorizacionNotificaciones.as_view(), name='autorizacion-notificaciones')
]
