from rest_framework import serializers
from recaudo.models.base_models import TiposPago
from recaudo.models.cobros_models import Cartera
from recaudo.models.liquidaciones_models import Deudores
from recaudo.models.planes_pagos_models import PlanPagos, ResolucionesPlanPago, PlanPagosCuotas
from recaudo.models.facilidades_pagos_models import FacilidadesPago, DetallesFacilidadPago


class TipoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposPago
        fields = ('id', 'descripcion')


class PlanPagosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanPagos
        fields = '__all__'


class PlanPagosCuotasSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanPagosCuotas
        fields = '__all__'


class ResolucionesPlanPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResolucionesPlanPago
        fields = '__all__'


class ResolucionesPlanPagoGetSerializer(serializers.ModelSerializer):
    doc_asociado = serializers.ReadOnlyField(source='doc_asociado.ruta_archivo.url', default=None)

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
    dias_mora = serializers.SerializerMethodField()
    valor_intereses = serializers.SerializerMethodField()

    class Meta:
        model = Cartera
        fields = ('id','nombre','monto_inicial','inicio','dias_mora','valor_intereses')

    def get_dias_mora(self, obj):
        detalle = DetallesFacilidadPago.objects.filter(id_cartera=obj.id).first()

        if detalle:
            fecha_abono = detalle.id_facilidad_pago.fecha_abono
            dias_mora = (fecha_abono - obj.inicio).days
            return dias_mora
        
    def get_valor_intereses(self, obj):
        dias_mora = self.get_dias_mora(obj)
        if dias_mora is not None:
            monto_inicial = float(obj.monto_inicial) 
            return (0.12 / 360 * monto_inicial) * dias_mora