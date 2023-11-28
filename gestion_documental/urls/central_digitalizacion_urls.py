from django.urls import path

from gestion_documental.views import central_digitalizacion_views as views


urlpatterns = [

    path('get-solicitudes-pendientes/', views.SolicitudesPendientesGet.as_view(), name='get-solicitudes-pendientes')
]