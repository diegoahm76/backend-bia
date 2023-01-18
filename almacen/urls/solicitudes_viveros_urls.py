from django.urls import path
from almacen.views import solicitudes_viveros_views as views

urlpatterns = [
    path('crear-solicitud-viveros/', views.CreateSolicitudViveros.as_view(), name='crear-solicitud-viveros'),
]