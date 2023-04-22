from rest_framework import serializers
from recaudo.models.liquidaciones_models import OpcionesLiquidacionBase, Deudores


class OpcionesLiquidacionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionesLiquidacionBase
        fields = '__all__'


class DeudoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deudores
        fields = ('codigo', 'identificacion', 'nombres', 'apellidos')
