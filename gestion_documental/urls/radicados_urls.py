from django.urls import path
from gestion_documental.views import radicados_views as views


urlpatterns = [

     path('imprimir-radicado/', views.GetRadicadosImprimir.as_view(), name='imprimir-radicado'),



     #OTROS
     path('otros/buscar-personas-documento/',views.FilterPersonasDocumento.as_view(), name='buscar-personas-documento'),
     path('otros/crear-personas-propia/',views.CrearPersonaTitularOtros.as_view(), name='crear-persona-propia'),
     path('otros/listar-medios-solicitud/',views.ListarMediosSolicitud.as_view(), name='listar-medios-solicitud'),
     path('otros/buscar-personas-general/',views.GetPersonasByFilters.as_view(), name='buscar-personas-general'),
     path('otros/buscar-personas-otros/',views.GetPersonasByFiltersOtros.as_view(), name='buscar-personas-otros'),
     path('otros/buscar-empresa-otros/',views.GetEmpresasByFiltersOtros.as_view(), name='buscar-empresa-otros'),
     path('otros/buscar-apoderados-otros/<int:id_poderdante>/', views.GetApoderadosByPoderdanteId.as_view(), name='buscar-apoderado-otros'),
     path('otros/crear-otros/',views.OtrosCreate.as_view(), name='crear-solicitud-otros'),
     path('otros/editar-otros/',views.OTROSUpdate.as_view(), name='editar-solicitud-otros'),
     path('otros/eliminar-otros/',views.OTROSDelete.as_view(), name='eliminar-solicitud-otros'),
     path('otros/radicar-otros/', views.RadicarOTROS.as_view(), name='radicar-otros'),
     path('otros/get_otros/<str:id_persona_titular>/', views.GetOTROSForStatus.as_view(), name='get-pqrsdf'),




    
]