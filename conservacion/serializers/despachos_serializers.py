from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from conservacion.models.despachos_models import (
    DespachoEntrantes,
    ItemsDespachoEntrante
)

class DespachosEntrantesSerializer(serializers.ModelSerializer):
    numero_despacho_consumo = serializers.ReadOnlyField(source='id_despacho_consumo_alm.numero_despacho_consumo', default=None)
    
    class Meta:
        model = DespachoEntrantes
        fields = '__all__'
        
class ItemsDespachosEntrantesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ItemsDespachoEntrante
        fields = '__all__'