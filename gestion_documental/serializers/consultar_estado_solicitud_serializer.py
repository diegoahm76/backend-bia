from rest_framework import serializers

from gestion_documental.models.radicados_models import  AsignacionTramites, ConfigTiposRadicadoAgno, EstadosSolicitudes
from tramites.models.tramites_models import  PermisosAmbSolicitudesTramite, SolicitudesTramites
from datetime import datetime, timedelta

class SolicitudesTramitesEstadoSolicitudGetSerializer(serializers.ModelSerializer):
    #nombre_cod_tipo_operacion_tramite = serializers.ReadOnlyField(source='get_cod_tipo_operacion_tramite_display',default=None)
    #nombre_cod_relacion_con_el_titular = serializers.ReadOnlyField(source='get_cod_relacion_con_el_titular_display', default=None)
    estado_actual = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre', default=None)
    nombre_completo_titular = serializers.SerializerMethodField()
    radicado = serializers.SerializerMethodField()
    tipo_solicitud = serializers.SerializerMethodField()
    tiempo_respuesta = serializers.SerializerMethodField()
    nombre_tramite = serializers.SerializerMethodField()
    persona_radica = serializers.SerializerMethodField()
    ubicacion_corporacion = serializers.SerializerMethodField()
    documento = serializers.SerializerMethodField()
    class Meta:
        model = SolicitudesTramites
        fields = ['id_solicitud_tramite','tipo_solicitud','nombre_completo_titular','radicado','fecha_radicado','persona_radica','tiempo_respuesta','estado_actual','nombre_tramite','ubicacion_corporacion','documento']


    def get_documento(self, obj):
        #PENDIENTE VALIDACIONES O ENTREGAS DE MODELADO
            return None

    def get_ubicacion_corporacion(self, obj):
        #PENDIENTE VALIDACIONES O ENTREGAS DE MODELADO
            if not obj.id_estado_actual_solicitud:
                return None
            
            if obj.id_estado_actual_solicitud.id_estado_solicitud== 5:

                asignacion = AsignacionTramites.objects.filter(id_solicitud_tramite=obj.id_solicitud_tramite,cod_estado_asignacion='Ac').first()
                return asignacion.id_und_org_seccion_asignada.nombre
            return obj.id_estado_actual_solicitud.ubicacion_corporacion
            return None

    def get_persona_radica(self,obj):

        if not obj.id_radicado:
            return None
        persona = obj.id_radicado.id_persona_radica

        if persona:
            nombre_completo_responsable = None
            nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                            persona.primer_apellido, persona.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
            return nombre_completo_responsable
        else:
            return None


    def get_nombre_tramite(self, obj):
        instance = PermisosAmbSolicitudesTramite.objects.filter(id_solicitud_tramite=obj.id_solicitud_tramite).first()
        if not instance:
            return None
        
        nombre_tramite = instance.id_permiso_ambiental.nombre
        return nombre_tramite
    def get_tiempo_respuesta(self,obj):
        fecha_radicado = obj.fecha_radicado

        if not fecha_radicado:
            return None
        
        fecha_actual = datetime.now()
        fecha_radicado_mas_15_dias = fecha_radicado + timedelta(days=15)
      
   
        dias_faltan = fecha_radicado_mas_15_dias - fecha_actual

        return dias_faltan.days

    def get_tipo_solicitud(self, obj):
        
        return 'TRAMITES Y SERVICIOS'
    
    def get_nombre_completo_titular(self, obj):

        if obj.id_persona_titular:
            nombre_completo_responsable = None
            nombre_list = [obj.id_persona_titular.primer_nombre, obj.id_persona_titular.segundo_nombre,
                            obj.id_persona_titular.primer_apellido, obj.id_persona_titular.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
            return nombre_completo_responsable
        else:
            if obj.es_anonima:
                return "Anonimo"
            else:
                return 'No Identificado'
            
    def get_radicado(self, obj):
        cadena = ""
        if obj.id_radicado:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=obj.id_radicado.agno_radicado,cod_tipo_radicado=obj.id_radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(obj.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            return cadena
        

class TramitesEstadosSolicitudesGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadosSolicitudes
        fields = ['id_estado_solicitud','nombre']