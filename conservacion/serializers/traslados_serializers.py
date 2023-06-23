from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from conservacion.models.traslados_models import (
    TrasladosViveros,
    ItemsTrasladoViveros
)
from conservacion.models.inventario_models import (
    InventarioViveros
)
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

class TrasladosViverosSerializers(serializers.ModelSerializer):
    class Meta:
        model = TrasladosViveros
        fields = '__all__'

class ItemsTrasladosViverosSerielizers(serializers.ModelSerializer):
    nombre_bien = serializers.ReadOnlyField(source='id_bien_origen.nombre', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien_origen.codigo_bien', default=None)
    es_semilla_vivero = serializers.ReadOnlyField(source='id_bien_origen.es_semilla_vivero', default=None)
    cod_tipo_elemento_vivero = serializers.ReadOnlyField(source='id_bien_origen.cod_tipo_elemento_vivero', default=None)
    
    class Meta:
        model = ItemsTrasladoViveros
        fields = '__all__'

class InventarioViverosSerielizers(serializers.ModelSerializer):
    nombre = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    id_unidad_medida = serializers.ReadOnlyField(source='id_bien.id_unidad_medida.id_unidad_medida', default=None)
    unidad_medida = serializers.ReadOnlyField(source='id_bien.id_unidad_medida.abreviatura', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    es_semilla_vivero = serializers.ReadOnlyField(source='id_bien.es_semilla_vivero', default=None)
    cod_tipo_elemento_vivero = serializers.ReadOnlyField(source='id_bien.cod_tipo_elemento_vivero', default=None)
    saldo_disponible = serializers.SerializerMethodField()
    
    def get_saldo_disponible(self, obj):
        cantidad_entrante = obj.cantidad_entrante if obj.cantidad_entrante else 0
        cantidad_bajas = obj.cantidad_bajas if obj.cantidad_bajas else 0
        cantidad_consumos_internos = obj.cantidad_consumos_internos if obj.cantidad_consumos_internos else 0
        cantidad_salidas = obj.cantidad_salidas if obj.cantidad_salidas else 0
        cantidad_traslados_lote_produccion_distribucion = obj.cantidad_traslados_lote_produccion_distribucion if obj.cantidad_traslados_lote_produccion_distribucion else 0
        cantidad_lote_cuarentena = obj.cantidad_lote_cuarentena if obj.cantidad_lote_cuarentena else 0
        saldo_disponible = None
        if obj.id_bien:
            if (obj.id_bien.cod_tipo_elemento_vivero == 'MV'and obj.id_bien.es_semilla_vivero == True) or obj.id_bien.cod_tipo_elemento_vivero == 'IN':
                saldo_disponible = cantidad_entrante - cantidad_bajas - cantidad_consumos_internos - cantidad_salidas
            elif obj.id_bien.cod_tipo_elemento_vivero == 'HE':
                saldo_disponible = cantidad_entrante - cantidad_bajas - cantidad_salidas
            elif obj.id_bien.cod_tipo_elemento_vivero == 'MV' and obj.id_bien.es_semilla_vivero == False:
                if obj.cod_etapa_lote == 'P':
                    saldo_disponible = cantidad_entrante - cantidad_bajas - cantidad_traslados_lote_produccion_distribucion - cantidad_salidas - cantidad_lote_cuarentena
                if obj.cod_etapa_lote == 'D':
                    saldo_disponible = cantidad_entrante - cantidad_bajas - cantidad_salidas - cantidad_lote_cuarentena
        return saldo_disponible
    
    class Meta:
        model = InventarioViveros
        fields = ['id_inventario_vivero', 
                  'id_bien', 
                  'agno_lote', 
                  'nro_lote', 
                  'cod_etapa_lote', 
                  'cantidad_entrante', 
                  'cantidad_bajas', 
                  'cantidad_traslados_lote_produccion_distribucion', 
                  'cantidad_consumos_internos', 
                  'cantidad_salidas', 
                  'cantidad_lote_cuarentena', 
                  'ult_altura_lote',
                  'id_unidad_medida',
                  'unidad_medida',
                  'nombre',
                  'codigo_bien',
                  'es_semilla_vivero',
                  'cod_tipo_elemento_vivero',
                  'saldo_disponible']

class CreateSiembraInventarioViveroSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventarioViveros
        fields = '__all__'
