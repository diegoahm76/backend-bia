#PQRSDFGet
from django.urls import path

from gestion_documental.views import panel_ventanilla_views as views

urlpatterns = [
    path('estados_solicitudes/get/', views.EstadosSolicitudesGet.as_view(),name='listar-estados_solicitud'),
    path('pqrsf/get/', views.PQRSDFGet.as_view(),name='listar-pqrs'),
]