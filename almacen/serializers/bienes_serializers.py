from almacen.models.generics_models import UnidadesMedida
from almacen.models.inventario_models import TiposEntradas
from transversal.serializers.personas_serializers import PersonasSerializer
from almacen.models.generics_models import Magnitudes
from almacen.models.inventario_models import Inventario
from rest_framework import serializers
from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen, ItemEntradaAlmacen
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

class CatalogoBienesSerializer(serializers.ModelSerializer):
    marca=serializers.ReadOnlyField(source='id_marca.nombre',default=None)
    nombre_padre=serializers.ReadOnlyField(source='id_bien_padre.nombre',default=None)
    unidad_medida=serializers.ReadOnlyField(source='id_unidad_medida.abreviatura',default=None)
    unidad_medida_vida_util=serializers.ReadOnlyField(source='id_unidad_medida_vida_util.abreviatura',default=None)
    porcentaje_iva=serializers.ReadOnlyField(source='id_porcentaje_iva.porcentaje',default=None)
    
    class Meta:
        model= CatalogoBienes
        fields='__all__'

# class CatalogoBienesCreateSerializer(serializers.ModelSerializer):
#     marca=serializers.ReadOnlyField(source='id_marca.nombre',default=None)
#     nombre_padre=serializers.ReadOnlyField(source='id_bien_padre.nombre',default=None)
#     unidad_medida=serializers.ReadOnlyField(source='id_unidad_medida.abreviatura',default=None)
#     unidad_medida_vida_util=serializers.ReadOnlyField(source='id_unidad_medida_vida_util.abreviatura',default=None)
#     porcentaje_iva=serializers.ReadOnlyField(source='id_porcentaje_iva.porcentaje',default=None)
    
#     class Meta:
#         model= CatalogoBienes
#         fields='__all__'


#     def get_hijos_bien(self, bien_padre):

#         hijos_bien = CatalogoBienes.objects.filter(id_bien_padre=bien_padre)
#         return hijos_bien

class CatalogoBienesActivoFijoPutSerializer(serializers.ModelSerializer):
    doc_identificador_bien = serializers.CharField(source='doc_identificador_nro')
    class Meta:
        model= CatalogoBienes
        fields=['doc_identificador_bien', 'id_porcentaje_iva', 'cantidad_vida_util', 'id_unidad_medida_vida_util', 'valor_residual']

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
            'id_persona_anula',
        )
        extra_kwargs = {
            'motivo': {'required': True},
            'id_proveedor': {'required': True},
            'id_tipo_entrada': {'required': True},
            'id_bodega': {'required': True},
            'fecha_ultima_actualizacion_diferente_creador':{'read_only': True},
            "id_persona_ult_act_dif_creador":{'read_only': True},
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

class SerializerItemEntradaConsumo(serializers.ModelSerializer):
    class Meta:
        model= ItemEntradaAlmacen
        fields = '__all__'
        extra_kwargs = {
            'id_entrada_almacen': {'required': True},
            'id_bodega': {'required': True},
            'numero_posicion': {'required': True},
            'id_bien': {'required': True},
            'cantidad': {'required': True},
            
        
            'valor_unitario': {'required': True},
            'porcentaje_iva': {'required': True},
            'valor_iva': {'required': True},
            'valor_total_item': {'required': True},
            'valor_iva': {'required': True},
            'doc_identificador_bien': {'read_only': True},
            'cantidad_vida_util': {'read_only': True}, 
            'id_unidad_medida_vida_util': {'read_only': True}, 
            'valor_residual': {'read_only': True},
            'cod_estado': {'read_only': True}
        }

class SerializerItemEntradaConsumoPut(serializers.ModelSerializer):
    class Meta:
        model= ItemEntradaAlmacen
        fields = '__all__'
        extra_kwargs = {
            'id_entrada_almacen': {'read_only': True},
            'numero_posicion': {'read_only': True},
            'id_bien': {'read_only': True},
            'cod_estado': {'read_only': True},
            'doc_identificador_bien': {'read_only': True},
            'cantidad_vida_util': {'read_only': True}, 
            'id_unidad_medida_vida_util': {'read_only': True}, 
            'valor_residual': {'read_only': True}
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
            'porcentaje_iva': {'required': True},
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

class SerializerUpdateItemEntradaActivosFijos(serializers.ModelSerializer):
    class Meta:
        model= ItemEntradaAlmacen
        fields = '__all__'
        extra_kwargs = {
            'id_entrada_almacen': {'read_only': True},
            'id_bien': {'read_only': True},
            'cantidad': {'read_only': True},
            'numero_posicion': {'read_only': True},
            'id_item_entrada_almacen': {'read_only': True},
            'valor_unitario': {'required': True},
            'porcentaje_iva': {'required': True},
            'valor_iva': {'required': True},
            'valor_total_item': {'required': True},
            'id_bodega': {'required': True},
            'doc_identificador_bien': {'required': True},
            'cantidad_vida_util': {'required': True}, 
            'id_unidad_medida_vida_util': {'required': True}, 
            'valor_residual': {'required': True},
            'cod_estado': {'required': True}
        }

class ItemEntradaSerializer(serializers.ModelSerializer):
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    unidad_medida = serializers.ReadOnlyField(source='id_unidad_medida.abreviatura',default=None)
    
    class Meta:
        model= ItemEntradaAlmacen
        fields = '__all__'

class TiposEntradasSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposEntradas
        fields = '__all__'

class EntradaSerializer(serializers.ModelSerializer):
    tipo_entrada = serializers.ReadOnlyField(source='id_tipo_entrada.nombre', default=None)
    
    class Meta:
        model = EntradasAlmacen
        fields = '__all__'


class CatalagoBienesYSerializer(serializers.ModelSerializer):
    marca=serializers.ReadOnlyField(source='id_marca.nombre',default=None)
    nombre_padre=serializers.ReadOnlyField(source='id_bien_padre.nombre',default=None)
    unidad_medida=serializers.ReadOnlyField(source='id_unidad_medida.abreviatura',default=None)
    unidad_medida_vida_util=serializers.ReadOnlyField(source='id_unidad_medida_vida_util.abreviatura',default=None)
    porcentaje_iva=serializers.ReadOnlyField(source='id_porcentaje_iva.porcentaje',default=None)
    
    class Meta:
        model= CatalogoBienes
        fields='__all__'