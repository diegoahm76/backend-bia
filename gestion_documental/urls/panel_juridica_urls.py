#PQRSDFGet
from django.urls import path

from gestion_documental.views import panel_juridica_views as views

urlpatterns = [
    #OPAS
    path('opas/solicitudes/get/',views.SolicitudesJuridicaGet.as_view(),name='get-solicitud-juridica-opas'),
    path('opas/informacion/get/<str:id_solicitud_tramite>/',views.SolicitudesJuridicaInformacionOPAGet.as_view(),name='get-informacion-opas'),
    path('opas/revision/create/<str:id_solicitud_de_juridica>/',views.SolicitudesJuridicaRevisionCreate.as_view(),name='create-revision-solicitud-juridica-opas'),
]