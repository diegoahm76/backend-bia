from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.ccd_models import (
    CuadrosClasificacionDocumental,
    SeriesDoc,
    SubseriesDoc,
    SeriesSubseriesUnidadOrg
)

class SubseriesDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubseriesDoc
        fields = '__all__'
        validators = [
           UniqueTogetherValidator(
               queryset=SubseriesDoc.objects.all(),
               fields = ['id_ccd', 'codigo'],
               message='El id_ccd y el codigo deben ser una pareja única'
           ),
           UniqueTogetherValidator(
               queryset=SubseriesDoc.objects.all(),
               fields = ['id_ccd', 'nombre'],
               message='El id_ccd y nombre deben ser una pareja única'
           )
        ]

class CCDSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuadrosClasificacionDocumental
        fields = '__all__'

class CCDPostSerializer(serializers.ModelSerializer):
    version = serializers.CharField(validators=[UniqueValidator(queryset=CuadrosClasificacionDocumental.objects.all(), message='La versión del Cuadro de Clasificación Documental debe ser único')])
    nombre = serializers.CharField(validators=[UniqueValidator(queryset=CuadrosClasificacionDocumental.objects.all(), message='El nombre del Cuadro de Clasificación Documental debe ser único')])
    class Meta:
        model = CuadrosClasificacionDocumental
        fields = ['id_ccd', 'id_organigrama', 'version', 'nombre']
        extra_kwargs = {
            'id_organigrama': {'required': True},
            'version': {'required': True},
            'nombre': {'required': True}
        }

class CCDPutSerializer(serializers.ModelSerializer):
    version = serializers.CharField(validators=[UniqueValidator(queryset=CuadrosClasificacionDocumental.objects.all(), message='La versión del Cuadro de Clasificación Documental debe ser único')])
    nombre = serializers.CharField(validators=[UniqueValidator(queryset=CuadrosClasificacionDocumental.objects.all(), message='El nombre del Cuadro de Clasificación Documental debe ser único')])
    class Meta:
        model = CuadrosClasificacionDocumental
        fields = ['version', 'nombre', 'ruta_soporte']
        extra_kwargs = {
            'version': {'required': True},
            'nombre': {'required': True}
        }

class CCDActivarSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuadrosClasificacionDocumental
        fields = ['fecha_terminado']
        extra_kwargs = {
            'fecha_terminado': {'read_only': True}
        }

    
class SeriesDocPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = SeriesDoc
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=SeriesDoc.objects.all(),
                fields = ['id_ccd', 'codigo'],
                message='El id_ccd y el codigo deben ser una pareja única'
            ),
            UniqueTogetherValidator(
                queryset=SeriesDoc.objects.all(),
                fields = ['id_ccd', 'nombre'],
                message='El id_ccd y nombre deben ser una pareja única'
            )
            ]  

class SeriesDocSerializer(serializers.ModelSerializer):
    id_ccd = CCDSerializer(read_only=True)
    
    class Meta:
        model = SeriesDoc
        fields = '__all__'

class SeriesSubseriesUnidadOrgSerializer(serializers.ModelSerializer):
    #id_unidad_organizacional = serializers.IntegerField()
    class Meta:
        model = SeriesSubseriesUnidadOrg
        fields = '__all__'      
        validators = [
            UniqueTogetherValidator(
                queryset=SeriesSubseriesUnidadOrg.objects.all(),
                fields = ['id_serie_doc', 'id_unidad_organizacional'],
                message='La combinación serie documental y unidad organizacional debe ser única'
            )
            ]  
