
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.encuencas_models import EncabezadoEncuesta, OpcionesRta, PreguntasEncuesta 



class  EncabezadoEncuestaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model =  EncabezadoEncuesta
        fields = '__all__'
class  EncabezadoEncuestaGetSerializer(serializers.ModelSerializer):
    class Meta:
        model =  EncabezadoEncuesta
        fields = ['id_encabezado_encuesta','nombre_encuesta','fecha_creacion']
            
class  EncabezadoEncuestaDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model =  EncabezadoEncuesta
        fields = '__all__'
            

class  PreguntasEncuestaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model =  PreguntasEncuesta
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=PreguntasEncuesta.objects.all(),
                fields=['id_encabezado_encuesta', 'redaccion_pregunta'],
                message='Esta pregunta ya existe en esta encuesta.'
            )
        ]
    

class  OpcionesRtaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model =  OpcionesRta
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=OpcionesRta.objects.all(),
                fields=['id_pregunta', 'opcion_rta'],
                message='Esta opcion ya existe en esta pregunta.'
            )
        ]
