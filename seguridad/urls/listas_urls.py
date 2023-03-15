from django.urls import path
from seguridad.views import listas_views as views
from rest_framework_simplejwt.views import (TokenRefreshView)

urlpatterns = [
    path('departamentos/', views.GetListDepartamentos.as_view(), name='get-list-departamentos'),
    path('municipios/', views.GetListMunicipios.as_view(), name='get-list-municipios'),
]