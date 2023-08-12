from django.urls import path
from seguridad.views import listas_views as views
from transversal.views import listas_views as views_transversal
from rest_framework_simplejwt.views import (TokenRefreshView)

urlpatterns = [
    path('departamentos/', views_transversal.GetListDepartamentos.as_view(),
         name='get-list-departamentos'),
    path('municipios/', views_transversal.GetListMunicipios.as_view(),
         name='get-list-municipios'),
    path('tipo-persona/', views.GetListTipoPersona.as_view(),
         name='get-list-tipo-persona'),
    path('paises/', views_transversal.GetListPaises.as_view(), name='get-list-paises'),
    path('tipo-documento/', views_transversal.GetListTipoDocumento.as_view(),
         name='get-list-tipo-documento'),
    path('tipo-usuario/', views.GetListTipoUsuario.as_view(),
         name='get-list-tipo-usuario'),
    path('clase-tercero/', views.GetLisClaseTercero.as_view(),
         name='get-list-clase-tercero'),
    path('cod-permiso/', views.GetLisCodPermiso.as_view(),
         name='get-list-cod-permiso'),
    path('estado-civil/', views_transversal.GetLisEstadoCivil.as_view(),
         name='get-list-estado-civil'),
    path('opc-usuario/', views.GetLisOpcUsuario.as_view(),
         name='get-list-opc-usuario'),
    path('sexo/', views_transversal.GetLisSexo.as_view(), name='get-list-sexo'),
    path('subsistema/', views.GetLisSubsistema.as_view(), name='get-list-subsistema'),
    path('tipo-direccion/', views.GetLisTipoDireccion.as_view(), name='get-list-tipo-direccion'),
    path('direcciones/', views_transversal.GetLisDirecciones.as_view(), name='get-list-direcciones'),
    path('indicativo-pais/', views_transversal.GetLisIndicativoPais.as_view(), name='get-list-indicativo-pais'),
    path('cod-naturaleza-empresa/', views.GetLisCodNaturalezEmpresa.as_view(), name='get-list-cod-naturaleza-empresa'),
    path('perfiles_sistema/', views.GetLisPerfilesSistema.as_view(), name='get-list-perfiles'),
    path('niveles_prioridad_alerta/', views.GetLisNivelesPrioridadAlerta.as_view(), name='get-list-prioridades_alerta'),
]
