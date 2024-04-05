
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.bandeja_tareas_models import AdicionalesDeTareas, ReasignacionesTareas, TareasAsignadas
from gestion_documental.models.expedientes_models import ArchivosDigitales

from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, AsignacionOtros, AsignacionPQR, AsignacionTramites, BandejaTareasPersona, ComplementosUsu_PQR, ConfigTiposRadicadoAgno, MetadatosAnexosTmp, Otros, RespuestaPQR, SolicitudAlUsuarioSobrePQRSDF, SolicitudDeDigitalizacion, TareaBandejaTareasPersona
from datetime import timedelta
from datetime import datetime
from tramites.models.tramites_models import AnexosTramite, PermisosAmbSolicitudesTramite, Requerimientos, RespuestaOPA, RespuestasRequerimientos, SolicitudesTramites
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.models.organigrama_models import UnidadesOrganizacionales

from transversal.models.personas_models import Personas

class TareasAsignadasOpasUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareasAsignadas
        fields = '__all__'

class SolicitudesTramitesOpaDetalleSerializer(serializers.ModelSerializer):
    nombre_completo_titular = serializers.SerializerMethodField()
    cantidad_anexos = serializers.SerializerMethodField()
    nombre_opa = serializers.ReadOnlyField(source='id_permiso_ambiental.nombre', default=None)
    tipo_operacion = serializers.ReadOnlyField(source='id_solicitud_tramite.get_cod_tipo_operacion_tramite_display', default=None)
    nombre_proyecto = serializers.ReadOnlyField(source='id_solicitud_tramite.nombre_proyecto', default=None)
    costo_proyecto = serializers.ReadOnlyField(source='id_solicitud_tramite.costo_proyecto', default=None)
    medio_solicitud = serializers.ReadOnlyField(source='id_solicitud_tramite.id_medio_solicitud.nombre', default=None)
    fecha_registro = serializers.ReadOnlyField(source='id_solicitud_tramite.fecha_registro', default=None)
    nombre_sucursal_recepcion_fisica = serializers.ReadOnlyField(source='id_solicitud_tramite.id_sucursal_recepcion_fisica.descripcion_sucursal', default=None)
    #cod_tipo_operacion_tramite
    radicado = serializers.SerializerMethodField(default=None)
    fecha_radicado = serializers.SerializerMethodField(default=None)
    def get_fecha_radicado (self, obj):
       
        if obj.id_solicitud_tramite.id_radicado:
          return obj.id_solicitud_tramite.fecha_radicado
        return None

    def get_radicado(self, obj):
        cadena = ""
        if obj.id_solicitud_tramite.id_radicado:
            #radicado = obj.id_solicitud_tramite.id_radicado
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=obj.id_solicitud_tramite.id_radicado.agno_radicado,cod_tipo_radicado=obj.id_solicitud_tramite.id_radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(obj.id_solicitud_tramite.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            return cadena
    class Meta:
        model = PermisosAmbSolicitudesTramite#PermisosAmbSolicitudesTramite
        fields = ['id_solicitud_tramite','nombre_completo_titular','nombre_opa','tipo_operacion','nombre_proyecto','costo_proyecto','medio_solicitud','fecha_registro','cantidad_anexos','nombre_sucursal_recepcion_fisica','radicado','fecha_radicado']


    def get_cantidad_anexos(self, obj):
        conteo_anexos = AnexosTramite.objects.filter(id_solicitud_tramite=obj.id_solicitud_tramite).count()

        
        return conteo_anexos

    def get_nombre_completo_titular(self, obj):

        if obj.id_solicitud_tramite.id_persona_titular:

            persona = obj.id_solicitud_tramite.id_persona_titular
            nombre_completo_responsable = None
            nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                            persona.primer_apellido, persona.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
            return nombre_completo_responsable
        else:
            if obj.es_anonima:
                return "Anonimo"
            else:
                return 'No Identificado'
class TareasAsignadasOpasGetSerializer(serializers.ModelSerializer):
   
    #cod_tipo_tarea es un choices
    tipo_tarea =serializers.ReadOnlyField(source='get_cod_tipo_tarea_display',default=None)
    asignado_por = serializers.SerializerMethodField()
    asignado_para = serializers.SerializerMethodField()
    radicado = serializers.SerializerMethodField(default=None)
    fecha_radicado =  serializers.SerializerMethodField(default=None)
    id_tramite = serializers.SerializerMethodField(default=None)
    tiempo_respuesta = serializers.SerializerMethodField(default=None)
    estado_tarea = serializers.ReadOnlyField(source='get_cod_estado_solicitud_display',default=None)
    estado_asignacion_tarea = serializers.ReadOnlyField(source='get_cod_estado_asignacion_display',default=None)#cod_estado_solicitud
    
    respondida_por = serializers.ReadOnlyField(source='nombre_persona_que_responde',default=None)
    tarea_reasignada_a = serializers.SerializerMethodField(default=None)
    unidad_org_destino = serializers.SerializerMethodField(default=None)
    estado_reasignacion_tarea = serializers.SerializerMethodField(default=None)

    class Meta:#
        model = TareasAsignadas
        fields = '__all__'
        #fields = ['id_tarea_asignada','id_otro','tipo_tarea','asignado_por','asignado_para','fecha_asignacion','comentario_asignacion','radicado','fecha_radicado','estado_tarea','estado_asignacion_tarea','unidad_org_destino','estado_reasignacion_tarea','tarea_reasignada_a','id_tarea_asignada_padre_inmediata']
        fields = ['id_tarea_asignada','id_asignacion','id_tramite','tipo_tarea','asignado_por','asignado_para','fecha_asignacion','comentario_asignacion','radicado','fecha_radicado','tiempo_respuesta','requerimientos_pendientes_respuesta','estado_tarea','estado_asignacion_tarea','tarea_reasignada_a','unidad_org_destino','estado_reasignacion_tarea','respondida_por']
        

    def get_id_tramite(self,obj):
        #buscamos la asignacion
        
      
           
        tarea = obj
        tramite = None

        if tarea.id_asignacion:
               
                asignacion = AsignacionTramites.objects.filter(id_asignacion_tramite=tarea.id_asignacion).first()
                #print(asignacion.id_asignacion_tramite)
                #print(asignacion)
                tramite = asignacion.id_solicitud_tramite.id_solicitud_tramite
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionTramites.objects.filter(id_asignacion_tramite=tarea.id_asignacion).first()

                    tramite = asignacion.id_solicitud_tramite.id_solicitud_tramite
                    break
        if not tramite:
            return None
        return tramite



    def get_asignado_por(self,obj):
        #buscamos la asignacion
        tarea = obj
    
        if tarea.id_asignacion:
                tarea = obj
        else:
            while not  tarea.id_asignacion:
                tarea = tarea.id_tarea_asignada_padre_inmediata
                if tarea.id_asignacion:
             
                    break
             
        persona = None
        asignacion_tarea = AsignacionTramites.objects.filter(id_asignacion_tramite=tarea.id_asignacion).first()

        if not asignacion_tarea:
            return None

        if not tarea:
            return None
        persona = asignacion_tarea.id_persona_asigna
        nombre_completo = None
        nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                        persona.primer_apellido, persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo = nombre_completo if nombre_completo != "" else None
        return nombre_completo



    def get_asignado_para(self,obj):
        #buscamos la asignacion
        tarea = obj
    
        if tarea.id_asignacion:
                tarea = obj
        else:
            while not  tarea.id_asignacion:
                tarea = tarea.id_tarea_asignada_padre_inmediata
                if tarea.id_asignacion:
             
                    break
             
        persona = None
        asignacion_tarea = AsignacionTramites.objects.filter(id_asignacion_tramite=tarea.id_asignacion).first()

        if not asignacion_tarea:
            return None

        if not tarea:
            return None
        persona = asignacion_tarea.id_persona_asignada
        nombre_completo = None
        nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                        persona.primer_apellido, persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo = nombre_completo if nombre_completo != "" else None
        return nombre_completo



    def get_radicado(self,obj):
        #buscamos la asignacion
        
        tarea = obj
        otro = None

        if tarea.id_asignacion:
                asignacion = AsignacionTramites.objects.filter(id_asignacion_tramite=tarea.id_asignacion).first()
                otro = asignacion.id_solicitud_tramite.id_solicitud_tramite
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionTramites.objects.filter(id_asignacion_tramite=tarea.id_asignacion).first()

                    otro = asignacion.id_solicitud_tramite.id_solicitud_tramite
                    break

        cadena = ""
        instance_tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=otro).first()
        if  instance_tramite and instance_tramite.id_radicado:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=instance_tramite.id_radicado.agno_radicado,cod_tipo_radicado=instance_tramite.id_radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(instance_tramite.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
        return cadena

   
         
    def get_fecha_radicado(self,obj):

        tarea = obj
        otro = None

        if tarea.id_asignacion:
                asignacion = AsignacionTramites.objects.filter(id_asignacion_tramite=tarea.id_asignacion).first()
                otro = asignacion.id_solicitud_tramite.id_solicitud_tramite
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionTramites.objects.filter(id_asignacion_tramite=tarea.id_asignacion).first()

                    otro = asignacion.id_solicitud_tramite.id_solicitud_tramite
                    break

      
        instance_tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=otro).first()
        if  instance_tramite and instance_tramite.id_radicado:
            return instance_tramite.fecha_radicado
        return None
    


    def get_tiempo_respuesta(self,obj):
        tarea = obj
        id_tramite = None

        if tarea.id_asignacion:
                asignacion = AsignacionTramites.objects.filter(id_asignacion_tramite=tarea.id_asignacion).first()
                id_tramite = asignacion.id_solicitud_tramite.id_solicitud_tramite
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionTramites.objects.filter(id_asignacion_tramite=tarea.id_asignacion).first()

                    id_tramite = asignacion.id_solicitud_tramite.id_solicitud_tramite
                    break

        #print(id_tramite)
        if not id_tramite:
            return None
        instance_tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_tramite).first()
        if not instance_tramite:
            return None
   

        fecha_radicado = instance_tramite.fecha_radicado

        if not fecha_radicado:
            return None
        
        fecha_actual = datetime.now()
        fecha_radicado_mas_15_dias = fecha_radicado + timedelta(days=15)
      
   
        dias_faltan = fecha_radicado_mas_15_dias - fecha_actual

        return dias_faltan.days


    def get_tarea_reasignada_a(self,obj):

        reasignacion = ReasignacionesTareas.objects.filter(id_tarea_asignada=obj.id_tarea_asignada).order_by('-fecha_reasignacion').first()

        #print(reasignacion)
        if not reasignacion:
            return None
        persona = None

        if reasignacion.id_persona_a_quien_se_reasigna:
            persona = reasignacion.id_persona_a_quien_se_reasigna
        else:
            return None
        
        nombre_completo = None
        nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                        persona.primer_apellido, persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo = nombre_completo if nombre_completo != "" else None
        return nombre_completo




    def get_estado_reasignacion_tarea(self,obj):
        reasignacion = ReasignacionesTareas.objects.filter(id_tarea_asignada=obj.id_tarea_asignada).order_by('-fecha_reasignacion').first()
        if not reasignacion:
            return None
        
        if reasignacion.cod_estado_reasignacion == 'Re':
            return reasignacion.get_cod_estado_reasignacion_display() +" "+reasignacion.justificacion_reasignacion_rechazada
        return reasignacion.get_cod_estado_reasignacion_display()
        
    
    def get_unidad_org_destino(self,obj):

        reasignacion = ReasignacionesTareas.objects.filter(id_tarea_asignada=obj.id_tarea_asignada).order_by('-fecha_reasignacion').first()

        #print(reasignacion)
        if not reasignacion:
            return None
        persona = None

        if reasignacion.id_persona_a_quien_se_reasigna:
            persona = reasignacion.id_persona_a_quien_se_reasigna
        else:
            return None
        
        unidad_actual = persona.id_unidad_organizacional_actual
        if not unidad_actual:
            return None
        cadena = ''
        if unidad_actual.cod_agrupacion_documental:
            cadena = unidad_actual.codigo+' ' + ' '+unidad_actual.nombre+' '+unidad_actual.cod_agrupacion_documental 
        else:
             cadena = unidad_actual.codigo+' ' + ' '+unidad_actual.nombre
        return cadena


class OpaTramiteDetalleGetBandejaTareasSerializer(serializers.ModelSerializer):
    radicado = serializers.SerializerMethodField()
    estado_actual = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre', default=None)
    tipo_operacion_tramite = serializers.ReadOnlyField(source='get_cod_tipo_operacion_tramite_display', default=None)

    class Meta:
        model = SolicitudesTramites
        fields = ['id_solicitud_tramite','radicado','fecha_radicado','tipo_operacion_tramite','estado_actual']


        
    def get_radicado(self, obj):
        cadena = ""
        radicado = obj.id_radicado
        if radicado:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=radicado.agno_radicado,cod_tipo_radicado=radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            return cadena
        else: 
            return 'SIN RADICAR'

class OpaTramiteTitularGetBandejaTareasSerializer(serializers.ModelSerializer):
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



class RequerimientosOpaTramiteCreateserializer(serializers.ModelSerializer):
    class Meta:
        model = Requerimientos
        fields = '__all__'


class RequerimientoSobreOPACreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudAlUsuarioSobrePQRSDF
        fields = '__all__'


class Anexos_RequerimientoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos_PQR
        fields = '__all__'
class AnexosTramiteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnexosTramite
        fields = '__all__'


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

class RequerimientoSobreOPAGetSerializer(serializers.ModelSerializer):
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
    
class AnexoArchivosDigitalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivosDigitales
        fields = ['ruta_archivo','nombre_de_Guardado']

class Anexos_TramitresAnexosGetSerializer(serializers.ModelSerializer):
   
    archivo = serializers.SerializerMethodField()
    numero = serializers.ReadOnlyField(source='id_anexo.orden_anexo_doc',default=None)
    nombre = serializers.ReadOnlyField(source='id_anexo.nombre_anexo',default=None)
    n_folios= serializers.ReadOnlyField(source='id_anexo.numero_folios',default=None)
    medio_almacenamiento = serializers.ReadOnlyField(source='id_anexo.get_cod_medio_almacenamiento_display',default=None)
    class Meta:
        model = AnexosTramite
        fields = ['id_anexo_tramite','id_anexo','numero','nombre','n_folios','medio_almacenamiento','archivo']

    def get_archivo(self,obj):
        id_anexo = obj.id_anexo
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=id_anexo).first()
        if meta_data:
            data_archivo  = AnexoArchivosDigitalesSerializer(meta_data.id_archivo_sistema)
            return data_archivo.data['ruta_archivo']
        return "Archivo"



#COMPLEMENTOS DE UNA TAREA OPA
class AdicionalesDeTareasopaGetByTareaSerializer(serializers.ModelSerializer):
    tipo = serializers.SerializerMethodField()
    titular = serializers.SerializerMethodField()
    descripcion = serializers.ReadOnlyField(source='id_respuesta_requerimiento.descripcion',default=None)
    cantidad_anexos = serializers.ReadOnlyField(source='id_complemento_usu_pqr.cantidad_anexos',default=None)
    radicado = serializers.SerializerMethodField(default=None)
    fecha_radicado = serializers.SerializerMethodField(default=None)
    class Meta:
        model = AdicionalesDeTareas
      
        fields =['id_adicional_de_tarea','id_respuesta_requerimiento','tipo','titular','descripcion','cantidad_anexos','radicado','fecha_radicado','fecha_de_adicion']

    def get_tipo(self,obj):


        return 'Respuesta a Solicitud'

    
    def get_titular(self, obj):
        respuesta = obj.id_respuesta_requerimiento
        if not respuesta:
            return None
        tramite = respuesta.id_solicitud_tramite
     
        nombre_completo_responsable = None
        nombre_list = [tramite.id_persona_titular.primer_nombre, tramite.id_persona_titular.segundo_nombre,
                        tramite.id_persona_titular.primer_apellido, tramite.id_persona_titular.segundo_apellido]
        nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
        return nombre_completo_responsable
    
    def get_radicado(self, obj):
        respuesta = obj.id_respuesta_requerimiento
        tramite = respuesta.id_solicitud_tramite
        cadena = ""
        if tramite.id_radicado:
            #radicado = obj.id_solicitud_tramite.id_radicado
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=tramite.id_radicado.agno_radicado,cod_tipo_radicado=tramite.id_radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(tramite.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            return cadena

    def get_fecha_radicado(self, obj):
        respuesta = obj.id_respuesta_requerimiento
        tramite = respuesta.id_solicitud_tramite
        
        if tramite.id_radicado:
            return tramite.id_radicado.fecha_radicado
        return None


class AnexosRespuestaRequerimientosGetSerializer(serializers.ModelSerializer):

    medio_almacenamiento = serializers.CharField(source='get_cod_medio_almacenamiento_display', default=None)
  
    class Meta:
        model = Anexos
        fields = '__all__'  



#RESPUESTA OPA

class RespuestaOpaTramiteCreateserializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaOPA
        fields = '__all__'

class RespuestaOPAGetSerializer(serializers.ModelSerializer):
    radicado = serializers.SerializerMethodField()
    class Meta:
        model = RespuestaOPA
        fields = '__all__'

    def get_radicado(self, obj):
        cadena = "SIN RADICAR"
        if obj.id_radicado_salida:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=obj.id_radicado_salida.agno_radicado,cod_tipo_radicado=obj.id_radicado_salida.cod_tipo_radicado).first()
            numero_con_ceros = str(obj.id_radicado_salida.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= obj.id_radicado_salida.prefijo_radicado+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
        return cadena
#RESPUESTA REQUERIMIENTO OPA

class RequerimientosOpaTramiteCreateserializer(serializers.ModelSerializer):
    class Meta:
        model = Requerimientos
        fields = '__all__'
class RespuestaRequerimientoOPACreateserializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestasRequerimientos
        fields = '__all__'
