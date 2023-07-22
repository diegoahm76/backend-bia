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



class RespuestaSolicitudFacilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaSolicitud
        fields = '__all__'


class TipoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposPago
        fields = ('id', 'descripcion')


class CumplimientoRequisitosSerializer (serializers.ModelSerializer):
    class Meta:
        model = CumplimientoRequisitos
        fields = '__all__'


class DetallesFacilidadPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model =DetallesFacilidadPago
        fields = '__all__'

