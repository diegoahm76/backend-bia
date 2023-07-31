from rest_framework import serializers
from recaudo.models.base_models import TipoActuacion, TiposPago, Ubicaciones
from recaudo.models.facilidades_pagos_models import (
    DetallesFacilidadPago,
    PlanPagos,
    TasasInteres,
)
from recaudo.models.cobros_models import Cartera
from recaudo.models.liquidaciones_models import Deudores
from seguridad.models import Personas, Municipio


class ObligacionesSerializer(serializers.ModelSerializer):
    nro_expediente = serializers.ReadOnlyField(source='id_expediente.cod_expediente',default=None)
    nro_resolucion = serializers.ReadOnlyField(source='id_expediente.numero_resolucion',default=None)
    valor_intereses = serializers.SerializerMethodField()
    dias_mora = serializers.SerializerMethodField()

    def get_carteras(self, obj):
        carteras = obj.cartera_set.filter(fin__isnull=True)
        if carteras.exists():
            return carteras.first()
        else:
            return None

    def get_valor_intereses(self, obj):
        cartera = self.get_carteras(obj)
        if cartera:
            return cartera.valor_intereses
        else:
            return None

    def get_dias_mora(self, obj):
        cartera = self.get_carteras(obj)
        if cartera:
            return cartera.dias_mora
        else:
            return None

    class Meta:
        model = Cartera
        fields = ('nombre','inicio','nro_expediente','nro_resolucion','monto_inicial','valor_intereses', 'dias_mora')



class CarteraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartera
        fields = ('id','valor_intereses','dias_mora')


class ConsultaObligacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartera
        fields = '__all__'


class ListadoDeudoresUltSerializer(serializers.ModelSerializer):
    nombre_contribuyente = serializers.SerializerMethodField()

    class Meta:
        model = Deudores
        fields = ('id','nombre_contribuyente','identificacion')
        #fields = ('nombres','apellidos','identificacion')

    def get_nombre_contribuyente(self, obj):
        return f"{obj.nombres} {obj.apellidos}"


class TipoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposPago
        fields = ('id', 'descripcion')


class DetallesFacilidadPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model =DetallesFacilidadPago
        fields = '__all__'

