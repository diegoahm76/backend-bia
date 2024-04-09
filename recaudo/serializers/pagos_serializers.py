from rest_framework import serializers
from recaudo.models.pagos_models import (
    Pagos
)
from recaudo.serializers.liquidaciones_serializers import LiquidacionesBasePostSerializer

class InicioPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagos
        fields = '__all__'

class ConsultarPagosSerializer(serializers.ModelSerializer):
    id_liquidacion = LiquidacionesBasePostSerializer(many=False, read_only=True)
    desc_estado_pago = serializers.CharField(source='get_estado_pago_display', read_only=True)

    class Meta:
        model = Pagos
        fields = '__all__'