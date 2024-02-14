from django.urls import path
from tramites.views import choices_views as views

urlpatterns = [
    # Choices
    path('cod-tipo-operacion-tramite/', views.CodTipoOperacionTramiteChoices.as_view(), name='cod-tipo-operacion-tramite'),
    path('cod-calendario-habiles/', views.CodCalendarioHabilesChoices.as_view(), name='cod-calendario-habiles'),
    path('cod-tipo-permiso-ambiental/', views.CodTipoPermisoAmbientalChoices.as_view(), name='cod-tipo-permiso-ambiental'),
    path('estado-solicitud-tramite/', views.EstadoSolicitudTramite.as_view(), name='estado-solicitud-tramite'),
]