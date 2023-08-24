from rest_framework import serializers
from recaudo.models.base_models import TiposPago
from recaudo.models.cobros_models import Cartera
from recaudo.models.liquidaciones_models import Deudores
from recaudo.models.planes_pagos_models import PlanPagos, ResolucionesPlanPago
from recaudo.models.facilidades_pagos_models import FacilidadesPago, DetallesFacilidadPago


class TipoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposPago
        fields = ('id', 'descripcion')


class PlanPagosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanPagos
        fields = '__all__'


class ResolucionesPlanPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResolucionesPlanPago
        fields = '__all__'


class VisualizacionCarteraSelecionadaSerializer(serializers.ModelSerializer):
    nro_expediente = serializers.ReadOnlyField(source='id_expediente.cod_expediente',default=None)
    nro_resolucion = serializers.ReadOnlyField(source='id_expediente.numero_resolucion',default=None)
    valor_abonado = serializers.SerializerMethodField()
    
    def get_valor_abonado(self, obj):
        print(type(obj), obj.id)
        facilidad_pago = DetallesFacilidadPago.objects.filter(id_cartera=obj.id).first()
        valor_abonado = facilidad_pago.id_facilidad_pago.valor_abonado

        return valor_abonado

    class Meta:
        model = Cartera
        fields = ('id','nombre','nro_expediente','nro_resolucion','monto_inicial','inicio','dias_mora','valor_intereses', 'valor_abonado')