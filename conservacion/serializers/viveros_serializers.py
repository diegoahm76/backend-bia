from transversal.models.personas_models import Personas
from conservacion.models.viveros_models import HistoricoResponsableVivero
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from conservacion.models.viveros_models import (
    Vivero,
    HistorialAperturaViveros,
    HistorialCuarentenaViveros
)
from almacen.models.bienes_models import (
    CatalogoBienes,
)
from transversal.choices.municipios_choices import municipios_CHOICES
from almacen.choices.cod_tipo_elemento_vivero_choices import cod_tipo_elemento_vivero_CHOICES

class AbrirViveroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vivero
        fields = ['justificacion_apertura', 'fecha_ultima_apertura', 'en_funcionamiento', 'item_ya_usado', 'id_persona_abre']
        extra_kwargs = {
            'justificacion_apertura': {'required': True, 'allow_null': False, 'allow_blank':False},
        }


class CerrarViveroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vivero
        fields = ['justificacion_cierre', 'fecha_cierre_actual', 'en_funcionamiento', 'item_ya_usado', 'id_persona_cierra']
        extra_kwargs = {
            'justificacion_cierre': {'required': True, 'allow_null': False, 'allow_blank':False},
        }
        
class ViveroSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Vivero
        fields = '__all__'


class ViveroSerializerDesactivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vivero
        fields = ['activo']
           
class ActivarDesactivarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vivero
        fields = ['justificacion_apertura', 'fecha_ultima_apertura', 'en_funcionamiento', 'item_ya_usado', 'id_persona_abre']
        extra_kwargs = {
            'justificacion_apertura': {'required': True},
        }

class ViveroPostSerializer(serializers.ModelSerializer):
    
    def validate_cod_municipio(self, value):
        if value == '':
            raise serializers.ValidationError('Error, el municipio no puede ir vacío')
        return value
    
    class Meta:
        model = Vivero
        fields = '__all__'
        extra_kwargs = {
            'id_vivero': {'read_only': True},
            'nombre': {'required': True},
            'cod_municipio': {'required': True, 'allow_null':False},
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

class ViveroPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vivero
        fields = '__all__'
        extra_kwargs = {
            'id_vivero': {'read_only': True},
            'direccion': {'required': False},
            'area_mt2': {'required': False},
            'area_propagacion_mt2': {'required': False},
            'tiene_area_produccion': {'required': False},
            'tiene_areas_pep_sustrato': {'required': False},
            'tiene_area_embolsado': {'required': False},
            'cod_tipo_vivero': {'required': False},
            'cod_origen_recursos_vivero': {'required': False},
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
            'ruta_archivo_creacion': {'read_only': True},
            'activo': {'read_only': True},
            'item_ya_usado': {'read_only': True},
            'nombre': {'read_only': True},
            'cod_municipio': {'read_only': True}
        }


class TipificacionBienViveroSerializer(serializers.ModelSerializer):
    cod_tipo_elemento_vivero = serializers.ChoiceField(choices=cod_tipo_elemento_vivero_CHOICES)
    
    def validate(self, data):
        if data['cod_tipo_elemento_vivero'] == 'MV' and data['es_semilla_vivero'] == None:
            raise serializers.ValidationError("Debe indicar si es o no semilla para tipo elemento Material Vegetal")
        if data['cod_tipo_elemento_vivero'] != 'MV':
            data['es_semilla_vivero'] = False
        return data
    class Meta:
        model = CatalogoBienes
        fields = ['nombre_cientifico', 'cod_tipo_elemento_vivero', 'es_semilla_vivero']
        extra_kwargs = {
            'cod_tipo_elemento_vivero': {'required': True}
        }   
        
        
class HistorialViveristaByViveroSerializers(serializers.ModelSerializer):
    nombre_viverista = serializers.SerializerMethodField()
    nombre_persona_cambia = serializers.SerializerMethodField()
    tipo_documento = serializers.ReadOnlyField(source='id_persona.tipo_documento.cod_tipo_documento',default=None)
    numero_documento = serializers.ReadOnlyField(source='id_persona.numero_documento',default=None)

    def get_nombre_viverista(slef,obj):
        
        nombre = obj.id_persona.primer_nombre + ' ' + obj.id_persona.primer_apellido
        
        return nombre
    
    def get_nombre_persona_cambia(slef,obj):
        
        nombre = obj.id_persona_cambia.primer_nombre + ' ' + obj.id_persona_cambia.primer_apellido
        
        return nombre
    
    class Meta:
        
        fields = '__all__'
        model = HistoricoResponsableVivero
        

class ViveristaActualSerializers(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()
    tipo_documento = serializers.ReadOnlyField(source='id_viverista_actual.tipo_documento.cod_tipo_documento',default=None)
    numero_documento = serializers.ReadOnlyField(source='id_viverista_actual.numero_documento',default=None)

    def get_nombre(slef,obj):
        nombre = None
        
        if obj.id_viverista_actual:
            nombre = obj.id_viverista_actual.primer_nombre + ' ' + obj.id_viverista_actual.primer_apellido
        
        return nombre
    
    class Meta:
        
        fields = ['id_vivero','id_viverista_actual','nombre','tipo_documento','numero_documento','fecha_inicio_viverista_actual']
        model = Vivero
        
class PersonasAsignacionViveroSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = '__all__'
        model = Personas