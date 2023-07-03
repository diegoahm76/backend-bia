from rest_framework import serializers
from datetime import datetime
from transversal.models.organigrama_models import Organigramas
from transversal.models.lideres_models import LideresUnidadesOrg

class BusquedaAvanzadaOrganigramasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organigramas
        fields = '__all__'
        
class GetListLideresAsignadosSerializer(serializers.ModelSerializer):
    nombre_organigrama = serializers.ReadOnlyField(source='id_unidad_organizacional.id_organigrama.nombre', default=None)
    version_organigra = serializers.ReadOnlyField(source='id_unidad_organizacional.id_organigrama.version', default=None)
    codigo_unidad_org = serializers.ReadOnlyField(source='id_unidad_organizacional.codigo', default=None)
    nombre_unidad_org = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
    tipo_documento = serializers.ReadOnlyField(source='id_persona.tipo_documento.cod_tipo_documento', default=None)
    numero_documento = serializers.ReadOnlyField(source='id_persona.numero_documento', default=None)
    nombre_completo = serializers.SerializerMethodField()
    
    def get_nombre_completo(self, obj):
        nombre_completo = None
        nombre_list = [obj.id_persona.primer_nombre, obj.id_persona.segundo_nombre, obj.id_persona.primer_apellido, obj.id_persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        return nombre_completo.upper()
    
    class Meta:
        model = LideresUnidadesOrg
        fields = '__all__'
        
class CreateAsignacionSerializer(serializers.ModelSerializer):
    def validate_id_unidad_organizacional(self, unidad_organizacional):
        if unidad_organizacional.id_organigrama.fecha_retiro_produccion:
            raise serializers.ValidationError('La unidad elegida no puede pertenecer a un organigrama retirado de producción')
        
        return unidad_organizacional
    
    def validate_id_persona(self, persona):
        current_date = datetime.now()
        
        if not persona.es_unidad_organizacional_actual or persona.fecha_a_finalizar_cargo_actual < current_date or not persona.id_cargo or not persona.id_unidad_organizacional_actual:
            raise serializers.ValidationError('La persona elegida no se encuentra actualmente vinculada')
        
        return persona
    
    class Meta:
        model = LideresUnidadesOrg
        fields = '__all__'
        extra_kwargs = {
            'id_lider_unidad_org': {'read_only': True},
            'fecha_asignacion': {'read_only': True},
            'id_unidad_organizacional': {'required': True, 'allow_null': False},
            'id_persona': {'required': True, 'allow_null': False},
            'id_persona_asigna': {'required': True, 'allow_null': False},
            'observaciones_asignacion': {'required': True, 'allow_null': False, 'allow_blank': False}
        }
        
class UpdateAsignacionSerializer(CreateAsignacionSerializer):
    
    class Meta:
        model =  LideresUnidadesOrg
        fields = CreateAsignacionSerializer.Meta.fields
        extra_kwargs = CreateAsignacionSerializer.Meta.extra_kwargs | {
            'fecha_asignacion': {'read_only': False},
            'id_unidad_organizacional': {'read_only': True},
            'id_persona_asigna': {'required': False}
        }