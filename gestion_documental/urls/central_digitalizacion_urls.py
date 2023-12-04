from django.urls import path

from gestion_documental.views import central_digitalizacion_views as views


urlpatterns = [
    path('get-solicitudes-pendientes/', views.SolicitudesPendientesGet.as_view(), name='get-solicitudes-pendientes'),
    path('get-solicitudes-respondidas/', views.SolicitudesRespondidasGet.as_view(), name='get-solicitudes-respondidas'),
    path('crear-digitalizacion/', views.DigitalizacionCreate.as_view(), name='crear-digitalizacion'),
    path('actualizar-digitalizacion/', views.DigitalizacionUpdate.as_view(), name='actualizar-digitalizacion'),
    path('eliminar-digitalizacion/', views.DigitalizacionDelete.as_view(), name='eliminar-digitalizacion'),
    path('responder-digitalizacion/', views.ResponderDigitalizacion.as_view(), name='responder-digitalizacion')
]