from rest_framework import serializers

from conservacion.models.inventario_models import InventarioViveros


class InventarioViverosSerializer(serializers.ModelSerializer):
    etapa_lote=serializers.SerializerMethodField() 
    codigo_bien=serializers.ReadOnlyField(source='id_bien.codigo_bien',default=None)
    nombre=serializers.ReadOnlyField(source='id_bien.nombre',default=None)

    def get_etapa_lote(self,obj):
        etapa_lote = None
        if obj.cod_etapa_lote == 'G':
            etapa_lote = 'Germinación'
        else:
            etapa_lote = 'Producción'
            
        return etapa_lote
    class Meta:
        model =  InventarioViveros
        fields = ['id_inventario_vivero','id_bien','codigo_bien','nombre','agno_lote','nro_lote','cod_etapa_lote','etapa_lote']