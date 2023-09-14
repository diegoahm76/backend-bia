from django.urls import path
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from django.db.models import F
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.db.models import Max 

from gestion_documental.views import metadatos_views as views


urlpatterns = [

    path('metadatos-personalizados/crear/',views.MetadatosPersonalizadosCreate.as_view(), name='crear-metadato'),
    path('metadatos-personalizados/listar/',views.MetadatosPersonalizadosList.as_view(), name='crear-metadato'),
    path('metadatos-personalizados/listar-orden-actual/',views.MetadatosPersonalizadosGetOrdenActual.as_view(), name='listar-orden-actual'),
    path('metadatos-personalizados/listar-orden-siguiente/',views.MetadatosPersonalizadosGetOrden.as_view(), name='listar-orden-actual'),
    path('metadatos-personalizados/eliminar/<int:id_metadato_personalizado>/', views.MetadatosPersonalizadosDelete.as_view(), name='eliminar_metadato'),
    path('metadatos-personalizados/editar/<int:id_metadato_personalizado>/',views.MetadatosPersonalizadosUpdate.as_view(), name='editar_metadato'),
    path('metadatos-personalizados/buscar/',views.MetadatosPersonalizadosSearch.as_view(), name='buscar-metadato'),



     
]