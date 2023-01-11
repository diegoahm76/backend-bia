from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from almacen.models.solicitudes_models import (
    DespachoConsumo,
    ItemDespachoConsumo
) 

class GetNumeroEntregas(serializers.ModelSerializer):
    class Meta:
        model = DespachoConsumo
        fields = ['numero_despacho_consumo']

class GetEntregasSerializer(serializers.ModelSerializer):
    class Meta:
        model = DespachoConsumo
        fields = '__all__'