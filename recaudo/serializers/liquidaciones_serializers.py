from rest_framework import serializers
from recaudo.models.liquidaciones_models import OpcionesLiquidacionBase


class OpcionesLiquidacionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionesLiquidacionBase
        fields = '__all__'
