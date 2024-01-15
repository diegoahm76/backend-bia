from django.urls import path
from tramites.views import listas_views as views_transversal

urlpatterns = [
    path('cod-tipo-operacion-tramite/', views_transversal.GetListCodTipoOperacionTramite.as_view(), name='get-cod-tipo-operacion-tramite'),
    path('cod-tipo-predio/', views_transversal.GetListCodTipoPredio.as_view(), name='get-cod-tipo-predio'),
    path('cod-clasificacion-territorial/', views_transversal.GetListCodClasificacionTerritorial.as_view(), name='get-cod-clasificacion-territorial'),
    path('cod-tipo-calidad-persona/', views_transversal.GetListCodTipoCalidadPersona.as_view(), name='get-cod-tipo-calidad-persona'),
    path('cod-tipo-permiso-ambiental/', views_transversal.GetListCodTipoPermisoAmbiental.as_view(), name='get-cod-tipo-permiso-ambiental'),
    path('cod-tipo-desistimiento/', views_transversal.GetListCodTipoDesistimiento.as_view(), name='get-cod-tipo-desistimiento'),
    path('cod-tipo-solicitud-al-requerimiento/', views_transversal.GetListCodTipoSolicitudAlRequerimiento.as_view(), name='get-cod-tipo-solicitud-al-requerimiento'),
    path('cod-calendario-habiles/', views_transversal.GetListCodCalendarioHabiles.as_view(), name='get-cod-calendario-habiles'),
    path('cod-tipo-solicitud-juridica/', views_transversal.GetListCodTipoSolicitudJuridica.as_view(), name='get-cod-tipo-solicitud-juridica'),
    path('cod-estado-solicitud-juridica/', views_transversal.GetListCodEstadoSolicitudJuridica.as_view(), name='get-cod-estado-solicitud-juridica'),
    path('tipos-radicado/', views_transversal.GetListTiposRadicado.as_view(), name='get-tipos-radicado'),
]
