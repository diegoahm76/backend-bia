from django.urls import path
from seguridad.views import choices_views as views
from transversal.views import choices_views as views_transversal

urlpatterns = [
    # Choices
    path('paises/', views_transversal.PaisesChoices.as_view(), name='paises'),
    path('indicativo-paises/', views_transversal.IndicativoPaisesChoices.as_view(), name='indicativo-paises'),
    path('departamentos/', views_transversal.DepartamentosChoices.as_view(), name='departamentos'),
    path('municipios/', views_transversal.MunicipiosChoices.as_view(), name='municipios'),
    path('estado-civil/', views_transversal.EstadoCivilChoices.as_view(), name='sexo'),
    path('sexo/', views_transversal.SexoChoices.as_view(), name='sexo'),
    path('subsistemas/', views.SubsistemasChoices.as_view(), name='subsistemas'),
    path('cod-permiso/', views.CodPermisoChoices.as_view(), name='cod-permiso'),
    path('opciones-usuario/', views.OpcionesUsuarioChoices.as_view(), name='opciones-usuario'),
    path('tipo-direccion/', views_transversal.TipoDireccionChoices.as_view(), name='tipo-direccion'),
    path('tipo-documento/', views_transversal.TipoDocumentoChoices.as_view(), name='tipo-documento'),
    path('tipo-persona/', views_transversal.TipoPersonaChoices.as_view(), name='tipo-persona'),
    path('tipo-usuario/', views.TipoUsuarioChoices.as_view(), name='tipo-usuario'),
    path('direcciones/', views.DireccionesChoices.as_view(), name='direcciones'),
    path('clases-tercero/', views.ClaseTerceroChoices.as_view(), name='clases-tercero'),
    path('cod-naturaleza-empresa/', views_transversal.CodNaturalezaEmpresaChoices.as_view(), name='cod-naturaleza-empresa')
]