from django.urls import path
from gestion_documental.views import consultar_estado_solicitud_tramite_views as views


urlpatterns = [

    #
    path('consultar/', views.EstadoSolicitudesTramitesGet.as_view(), name='consultar_estado_solicitud_tramite'),
    #TramitesEstadosSolicitudesGet
    path('estados/tramites/', views.TramitesEstadosSolicitudesGet.as_view(), name='consultar_estado_solicitud_tramite'),

]