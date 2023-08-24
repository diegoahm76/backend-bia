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


class FacilidadPagoDatosPlanSerializer(serializers.ModelSerializer):
    porcentaje_abonado = serializers.SerializerMethodField()
    nombre_deudor = serializers.SerializerMethodField()
    identificacion = serializers.ReadOnlyField(source='id_deudor.identificacion',default=None)

    class Meta:
        model = FacilidadesPago
        fields = ('id', 'nombre_deudor', 'identificacion', 'valor_abonado', 'porcentaje_abonado', 'fecha_abono', 'cuotas', 'periodicidad')

    def get_valor_total(self, carteras):
        monto_total = sum(cartera.monto_inicial for cartera in carteras)
        intereses_total = sum(cartera.valor_intereses for cartera in carteras)
        valor_total = monto_total + intereses_total
        return valor_total

    def get_porcentaje_abonado(self, obj):
        cartera_ids = DetallesFacilidadPago.objects.filter(id_facilidad_pago=obj.id)
        ids_cartera = [cartera_id.id_cartera.id for cartera_id in cartera_ids if cartera_id]
        cartera_seleccion = Cartera.objects.filter(id__in=ids_cartera)
        valor_total = self.get_valor_total(cartera_seleccion)
        porcentaje_abonado = (obj.valor_abonado / valor_total) *100
        return float("{:.2f}".format(porcentaje_abonado))
    
    def get_nombre_deudor(self, obj):
        return f"{obj.id_deudor.nombres} {obj.id_deudor.apellidos}"
        

    

class VisualizacionCarteraSelecionadaSerializer(serializers.ModelSerializer):
    nro_expediente = serializers.ReadOnlyField(source='id_expediente.cod_expediente',default=None)
    nro_resolucion = serializers.ReadOnlyField(source='id_expediente.numero_resolucion',default=None)    

    class Meta:
        model = Cartera
        fields = ('id','nombre','nro_expediente','nro_resolucion','monto_inicial','inicio','dias_mora','valor_intereses')