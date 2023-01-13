from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from almacen.models.solicitudes_models import (
    DespachoConsumo,
    ItemDespachoConsumo
)
from almacen.models.bienes_models import (
    EntradasAlmacen,
    ItemEntradaAlmacen
) 

class GetNumeroEntregas(serializers.ModelSerializer):
    class Meta:
        model = DespachoConsumo
        fields = ['numero_despacho_consumo']

class GetEntregasSerializer(serializers.ModelSerializer):
    class Meta:
        model = DespachoConsumo
        fields = '__all__'

class CreateEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DespachoConsumo
        fields = '__all__'

class GetEntradasEntregasSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntradasAlmacen
        fields = '__all__'

class GetItemsEntradasEntregasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemEntradaAlmacen
        fields = '__all__'