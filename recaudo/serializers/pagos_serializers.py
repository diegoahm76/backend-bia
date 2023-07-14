from rest_framework import serializers
from seguridad.models import Personas
from recaudo.models.base_models import TipoActuacion, TiposPago, Ubicaciones
from recaudo.models.pagos_models import (
    FacilidadesPago,
    RequisitosActuacion,
    CumplimientoRequisitos,
    DetallesFacilidadPago,
    PlanPagos,
    TasasInteres,
    RespuestaSolicitud
)
from recaudo.models.cobros_models import Obligaciones, Cartera, Deudores
from seguridad.models import Personas, Municipio


class ObligacionesSerializer(serializers.ModelSerializer):
    nro_expediente = serializers.ReadOnlyField(source='id_expediente.codigo_expediente',default=None)
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
        model = Obligaciones
        fields = ('nombre','fecha_inicio','nro_expediente','nro_resolucion','monto_inicial','valor_intereses', 'dias_mora')


class DeudorFacilidadPagoSerializer(serializers.ModelSerializer):
    ubicacion = serializers.SerializerMethodField()
    
    def get_ubicacion(self, obj):
        ubicacion = obj.ubicacion_id.nombre
        return ubicacion

    class Meta:
        model = Deudores
        fields = ('id', 'identificacion', 'nombres', 'apellidos', 'email', 'ubicacion')


class DatosContactoDeudorSerializer(serializers.ModelSerializer):
    ciudad = serializers.SerializerMethodField()

    def get_ciudad(self, obj):
        ubicacion = Municipio.objects.filter(cod_municipio=obj.municipio_residencia).first()
        ubicacion = ubicacion.nombre
        return ubicacion
        
    class Meta:
        model = Personas
        fields = ('direccion_notificaciones', 'ciudad', 'telefono_celular')
        

class FacilidadesPagoSerializer(serializers.ModelSerializer):
    id_deudor = DeudorFacilidadPagoSerializer

    class Meta:
        model = FacilidadesPago
        fields = '__all__'
        extra_kwargs = {
            'id_deudor': {'required': True},
            'id_tipo_actuacion': {'required': True},
            'id_tasas_interes': {'required': True},
            'documento_soporte': {'required': True},
            'consignacion_soporte': {'required':True}
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



class ConsultaObligacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Obligaciones
        fields = '__all__'

# class ListadoFacilidadesPagoSerializer(serializers.ModelSerializer):
#     identificacion = serializers.ReadOnlyField(source='id_deudor.identificacion',default=None)
#     nombre_de_usuario = serializers.SerializerMethodField()
#     id_facilidad = serializers.ReadOnlyField(source='id', default=None)

#     class Meta:
#         model = FacilidadesPago
#         fields = ('id_facilidad','nombre_de_usuario','identificacion', 'fecha_generacion')

#     def get_nombre_de_usuario(self, obj):
#         nombre_de_usuario = None
#         persona = Personas.objects.filter(numero_documento=obj.id_deudor.identificacion).first()
#         if persona: 
#             usuario = persona.user_set.exclude(id_usuario=1).first() 
#             nombre_de_usuario = usuario.nombre_de_usuario if usuario else None
#         return nombre_de_usuario


class ListadoFacilidadesPagoSerializer(serializers.ModelSerializer):
    identificacion = serializers.ReadOnlyField(source='id_deudor.identificacion',default=None)
    nombre_de_usuario = serializers.SerializerMethodField()
    nombre_funcionario = serializers.SerializerMethodField()
    id_facilidad = serializers.ReadOnlyField(source='id', default=None)

    class Meta:
        model = FacilidadesPago
        fields = ('id_facilidad','nombre_de_usuario','identificacion','numero_radicacion','fecha_generacion','nombre_funcionario')

    def get_nombre_de_usuario(self, obj):
        return f"{obj.id_deudor.nombres} {obj.id_deudor.apellidos}"


    def get_nombre_funcionario(self, obj):
        funcionario = Personas.objects.filter(id_persona=obj.id_funcionario).first()
        return f"{funcionario.primer_nombre} {funcionario.primer_apellido}"




class ConsultaFacilidadesPagosSerializer(serializers.ModelSerializer):
    tipo_actuacion = serializers.ReadOnlyField(source='id_tipo_actuacion.descripcion',default=None)

    class Meta:
        model = FacilidadesPago
        fields = ('id', 'id_deudor', 'tipo_actuacion', 'fecha_generacion',
                  'observaciones', 'periodicidad', 'cuotas',
                  'documento_soporte', 'consignacion_soporte', 'documento_garantia', 
                  'documento_no_enajenacion', 'id_funcionario','notificaciones',
                  )


class ListadoDeudoresUltSerializer(serializers.ModelSerializer):
    nombre_contribuyente = serializers.SerializerMethodField()

    class Meta:
        model = Deudores
        fields = ('id','nombre_contribuyente','identificacion')
        #fields = ('nombres','apellidos','identificacion')

    def get_nombre_contribuyente(self, obj):
        return f"{obj.nombres} {obj.apellidos}"

class AutorizacionNotificacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilidadesPago
        fields = ['notificaciones']


class RespuestaSolicitudFacilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaSolicitud
        fields = '__all__'


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

    
class PlanPagosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanPagos
        fields = '__all__'

    
class TasasInteresSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasasInteres
        fields = '__all__'
