#PQRSDFGet
from django.urls import path

from gestion_documental.views import panel_ventanilla_views as views

urlpatterns = [
    path('estados_solicitudes/get/', views.EstadosSolicitudesGet.as_view(),name='listar-estados_solicitud'),
    path('pqrsdf/get/', views.PQRSDFGet.as_view(),name='listar-pqrs'),
    path('complementos/get/<str:pqr>/', views.PQRSDFGetDetalle.as_view(),name='listar-complementos-pqrs'),

    #SOLICITUD DE DIGITALIZACION
    path('pqrsdf/solicitudd_digitalizacion/create/', views.SolicitudDeDigitalizacionCreate.as_view(),name='crear-solicitud-digitalizacion'),
    path('estado/create/',views.Estados_PQRCreate.as_view(),name='crear-estado-pqrsdf'),

    #COMPLEMENTOS
    path('complementos/digitalizacion/create/',views.SolicitudDeDigitalizacionComplementoCreate.as_view(),name='crear-solicitud-complemento-pqrsdf'),
    #HISTORICO DE SOLICITUDES 
    path('historico/get/',views.CabezerasPQRSDFGet.as_view(),name='listar-historico-pqrsdf'),
    #Historico_Solicitud_PQRSDFGet,
    path('historico/get/<str:pqr>/',views.Historico_Solicitud_PQRSDFGet.as_view(),name='listar-historico-pqrsdf-detalle'),
]