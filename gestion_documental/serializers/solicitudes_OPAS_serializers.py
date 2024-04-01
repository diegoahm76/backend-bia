from rest_framework import serializers
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad

from gestion_documental.models.expedientes_models import ExpedientesDocumentales
from gestion_documental.models.radicados_models import AsignacionTramites, ConfigTiposRadicadoAgno
from tramites.models.tramites_models import AnexosTramite, PermisosAmbSolicitudesTramite, Requerimientos
from transversal.models.entidades_models import SucursalesEmpresas
from transversal.models.organigrama_models import UnidadesOrganizacionales



class OPAGetSerializer(serializers.ModelSerializer):
    
    tipo_solicitud = serializers.SerializerMethodField()
    nombre_completo_titular = serializers.SerializerMethodField()
    costo_proyecto = serializers.ReadOnlyField(source='id_solicitud_tramite.costo_proyecto', default=None)
    pagado = serializers.ReadOnlyField(source = 'id_solicitud_tramite.pago',default=None)
    cantidad_predios = serializers.ReadOnlyField(source='id_solicitud_tramite.cantidad_predios', default=None)
    cantidad_anexos = serializers.SerializerMethodField()
    radicado = serializers.SerializerMethodField()
    fecha_radicado = serializers.ReadOnlyField(source='id_solicitud_tramite.fecha_radicado', default=None)
    id_sede = serializers.ReadOnlyField(source='id_solicitud_tramite.id_sucursal_recepcion_fisica', default=None)
    sede = serializers.ReadOnlyField(source='id_solicitud_tramite.id_sucursal_recepcion_fisica.descripcion_sucursal', default=None)
    requiere_digitalizacion = serializers.ReadOnlyField(source='id_solicitud_tramite.requiere_digitalizacion', default=None)
    estado_actual = serializers.ReadOnlyField(source='id_solicitud_tramite.id_estado_actual_solicitud.nombre', default=None)
    nombre_proyecto = serializers.ReadOnlyField(source='id_solicitud_tramite.nombre_proyecto', default=None)
    persona_asignada  = serializers.SerializerMethodField()
    estado_asignacion_grupo = serializers.SerializerMethodField()
    unidad_asignada = serializers.SerializerMethodField()
    tiene_anexos = serializers.SerializerMethodField()
    nombre_opa = serializers.ReadOnlyField(source='id_permiso_ambiental.nombre', default=None)


    def get_tiene_anexos(self, obj):
        instance =PermisosAmbSolicitudesTramite.objects.filter(id_solicitud_tramite=obj.id_solicitud_tramite).first()

        if not instance:
            return False
        tramite = instance.id_solicitud_tramite
        tabla_intermedia_anexos_tramites = AnexosTramite.objects.filter(id_solicitud_tramite=tramite)
     
        if not tabla_intermedia_anexos_tramites:
            return False
        else:
            return True

    def get_tipo_solicitud(self, obj):
        return "OPA"
    # SERIALIZERMETHODFIELD ARCHIVOS
    def get_nombre_completo_titular(self, obj):
        nombre_persona_titular = None
        if obj.id_solicitud_tramite.id_persona_titular:
            if obj.id_solicitud_tramite.id_persona_titular.tipo_persona == 'J':
                nombre_persona_titular = obj.id_solicitud_tramite.id_persona_titular.razon_social
            else:
                nombre_list = [obj.id_solicitud_tramite.id_persona_titular.primer_nombre, obj.id_solicitud_tramite.id_persona_titular.segundo_nombre,
                                obj.id_solicitud_tramite.id_persona_titular.primer_apellido, obj.id_solicitud_tramite.id_persona_titular.segundo_apellido]
                nombre_persona_titular = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_titular = nombre_persona_titular if nombre_persona_titular != "" else None
        return nombre_persona_titular
    
    def get_radicado(self, obj):
        cadena = ""
        radicado = obj.id_solicitud_tramite.id_radicado
        if radicado:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=radicado.agno_radicado,cod_tipo_radicado=radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            return cadena
        else: 
            return 'SIN RADICAR'
    def get_cantidad_anexos(self, obj):
        conteo_anexos = AnexosTramite.objects.filter(id_solicitud_tramite=obj.id_solicitud_tramite).count()

        
        return conteo_anexos
    def get_estado_asignacion_grupo(self,obj):
        
        estado_asignacion_grupo = AsignacionTramites.objects.filter(id_solicitud_tramite=obj.id_solicitud_tramite).first()
        if estado_asignacion_grupo:
            if estado_asignacion_grupo.cod_estado_asignacion:
                if estado_asignacion_grupo.cod_estado_asignacion == 'Ac':
                    return "Aceptado"
                if estado_asignacion_grupo.cod_estado_asignacion == 'Re':
                    return "Rechazado"
                if estado_asignacion_grupo.cod_estado_asignacion == '':
                    return None
            else:
                return None
        else:
            return None
    
    def get_persona_asignada(self,obj):
        estado_asignacion_grupo = AsignacionTramites.objects.filter(id_solicitud_tramite=obj.id_solicitud_tramite).first()
        if estado_asignacion_grupo:

            if estado_asignacion_grupo.cod_estado_asignacion == 'Ac':
                if estado_asignacion_grupo.id_persona_asignada:
                    nombre_completo_responsable = None
                    nombre_list = [estado_asignacion_grupo.id_persona_asignada.primer_nombre, estado_asignacion_grupo.id_persona_asignada.segundo_nombre,
                                estado_asignacion_grupo.id_persona_asignada.primer_apellido, estado_asignacion_grupo.id_persona_asignada.segundo_apellido]
                    nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
                    return nombre_completo_responsable
                else:
                    return 'No tiene persona asignada'
            else:
                if estado_asignacion_grupo.cod_estado_asignacion == 'Re':
                    return 'La solicitud fue rechazada'
                if estado_asignacion_grupo.cod_estado_asignacion == '':
                    return None         
                if estado_asignacion_grupo.cod_estado_asignacion == None:
                    return None
        
    def get_unidad_asignada(self,obj):
            
        id = obj.id_solicitud_tramite
        estado_asignacion_grupo = AsignacionTramites.objects.filter(id_solicitud_tramite=id).order_by('-id_asignacion_tramite').first()

        if estado_asignacion_grupo:
            if estado_asignacion_grupo.cod_estado_asignacion == 'Ac':#

                
                if estado_asignacion_grupo.id_und_org_seccion_asignada:
                    return estado_asignacion_grupo.id_und_org_seccion_asignada.nombre
                
                if estado_asignacion_grupo.id_und_org_oficina_asignada:
                    return estado_asignacion_grupo.id_und_org_oficina_asignada.nombre
                
            else:
                if estado_asignacion_grupo.cod_estado_asignacion == 'Re':
                    return 'La solicitud fue rechazada'
                if estado_asignacion_grupo.cod_estado_asignacion == '':
                    return None
                if estado_asignacion_grupo.cod_estado_asignacion == None:
                    return None
    class Meta:
        model = PermisosAmbSolicitudesTramite
        fields = ['id_solicitud_tramite','tipo_solicitud','nombre_proyecto','nombre_opa','nombre_completo_titular','costo_proyecto','pagado','cantidad_predios','cantidad_anexos','radicado','fecha_radicado','id_sede','sede','requiere_digitalizacion','estado_actual','estado_asignacion_grupo','persona_asignada','unidad_asignada','tiene_anexos']




class RequerimientoSobreOPATramiteGetSerializer(serializers.ModelSerializer):
    tipo_tramite = serializers.SerializerMethodField()
    numero_radicado = serializers.SerializerMethodField()
    estado = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre',default=None)
    class Meta:
        model = Requerimientos
        # fields = ['id_solicitud_al_usuario_sobre_pqrsdf']
        fields = ['id_requerimiento','tipo_tramite','fecha_radicado','numero_radicado','estado']

    def get_tipo_tramite(self,obj):
        return "Requerimiento a una solicitud"
    def get_numero_radicado(self,obj):
        cadena = ""
        if obj.id_radicado:
            cadena= str(obj.id_radicado.prefijo_radicado)+'-'+str(obj.id_radicado.agno_radicado)+'-'+str(obj.id_radicado.nro_radicado)
            return cadena
        return 'SIN RADICAR'