from almacen.models.generics_models import UnidadesMedida
from seguridad.serializers.personas_serializers import PersonasSerializer
from almacen.models.generics_models import Magnitudes
from rest_framework import serializers
from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen, ItemEntradaAlmacen
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


class CreateUpdateItemEntradaConsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model= ItemEntradaAlmacen
        exclude = (
            'doc_identificador_bien', 
            'cantidad_vida_util', 
            'id_unidad_medida_vida_util', 
            'valor_residual',
            'cod_estado'
        )
        extra_kwargs = {
            'id_entrada_almacen': {'required': True},
            'id_bien': {'required': True},
            'cantidad': {'required': True},
            'valor_unitario': {'required': True},
            'id_porcentaje_iva': {'required': True},
            'valor_iva': {'required': True},
            'valor_total_item': {'required': True},
            'id_bodega': {'required': True}
        }


class SerializerItemEntradaActivosFijos(serializers.ModelSerializer):
    id_bien_padre = serializers.IntegerField(read_only=True)
    tiene_hoja_vida = serializers.BooleanField(read_only=True)
    class Meta:
        model= ItemEntradaAlmacen
        fields = '__all__'
        extra_kwargs = {
            'id_item_entrada_almacen': {'read_only': True},
            'id_entrada_almacen': {'required': True},
            'cantidad': {'required': True},
            'valor_unitario': {'required': True},
            'id_porcentaje_iva': {'required': True},
            'valor_iva': {'required': True},
            'valor_total_item': {'required': True},
            'id_bodega': {'required': True},
            'valor_iva': {'required': True},
            'doc_identificador_bien': {'required': True},
            'cantidad_vida_util': {'required': True}, 
            'id_unidad_medida_vida_util': {'required': True}, 
            'valor_residual': {'required': True},
            'cod_estado': {'required': True}
        }