from almacen.models.generics_models import UnidadesMedida
from seguridad.serializers.personas_serializers import PersonasSerializer
from almacen.models.generics_models import Magnitudes
from rest_framework import serializers
from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

class CatalogoBienesSerializer(serializers.ModelSerializer):
    class Meta:
        model= CatalogoBienes
        fields='__all__'

class EntradaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model= EntradasAlmacen
        exclude = ['id_persona_ult_act_dif_creador', 'fecha_ultima_actualizacion_diferente_creador', 'entrada_anulada', 'justificacion_anulacion', 'fecha_anulacion', 'id_persona_anula']
        extra_kwargs = {
            'numero_entrada_almacen': {'required': True},
            'fecha_entrada': {'required': True},
            'id_entrada_almacen': {'read_only': True},
            'motivo': {'required': True},
            'id_proveedor': {'required': True},
            'id_tipo_entrada': {'required': True},
            'id_bodega': {'required': True},
            'valor_total_entrada': {'required': True},
            'id_creador': {'required': True}
        }


class EntradaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model= EntradasAlmacen
        exclude = (
            'id_entrada_almacen', 
            'numero_entrada_almacen', 
            'fecha_real_registro', 
            'id_creador',
            'entrada_anulada', 
            'justificacion_anulacion', 
            'fecha_anulacion', 
            'id_persona_anula'
        )
        extra_kwargs = {
            'fecha_entrada': {'required': True},
            'motivo': {'required': True},
            'id_proveedor': {'required': True},
            'id_tipo_entrada': {'required': True},
            'id_bodega': {'required': True},
            'valor_total_entrada': {'required': True}
        }