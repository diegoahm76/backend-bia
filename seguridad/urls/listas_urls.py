from django.urls import path
from seguridad.views import listas_views as views
from rest_framework_simplejwt.views import (TokenRefreshView)

urlpatterns = [
    path('departamentos/', views.GetListDepartamentos.as_view(), name='get-list-departamentos'),
    path('municipios/', views.GetListMunicipios.as_view(), name='get-list-municipios'),
    path('tipo-persona/', views.GetListTipoPersona.as_view(), name='get-list-tipo-persona'),
    path('paises/', views.GetListPaises.as_view(), name='get-list-paises'),
    path('tipo-documento/', views.GetListTipoDocumento.as_view(), name='get-list-tipo-documento'),
    path('tipo-usuario/', views.GetListTipoUsuario.as_view(), name='get-list-tipo-usuario'),
]