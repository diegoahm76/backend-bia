
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.bandeja_tareas_models import AdicionalesDeTareas, ReasignacionesTareas, TareasAsignadas
from gestion_documental.models.expedientes_models import ArchivosDigitales

from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, AsignacionOtros, AsignacionPQR, BandejaTareasPersona, ComplementosUsu_PQR, ConfigTiposRadicadoAgno, MetadatosAnexosTmp, Otros, RespuestaPQR, SolicitudAlUsuarioSobrePQRSDF, SolicitudDeDigitalizacion, TareaBandejaTareasPersona
from datetime import timedelta
from datetime import datetime
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.models.organigrama_models import UnidadesOrganizacionales

from transversal.models.personas_models import Personas





class TareasAsignadasOtrosGetSerializer(serializers.ModelSerializer):
   
    #cod_tipo_tarea es un choices
    tipo_tarea =serializers.ReadOnlyField(source='get_cod_tipo_tarea_display',default=None)
    asignado_por = serializers.SerializerMethodField()
    asignado_para = serializers.SerializerMethodField()
    radicado = serializers.SerializerMethodField(default=None)
    fecha_radicado =  serializers.SerializerMethodField(default=None)
    
    estado_tarea = serializers.ReadOnlyField(source='get_cod_estado_solicitud_display',default=None)
    estado_asignacion_tarea = serializers.ReadOnlyField(source='get_cod_estado_asignacion_display',default=None)#cod_estado_solicitud
    id_otro = serializers.SerializerMethodField(default=None)
    # respondida_por = serializers.ReadOnlyField(source='nombre_persona_que_responde',default=None)
    tarea_reasignada_a = serializers.SerializerMethodField(default=None)
    unidad_org_destino = serializers.SerializerMethodField(default=None)
    estado_reasignacion_tarea = serializers.SerializerMethodField(default=None)

    class Meta:#
        model = TareasAsignadas
        fields = '__all__'
        fields = ['id_tarea_asignada','id_otro','tipo_tarea','asignado_por','asignado_para','fecha_asignacion','comentario_asignacion','radicado','fecha_radicado','estado_tarea','estado_asignacion_tarea','unidad_org_destino','estado_reasignacion_tarea','tarea_reasignada_a','id_tarea_asignada_padre_inmediata']
        


    def get_id_otro(self,obj):
        #buscamos la asignacion
        
      
           
        tarea = obj
        otro = None

        if tarea.id_asignacion:
                asignacion = AsignacionOtros.objects.filter(id_asignacion_otros=tarea.id_asignacion).first()
                otro = asignacion.id_otros
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionOtros.objects.filter(id_asignacion_otros=tarea.id_asignacion).first()

                    otro = asignacion.id_otros
                    break
        if not otro:
            return None
        return otro.id_otros
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



    #     return None
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
        asignacion_tarea = AsignacionOtros.objects.filter(id_asignacion_otros=tarea.id_asignacion).first()

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
        asignacion_tarea = AsignacionOtros.objects.filter(id_asignacion_otros=tarea.id_asignacion).first()

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
                asignacion = AsignacionOtros.objects.filter(id_asignacion_otros=tarea.id_asignacion).first()
                otro = asignacion.id_otros
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionOtros.objects.filter(id_asignacion_otros=tarea.id_asignacion).first()

                    otro = asignacion.id_otros
                    break


            
        # print("PQRSDF")
        # print(pqrsdf)
        cadena = ""
        if  otro and otro.id_radicados:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=otro.id_radicados.agno_radicado,cod_tipo_radicado=otro.id_radicados.cod_tipo_radicado).first()
            numero_con_ceros = str(otro.id_radicados.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
        return cadena

    def get_fecha_radicado(self,obj):
        #buscamos la asignacion
        
      
           
        tarea = obj
        otro = None

        if tarea.id_asignacion:
                asignacion = AsignacionOtros.objects.filter(id_asignacion_otros=tarea.id_asignacion).first()
                otro = asignacion.id_otros
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionOtros.objects.filter(id_asignacion_otros=tarea.id_asignacion).first()

                    otro = asignacion.id_otros
                    break
        if not otro:
            return None
        return otro.fecha_radicado           

        




class DetalleOtrosGetSerializer(serializers.ModelSerializer):
    nombre_completo_titular = serializers.SerializerMethodField(default=None)
    medio_solicitud = serializers.ReadOnlyField(source='id_medio_solicitud.nombre',default=None)
    forma_presentacion = serializers.CharField(source='get_cod_forma_presentacion_display', default=None)
    persona_recibe = serializers.SerializerMethodField(default=None)
    nombre_sucursal_recepciona_fisica = serializers.SerializerMethodField(default=None)
    radicado = serializers.SerializerMethodField(default=None)
    class Meta:
        model = Otros
        fields =['nombre_completo_titular','fecha_registro','medio_solicitud','forma_presentacion','cantidad_anexos','nro_folios_totales','persona_recibe','nombre_sucursal_recepciona_fisica','radicado','fecha_radicado','asunto','descripcion']
    
    def get_nombre_sucursal_recepciona_fisica(self, obj):
        if not obj.id_sucursal_recepciona_fisica:
            return None
        return obj.id_sucursal_recepciona_fisica.descripcion_sucursal
    
    def get_persona_recibe(self,obj):
        if not obj.id_persona_recibe:
            return None
        nombre_completo = None
        nombre_list = [obj.id_persona_recibe.primer_nombre, obj.id_persona_recibe.segundo_nombre,
                        obj.id_persona_recibe.primer_apellido, obj.id_persona_recibe.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo = nombre_completo if nombre_completo != "" else None
        return nombre_completo
    def get_nombre_completo_titular(self,obj):
        if not obj.id_persona_titular:
            return None
        nombre_completo = None
        nombre_list = [obj.id_persona_titular.primer_nombre, obj.id_persona_titular.segundo_nombre,
                        obj.id_persona_titular.primer_apellido, obj.id_persona_titular.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo = nombre_completo if nombre_completo != "" else None
        return nombre_completo
    
    def get_radicado(self,obj):
        #buscamos la asignacion
        
      
           
        otro = obj

        cadena = ""
        if  otro and otro.id_radicados:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=otro.id_radicados.agno_radicado,cod_tipo_radicado=otro.id_radicados.cod_tipo_radicado).first()
            numero_con_ceros = str(otro.id_radicados.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
        return cadena
    

class AnexosOtrosGetSerializer(serializers.ModelSerializer):

    medio_almacenamiento = serializers.CharField(source='get_cod_medio_almacenamiento_display', default=None)
  
    class Meta:
        model = Anexos
        fields = '__all__'  


class MetadatosAnexosOtrosTmpSerializerGet(serializers.ModelSerializer):
    origen_archivo = serializers.CharField(source='get_cod_origen_archivo_display', default=None)
    categoria_archivo = serializers.CharField(source='get_cod_categoria_archivo_display', default=None)
    nombre_tipologia_documental = serializers.CharField(source='id_tipologia_doc.nombre', default=None)
    numero_folios = serializers.SerializerMethodField()
    fecha_creacion_archivo = serializers.ReadOnlyField(source='id_archivo_sistema.fecha_creacion_doc',default=None)
    palabras_clave_doc = serializers.SerializerMethodField()
    class Meta:
        model = MetadatosAnexosTmp
        fields = ['id_metadatos_anexo_tmp','asunto','numero_folios','fecha_creacion_archivo','origen_archivo','categoria_archivo','tiene_replica_fisica','es_version_original','palabras_clave_doc','nombre_tipologia_documental','descripcion']
    def get_numero_folios(self, obj):
        return obj.nro_folios_documento
    
    def get_palabras_clave_doc(self, obj):
        if obj.palabras_clave_doc:
            lista_datos =  obj.palabras_clave_doc.split("|")
            return lista_datos
        return None

class TareasAsignadasOotrosUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareasAsignadas
        fields = '__all__'