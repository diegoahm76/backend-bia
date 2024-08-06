from decimal import Decimal
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
from recaudo.models.procesos_models import Procesos
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


class GarantiasFacilidadGetSerializer(serializers.ModelSerializer):
    documento_garantia = serializers.ReadOnlyField(source='documento_garantia.ruta_archivo.url', default=None)

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


class CumplimientoRequisitosGetSerializer (serializers.ModelSerializer):
    documento = serializers.ReadOnlyField(source='documento.ruta_archivo.url', default=None)

    class Meta:
        model = CumplimientoRequisitos
        fields = '__all__'


class DeudorDatosSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='id_persona', default=None)
    identificacion = serializers.ReadOnlyField(source='numero_documento', default=None)
    nombre_completo = serializers.SerializerMethodField()
    ciudad = serializers.ReadOnlyField(source='municipio_residencia.nombre', default=None)
    class Meta:
        model = Personas
        fields = ('id', 'identificacion', 'nombre_completo', 'email', 'direccion_notificaciones', 'telefono_celular', 'ciudad')


    def get_nombre_completo(self, obj):
        if obj.id_persona:
            if obj.razon_social:
                nombre_completo = obj.razon_social
            else:
                nombre_completo = ' '.join(filter(None, [obj.primer_nombre, obj.segundo_nombre, obj.primer_apellido, obj.segundo_apellido]))
            return nombre_completo
        # elif obj.id_persona_deudor_pymisis:
        #     return f"{obj.id_persona_deudor_pymisis.t03nombre}"
        else:
            return None
        

class FacilidadesPagoSerializer(serializers.ModelSerializer):
    numero_radicado = serializers.SerializerMethodField()

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

    def get_numero_radicado(self,obj):
        cadena = ""
        if obj.id_radicado:
            cadena= str(obj.id_radicado.prefijo_radicado)+'-'+str(obj.id_radicado.agno_radicado)+'-'+str(obj.id_radicado.nro_radicado)
            return cadena
        return 'SIN RADICAR'


class ListadoFacilidadesPagoSerializer(serializers.ModelSerializer):
    identificacion = serializers.ReadOnlyField(source='id_deudor.numero_documento', default=None)
    nombre_de_usuario = serializers.SerializerMethodField()
    nombre_funcionario = serializers.SerializerMethodField()
    id_facilidad = serializers.ReadOnlyField(source='id', default=None)
    tiene_plan_pago = serializers.SerializerMethodField()
    numero_radicado = serializers.SerializerMethodField()

    def get_nombre_de_usuario(self, obj):
        if obj.id_deudor.razon_social:
            nombre_completo = obj.id_deudor.razon_social
        else:
            nombre_completo = ' '.join(filter(None, [obj.id_deudor.primer_nombre, obj.id_deudor.segundo_nombre, obj.id_deudor.primer_apellido, obj.id_deudor.segundo_apellido]))
        return nombre_completo

    def get_nombre_funcionario(self, obj):
        nombre_completo = ' '.join(filter(None, [obj.primer_nombre, obj.segundo_nombre, obj.primer_apellido, obj.segundo_apellido]))
        return nombre_completo
    
    def get_tiene_plan_pago(self, obj):
        tiene_plan_pago = False
        if PlanPagos.objects.filter(id_facilidad_pago=obj.id).first():
            tiene_plan_pago = True
        return tiene_plan_pago
    
    def get_numero_radicado(self,obj):
        cadena = ""
        if obj.id_radicado:
            cadena= str(obj.id_radicado.prefijo_radicado)+'-'+str(obj.id_radicado.agno_radicado)+'-'+str(obj.id_radicado.nro_radicado)
            return cadena
        return 'SIN RADICAR'
      
    class Meta:
        model = FacilidadesPago
        fields = ('id_facilidad','nombre_de_usuario','identificacion','numero_radicado','fecha_generacion','nombre_funcionario', 'id_persona','tiene_plan_pago')


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
    documento_soporte = serializers.ReadOnlyField(source='documento_soporte.ruta_archivo.url', default=None)
    consignacion_soporte = serializers.ReadOnlyField(source='consignacion_soporte.ruta_archivo.url', default=None)
    documento_no_enajenacion = serializers.ReadOnlyField(source='documento_no_enajenacion.ruta_archivo.url', default=None)
    numero_radicado = serializers.SerializerMethodField()

    class Meta:
        model = FacilidadesPago
        fields = ('id', 'id_deudor', 'id_tipo_actuacion', 'tipo_actuacion', 'fecha_generacion',
                  'observaciones', 'periodicidad', 'cuotas', 'documento_soporte', 'consignacion_soporte',
                  'valor_abonado', 'fecha_abono', 'documento_no_enajenacion', 'id_funcionario',
                  'notificaciones', 'numero_radicado'
                  )
        
    def get_numero_radicado(self,obj):
        cadena = ""
        if obj.id_radicado:
            cadena= str(obj.id_radicado.prefijo_radicado)+'-'+str(obj.id_radicado.agno_radicado)+'-'+str(obj.id_radicado.nro_radicado)
            return cadena
        return 'SIN RADICAR'


class BienesDeudorSerializer(serializers.ModelSerializer):
    ubicacion = serializers.ReadOnlyField(source='id_ubicacion.nombre', default=None)
    nombre_tipo_bien = serializers.ReadOnlyField(source='id_tipo_bien.descripcion', default=None)
    documento_soporte = serializers.ReadOnlyField(source='documento_soporte.ruta_archivo.url', default=None)
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


class RespuestaSolicitudGetSerializer(serializers.ModelSerializer):
    informe_dbme = serializers.ReadOnlyField(source='informe_dbme.ruta_archivo.url', default=None)

    class Meta:
        model = RespuestaSolicitud
        fields = '__all__'


class CarteraSerializer(serializers.ModelSerializer):
    # nro_resolucion = serializers.ReadOnlyField(source='id_expediente.numero_resolucion',default=None)
    # estado = serializers.ReadOnlyField(source='id_expediente.estado',default=None)
    procesos = serializers.SerializerMethodField()
    expediente = serializers.SerializerMethodField()
    tipo_renta = serializers.ReadOnlyField(source='tipo_renta.nombre_tipo_renta',default=None)


    def get_procesos(self, obj):
        procesos = Procesos.objects.filter(id_cartera=obj.id)
        serializers_procesos = ProcesosCarteraSerializer(procesos, many = True)
        return serializers_procesos.data
    
    def get_expediente(self, obj):
        if obj.id_expediente:
            if obj.id_expediente.id_expediente_pimisys:
                return obj.id_expediente.id_expediente_pimisys.t920codexpediente
            elif obj.id_expediente.id_expediente_doc:
                return f"{obj.id_expediente.id_expediente_doc.codigo_exp_und_serie_subserie}-{obj.id_expediente.id_expediente_doc.codigo_exp_Agno}-{obj.id_expediente.id_expediente_doc.codigo_exp_consec_por_agno}"
            else:
                return None
        else:
            return None

    class Meta:
        model = Cartera
        fields = '__all__'


class ConsultaCarteraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartera
        fields = '__all__'


class ListadoDeudoresUltSerializer(serializers.ModelSerializer):
    nombre_contribuyente = serializers.SerializerMethodField()
    identificacion = serializers.ReadOnlyField(source='numero_documento',default=None)
    obligaciones = serializers.SerializerMethodField()
    monto_total = serializers.SerializerMethodField()
    monto_total_con_intereses = serializers.SerializerMethodField()

    class Meta:
        model = Personas
        fields = ('id_persona','nombre_contribuyente','identificacion', 'obligaciones', 'monto_total', 'monto_total_con_intereses','email','telefono_celular','direccion_residencia')

    def get_nombre_contribuyente(self, obj):
        if obj.razon_social:
            nombre_completo = obj.razon_social
        else:
            nombre_completo = ' '.join(filter(None, [obj.primer_nombre, obj.segundo_nombre, obj.primer_apellido, obj.segundo_apellido]))
        return nombre_completo
        
        
    def get_obligaciones(self, obj):
        cartera = Cartera.objects.filter(id_deudor=obj.id_persona)
        if cartera:
            return True
        else:
            return False
    
    def get_monto_total(self, obj):
        monto_total = Decimal('0.0')
        cartera = Cartera.objects.filter(id_deudor=obj.id_persona)
        for item in cartera:
            monto_total += item.monto_inicial if item.monto_inicial else Decimal('0.0')
        return monto_total

    def get_monto_total_con_intereses(self, obj):
        monto_total = Decimal('0.0')
        cartera = Cartera.objects.filter(id_deudor=obj.id_persona)
        for item in cartera:
            monto_inicial = item.monto_inicial if item.monto_inicial else Decimal('0.0')
            valor_intereses = item.valor_intereses if item.valor_intereses else Decimal('0.0')
            monto_total += monto_inicial + valor_intereses
        return monto_total


class ListadoFacilidadesSeguimientoSerializer(serializers.ModelSerializer):
    estado = serializers.SerializerMethodField()
    numero_radicado = serializers.SerializerMethodField()

    class Meta:
        model = FacilidadesPago
        fields = ('id','numero_radicado','estado')

    def get_estado(self, obj):
        respuesta_solicitud = RespuestaSolicitud.objects.filter(id_facilidad_pago=obj.id).first()
        if not respuesta_solicitud:
            estado = 'SIN RESPONDER'
        else:
            estado = respuesta_solicitud.estado
        return estado
    
    def get_numero_radicado(self,obj):
        cadena = ""
        if obj.id_radicado:
            cadena= str(obj.id_radicado.prefijo_radicado)+'-'+str(obj.id_radicado.agno_radicado)+'-'+str(obj.id_radicado.nro_radicado)
            return cadena
        return 'SIN RADICAR'
    

class ProcesosCarteraSerializer(serializers.ModelSerializer):
    nombre_etapa = serializers.ReadOnlyField(source='id_etapa.etapa',default=None)
    descripcion_etapa = serializers.ReadOnlyField(source='id_etapa.descripcion',default=None)
    nombre_categoria = serializers.ReadOnlyField(source='id_categoria.categoria',default=None)
    orden_categoria= serializers.ReadOnlyField(source='id_categoria.orden',default=None)


    class Meta:
        model = Procesos
        fields = '__all__'
