
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.bandeja_tareas_models import AdicionalesDeTareas, ReasignacionesTareas, TareasAsignadas
from gestion_documental.models.expedientes_models import ArchivosDigitales

from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, AsignacionDocs, AsignacionPQR, BandejaTareasPersona, ComplementosUsu_PQR, ConfigTiposRadicadoAgno, MetadatosAnexosTmp, Otros, RespuestaPQR, SolicitudAlUsuarioSobrePQRSDF, SolicitudDeDigitalizacion, TareaBandejaTareasPersona
from datetime import timedelta
from datetime import datetime
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.models.organigrama_models import UnidadesOrganizacionales

from transversal.models.personas_models import Personas



class TareasAsignadasDocsGetSerializer(serializers.ModelSerializer):
   
    #cod_tipo_tarea es un choices
    tipo_tarea =serializers.ReadOnlyField(source='get_cod_tipo_tarea_display',default=None)
    asignado_por = serializers.SerializerMethodField()
    asignado_para = serializers.SerializerMethodField()
    consecutivo = serializers.SerializerMethodField()
    fecha_consecutivo = serializers.SerializerMethodField()
    persona_genera = serializers.SerializerMethodField()
    radicado = serializers.SerializerMethodField(default=None)
    fecha_radicado =  serializers.SerializerMethodField(default=None)
    
    estado_tarea = serializers.ReadOnlyField(source='get_cod_estado_solicitud_display',default=None)
    estado_asignacion_tarea = serializers.ReadOnlyField(source='get_cod_estado_asignacion_display',default=None)#cod_estado_solicitud
    documento = serializers.SerializerMethodField(default=None)
    # respondida_por = serializers.ReadOnlyField(source='nombre_persona_que_responde',default=None)
    tarea_reasignada_a = serializers.SerializerMethodField(default=None)
    unidad_org_destino = serializers.SerializerMethodField(default=None)
    estado_reasignacion_tarea = serializers.SerializerMethodField(default=None)

    class Meta:#
        model = TareasAsignadas
        fields = '__all__'
        fields = ['id_tarea_asignada','id_otro','tipo_tarea','asignado_por','asignado_para','fecha_asignacion','comentario_asignacion','radicado','fecha_radicado','estado_tarea','estado_asignacion_tarea','unidad_org_destino','estado_reasignacion_tarea','tarea_reasignada_a','id_tarea_asignada_padre_inmediata']
        


    def get_documento(self,obj):
        #buscamos la asignacion
        
      
           
        tarea = obj
        documento = None

        if tarea.id_asignacion:
                asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()
                documento = asignacion.id_consecutivo
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()

                    documento = asignacion.id_consecutivo
                    break
        if not documento:
            return None
        return documento.id_consecutivo_tipologia
    
    def get_consecutivo(self,obj):
        tarea = obj
        documento = None

        if tarea.id_asignacion:
                asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()
                consecutivo = f"{asignacion.id_consecutivo.prefijo_consecutivo}.{asignacion.id_consecutivo.id_unidad_organizacional.codigo}.{asignacion.id_consecutivo.nro_consecutivo}"
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()

                    documento = asignacion.id_consecutivo
                    break
        if not documento:
            return None
        return documento.id_consecutivo_tipologia
    
    
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
        asignacion_tarea = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()

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
        asignacion_tarea = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()

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
        documento = None

        if tarea.id_asignacion:
                asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()
                documento = asignacion.id_consecutivo
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()

                    documento = asignacion.id_consecutivo
                    break


            
        # print("PQRSDF")
        # print(pqrsdf)
        cadena = ""
        if  documento and documento.id_radicado_salida:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=documento.id_radicado_salida.agno_radicado,cod_tipo_radicado=documento.id_radicado_salida.cod_tipo_radicado).first()
            numero_con_ceros = str(documento.id_radicado_salida.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
        return cadena

    def get_fecha_radicado(self,obj):
        #buscamos la asignacion
        
      
           
        tarea = obj
        documento = None

        if tarea.id_asignacion:
                asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()
                documento = asignacion.id_consecutivo
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()

                    documento = asignacion.id_consecutivo
                    break
        if not documento:
            return None
        return documento.fecha_radicado_salida       

        





class TareasAsignadasOotrosUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareasAsignadas
        fields = '__all__'
    
