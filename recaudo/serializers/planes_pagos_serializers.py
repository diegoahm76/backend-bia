from rest_framework import serializers
from recaudo.models.base_models import TiposPago

from recaudo.models.cobros_models import Cartera
from recaudo.models.liquidaciones_models import Deudores
from recaudo.models.planes_pagos_models import PlanPagos
from seguridad.models import Personas, Municipio


class TipoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposPago
        fields = ('id', 'descripcion')


class PlanPagosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanPagos
        fields = '__all__'