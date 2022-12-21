from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from conservacion.models.viveros_models import (
    Vivero,
    HistorialAperturaViveros,
    HistorialCuarentenaViveros
)

class ViveroSerializer(serializers.Serializer):
    class Meta:
        model = Vivero
        fields = '__all__'


class ActivarDesactivarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vivero
        fields = ['justificacion_apertura', 'fecha_ultima_apertura', 'en_funcionamiento', 'item_ya_usado', 'id_persona_abre']
        extra_kwargs = {
            'justificacion_apertura': {'required': True},
        }

class ViveroPostSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(validators=[UniqueValidator(queryset=Vivero.objects.all(), message='El nombre del Vivero debe ser único')])
    class Meta:
        model = Vivero
        fields = '__all__'
        extra_kwargs = {
            'id_vivero': {'read_only': True},
            'nombre': {'required': True},
            'cod_municipio': {'required': True},
            'direccion': {'required': True},
            'area_mt2': {'required': True},
            'area_propagacion_mt2': {'required': True},
            'tiene_area_produccion': {'required': True},
            'tiene_areas_pep_sustrato': {'required': True},
            'tiene_area_embolsado': {'required': True},
            'cod_tipo_vivero': {'required': True},
            'cod_origen_recursos_vivero': {'required': True},
            'id_persona_crea': {'required': True},
            'en_funcionamiento': {'read_only': True},
            'fecha_ultima_apertura': {'read_only': True},
            'id_persona_abre': {'read_only': True},
            'justificacion_apertura': {'read_only': True},
            'fecha_cierre_actual': {'read_only': True},
            'id_persona_cierra': {'read_only': True},
            'justificacion_cierre': {'read_only': True},
            'vivero_en_cuarentena': {'read_only': True},
            'id_persona_cuarentena': {'read_only': True},
            'justificacion_cuarentena': {'read_only': True},
            'ruta_archivo_creacion': {'required': True},
            'activo': {'read_only': True},
            'item_ya_usado': {'read_only': True}
        }
