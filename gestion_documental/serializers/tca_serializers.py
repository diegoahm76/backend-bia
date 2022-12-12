from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.tca_models import (
    TablasControlAcceso,
)

class TCASerializer(serializers.ModelSerializer):
    class Meta:
        model = TablasControlAcceso
        fields = '__all__'

class TCAPostSerializer(serializers.ModelSerializer):
    version = serializers.CharField(validators=[UniqueValidator(queryset=TablasControlAcceso.objects.all(), message='La versión de la Tabla de Control de Acceso debe ser único')])
    nombre = serializers.CharField(validators=[UniqueValidator(queryset=TablasControlAcceso.objects.all(), message='El nombre de la Tabla de Control de Acceso debe ser único')])

    class Meta:
        model = TablasControlAcceso
        fields = ['id_ccd', 'version', 'nombre']
        extra_kwargs = {
            'id_ccd': {'required': True},
            'version': {'required': True},
            'nombre': {'required': True}
        }

class TCAPutSerializer(serializers.ModelSerializer):
    version = serializers.CharField(validators=[UniqueValidator(queryset=TablasControlAcceso.objects.all(), message='La versión de la Tabla de Control de Acceso debe ser único')])
    nombre = serializers.CharField(validators=[UniqueValidator(queryset=TablasControlAcceso.objects.all(), message='El nombre de la Tabla de Control de Acceso debe ser único')])

    class Meta:
        model = TablasControlAcceso
        fields = ['version', 'nombre', 'ruta_soporte']
        extra_kwargs = {
            'version': {'required': True},
            'nombre': {'required': True}
        }