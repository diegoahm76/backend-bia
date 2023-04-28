from rest_framework import serializers
from recaudo.models.base_models import TipoActuacion, TiposPago
from recaudo.models.pagos_models import (
    FacilidadesPago,
    RequisitosActuacion,
    CumplimientoRequisitos,
    DetallesFacilidadPago,
    GarantiasFacilidad,
    PlanPagos,
    TasasInteres
)

class TipoPagoSerializer(serializers.ModelField):
    class Meta:
        model = TiposPago
        fields = ('id', 'descripcion')


class TipoActuacionSerializer(serializers.ModelField):
    class Meta:
        model = TipoActuacion
        fields = ('id', 'descripcion')


class FacilidadesPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilidadesPago
        fields = '__all__'


class RequisitosActuacionSerializer (serializers.ModelField):
    class Meta:
        model = RequisitosActuacion
        fields = '__all__'


class CumplimientoRequisitosSerializer (serializers.ModelField):
    class Meta:
        model = CumplimientoRequisitos
        fields = '__all__'


class DetallesFacilidadPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model =DetallesFacilidadPago
        fields = '__all__'


class GarantiasFacilidadSerializer(serializers.ModelField):
    class Meta:
        model = GarantiasFacilidad
        fields = '__all__'
    
    
class PlanPagosSerializer(serializers.ModelField):
    class Meta:
        model = PlanPagos
        fields = '__all__'

    
class TasasInteresSerializer(serializers.ModelField):
    class Meta:
        model = TasasInteres
        fields = '__all__'
