from rest_framework import serializers
from seguridad.models import Personas, ClasesTerceroPersona
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
from recaudo.models.liquidaciones_models import Deudores

class TipoPagoSerializer(serializers.ModelField):
    class Meta:
        model = TiposPago
        fields = ('id', 'descripcion')


class TipoActuacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoActuacion
        fields = '__all__'


class RequisitosActuacionSerializer (serializers.ModelSerializer):
    class Meta:
        model = RequisitosActuacion
        fields = '__all__'


class CumplimientoRequisitosSerializer (serializers.ModelSerializer):
    class Meta:
        model = CumplimientoRequisitos
        fields = '__all__'


class DetallesFacilidadPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model =DetallesFacilidadPago
        fields = '__all__'


class GarantiasFacilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = GarantiasFacilidad
        fields = '__all__'
    
    
class PlanPagosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanPagos
        fields = '__all__'

    
class TasasInteresSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasasInteres
        fields = '__all__'


class DeudorFacilidadPagoSerializer(serializers.ModelSerializer):
    #fecha_creacion = serializers.DateTimeField()
    class Meta:
        model = Deudores
        fields = ('codigo', 'identificacion', 'nombres', 'apellidos', 'email')
        

class FacilidadesPagoSerializer(serializers.ModelSerializer):
    id_deudor_actiacion = DeudorFacilidadPagoSerializer

    class Meta:
        model = FacilidadesPago
        fields = '__all__'
        extra_kwargs = {
            'id_deudor_actuacion': {'required': True},
            'id_tipo_actuacion': {'required': True},
            'id_tasas_interes': {'required': True},
            'documento_soporte': {'required': True}
        }


class FacilidadesPagoPutSerializer(serializers.ModelSerializer):

    class Meta:
        model = FacilidadesPago
        fields = ('id','id_funcionario')



class FuncionariosSerializer(serializers.ModelSerializer):
    nombre_funcionario = serializers.SerializerMethodField()
    
    def get_nombre_funcionario(self, obj):
        nombre_funcionario = None
        nombre_list = [obj.primer_nombre, obj.primer_apellido]
        nombre_funcionario = ' '.join(item for item in nombre_list if item is not None)
        return nombre_funcionario
    
    class Meta:
        model = Personas
        fields = ('id_persona', 'nombre_funcionario')