
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.bandeja_tareas_models import TareasAsignadas

from gestion_documental.models.radicados_models import AsignacionPQR, BandejaTareasPersona, TareaBandejaTareasPersona
from datetime import timedelta
from datetime import datetime

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
    radicado = serializers.SerializerMethodField()
    fecha_radicado =  serializers.SerializerMethodField()
    dias_para_respuesta = serializers.SerializerMethodField()
    estado_tarea = serializers.ReadOnlyField(source='get_cod_estado_asignacion_display',default=None)
    id_pqrsdf = serializers.SerializerMethodField()
    respondida_por = serializers.ReadOnlyField(source='nombre_persona_que_responde',default=None)
    tarea_reasignada_a = serializers.SerializerMethodField()
    unidad_org_destino = serializers.SerializerMethodField()
    estado_reasignacion_tarea = serializers.SerializerMethodField()
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
        pqrsdf = asignacion.id_pqrsdf
        id_pqrsdf = pqrsdf.id_PQRSDF
        return id_pqrsdf

class TareasAsignadasGetJustificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareasAsignadas
        fields = ['id_tarea_asignada','justificacion_rechazo']


    



