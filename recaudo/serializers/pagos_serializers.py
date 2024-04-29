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
    tipo_usuario = serializers.CharField(source='id_persona_pago.get_tipo_persona_display', read_only=True)
    comprobante_pago_url = serializers.ReadOnlyField(source='comprobante_pago.ruta_archivo.url', default=None)
    nombre_persona_pago = serializers.SerializerMethodField()

    def get_nombre_persona_pago(self, obj):
        nombre_persona_pago = None
        if obj.id_persona_pago:
            if obj.id_persona_pago.tipo_persona == 'J':
                nombre_persona_pago = obj.id_persona_pago.razon_social
            else:
                nombre_list = [obj.id_persona_pago.primer_nombre, obj.id_persona_pago.segundo_nombre,
                                obj.id_persona_pago.primer_apellido, obj.id_persona_pago.segundo_apellido]
                nombre_persona_pago = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_pago = nombre_persona_pago if nombre_persona_pago != "" else None
        return nombre_persona_pago

    class Meta:
        model = Pagos
        fields = '__all__'