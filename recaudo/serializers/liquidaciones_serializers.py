from rest_framework import serializers
from recaudo.models.liquidaciones_models import (
    OpcionesLiquidacionBase,
    Deudores,
    LiquidacionesBase,
    DetalleLiquidacionBase,
    Expedientes
)


class OpcionesLiquidacionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionesLiquidacionBase
        fields = '__all__'


class DeudoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deudores
        fields = ('codigo', 'identificacion', 'nombres', 'apellidos')


class DetallesLiquidacionBaseSerializer(serializers.ModelSerializer):
    id_opcion_liq = OpcionesLiquidacionBaseSerializer(many=False)

    class Meta:
        model = DetalleLiquidacionBase
        fields = '__all__'


class ExpedientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expedientes
        fields = '__all__'


class LiquidacionesBaseSerializer(serializers.ModelSerializer):
    cod_deudor = DeudoresSerializer(many=False)
    cod_expediente = ExpedientesSerializer(many=False)
    detalles = DetallesLiquidacionBaseSerializer(many=True)

    class Meta:
        model = LiquidacionesBase
        fields = ('id', 'cod_deudor', 'cod_expediente', 'fecha_liquidacion', 'vencimiento', 'periodo_liquidacion', 'valor', 'estado', 'detalles')


class LiquidacionesBasePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiquidacionesBase
        fields = '__all__'


class DetallesLiquidacionBasePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleLiquidacionBase
        fields = '__all__'