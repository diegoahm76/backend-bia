from rest_framework import serializers
from almacen.models.inventario_models import Inventario

class SerializerUpdateInventariosActivosFijos(serializers.ModelSerializer):
    valor_total_item = serializers.FloatField(source='valor_ingreso')
    cod_estado = serializers.ReadOnlyField(source='cod_estado_activo.cod_estado', default=None)
    class Meta:
        model= Inventario
        fields = ['id_bodega', 'valor_total_item', 'cod_estado']

class SerializerUpdateInventariosConsumo(serializers.ModelSerializer):
    class Meta:
        model= Inventario
        fields = ['id_bodega', 'cantidad_entrante_consumo']