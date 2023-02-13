from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from conservacion.models import (
    BajasVivero,
    ItemsBajasVivero,
    InventarioViveros,
    CuarentenaMatVegetal
)
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from conservacion.utils import UtilConservacion

class RegistrarMortalidadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BajasVivero
        fields = '__all__'
        extra_kwargs = {
            'id_baja': {'read_only': True},
            'justificacion_anulacion': {'read_only': True},
            'fecha_anulacion': {'read_only': True},
            'id_persona_anula': {'read_only': True},
            'fecha_registro': {'read_only': True},
        }

class ActualizarMortalidadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BajasVivero
        fields = ['motivo', 'ruta_archivo_soporte']

class RegistrarItemsMortalidadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ItemsBajasVivero
        fields = '__all__'
        extra_kwargs = {
            'id_item_baja_viveros': {'read_only': True}
        }
        
class ActualizarItemsMortalidadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ItemsBajasVivero
        fields = ['cantidad_baja', 'observaciones']

class RegistrosCuarentenaSerializer(serializers.ModelSerializer):
    saldo_por_levantar = serializers.SerializerMethodField()
    
    def get_saldo_por_levantar(self, obj):
        saldo_por_levantar = UtilConservacion.get_saldo_por_levantar(obj)
        
        return saldo_por_levantar
    
    class Meta:
        model = CuarentenaMatVegetal
        fields = ['id_cuarentena_mat_vegetal', 'consec_cueren_por_lote_etapa', 'fecha_cuarentena', 'descrip_corta_diferenciable', 'saldo_por_levantar']
        
class MortalidadMaterialVegetalSerializer(serializers.ModelSerializer):
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    unidad_medida = serializers.ReadOnlyField(source='id_bien.id_unidad_medida.abreviatura', default=None)
    desc_etapa_lote = serializers.SerializerMethodField()
    saldo_disponible = serializers.SerializerMethodField()
    registros_cuarentena = serializers.SerializerMethodField()
    
    def get_desc_etapa_lote(self,obj):
        desc_etapa_lote = 'Produccion' if obj.cod_etapa_lote == 'P' else 'Distribución'
        return desc_etapa_lote
    
    def get_saldo_disponible(self,obj):
        
        saldo_disponible = 0
        
        if obj.cod_etapa_lote == 'P':
            saldo_disponible = UtilConservacion.get_cantidad_disponible_etapa_produccion(obj)
        else:
            saldo_disponible = UtilConservacion.get_cantidad_disponible_etapa(obj)
        
        if saldo_disponible < 0:
            saldo_disponible = 0
        
        return saldo_disponible
    
    def get_registros_cuarentena(self,obj):
        registros_cuarentena = CuarentenaMatVegetal.objects.filter(
            id_vivero=obj.id_vivero,
            id_bien=obj.id_bien,
            cod_etapa_lote=obj.cod_etapa_lote,
            agno_lote=obj.agno_lote,
            nro_lote=obj.nro_lote,
            cuarentena_abierta=True,
            cuarentena_anulada=False
        )
        registros_cuarentena_serializer = RegistrosCuarentenaSerializer(registros_cuarentena, many=True)
        registros_cuarentena_data = registros_cuarentena_serializer.data
        
        registros_cuarentena_data = [registro for registro in registros_cuarentena_data if registro['saldo_por_levantar'] > 0]
        
        return registros_cuarentena_data
    
    class Meta:
        model = InventarioViveros
        fields = [
            'id_inventario_vivero',
            'id_bien',
            'codigo_bien',
            'nombre_bien',
            'agno_lote',
            'nro_lote',
            'cod_etapa_lote',
            'desc_etapa_lote',
            'saldo_disponible',
            'unidad_medida',
            'registros_cuarentena'
        ]