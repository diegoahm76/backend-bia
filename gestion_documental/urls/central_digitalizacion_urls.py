from django.urls import path

from gestion_documental.views import central_digitalizacion_views as views


urlpatterns = [
    path('get-solicitudes-pendientes/', views.SolicitudesPendientesGet.as_view(), name='get-solicitudes-pendientes'),
    path('get-solicitudes-respondidas/', views.SolicitudesRespondidasGet.as_view(), name='get-solicitudes-respondidas'),
    path('get-solicitudes-by-id/<int:id_solicitud>/', views.SolicitudByIdGet.as_view(), name='get-solicitudes-respondidas'),
    path('crear-digitalizacion/', views.DigitalizacionCreate.as_view(), name='crear-digitalizacion'),
    path('actualizar-digitalizacion/', views.DigitalizacionUpdate.as_view(), name='actualizar-digitalizacion'),
    path('eliminar-digitalizacion/', views.DigitalizacionDelete.as_view(), name='eliminar-digitalizacion'),
    path('responder-digitalizacion/', views.ResponderDigitalizacion.as_view(), name='responder-digitalizacion'),
    
    # OTROS
    path('otros/get-solicitudes-pendientes/', views.OtrosSolicitudesPendientesGet.as_view(), name='otros-get-solicitudes-pendientes'),
    path('otros/crear-digitalizacion/', views.OtrosDigitalizacionCreate.as_view(), name='otros-crear-digitalizacion'),
    path('otros/actualizar-digitalizacion/', views.OtrosDigitalizacionUpdate.as_view(), name='otros-actualizar-digitalizacion'),
    path('otros/eliminar-digitalizacion/', views.OtrosDigitalizacionDelete.as_view(), name='otros-eliminar-digitalizacion'),
    path('otros/responder-digitalizacion/', views.OtrosResponderDigitalizacion.as_view(), name='otros-responder-digitalizacion'),
    path('otros/get-solicitudes-respondidas/', views.OtrosSolicitudesRespondidasGet.as_view(), name='otros-get-solicitudes-respondidas'),
    path('otros/get-solicitudes-by-id/<int:id_solicitud>/', views.OtrosSolicitudByIdGet.as_view(), name='otros-get-solicitudes-by-id'),

    #OPAS
    path('opas/get-solicitudes-pendientes/', views.OpasSolicitudesPendientesGet.as_view(), name='otros-get-solicitudes-pendientes'),
    path('opas/crear-digitalizacion/', views.OpasDigitalizacionCreate.as_view(), name='opas-crear-digitalizacion'),
    path('opas/actualizar-digitalizacion/', views.OpasDigitalizacionUpdate.as_view(), name='opas-actualizar-digitalizacion'),
    path('opas/eliminar-digitalizacion/', views.OpasDigitalizacionDelete.as_view(), name='opas-eliminar-digitalizacion'),
    path('opas/responder-digitalizacion/', views.OpasResponderDigitalizacion.as_view(), name='opas-responder-digitalizacion'),
    path('opas/get-solicitudes-respondidas/', views.OpasSolicitudesRespondidasGet.as_view(), name='opas-get-solicitudes-respondidas'),
    path('opas/get-solicitudes-by-id/<int:id_solicitud>/', views.OpasSolicitudByIdGet.as_view(), name='opas-get-solicitudes-by-id'),
    



]