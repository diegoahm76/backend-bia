from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from conservacion.models.despachos_models import (
    DespachoEntrantes,
    ItemsDespachoEntrante,
    DistribucionesItemDespachoEntrante
)

class DespachosEntrantesSerializer(serializers.ModelSerializer):
    numero_despacho_consumo = serializers.ReadOnlyField(source='id_despacho_consumo_alm.numero_despacho_consumo', default=None)
    
    class Meta:
        model = DespachoEntrantes
        fields = '__all__'
        
class ItemsDespachosEntrantesSerializer(serializers.ModelSerializer):
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    tipo_documento = serializers.ReadOnlyField(source='id_entrada_alm_del_bien.id_tipo_entrada.nombre', default=None)
    numero_documento = serializers.ReadOnlyField(source='id_entrada_alm_del_bien.numero_entrada_almacen', default=None)
    cantidad_restante = serializers.IntegerField(read_only=True, default=None)
    class Meta:
        model = ItemsDespachoEntrante
        fields = '__all__'
        
class DistribucionesItemDespachoEntranteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistribucionesItemDespachoEntrante
        fields = '__all__'