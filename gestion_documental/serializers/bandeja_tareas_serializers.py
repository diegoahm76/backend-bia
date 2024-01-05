
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.bandeja_tareas_models import AdicionalesDeTareas, TareasAsignadas

from gestion_documental.models.radicados_models import PQRSDF, Anexos_PQR, AsignacionPQR, BandejaTareasPersona, ComplementosUsu_PQR, SolicitudAlUsuarioSobrePQRSDF, TareaBandejaTareasPersona
from datetime import timedelta
from datetime import datetime

from transversal.models.personas_models import Personas

class BandejaTareasPersonaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandejaTareasPersona
        fields = '__all__'

#TareasAsignadas crear
        

class TareaBandejaTareasPersonaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaBandejaTareasPersona
        fields = '__all__'
        
class TareasAsignadasCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareasAsignadas
        fields = '__all__'

class TareasAsignadasUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareasAsignadas
        fields = '__all__'

class TareaBandejaTareasPersonaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaBandejaTareasPersona
        fields = '__all__'
class TareasAsignadasGetSerializer(serializers.ModelSerializer):
    #   tipo_mantenimiento = serializers.CharField(source='get_cod_tipo_mantenimiento_display')
    #cod_tipo_tarea es un choices
    tipo_tarea =serializers.ReadOnlyField(source='get_cod_tipo_tarea_display',default=None)
    asignado_por = serializers.SerializerMethodField()
    asignado_para = serializers.SerializerMethodField()
    #fecha asignacion
    #comentario asignacion
    radicado = serializers.SerializerMethodField(default=None)
    fecha_radicado =  serializers.SerializerMethodField(default=None)
    dias_para_respuesta = serializers.SerializerMethodField(default=None)
    estado_tarea = serializers.ReadOnlyField(source='get_cod_estado_asignacion_display',default=None)
    id_pqrsdf = serializers.SerializerMethodField(default=None)
    respondida_por = serializers.ReadOnlyField(source='nombre_persona_que_responde',default=None)
    tarea_reasignada_a = serializers.SerializerMethodField(default=None)
    unidad_org_destino = serializers.SerializerMethodField(default=None)
    estado_reasignacion_tarea = serializers.SerializerMethodField(default=None)
    class Meta:#
        model = TareasAsignadas
        #fields = '__all__'
        fields =['id_tarea_asignada','id_pqrsdf','tipo_tarea','asignado_por','asignado_para','fecha_asignacion',
                 'comentario_asignacion','radicado','fecha_radicado','dias_para_respuesta',
                 'requerimientos_pendientes_respuesta','estado_tarea','fecha_respondido','respondida_por','tarea_reasignada_a','unidad_org_destino','estado_reasignacion_tarea']
    def get_tarea_reasignada_a(self,obj):
        return None
    def get_estado_reasignacion_tarea(self,obj):
        return None
    def get_unidad_org_destino(self,obj):
        return None
    def get_asignado_por(self,obj):
        #buscamos la asignacion
        asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=obj.id_asignacion).first()
        if not asignacion:
            return None

        persona = None

        if asignacion.id_persona_asigna:
            persona = asignacion.id_persona_asigna
        else:
            return None
        
        nombre_completo = None
        nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                        persona.primer_apellido, persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo = nombre_completo if nombre_completo != "" else None
        return nombre_completo
    
    def get_asignado_para(self,obj):
        #buscamos la asignacion
        asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=obj.id_asignacion).first()
   
        persona = None
        if not asignacion:
            return None
        if asignacion.id_persona_asignada:
            persona = asignacion.id_persona_asignada
        else:
            return None
        
        nombre_completo = None
        nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                        persona.primer_apellido, persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo = nombre_completo if nombre_completo != "" else None
        return nombre_completo
    
    def get_radicado(self,obj):
        #buscamos la asignacion
        asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=obj.id_asignacion).first()
        pqrsdf = asignacion.id_pqrsdf
        cadena = ""
        if pqrsdf.id_radicado:
            cadena= str(pqrsdf.id_radicado.prefijo_radicado)+'-'+str(pqrsdf.id_radicado.agno_radicado)+'-'+str(pqrsdf.id_radicado.nro_radicado)
            return cadena
        else: return cadena

    def get_fecha_radicado(self,obj):
        #buscamos la asignacion
        asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=obj.id_asignacion).first()
        pqrsdf = asignacion.id_pqrsdf
        fecha_radicado = pqrsdf.fecha_radicado
        return fecha_radicado

    def get_dias_para_respuesta(self,obj):
        #buscamos la asignacion
        fecha_actual = datetime.now()
        asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=obj.id_asignacion).first()
        pqrsdf = asignacion.id_pqrsdf
        dias = pqrsdf.dias_para_respuesta
        fecha_radicado = pqrsdf.fecha_radicado
        if fecha_radicado:
            fecha_maxima = fecha_radicado + timedelta(days=dias)

            dias = (fecha_maxima - fecha_actual)
            dias = dias.days
            return dias
        return None 
        
    def get_id_pqrsdf(self,obj):
        #buscamos la asignacion
        asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=obj.id_asignacion).first()

        if asignacion:
            pqrsdf = asignacion.id_pqrsdf
            id_pqrsdf = pqrsdf.id_PQRSDF
            return id_pqrsdf
        return None

class TareasAsignadasGetJustificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareasAsignadas
        fields = ['id_tarea_asignada','justificacion_rechazo']


class AdicionalesDeTareasGetByTareaSerializer(serializers.ModelSerializer):
    tipo = serializers.SerializerMethodField()
    titular = serializers.SerializerMethodField()
    asunto = serializers.ReadOnlyField(source='id_complemento_usu_pqr.asunto',default=None)
    cantidad_anexos = serializers.ReadOnlyField(source='id_complemento_usu_pqr.cantidad_anexos',default=None)
    radicado = serializers.SerializerMethodField(default=None)
    fecha_radicado = serializers.SerializerMethodField(default=None)
    class Meta:
        model = AdicionalesDeTareas
      
        fields =['id_adicional_de_tarea','id_complemento_usu_pqr','tipo','titular','asunto','cantidad_anexos','radicado','fecha_radicado','fecha_de_adicion']

    def get_tipo(self,obj):
        complemento = obj.id_complemento_usu_pqr
        if complemento:
            #print(complemento.id_PQRSDF)
            #print(complemento.id_solicitud_usu_PQR)
            if complemento.id_PQRSDF and complemento.id_solicitud_usu_PQR == None:
                return 'Complemento de PQRSDF'
            if complemento.id_PQRSDF == None and complemento.id_solicitud_usu_PQR:
                return 'Respuesta a Solicitud'
        return None
    
    def get_titular(self, obj):
        complemento = obj.id_complemento_usu_pqr
        if not complemento:
            return None
        pqrsdf= complemento.id_PQRSDF
        if not pqrsdf:
            return None
     
        nombre_completo_responsable = None
        nombre_list = [pqrsdf.id_persona_titular.primer_nombre, pqrsdf.id_persona_titular.segundo_nombre,
                        pqrsdf.id_persona_titular.primer_apellido, pqrsdf.id_persona_titular.segundo_apellido]
        nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
        return nombre_completo_responsable
    
    def get_radicado(self, obj):
        cadena = ""
        complemento = obj.id_complemento_usu_pqr
        if complemento.id_radicado:
            cadena= str(complemento.id_radicado.prefijo_radicado)+'-'+str(complemento.id_radicado.agno_radicado)+'-'+str(complemento.id_radicado.nro_radicado)
            return cadena
        return None

    def get_fecha_radicado(self, obj):
        complemento = obj.id_complemento_usu_pqr
        if complemento.id_radicado:
            return complemento.id_radicado.fecha_radicado
        return None

#REQUERIMIENTO SOBRE PQRSDF 103
class PQRSDFTitularGetBandejaTareasSerializer(serializers.ModelSerializer):
    nombres = serializers.SerializerMethodField()
    apellidos = serializers.SerializerMethodField() 
    tipo_documento = serializers.ReadOnlyField(source='tipo_documento.nombre',default=None)
    unidad_organizacional_actual = serializers.ReadOnlyField(source='id_unidad_organizacional_actual.nombre',default=None)
    class Meta:
        model = Personas
        fields = ['nombres','apellidos','tipo_documento','numero_documento','unidad_organizacional_actual']
    def obtener_nombres(self, persona):
        nombres = [
            persona.primer_nombre,
            persona.segundo_nombre,
        ]
        return ' '.join(item for item in nombres if item is not None)

    def obtener_apellidos(self, persona):
        apellidos = [
            persona.primer_apellido,
            persona.segundo_apellido,
        ]
        return ' '.join(item for item in apellidos if item is not None)

    def get_nombres(self, obj):
        if obj:
            return self.obtener_nombres(obj)
        return None

    def get_apellidos(self, obj):
        if obj:
            return self.obtener_apellidos(obj)
        return None


class PQRSDFDetalleRequerimiento(serializers.ModelSerializer):
   
    estado_actual = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre',default=None)
    radicado = serializers.SerializerMethodField()
    fecha_radicado_entrada = serializers.ReadOnlyField(source='fecha_radicado',default=None)
    tipo = serializers.CharField(source='get_cod_tipo_PQRSDF_display')
    class Meta:
        model = PQRSDF
        fields = ['tipo','id_PQRSDF','estado_actual','radicado','fecha_radicado_entrada','asunto','descripcion']

    def get_radicado(self, obj):
        cadena = ""
        if obj.id_radicado:
            cadena= str(obj.id_radicado.prefijo_radicado)+'-'+str(obj.id_radicado.agno_radicado)+'-'+str(obj.id_radicado.nro_radicado)
            return cadena
        
class RequerimientoSobrePQRSDFGetSerializer(serializers.ModelSerializer):
    tipo_tramite = serializers.SerializerMethodField()
    numero_radicado = serializers.SerializerMethodField()
    estado = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre',default=None)
    class Meta:
        model = SolicitudAlUsuarioSobrePQRSDF
        # fields = ['id_solicitud_al_usuario_sobre_pqrsdf']
        fields = ['id_solicitud_al_usuario_sobre_pqrsdf','tipo_tramite','fecha_radicado_salida','numero_radicado','estado']

    def get_tipo_tramite(self,obj):
        return "Requerimiento a una solicitud"
    def get_numero_radicado(self,obj):
        cadena = ""
        if obj.id_radicado_salida:
            cadena= str(obj.id_radicado_salida.prefijo_radicado)+'-'+str(obj.id_radicado_salida.agno_radicado)+'-'+str(obj.id_radicado_salida.nro_radicado)
            return cadena
        return 'SIN RADICAR'

class RequerimientoSobrePQRSDFCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudAlUsuarioSobrePQRSDF
        fields = '__all__'


class Anexos_RequerimientoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos_PQR
        fields = '__all__'
#reasignacion de tarea
class TareasAsignadasGetDetalleByIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareasAsignadas
        fields = '__all__'
    
 