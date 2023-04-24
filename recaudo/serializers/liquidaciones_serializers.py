from rest_framework import serializers
from recaudo.models.liquidaciones_models import (
    OpcionesLiquidacionBase,
    Deudores,
    LiquidacionesBase,
    DetalleLiquidacionBase,
    Expedientes
)
from recaudo.models.base_models import VariablesBase


class OpcionesLiquidacionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionesLiquidacionBase
        fields = '__all__'


class DeudoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deudores
        fields = ('codigo', 'identificacion', 'nombres', 'apellidos')


class VariablesBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariablesBase
        fields = ('id', 'nombre', 'tipo', 'valor_defecto', 'estado')


class DetallesLiquidacionBaseSerializer(serializers.ModelSerializer):
    id_variable = VariablesBaseSerializer(many=False)

    class Meta:
        model = DetalleLiquidacionBase
        fields = ('id', 'id_variable', 'valor', 'estado')


class ExpedientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expedientes
        fields = '__all__'


class LiquidacionesBaseSerializer(serializers.ModelSerializer):
    cod_deudor = DeudoresSerializer(many=False)
    id_opcion_liq = OpcionesLiquidacionBaseSerializer(many=False)
    cod_expediente = ExpedientesSerializer(many=False)
    detalles = DetallesLiquidacionBaseSerializer(many=True)

    class Meta:
        model = LiquidacionesBase
        fields = ('id', 'id_opcion_liq', 'cod_deudor', 'cod_expediente', 'fecha_liquidacion', 'vencimiento', 'periodo_liquidacion', 'valor', 'estado', 'detalles')


class LiquidacionesBasePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiquidacionesBase
        fields = '__all__'


class DetallesLiquidacionBasePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleLiquidacionBase
        fields = '__all__'