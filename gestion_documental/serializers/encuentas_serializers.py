
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.encuencas_models import EncabezadoEncuesta 



class  EncabezadoEncuestaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model =  EncabezadoEncuesta
        fields = '__all__'