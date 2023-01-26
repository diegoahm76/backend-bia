from rest_framework import serializers

from conservacion.models.inventario_models import InventarioViveros


class InventarioViverosSerializer(serializers.ModelSerializer):
    etapa_lote=serializers.SerializerMethodField()
    cantidad_disponible=serializers.SerializerMethodField()
    codigo_bien=serializers.ReadOnlyField(source='id_bien.codigo_bien',default=None)
    nombre=serializers.ReadOnlyField(source='id_bien.nombre',default=None)

    def get_etapa_lote(self,obj):
        etapa_lote = None
        if obj.cod_etapa_lote == 'G':
            etapa_lote = 'Germinación'
        else:
            etapa_lote = 'Producción'
            
        return etapa_lote
    
    def get_cantidad_disponible(self,obj):
        cantidad_entrante = obj.cantidad_entrante if obj.cantidad_entrante else 0
        cantidad_bajas = obj.cantidad_bajas if obj.cantidad_bajas else 0
        cantidad_traslados = obj.cantidad_traslados_lote_produccion_distribucion if obj.cantidad_traslados_lote_produccion_distribucion else 0
        cantidad_salidas = obj.cantidad_salidas if obj.cantidad_salidas else 0
        cantidad_lote_cuarentena = obj.cantidad_lote_cuarentena if obj.cantidad_lote_cuarentena else 0
        
        cantidad_disponible = cantidad_entrante - cantidad_bajas - cantidad_traslados - cantidad_salidas - cantidad_lote_cuarentena
            
        return cantidad_disponible
    
    class Meta:
        model =  InventarioViveros
        fields = ['id_inventario_vivero','id_bien','codigo_bien','nombre','agno_lote','nro_lote','cod_etapa_lote','etapa_lote']