
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.bandeja_tareas_models import AdicionalesDeTareas, ReasignacionesTareas, TareasAsignadas
from gestion_documental.models.expedientes_models import ArchivosDigitales

from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, AsignacionPQR, BandejaTareasPersona, ComplementosUsu_PQR, ConfigTiposRadicadoAgno, MetadatosAnexosTmp, RespuestaPQR, SolicitudAlUsuarioSobrePQRSDF, SolicitudDeDigitalizacion, TareaBandejaTareasPersona
from datetime import timedelta
from datetime import datetime
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.models.organigrama_models import UnidadesOrganizacionales

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
   
    #cod_tipo_tarea es un choices
    tipo_tarea =serializers.ReadOnlyField(source='get_cod_tipo_tarea_display',default=None)
    asignado_por = serializers.SerializerMethodField()
    asignado_para = serializers.SerializerMethodField()
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
                 'requerimientos_pendientes_respuesta','estado_tarea','fecha_respondido','respondida_por','tarea_reasignada_a','unidad_org_destino','estado_reasignacion_tarea','id_tarea_asignada_padre_inmediata']
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



        return None
    def get_estado_reasignacion_tarea(self,obj):
        reasignacion = ReasignacionesTareas.objects.filter(id_tarea_asignada=obj.id_tarea_asignada).order_by('-fecha_reasignacion').first()
        if not reasignacion:
            return None
        return reasignacion.get_cod_estado_reasignacion_display()
        return None
    
    def get_unidad_org_destino(self,obj):
        return None
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
        asignacion_tarea = TareaBandejaTareasPersona.objects.filter(id_tarea_asignada=tarea.id_tarea_asignada).first()

        
        

        if not tarea:
            return None
        persona = asignacion_tarea.id_bandeja_tareas_persona.id_persona
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

        reasignacion = ReasignacionesTareas.objects.filter(id_tarea_asignada=tarea.id_tarea_asignada,cod_estado_reasignacion='Ep').first()
        print(reasignacion)
        print('ACABAMOS')

        persona = None

        if reasignacion:
            persona = reasignacion.id_persona_a_quien_se_reasigna
        if not persona:
            return None
        nombre_completo = None
        nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                        persona.primer_apellido, persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo = nombre_completo if nombre_completo != "" else None
        return nombre_completo
    

    def get_radicado(self,obj):
        #buscamos la asignacion
        
        if obj.cod_tipo_tarea == 'Rpqr':
           
            tarea = obj
            pqrsdf = None

            if tarea.id_asignacion:
                 asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=tarea.id_asignacion).first()
                 pqrsdf = asignacion.id_pqrsdf
            else:

                while tarea:
                    tarea = tarea.id_tarea_asignada_padre_inmediata

                    if tarea.id_asignacion:
                        asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=tarea.id_asignacion).first()

                        pqrsdf = asignacion.id_pqrsdf
                        break


                
            # print("PQRSDF")
            # print(pqrsdf)
            cadena = ""
            if  pqrsdf and pqrsdf.id_radicado:
                instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=pqrsdf.id_radicado.agno_radicado,cod_tipo_radicado=pqrsdf.id_radicado.cod_tipo_radicado).first()
                numero_con_ceros = str(pqrsdf.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
                cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
            
            return cadena
        else:
            return None

    def get_fecha_radicado(self,obj):
        #buscamos la asignacion
        tarea = obj
        pqrsdf = None

        if tarea.id_asignacion:
                asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=tarea.id_asignacion).first()
                pqrsdf = asignacion.id_pqrsdf
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=tarea.id_asignacion).first()

                    pqrsdf = asignacion.id_pqrsdf
                    break
            
        #pqrsdf = asignacion.id_pqrsdf
        if not pqrsdf:
            return None
        fecha_radicado = pqrsdf.fecha_radicado
        return fecha_radicado

    def get_dias_para_respuesta(self,obj):
        #buscamos la asignacion
        fecha_actual = datetime.now()

        tarea = obj
        pqrsdf = None

        if tarea.id_asignacion:
                asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=tarea.id_asignacion).first()
                pqrsdf = asignacion.id_pqrsdf
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=tarea.id_asignacion).first()

                    pqrsdf = asignacion.id_pqrsdf
                    break



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
        tarea = obj
        pqrsdf = None

        if tarea.id_asignacion:
                asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=tarea.id_asignacion).first()
                pqrsdf = asignacion.id_pqrsdf
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if  tarea and tarea.id_asignacion:
                    asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=tarea.id_asignacion).first()

                    pqrsdf = asignacion.id_pqrsdf
                    break

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



class ComplementosUsu_PQRGetByIdSerializer(serializers.ModelSerializer):
    tipo = serializers.SerializerMethodField()
    nombre_completo_titular = serializers.SerializerMethodField()
    radicado = serializers.SerializerMethodField()
    numero_solicitudes = serializers.SerializerMethodField()
    es_complemento = serializers.SerializerMethodField()
    medio_solicitud = serializers.ReadOnlyField(source='id_medio_solicitud.nombre')
    nombre_completo_recibe = serializers.SerializerMethodField()
    class Meta:
        model = ComplementosUsu_PQR
        fields = ['idComplementoUsu_PQR','tipo','nombre_completo_titular','asunto','cantidad_anexos','radicado','fecha_radicado','requiere_digitalizacion','numero_solicitudes','es_complemento','complemento_asignado_unidad','fecha_complemento','medio_solicitud','nro_folios_totales','nombre_completo_recibe','asunto','descripcion']
    
    def get_es_complemento(self, obj):
        return True
    def get_tipo(self, obj):
        return "Complemento de PQRSDF"
    
    def get_nombre_completo_recibe(self, obj):
        if obj.id_persona_recibe:
            nombre_completo_responsable = None
            nombre_list = [obj.id_persona_recibe.primer_nombre, obj.id_persona_recibe.segundo_nombre,
                            obj.id_persona_recibe.primer_apellido, obj.id_persona_recibe.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
            return nombre_completo_responsable
        else:
            return 'No Identificado'
    def get_nombre_completo_titular(self, obj):

        if obj.id_persona_interpone:
            nombre_completo_responsable = None
            nombre_list = [obj.id_persona_interpone.primer_nombre, obj.id_persona_interpone.segundo_nombre,
                            obj.id_persona_interpone.primer_apellido, obj.id_persona_interpone.segundo_apellido]
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
            cadena= str(obj.id_radicado.prefijo_radicado)+'-'+str(obj.id_radicado.agno_radicado)+'-'+str(obj.id_radicado.nro_radicado)
            return cadena
    def get_numero_solicitudes(self, obj):
            
        id= obj.idComplementoUsu_PQR
        numero_solicitudes = SolicitudDeDigitalizacion.objects.filter(id_complemento_usu_pqr=id).count()
        return numero_solicitudes


class AnexosComplementoGetByComBandejaTareasSerializer(serializers.ModelSerializer):

    medio_almacenamiento = serializers.CharField(source='get_cod_medio_almacenamiento_display', default=None)
    complemento = serializers.SerializerMethodField()
    class Meta:
        model = Anexos
        fields = '__all__'  
    def get_complemento(self, obj):
        return True

class MetadatosAnexoerializerGet(serializers.ModelSerializer):
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

class TareasAnexoArchivosDigitalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivosDigitales
        fields = ['ruta_archivo','nombre_de_Guardado']
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



class DetalleRequerimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudAlUsuarioSobrePQRSDF
        fields = ['id_solicitud_al_usuario_sobre_pqrsdf','asunto','descripcion','fecha_solicitud']

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
    
class UnidadOrganizacionalBandejaTareasSerializer(serializers.ModelSerializer):
   
    agrupacion_documental =serializers.ReadOnlyField(source='get_cod_agrupacion_documental_display',default=None)
    class Meta:
        model = UnidadesOrganizacionales
        fields = ['id_unidad_organizacional','codigo','nombre','agrupacion_documental']
 
class LiderUnidadGetSerializer(serializers.ModelSerializer):
   
    lider = serializers.SerializerMethodField()
    cargo = serializers.SerializerMethodField()
    cargo =serializers.ReadOnlyField(source='id_persona.id_cargo.nombre',default=None)
   # solicitud_actual = serializers.SerializerMethodField()
    class Meta:
        model = LideresUnidadesOrg
        fields = ['id_unidad_organizacional','id_persona','lider','cargo']

        
    def get_lider(self, obj):

        if obj.id_persona:
            nombre_completo_responsable = None
            nombre_list = [obj.id_persona.primer_nombre, obj.id_persona.segundo_nombre,
                            obj.id_persona.primer_apellido, obj.id_persona.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
            return nombre_completo_responsable
        else :
         
            return None
        


class PersonaUnidadSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    cargo =serializers.ReadOnlyField(source='id_cargo.nombre',default=None)
    class Meta:
        model = Personas
        fields = ['id_persona','nombre_completo','cargo','id_cargo']

    def get_nombre_completo(self, obj):
        nombre_completo = None
        nombre_list = [obj.primer_nombre, obj.segundo_nombre, obj.primer_apellido, obj.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        return nombre_completo.upper()
    
class ReasignacionesTareasCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReasignacionesTareas
        fields = '__all__'

class ReasignacionesTareasgetByIdSerializer(serializers.ModelSerializer):
    persona_reasignada = serializers.SerializerMethodField()
    cargo =serializers.ReadOnlyField(source='id_persona_a_quien_se_reasigna.id_cargo.nombre',default=None)
    unidad_organizacional = serializers.SerializerMethodField()
    estado_asignacion = serializers.ReadOnlyField(source='get_cod_estado_reasignacion_display',default=None)
    class Meta:
        model = ReasignacionesTareas
        fields = ['id_reasignacion_tarea','fecha_reasignacion','persona_reasignada','cargo','unidad_organizacional','comentario_reasignacion','estado_asignacion','justificacion_reasignacion_rechazada']

    def get_persona_reasignada(self, obj):
        persona = obj.id_persona_a_quien_se_reasigna
        nombre_completo = None
        if persona:

            nombre_list = [persona.primer_nombre, persona.segundo_nombre, persona.primer_apellido, persona.segundo_apellido]
            nombre_completo = ' '.join(item for item in nombre_list if item is not None)
            return nombre_completo.upper()
    def  get_unidad_organizacional(self, obj):
        persona = obj.id_persona_a_quien_se_reasigna
        if persona:
            unidad = persona.id_unidad_organizacional_actual
            if unidad:
                serializador_unidad = UnidadOrganizacionalBandejaTareasSerializer(unidad)
                return serializador_unidad.data
        return None
    

class ReasignacionesTareasgetByIdTareaSerializer(serializers.ModelSerializer):
    persona_reasignada = serializers.SerializerMethodField()
    cargo =serializers.ReadOnlyField(source='id_persona_a_quien_se_reasigna.id_cargo.nombre',default=None)
    unidad_organizacional = serializers.SerializerMethodField()
    estado_asignacion = serializers.ReadOnlyField(source='get_cod_estado_reasignacion_display',default=None)
    persona_reasigno = serializers.SerializerMethodField()
    class Meta:
        model = ReasignacionesTareas
        fields = ['id_reasignacion_tarea','persona_reasigno','fecha_reasignacion','persona_reasignada','cargo','unidad_organizacional','comentario_reasignacion','estado_asignacion','justificacion_reasignacion_rechazada']

    def get_persona_reasignada(self, obj):
        persona = obj.id_persona_a_quien_se_reasigna
        nombre_completo = None
        if persona:

            nombre_list = [persona.primer_nombre, persona.segundo_nombre, persona.primer_apellido, persona.segundo_apellido]
            nombre_completo = ' '.join(item for item in nombre_list if item is not None)
            return nombre_completo.upper()
    def  get_unidad_organizacional(self, obj):
        persona = obj.id_persona_a_quien_se_reasigna
        if persona:
            unidad = persona.id_unidad_organizacional_actual
            if unidad:
                serializador_unidad = UnidadOrganizacionalBandejaTareasSerializer(unidad)
                return serializador_unidad.data
        return None
    
    def get_persona_reasigno (self, obj):

        asignacion_bandeja = TareaBandejaTareasPersona.objects.filter(id_tarea_asignada=obj.id_tarea_asignada).first()
        if not asignacion_bandeja:
            return None
        bandeja = asignacion_bandeja.id_bandeja_tareas_persona
        persona = bandeja.id_persona

        nombre_completo = None
        if persona:

            nombre_list = [persona.primer_nombre, persona.segundo_nombre, persona.primer_apellido, persona.segundo_apellido]
            nombre_completo = ' '.join(item for item in nombre_list if item is not None)
            return nombre_completo.upper()
        return None
    



class RespuestasPQRGetSeralizer(serializers.ModelSerializer):
    persona_responde = serializers.SerializerMethodField()
    class Meta:
        model = RespuestaPQR
        fields = ['id_respuesta_pqr','fecha_respuesta','persona_responde']

    def get_persona_responde(self, obj):
        persona = obj.id_persona_responde
        nombre_completo = None
        if persona:

            nombre_list = [persona.primer_nombre, persona.segundo_nombre, persona.primer_apellido, persona.segundo_apellido]
            nombre_completo = ' '.join(item for item in nombre_list if item is not None)
            return nombre_completo.upper()