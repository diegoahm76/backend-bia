from rest_framework import serializers
from seguridad.models import Personas
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
from recaudo.models.cobros_models import Obligaciones, Cartera, Deudores
from seguridad.models import Personas


class TipoPagoSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Deudores
        fields = ('codigo', 'identificacion', 'nombres', 'apellidos', 'email')
        

class FacilidadesPagoSerializer(serializers.ModelSerializer):
    id_deudor_actuacion = DeudorFacilidadPagoSerializer

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


class CarteraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartera
        fields = ('id','valor_intereses','dias_mora')


class ObligacionesSerializer(serializers.ModelSerializer):
    carteras = serializers.SerializerMethodField()

    def get_carteras(self, obj):
        carteras = obj.cartera_set.filter(fin__isnull=True)
        carteras_serializer = CarteraSerializer(carteras, many=True)
        carteras_data = carteras_serializer.data if carteras_serializer else []
        return carteras_data
    
    class Meta:
        model = Obligaciones
        fields = ('id','fecha_inicio', 'id_expediente','monto_inicial','carteras')


class ConsultaObligacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Obligaciones
        fields = '__all__'

class ListadoFacilidadesPagoSerializer(serializers.ModelSerializer):
    identificacion = serializers.ReadOnlyField(source='id_deudor_actuacion.identificacion',default=None)
    nombre_de_usuario = serializers.SerializerMethodField()

    class Meta:
        model = FacilidadesPago
        fields = ('id', 'nombre_de_usuario','identificacion', 'fecha_generacion')

    def get_nombre_de_usuario(self, obj):
        nombre_de_usuario = None
        persona = Personas.objects.filter(numero_documento=obj.id_deudor_actuacion.identificacion).first()
        if persona: 
            usuario = persona.user_set.exclude(id_usuario=1).first() 
            nombre_de_usuario = usuario.nombre_de_usuario if usuario else None
        return nombre_de_usuario


class ConsultaFacilidadesPagosSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilidadesPago
        fields = '__all__'

class ListadoDeudoresUltSerializer(serializers.ModelSerializer):
    nombre_contribuyente = serializers.SerializerMethodField()

    class Meta:
        model = Deudores
        fields = ('nombre_contribuyente','identificacion')

    def get_nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellidos}"




