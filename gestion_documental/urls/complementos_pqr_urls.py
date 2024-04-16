from django.urls import path
from gestion_documental.views import complementos_pqr_views as views

urlpatterns = [
    path('get-complementos-pqrsdf/', views.ComplementosPQRSDFGet.as_view(), name='get-complementos-pqrsdf'),
    path('create-complemento-pqrsdf/', views.ComplementoPQRSDFCreate.as_view(), name='create-complemento-pqrsdf'),
    path('update-complemento-pqrsdf/', views.ComplementoPQRSDFUpdate.as_view(), name='update-complemento-pqrsdf'),
    path('delete-complemento-pqrsdf/', views.ComplementoPQRSDFDelete.as_view(), name='delete-complemento-pqrsdf'),
    path('radicar-complemento-pqrsdf/', views.RadicarComplementoPQRSDF.as_view(), name='radicar-complemento-pqrsdf'),
    
    #Respuesta a solicitudes pqr
    path('respuesta-solicitud/respuesta-solicitud-pqrsdf/', views.RespuestaSolicitudGet.as_view(), name='respuesta-solicitud-pqrsdf'),
    path('respuesta-solicitud/create-respuesta-solicitud/', views.RespuestaSolicitudCreate.as_view(), name='create-respuesta-solicitud'),
    path('respuesta-solicitud/update-respuesta-solicitud/', views.RespuestaSolicitudUpdate.as_view(), name='update-respuesta-solicitud'),
    path('respuesta-solicitud/delete-respuesta-solicitud/', views.RespuestaSolicitudDelete.as_view(), name='delete-respuesta-solicitud'),
    path('respuesta-solicitud/radicar-respuesta-solicitud/', views.RadicarRespuestaSolicitud.as_view(), name='radicar-respuesta-solicitud'),

    #Respuesta Requerimiento PQRSDF
    #RespuestaRequerimientoSobrePQRSDFCreate
    path('respuesta-requerimiento/create-respuesta-requerimiento/', views.RespuestaRequerimientoSobrePQRSDFCreate.as_view(), name='create-respuesta-requerimiento'),

]