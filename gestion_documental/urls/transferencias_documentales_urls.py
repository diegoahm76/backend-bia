from django.urls import path
from gestion_documental.views import transferencias_documentales_views as views


urlpatterns = [

    path('get-unidades-organizacionales/', views.GetUnidadesOrganizacionales.as_view(), name='get-unidades-organizacionales'),
    path('get-historico-transferencias/', views.GetHistoricoTransferencias.as_view(), name='get-historico-transferencias'),
    path('get-expedientes-transferidos/<str:id_transferencia_documental>/', views.GetExpedientesTransferidos.as_view(), name='get-expedientes-transferidos'),
    path('get-expedientes-transferir/', views.GetExpedientesATransferir.as_view(), name='get-expedientes-transferir'),
    path('get-permisos-expedientes/<int:id_expediente>/', views.GetPermisosUsuario.as_view(), name='get-permisos-expedientes'),
    path('create-transferencias/', views.CreateTransferencia.as_view(), name='create-transferencias'),

]