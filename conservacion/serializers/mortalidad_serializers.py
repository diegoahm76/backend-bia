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

class AnularMortalidadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BajasVivero
        fields = ['baja_anulado', 'justificacion_anulacion', 'fecha_anulacion', 'id_persona_anula']
        extra_kwargs = {
            'justificacion_anulacion': {'required': True},
        }

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
    saldo_disponible_busqueda = serializers.SerializerMethodField()
    registros_cuarentena = serializers.SerializerMethodField()
    
    def get_desc_etapa_lote(self,obj):
        desc_etapa_lotes = {'G':'Camas de Germinación', 'P':'Producción', 'D':'Distribución'}
        desc_etapa_lote = desc_etapa_lotes[obj.cod_etapa_lote]
        return desc_etapa_lote
    
    def get_saldo_disponible_busqueda(self,obj):
        
        saldo_disponible_busqueda = 0
        
        if obj.cod_etapa_lote == 'P':
            saldo_disponible_busqueda = UtilConservacion.get_cantidad_disponible_produccion(obj)
        elif obj.cod_etapa_lote == 'D':
            saldo_disponible_busqueda = UtilConservacion.get_cantidad_disponible_distribucion(obj)
        else:
            saldo_disponible_busqueda = None
        
        if saldo_disponible_busqueda != None:
            if saldo_disponible_busqueda < 0:
                saldo_disponible_busqueda = 0
        
        return saldo_disponible_busqueda
    
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
            'saldo_disponible_busqueda',
            'unidad_medida',
            'registros_cuarentena'
        ]

class GetItemsMortalidadSerializer(serializers.ModelSerializer):
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    unidad_medida = serializers.ReadOnlyField(source='id_bien.id_unidad_medida.abreviatura', default=None)
    desc_etapa_lote = serializers.SerializerMethodField()
    
    def get_desc_etapa_lote(self,obj):
        desc_etapa_lote = 'Produccion' if obj.cod_etapa_lote == 'P' else 'Distribución'
        return desc_etapa_lote
    
    class Meta:
        model = ItemsBajasVivero
        fields = '__all__'

class GetMortalidadSerializer(serializers.ModelSerializer):
    nombre_vivero = serializers.ReadOnlyField(source='id_vivero.nombre', default=None)
    persona_baja = serializers.SerializerMethodField()
    persona_anula = serializers.SerializerMethodField()
    items_mortalidad = serializers.SerializerMethodField()
    
    def get_persona_baja(self,obj):
        primer_nombre = obj.id_persona_baja.primer_nombre
        primer_apellido = obj.id_persona_baja.primer_apellido
        
        persona_baja = str(primer_nombre) + ' ' + str(primer_apellido)
        
        return persona_baja
    
    def get_persona_anula(self,obj):
        persona_anula = None
        if obj.id_persona_anula:
            primer_nombre = obj.id_persona_anula.primer_nombre
            primer_apellido = obj.id_persona_anula.primer_apellido
            
            persona_anula = str(primer_nombre)+' '+str(primer_apellido)
        
        return persona_anula
    
    def get_items_mortalidad(self,obj):
        items_mortalidad = ItemsBajasVivero.objects.filter(
            id_baja=obj.id_baja
        ).order_by('nro_posicion')
        items_mortalidad_serializer = GetItemsMortalidadSerializer(items_mortalidad, many=True)
        
        return items_mortalidad_serializer.data
    
    class Meta:
        model = BajasVivero
        fields = [
            'id_baja',
            'tipo_baja',
            'nro_baja_por_tipo',
            'fecha_baja',
            'fecha_registro',
            'motivo',
            'baja_anulado',
            'justificacion_anulacion',
            'fecha_anulacion',
            'ruta_archivo_soporte',
            'id_vivero',
            'nombre_vivero',
            'id_persona_baja',
            'persona_baja',
            'id_persona_anula',
            'persona_anula',
            'items_mortalidad'
        ]
        
class GetHistorialMortalidadSerializer(serializers.ModelSerializer):
    consecutivo_mortalidad = serializers.ReadOnlyField(source='id_baja.nro_baja_por_tipo', default=None)
    fecha_mortalidad = serializers.ReadOnlyField(source='id_baja.fecha_baja', default=None)
    cantidad_mortalidad = serializers.ReadOnlyField(source='cantidad_baja', default=None)
    realizado_por = serializers.SerializerMethodField()
    
    def get_realizado_por(self,obj):
        primer_nombre = obj.id_baja.id_persona_baja.primer_nombre
        primer_apellido = obj.id_baja.id_persona_baja.primer_apellido
        
        persona_baja = str(primer_nombre) + ' ' + str(primer_apellido)
        
        return persona_baja
    
    class Meta:
        model = ItemsBajasVivero
        fields = [
            'id_item_baja_viveros',
            'consecutivo_mortalidad',
            'fecha_mortalidad',
            'cantidad_mortalidad',
            'observaciones',
            'realizado_por'
        ]