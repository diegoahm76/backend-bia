from django.urls import path
from seguridad.views import listas_views as views
from rest_framework_simplejwt.views import (TokenRefreshView)

urlpatterns = [
    path('departamentos/', views.GetListDepartamentos.as_view(),
         name='get-list-departamentos'),
    path('municipios/', views.GetListMunicipios.as_view(),
         name='get-list-municipios'),
    path('tipo-persona/', views.GetListTipoPersona.as_view(),
         name='get-list-tipo-persona'),
    path('paises/', views.GetListPaises.as_view(), name='get-list-paises'),
    path('tipo-documento/', views.GetListTipoDocumento.as_view(),
         name='get-list-tipo-documento'),
    path('tipo-usuario/', views.GetListTipoUsuario.as_view(),
         name='get-list-tipo-usuario'),
    path('clase-tercero/', views.GetLisClaseTercero.as_view(),
         name='get-list-clase-tercero'),
    path('cod-permiso/', views.GetLisCodPermiso.as_view(),
         name='get-list-cod-permiso'),
    path('estado-civil/', views.GetLisEstadoCivil.as_view(),
         name='get-list-estado-civil'),
    path('opc-usuario/', views.GetLisOpcUsuario.as_view(),
         name='get-list-opc-usuario'),
    path('sexo/', views.GetLisSexo.as_view(), name='get-list-sexo'),
    path('subsistema/', views.GetLisSubsistema.as_view(), name='get-list-subsistema'),
    path('tipo-direccion/', views.GetLisTipoDireccion.as_view(), name='get-list-tipo-direccion'),
    path('direcciones/', views.GetLisDirecciones.as_view(), name='get-list-direcciones'),
    path('indicativo-pais/', views.GetLisIndicativoPais.as_view(), name='get-list-indicativo-pais'),
]
