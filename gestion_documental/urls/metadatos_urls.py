from django.urls import path
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from django.db.models import F
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.db.models import Max 

from gestion_documental.views import metadatos_views as views


urlpatterns = [

    #Metadatos_Personalizados
    path('metadatos-personalizados/crear/',views.MetadatosPersonalizadosCreate.as_view(), name='crear-metadato'),
    path('metadatos-personalizados/listar/',views.MetadatosPersonalizadosList.as_view(), name='listar-metadato'),
    path('metadatos-personalizados/listar-orden-actual/',views.MetadatosPersonalizadosGetOrdenActual.as_view(), name='listar-orden-actual'),
    path('metadatos-personalizados/listar-orden-siguiente/',views.MetadatosPersonalizadosGetOrden.as_view(), name='listar-orden-actual'),
    path('metadatos-personalizados/eliminar/<int:id_metadato_personalizado>/', views.MetadatosPersonalizadosDelete.as_view(), name='eliminar_metadato'),
    path('metadatos-personalizados/editar/<int:id_metadato_personalizado>/',views.MetadatosPersonalizadosUpdate.as_view(), name='editar_metadato'),
    path('metadatos-personalizados/buscar/',views.MetadatosPersonalizadosSearch.as_view(), name='buscar-metadato'),


    #Lista_Valores_Metadatos_Personalizados
    path('valores-metadatos/crear/',views.MetadatosValoresCreate.as_view(), name='crear-valores'),
    path('valores-metadatos/listar/',views.ValoresMetadatosGet.as_view(), name='listar'),
    path('valores-metadatos/listar-orden-actual/',views.MetadatosValoresGetOrdenActual.as_view(), name='listar-orden-actual'),
    path('valores-metadatos/eliminar/<int:pk>/', views.ValoresMetadatosDelete.as_view(), name='eliminar_valor'),








     
]