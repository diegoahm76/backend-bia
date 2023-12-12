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

    
]