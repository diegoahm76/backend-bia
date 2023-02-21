from django.urls import path
from conservacion.views import solicitudes_views as views 

urlpatterns = [
    path('get-numero-consecutivo/', views.GetNumeroConsecutivoSolicitudView.as_view(), name='get-numero-consecutivo'),
    path('get-solicitud-by-numero-consecutivo/<str:nro_solicitud>/', views.GetSolicitudByNumeroSolicitudView.as_view(), name='get-solicitud-by-numero-consecutivo'),
    path('get-unidad-organizacional/', views.GetUnidadOrganizacionalView.as_view(), name='get-unidad-organizacional'),
    path('get-funcionario-responsable/<str:tipodocumento>/<str:numerodocumento>/', views.GetFuncionarioResponsableView.as_view(), name='get-funcionario-responsable'),
    path('create/', views.GetFuncionarioResponsableView.as_view(), name='create-solicitud-viveros'),
]
