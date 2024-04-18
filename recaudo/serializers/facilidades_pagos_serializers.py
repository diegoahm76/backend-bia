from rest_framework import serializers
from recaudo.models.procesos_models import (
    Avaluos, 
    Bienes
)
from recaudo.models.facilidades_pagos_models import (
    FacilidadesPago,
    GarantiasFacilidad,
    DetallesBienFacilidadPago,
    CumplimientoRequisitos, 
    RequisitosActuacion,
    RespuestaSolicitud,
    DetallesFacilidadPago
)
from recaudo.models.planes_pagos_models import PlanPagos
from recaudo.models.base_models import TiposBien, TipoActuacion
from recaudo.models.cobros_models import Deudores, Cartera

from transversal.models.personas_models import Personas
from transversal.models.base_models import Municipio

class DetallesFacilidadPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model =DetallesFacilidadPago
        fields = '__all__'


class TipoBienSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposBien
        fields = '__all__'


class TipoActuacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoActuacion
        fields = '__all__'


class BienSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bienes
        fields = '__all__'


class AvaluosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avaluos
        fields = '__all__'


class RequisitosActuacionSerializer (serializers.ModelSerializer):
    class Meta:
        model = RequisitosActuacion
        fields = '__all__'


class GarantiasFacilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = GarantiasFacilidad
        fields = '__all__'    


class DetallesBienFacilidadPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallesBienFacilidadPago
        fields = '__all__'


class CumplimientoRequisitosSerializer (serializers.ModelSerializer):
    class Meta:
        model = CumplimientoRequisitos
        fields = '__all__'


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
        ubicacion = Municipio.objects.filter(cod_municipio=obj.municipio_residencia.cod_municipio).first()
        ubicacion = ubicacion.nombre
        return ubicacion
        
    class Meta:
        model = Personas
        fields = ('direccion_notificaciones', 'ciudad', 'telefono_celular')


class FacilidadesPagoSerializer(serializers.ModelSerializer):
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


class ListadoFacilidadesPagoSerializer(serializers.ModelSerializer):
    identificacion = serializers.ReadOnlyField(source='id_deudor.identificacion',default=None)
    nombre_de_usuario = serializers.SerializerMethodField()
    nombre_funcionario = serializers.SerializerMethodField()
    id_facilidad = serializers.ReadOnlyField(source='id', default=None)
    tiene_plan_pago = serializers.SerializerMethodField()
    id_persona = serializers.SerializerMethodField()

    def get_nombre_de_usuario(self, obj):
        return f"{obj.id_deudor.nombres} {obj.id_deudor.apellidos}"

    def get_nombre_funcionario(self, obj):      
        return f"{obj.id_funcionario.primer_nombre} {obj.id_funcionario.primer_apellido}"
    
    def get_tiene_plan_pago(self, obj):
        tiene_plan_pago = False
        if PlanPagos.objects.filter(id_facilidad_pago=obj.id).first():
            tiene_plan_pago = True
        return tiene_plan_pago
    
    def get_id_persona(self, obj):
        persona = Personas.objects.filter(numero_documento=obj.id_deudor.identificacion).first()
        if persona:
            id_persona = persona.id_persona
        else:
            id_persona = None
        return id_persona
    
    
    class Meta:
        model = FacilidadesPago
        fields = ('id_facilidad','nombre_de_usuario','identificacion','numero_radicacion','fecha_generacion','nombre_funcionario', 'id_persona','tiene_plan_pago')


class FacilidadesPagoFuncionarioPutSerializer(serializers.ModelSerializer):
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


class FacilidadPagoGetByIdSerializer(serializers.ModelSerializer):
    tipo_actuacion = serializers.ReadOnlyField(source='id_tipo_actuacion.descripcion',default=None)

    class Meta:
        model = FacilidadesPago
        fields = ('id', 'id_deudor', 'id_tipo_actuacion', 'tipo_actuacion', 'fecha_generacion',
                  'observaciones', 'periodicidad', 'cuotas', 'documento_soporte', 'consignacion_soporte',
                  'valor_abonado', 'fecha_abono', 'documento_no_enajenacion', 'id_funcionario',
                  'notificaciones', 'numero_radicacion'
                  )


class BienesDeudorSerializer(serializers.ModelSerializer):
    ubicacion = serializers.ReadOnlyField(source='id_ubicacion.nombre', default=None)
    nombre_tipo_bien = serializers.ReadOnlyField(source='id_tipo_bien.descripcion', default=None)
    valor = serializers.SerializerMethodField()
    
    def get_valor(self, obj):
        valor_avaluo = Avaluos.objects.filter(id_bien=obj.id).first()
        valora = valor_avaluo.valor
        return valora

    class Meta:
        model = Bienes
        fields = ('nombre_tipo_bien','descripcion','valor','direccion','ubicacion','documento_soporte')


class RespuestaSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaSolicitud
        fields = '__all__'


class CarteraSerializer(serializers.ModelSerializer):
    nro_expediente = serializers.ReadOnlyField(source='id_expediente.cod_expediente',default=None)
    nro_resolucion = serializers.ReadOnlyField(source='id_expediente.numero_resolucion',default=None)
    estado = serializers.ReadOnlyField(source='id_expediente.estado',default=None)
    class Meta:
        model = Cartera
        fields = ('id','nombre','inicio','nro_expediente','nro_resolucion','monto_inicial','valor_intereses', 'dias_mora','estado')


class ConsultaCarteraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartera
        fields = '__all__'


class ListadoDeudoresUltSerializer(serializers.ModelSerializer):
    nombre_contribuyente = serializers.SerializerMethodField()

    class Meta:
        model = Deudores
        fields = ('id','nombre_contribuyente','identificacion')

    def get_nombre_contribuyente(self, obj):
        return f"{obj.nombres} {obj.apellidos}"


class ListadoFacilidadesSeguimientoSerializer(serializers.ModelSerializer):
    estado = serializers.SerializerMethodField()

    class Meta:
        model = FacilidadesPago
        fields = ('id','numero_radicacion','estado')

    def get_estado(self, obj):
        respuesta_solicitud = RespuestaSolicitud.objects.filter(id_facilidad_pago=obj.id).first()
        if not respuesta_solicitud:
            estado = 'SIN RESPONDER'
        else:
            estado = respuesta_solicitud.estado
        return estado
