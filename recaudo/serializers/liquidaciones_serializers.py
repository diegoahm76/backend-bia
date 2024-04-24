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
    usada = serializers.SerializerMethodField()

    def get_usada(self, obj):
        detalles_liquidacion = DetalleLiquidacionBase.objects.filter(id_opcion_liq=obj.id)
        if detalles_liquidacion.exists():
            return True
        else:
            return False

    class Meta:
        model = OpcionesLiquidacionBase
        fields = '__all__'


class OpcionesLiquidacionBasePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionesLiquidacionBase
        fields = ('nombre', 'estado', 'version', 'funcion', 'variables', 'bloques','tipo_cobro','tipo_renta')


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

class LiquidacionesBasePostMasivoSerializer(serializers.ModelSerializer):
    id_expediente = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = LiquidacionesBase
        fields = ('id', 'id_deudor', 'id_expediente', 'fecha_liquidacion', 'vencimiento', 'periodo_liquidacion', 'estado', 'ciclo_liquidacion')

    def create(self, validated_data):
        id_expedientes = validated_data.pop('id_expediente', [])
        instance = super().create(validated_data)
        for id_expediente in id_expedientes:
            expediente = Expedientes.objects.get(pk=id_expediente)
            expediente.estado = 'guardado'
            expediente.save()
        return instance

class DetallesLiquidacionBasePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleLiquidacionBase
        fields = '__all__'


class CalculosLiquidacionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculosLiquidacionBase
        fields = '__all__'