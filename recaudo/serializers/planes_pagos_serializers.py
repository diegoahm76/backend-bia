from rest_framework import serializers
from recaudo.models.base_models import TiposPago

from recaudo.models.cobros_models import Cartera
from recaudo.models.liquidaciones_models import Deudores
from recaudo.models.planes_pagos_models import PlanPagos
from transversal.models.personas_models import Personas
from transversal.models.base_models import Municipio


class TipoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposPago
        fields = ('id', 'descripcion')

