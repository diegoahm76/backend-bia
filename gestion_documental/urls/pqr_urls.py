from django.urls import path
from gestion_documental.views import pqr_views as views


urlpatterns = [

    path('tipos_pqr/get/<str:pk>/', views.TiposPQRGet.as_view(), name='get-tipos-radicado'),
    path('tipos_pqr/update/<str:pk>/', views.TiposPQRUpdate.as_view(), name='update-tipos-radicado'),
    path('get_pqrsdf/<str:id_persona_titular>/', views.GetPQRSDFForStatus.as_view(), name='get-pqrsdf'),
    path('get_pqrsdf-panel/<int:id_PQRSDF>/', views.GetPQRSDFForPanel.as_view(), name='get_pqrsdf-panel'),
    path('crear-pqrsdf/', views.PQRSDFCreate.as_view(), name='crear-pqrsdf'),
    path('update-pqrsdf/', views.PQRSDFUpdate.as_view(), name='update-pqrsdf'),
    path('delete-pqrsdf/', views.PQRSDFDelete.as_view(), name='delete-pqrsdf'),
    path('radicar-pqrsdf/', views.RadicarPQRSDF.as_view(), name='radicar-pqrsdf'),

    
    #Medios_Solicitud
    path('tipos_pqr/crear-medio-solicitud/',views.MediosSolicitudCreate.as_view(), name='crear-medio-solicitud'),
    path('tipos_pqr/buscar-medio-solicitud/',views.MediosSolicitudSearch.as_view(), name='buscar-medio-solicitud'),
    path('tipos_pqr/eliminar-medio-solicitud/<int:id_medio_solicitud>/',views.MediosSolicitudDelete.as_view(), name='eliminar-medio-solicitud'),
    path('tipos_pqr/actualizar-medio-solicitud/<int:id_medio_solicitud>/',views.MediosSolicitudUpdate.as_view(), name='actualizar-medio-solicitud'),

    #Respuesta_Solicitud_PQRSDF
    
    path('crear-respuesta-pqrsdf/', views.RespuestaPQRSDFCreate.as_view(), name='crear-respuesta-pqrsdf'),
    path('get_respuesta_pqrsdf-panel/<int:id_pqrsdf>/', views.GetRespuestaPQRSDFForPanel.as_view(), name='get_respuesta_pqrsdf-panel'),





]