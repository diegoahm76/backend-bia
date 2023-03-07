from conservacion.models.incidencias_models import ConsumosIncidenciasMV
from conservacion.utils import UtilConservacion
from rest_framework import serializers
from conservacion.models.inventario_models import InventarioViveros
from conservacion.models import (
    CuarentenaMatVegetal
)
from conservacion.serializers.mortalidad_serializers import RegistrosCuarentenaSerializer
from conservacion.models.incidencias_models import IncidenciasMatVegetal


class MaterialVegetalSerializer(serializers.ModelSerializer):
    nombre = serializers.ReadOnlyField(source='id_bien.nombre',default=None)
    codigo = serializers.ReadOnlyField(source='id_bien.codigo_bien',default=None)
    unidad_medida = serializers.ReadOnlyField(source='id_bien.id_unidad_medida.abreviatura',default=None)
    saldo_total = serializers.SerializerMethodField()
    registros_cuarentena = serializers.SerializerMethodField()
    
    def get_saldo_total(self,obj):
        
        saldo_disponible = 0
        
        if obj.cod_etapa_lote == 'P':
            saldo_disponible = UtilConservacion.get_cantidad_disponible_produccion(obj)
        elif obj.cod_etapa_lote == 'D':
            saldo_disponible = UtilConservacion.get_cantidad_disponible_distribucion(obj)
        elif obj.cod_etapa_lote == 'G':
            saldo_disponible = None
        
        if saldo_disponible != None:
            if saldo_disponible< 0:
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
        fields = ['id_inventario_vivero','nombre','codigo','agno_lote','nro_lote','cod_etapa_lote','saldo_total','unidad_medida','registros_cuarentena']
        model = InventarioViveros

class IncidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = IncidenciasMatVegetal  
        
class ActualizacionIncidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['descripcion','nombre_incidencia','altura_lote_en_cms','ruta_archivos_soporte']
        model = IncidenciasMatVegetal          
        
          
class GetTipoBienSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()
    codigo_bien  = serializers.ReadOnlyField(source='id_bien.codigo_bien',default=None)
    unidad_medida = serializers.SerializerMethodField()
    tipo_bien = serializers.SerializerMethodField()
    saldo_disponible = serializers.SerializerMethodField()
    
    def get_nombre(self,obj):
        
        if obj.id_bien:
            nombre = obj.id_bien.nombre
        else:
            nombre = obj.id_mezcla.nombre
            
        return nombre

    def get_unidad_medida(self,obj):
        
        if obj.id_bien:
            unidad_medida = obj.id_bien.id_unidad_medida.abreviatura
        else:
            unidad_medida = obj.id_mezcla.id_unidad_medida.abreviatura
            
        return unidad_medida
    
    def get_tipo_bien(self,obj):
        
        if obj.id_bien:
            tipo_bien = 'Insumo'
        else: 
            tipo_bien = 'Mezcla'
            
        return tipo_bien
    
    def get_saldo_disponible (self,obj):
        
        if obj.id_bien:
            saldo_disponible = UtilConservacion.get_cantidad_disponible_consumir(obj)
            
        else:
            saldo_disponible = UtilConservacion.get_cantidad_disponible_mezclas(obj)
        
        return saldo_disponible
            
    class Meta:
        fields = ['id_bien','id_mezcla','id_vivero','nombre','codigo_bien','unidad_medida','tipo_bien','saldo_disponible']
        model = InventarioViveros
        
class ConsumosIncidenciasMVSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields= '__all__'
        model = ConsumosIncidenciasMV