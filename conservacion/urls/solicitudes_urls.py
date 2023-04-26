from django.urls import path
from conservacion.views import solicitudes_views as views 

urlpatterns = [
    path('get-numero-consecutivo/', views.GetNumeroConsecutivoSolicitudView.as_view(), name='get-numero-consecutivo'),
    path('get-solicitud-by-numero-consecutivo/<str:nro_solicitud>/', views.GetSolicitudByNumeroSolicitudView.as_view(), name='get-solicitud-by-numero-consecutivo'),
    path('get-unidad-organizacional/', views.GetUnidadOrganizacionalView.as_view(), name='get-unidad-organizacional'),
    path('get-funcionario-responsable/<str:tipodocumento>/<str:numerodocumento>/', views.GetFuncionarioResponsableView.as_view(), name='get-funcionario-responsable'),
    path('get-funcionario-responsable-by-filters/', views.GetFuncionarioByFiltersView.as_view(), name='get-funcionario-responsable-by-filters'),
    path('create/', views.CreateSolicitudViverosView.as_view(), name='create-solicitud-viveros'),
    path('get-bien-by-codigo/<str:id_vivero>/<str:codigito_bien>/', views.GetBienByCodigoViveroView.as_view(), name='get-bien-by-codigo-solicitud-vivero'),
    path('get-bien-by-codigo/<str:id_vivero>/', views.GetBienByFiltrosView.as_view(), name='get-bien-by-filters'),
    path('get-listar-solicitudes/', views.GetSolicitudesView.as_view(), name='get-listar-solicitudes'),
    path('get-listar-solicitudes-by-id/<str:id_solicitud>/', views.GetItemsSolicitudView.as_view(), name='get-listar-solicitudes-id'),
    path('update-solicitud/<str:id_solicitud>/', views.UpdateSolicitudesView.as_view(), name='update-solicitud'),
    path('update-items-solicitud/<str:id_solicitud>/', views.UpdateItemsSolicitudView.as_view(), name='update-items-solicitud'),
    path('delete-items-solicitud/<str:id_solicitud>/', views.DeleteItemsSolicitudView.as_view(), name='delete-items-solicitud'),
    path('anular-solicitud/<str:solicitudsita>/', views.AnulacionSolicitudesView.as_view(), name='anulacion-solicitud'),

    #Cerrar Solicitud Por No Disponibilidad
    path('cerrar-solicitud/<str:id_solicitud>/', views.CerrarSolicitudNoDisponibilidadView.as_view(), name='cerrar-solicitud'),
]