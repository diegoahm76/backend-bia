from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.tca_models import (
    TablasControlAcceso,
    Clasif_Serie_Subserie_Unidad_TCA
)
from gestion_documental.choices.tipo_clasificacion_choices import tipo_clasificacion_CHOICES

class TCASerializer(serializers.ModelSerializer):
    class Meta:
        model = TablasControlAcceso
        fields = '__all__'

class TCAPostSerializer(serializers.ModelSerializer):
    version = serializers.CharField(validators=[UniqueValidator(queryset=TablasControlAcceso.objects.all(), message='La versión de la Tabla de Control de Acceso debe ser único')])
    nombre = serializers.CharField(validators=[UniqueValidator(queryset=TablasControlAcceso.objects.all(), message='El nombre de la Tabla de Control de Acceso debe ser único')])

    class Meta:
        model = TablasControlAcceso
        fields = ['id_tca', 'id_ccd', 'version', 'nombre']
        extra_kwargs = {
            'id_tca': {'read_only': True},
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

class ClasifSerieSubserieUnidadTCASerializer(serializers.ModelSerializer):
    cod_clas_expediente = serializers.ChoiceField(choices=tipo_clasificacion_CHOICES)
    class Meta:
        model = Clasif_Serie_Subserie_Unidad_TCA
        fields = '__all__'
        extra_kwargs = {
            'id_clasif_serie_subserie_unidad_tca': {'read_only': True},
            'id_tca': {'required': True},
            'id_serie_subserie_unidad': {'required': True},
            'cod_clas_expediente': {'required': True},
            'fecha_registro': {'read_only': True},
            'justificacion_cambio': {'read_only': True},
            'ruta_archivo_cambio': {'read_only': True}
        }
        validators = [
           UniqueTogetherValidator(
               queryset=Clasif_Serie_Subserie_Unidad_TCA.objects.all(),
               fields = ['id_tca', 'id_serie_subserie_unidad'],
               message='El TCA y la serie subserie unidad deben ser una pareja única'
           )
        ]     

class ClasifSerieSubserieUnidadTCAPutSerializer(serializers.ModelSerializer):
    cod_clas_expediente = serializers.ChoiceField(choices=tipo_clasificacion_CHOICES)
    class Meta:
        model = Clasif_Serie_Subserie_Unidad_TCA
        fields = '__all__'
        extra_kwargs = {
            'id_clasif_serie_subserie_unidad_tca': {'read_only': True},
            'id_tca': {'read_only': True},
            'id_serie_subserie_unidad': {'read_only': True},
            'cod_clas_expediente': {'required': True},
            'fecha_registro': {'read_only': True},
            'justificacion_cambio': {'read_only': True},
            'ruta_archivo_cambio': {'read_only': True}
        }