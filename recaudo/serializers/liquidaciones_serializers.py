from rest_framework import serializers
from recaudo.models.liquidaciones_models import (
    OpcionesLiquidacionBase,
    Deudores,
    LiquidacionesBase,
    DetalleLiquidacionBase,
    Expedientes,
    CalculosLiquidacionBase
)


class OpcionesLiquidacionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionesLiquidacionBase
        fields = '__all__'


class OpcionesLiquidacionBasePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionesLiquidacionBase
        fields = ('nombre', 'estado', 'version', 'funcion', 'variables', 'bloques')


class DeudoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deudores
        fields = ('id', 'identificacion', 'nombres', 'apellidos')


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
    id_deudor = DeudoresSerializer(many=False)
    id_expediente = ExpedientesSerializer(many=False)
    detalles = DetallesLiquidacionBaseSerializer(many=True)

    class Meta:
        model = LiquidacionesBase
        fields = ('id', 'id_deudor', 'id_expediente', 'fecha_liquidacion', 'vencimiento', 'periodo_liquidacion', 'valor', 'estado', 'detalles', 'ciclo_liquidacion')


class LiquidacionesBasePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiquidacionesBase
        fields = '__all__'


class DetallesLiquidacionBasePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleLiquidacionBase
        fields = '__all__'


class CalculosLiquidacionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculosLiquidacionBase
        fields = '__all__'