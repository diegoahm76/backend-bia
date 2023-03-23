from django.urls import path
from gestion_documental.views import ventanilla_views as views

urlpatterns = [
     path('personas/autorizacion-notificaciones/<str:id_persona>/', views.AutorizacionNotificacionesVentanilla.as_view(), name='autorizacion-notificaciones'),
     path('personas/register-persona-juridica/', views.RegisterPersonaJuridica.as_view(), name='ventanilla-register-persona-juridica'),
     path('personas/register-persona-natural/', views.RegisterPersonaNatural.as_view(), name='ventanilla-register-persona-natural'),
     path('personas/update-persona-juridica/<str:id_persona>/', views.UpdatePersonaJuridicaByVentanilla.as_view(), name='ventanilla-update-persona-juridica'),
     path('personas/update-persona-natural/<str:id_persona>/', views.UpdatePersonaNaturalByVentanilla.as_view(), name='ventanilla-update-persona-natural')
]
