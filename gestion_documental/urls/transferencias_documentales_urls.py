from django.urls import path
from gestion_documental.views import transferencias_documentales_views as views


urlpatterns = [

    path('get-unidades-organizacionales/', views.GetUnidadesOrganizacionales.as_view(), name='get-unidades-organizacionales'),
    path('get-historico-transferencias/', views.GetHistoricoTransferencias.as_view(), name='get-historico-transferencias'),
    path('get-expedientes-transferir/', views.GetExpedientesATransferir.as_view(), name='get-expedientes-transferir'),

]