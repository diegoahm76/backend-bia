from rest_framework import serializers
from gestion_documental.models.bandeja_tareas_models import AdicionalesDeTareas
from gestion_documental.models.expedientes_models import ArchivosDigitales

from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, AsignacionOtros, AsignacionPQR, AsignacionTramites, ComplementosUsu_PQR, ConfigTiposRadicadoAgno, Estados_PQR, EstadosSolicitudes, InfoDenuncias_PQRSDF, MetadatosAnexosTmp, Otros, SolicitudAlUsuarioSobrePQRSDF, SolicitudDeDigitalizacion, TiposPQR, MediosSolicitud
from tramites.models.tramites_models import AnexosTramite, PermisosAmbSolicitudesTramite, SolicitudesTramites
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.models.organigrama_models import UnidadesOrganizacionales
from transversal.models.personas_models import Personas
from datetime import datetime, timedelta

from django.db.models import Q


class EstadosSolicitudesGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadosSolicitudes
        fields = ['id_estado_solicitud','nombre']


class PQRSDFGetSerializer(serializers.ModelSerializer):
    estado_solicitud = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre',default=None)
    nombre_sucursal = serializers.ReadOnlyField(source='id_sucursal_recepcion_fisica.descripcion_sucursal',default=None)
    radicado = serializers.SerializerMethodField()
    nombre_completo_titular = serializers.SerializerMethodField()
    tipo_solicitud = serializers.SerializerMethodField()
    estado_asignacion_grupo = serializers.SerializerMethodField()
    numero_solicitudes_digitalizacion = serializers.SerializerMethodField()
    numero_solicitudes_usuario = serializers.SerializerMethodField()
    tiene_complementos = serializers.SerializerMethodField()
    dias_respuesta = serializers.SerializerMethodField()
    medio_solicitud = serializers.ReadOnlyField(source='id_medio_solicitud.nombre',default=None)
    forma_presentacion = serializers.CharField(source='get_cod_forma_presentacion_display', default=None)
    numero_folios = serializers.SerializerMethodField()
    persona_recibe = serializers.SerializerMethodField()
    #medio_almacenamiento = serializers.CharField(source='get_cod_medio_almacenamiento_display', default=None)
    #sucursal_implicada = serializers.SerializerMethodField()
    nombre_sucursal_implicada = serializers.ReadOnlyField(source='id_sucursal_especifica_implicada.descripcion',default=None)
    nombre_sucursal_recepcion_fisica = serializers.ReadOnlyField(source='id_sucursal_recepcion_fisica.descripcion',default=None)
    es_pqrsdf = serializers.SerializerMethodField()
    tipo_PQRSDF = serializers.ReadOnlyField(source='get_cod_tipo_PQRSDF_display',default=True)
    persona_asignada = serializers.SerializerMethodField()
    unidad_asignada = serializers.SerializerMethodField()
    
    class Meta:
        model = PQRSDF
        fields = ['id_PQRSDF','cod_tipo_PQRSDF','tipo_PQRSDF','tipo_solicitud','nombre_completo_titular','asunto','cantidad_anexos','radicado','fecha_radicado','requiere_digitalizacion',
                  'estado_solicitud','nombre_sucursal','numero_solicitudes_digitalizacion','numero_solicitudes_usuario',
                  'tiene_complementos','dias_respuesta','medio_solicitud','forma_presentacion','numero_folios','persona_recibe',
                  'nombre_sucursal_implicada','nombre_sucursal_recepcion_fisica','fecha_registro','estado_asignacion_grupo','persona_asignada','unidad_asignada','es_pqrsdf']

    # def get_radicado(self, obj):
    #     cadena = ""
    #     if obj.id_radicado:
    #         cadena= str(obj.id_radicado.prefijo_radicado)+'-'+str(obj.id_radicado.agno_radicado)+'-'+str(obj.id_radicado.nro_radicado)
    #         return cadena

    def get_radicado(self, obj):
        cadena = ""
        if obj.id_radicado:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=obj.id_radicado.agno_radicado,cod_tipo_radicado=obj.id_radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(obj.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            return cadena
    def get_tipo_solicitud(self, obj):
        return "PQRSDF"
    def get_es_pqrsdf(self, obj):
        return True
    
    #id_persona_recibe persona_recibe_nombre
    def get_persona_recibe(self, obj):
        if obj.id_persona_recibe:
            nombre_completo_responsable = None
            nombre_list = [obj.id_persona_recibe.primer_nombre, obj.id_persona_recibe.segundo_nombre,
                            obj.id_persona_recibe.primer_apellido, obj.id_persona_recibe.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
            return nombre_completo_responsable
        return None
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
    def get_estado_asignacion_grupo(self,obj):
        id= obj.id_PQRSDF
        estado_asignacion_grupo = AsignacionPQR.objects.filter(id_pqrsdf=id).first()
        if estado_asignacion_grupo:
            if estado_asignacion_grupo.cod_estado_asignacion:
                #('Ac', 'Aceptado'),('Re', 'Rechazado')
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
    def get_numero_solicitudes_digitalizacion(self,obj):
        id= obj.id_PQRSDF
        numero_solicitudes = SolicitudDeDigitalizacion.objects.filter(id_pqrsdf=id).count()
        return numero_solicitudes
    def get_numero_solicitudes_usuario(self,obj):

        id = obj.id_PQRSDF
        conteo = SolicitudAlUsuarioSobrePQRSDF.objects.filter(id_pqrsdf=id).count()
        
        return conteo
    
    def get_tiene_complementos(self,obj):
        id= obj.id_PQRSDF
        complementos = ComplementosUsu_PQR.objects.filter(id_PQRSDF=id).first()
        if complementos:
            return True
        else:
            return False
    def get_dias_respuesta(self,obj):
        fecha_radicado = obj.fecha_radicado
        dias_respuesta = obj.dias_para_respuesta
        if not fecha_radicado:
            return None
        
        fecha_actual = datetime.now()
        #print(obj.id_PQRSDF)
        #print("FECHA RADICADO "+str(fecha_radicado))
        #print("DIAS RESPUESTA "+str(dias_respuesta))
        #print("FECHA ACTUAL " + str(fecha_actual))
        fecha_limite =fecha_radicado + timedelta(hours=dias_respuesta * 24)
        #print("fecha_limite " + str(fecha_limite) )
        
   
        dias_faltan = fecha_limite - fecha_actual
        #print("TIENE ESTOS DIAS "+str(dias_faltan.days))
        #print("-----------")
        return dias_faltan.days
    def get_numero_folios(self,obj):
        return 10
    
    def get_persona_asignada(self,obj):
        id= obj.id_PQRSDF
        estado_asignacion_grupo = AsignacionPQR.objects.filter(id_pqrsdf=id).first()
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

        else:
            return None
    def get_unidad_asignada (self,obj):
        id = obj.id_PQRSDF
        estado_asignacion_grupo = AsignacionPQR.objects.filter(id_pqrsdf=id).first()

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
                

class ComplementosUsu_PQRGetSerializer(serializers.ModelSerializer):
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

class SolicitudDeDigitalizacionPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudDeDigitalizacion
        fields = '__all__'

##CAMBIO DE ESTADO DE LA SOLICITUD DE PQR
class Estados_PQRSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estados_PQR
        fields = '__all__'



#OTROS
class Estados_OTROSSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estados_PQR
        fields = '__all__'


        
class Estados_PQRPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estados_PQR
        fields = '__all__'


class PQRSDFPutSerializer(serializers.ModelSerializer):

    class Meta:
        model = PQRSDF
        fields = '__all__'

class ComplementosUsu_PQRPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplementosUsu_PQR
        fields = '__all__'

class AdicionalesDeTareasCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdicionalesDeTareas
        fields = '__all__'

class SolicitudDeDigitalizacionGetSerializer(serializers.ModelSerializer):
    estado_digitalizacion = serializers.SerializerMethodField()
    fecha_respuesta = serializers.ReadOnlyField(source='fecha_rta_solicitud',default=None)
    observaciones = serializers.ReadOnlyField(source='observacion_digitalizacion',default=None)
    id = serializers.ReadOnlyField(source='id_solicitud_de_digitalizacion',default=None)
    class Meta:
        model = SolicitudDeDigitalizacion
        fields = ['id','fecha_respuesta','estado_digitalizacion','observaciones']


    def get_estado_digitalizacion(self, obj):
        if obj.digitalizacion_completada and not obj.devuelta_sin_completar:
            return "COMPLETA"
        else:
            return "INCOMPLETA"


class PQRSDFCabezeraGetSerializer(serializers.ModelSerializer):
    
    
    radicado = serializers.SerializerMethodField()
    #solicitudes = SolicitudDeDigitalizacionGetSerializer()
    class Meta:
        model = PQRSDF
        fields = ['id_PQRSDF','radicado']
    def get_radicado(self, obj):
        cadena = ""
        if obj.id_radicado:
            cadena= str(obj.id_radicado.prefijo_radicado)+'-'+str(obj.id_radicado.agno_radicado)+'-'+str(obj.id_radicado.nro_radicado)
            return cadena

class Estados_PQR_Actual_GetSerializer(serializers.ModelSerializer):
    nombre_estado = serializers.ReadOnlyField(source='estado_solicitud.nombre',default=None)
    class Meta:
        model = Estados_PQR
        fields = ['id_estado_PQR','nombre_estado','fecha_iniEstado']

class PQRSDFHistoricoGetSerializer(serializers.ModelSerializer):
    registros = serializers.SerializerMethodField()
    titular = serializers.SerializerMethodField()
    estado_actual_solicitud = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre',default=None)#id_estado_actual_solicitud
    solicitud_actual = serializers.SerializerMethodField()
   # solicitud_actual = serializers.SerializerMethodField()
    class Meta:
        model = PQRSDF
        fields = ['id_PQRSDF','cantidad_anexos','asunto','titular','estado_actual_solicitud','solicitud_actual','registros']

    def get_registros(self,obj):
        id = obj.id_PQRSDF
        respuesta=[]
        if id:
            estados = Estados_PQR.objects.filter(PQRSDF=obj)
            #print(estados)
            for estado in estados:
                if estado.estado_solicitud.id_estado_solicitud == 10:
                    solicitudes = SolicitudDeDigitalizacion.objects.filter(id_pqrsdf=id,fecha_rta_solicitud=estado.fecha_iniEstado).first()
                    #print(solicitudes)
                    re = SolicitudDeDigitalizacionGetSerializer(solicitudes)
                    respuesta.append({'accion':estado.estado_solicitud.nombre,**re.data})
                else:
                    respuesta.append({'accion':estado.estado_solicitud.nombre,'id':0,'fecha_respuesta':"2023-11-21T00:17:01.369238",'estado_digitalizacion':'NO APLICA','observaciones':'No menciona'})
            return respuesta
    def get_solicitud_actual(self,obj):
        id = obj.id_PQRSDF
        data =[]
        if id:
            estado_actual = obj.id_estado_actual_solicitud
            if estado_actual:
                estados = Estados_PQR.objects.filter(PQRSDF=obj,estado_solicitud__in=[9, 11])
                for estado in estados:
                    #print(estado.estado_solicitud.nombre)
                    #print(estado.estado_solicitud)
                    if estado.estado_solicitud.id_estado_solicitud == 9:
                        
                        solicitud = SolicitudDeDigitalizacion.objects.filter(id_pqrsdf=id,fecha_solicitud=estado.fecha_iniEstado).first()
                        #dato = SolicitudDeDigitalizacionGetSerializer(solicitud)
                        if solicitud:
                            data.append({'accion':estado.estado_solicitud.nombre,'fecha_solicitud':solicitud.fecha_solicitud})
                    if estado.estado_solicitud.id_estado_solicitud == 11:
                         data.append({'accion':estado.estado_solicitud.nombre,'fecha_solicitud':estado.fecha_iniEstado})
        
                    
            
            return data
            #return data_estado_actual.data
        
    def get_titular(self, obj):

        if obj.id_persona_titular:
            nombre_completo_responsable = None
            nombre_list = [obj.id_persona_titular.primer_nombre, obj.id_persona_titular.segundo_nombre,
                            obj.id_persona_titular.primer_apellido, obj.id_persona_titular.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
            return nombre_completo_responsable
        



class AnexosGetSerializer(serializers.ModelSerializer):

    medio_almacenamiento = serializers.CharField(source='get_cod_medio_almacenamiento_display', default=None)
    otros = serializers.SerializerMethodField()
        
    def get_otros(self, obj):
        return True
    
    class Meta:
        model = Anexos
        fields = '__all__'
    
class AnexosComplementoGetSerializer(serializers.ModelSerializer):

    medio_almacenamiento = serializers.CharField(source='get_cod_medio_almacenamiento_display', default=None)
    complemento = serializers.SerializerMethodField()
    class Meta:
        model = Anexos
        fields = '__all__'  
    def get_complemento(self, obj):
        return True


class AnexosDocumentoDigitalGetSerializer(serializers.ModelSerializer):

    
    #ruta_archivo = serializers.ReadOnlyField(source='id_docu_arch_exp.ruta_archivo',default=None)
    class Meta:
        model = Anexos
        #fields = ['id_anexo','ruta_archivo']  
        fields = '__all__'  

class AnexoArchivosDigitalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivosDigitales
        fields = ['ruta_archivo','nombre_de_Guardado']

class MetadatosAnexosTmpSerializerGet(serializers.ModelSerializer):
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

#asignacion PQR A SECCION O SUB O GRUPO

class UnidadesOrganizacionalesSecSubVentanillaGetSerializer(serializers.ModelSerializer):
    nombre_unidad = serializers.SerializerMethodField()
    class Meta:
        model = UnidadesOrganizacionales
        fields = ['id_unidad_organizacional','nombre_unidad']
    def get_nombre_unidad(self, obj):
        tipo = ""
        if obj.cod_agrupacion_documental == 'SEC':
            tipo = " - SECCION - "
        if obj.cod_agrupacion_documental == 'SUB':
            tipo = " - SUBSECCION - "
        if  not obj.cod_agrupacion_documental :
            tipo = " - OFICINA - "
        return str(obj.codigo)+tipo+str(obj.nombre)
    
class LiderGetSerializer(serializers.ModelSerializer):
   
    lider = serializers.SerializerMethodField()

   # solicitud_actual = serializers.SerializerMethodField()
    class Meta:
        model = LideresUnidadesOrg
        fields = ['id_unidad_organizacional','id_persona','lider']

        
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
class AsignacionPQRPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsignacionPQR
        fields = '__all__'


class AsignacionPQRGetSerializer(serializers.ModelSerializer):
    accion = serializers.SerializerMethodField()
    asignado_para = serializers.SerializerMethodField()
    estado_asignado = serializers.SerializerMethodField()
    grupo = serializers.SerializerMethodField()
    sec_sub = serializers.SerializerMethodField()
    class Meta:
        model = AsignacionPQR
        fields = ['consecutivo_asign_x_pqrsdf','accion','fecha_asignacion','fecha_eleccion_estado','asignado_para','sec_sub','grupo','estado_asignado','justificacion_rechazo']
    def get_accion(self,obj):
        return "ASIGNACION DE PQRSDF"
    def get_asignado_para(self,obj):
          if obj.id_persona_asignada:
            nombre_completo_responsable = None
            nombre_list = [obj.id_persona_asignada.primer_nombre, obj.id_persona_asignada.segundo_nombre,
                            obj.id_persona_asignada.primer_apellido, obj.id_persona_asignada.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
            return nombre_completo_responsable
          else:
              
              return None
    def get_estado_asignado(self,obj):
        estado = obj.cod_estado_asignacion
        if not estado:
            return "EN ESPERA"
        if estado == 'Ac':
            return "ACEPTADO"
        if estado == 'Re':
            return "RECHAZADO"
    def get_grupo(self,obj):
        return ''
    
    def get_sec_sub(self,obj):
        if obj.id_und_org_seccion_asignada:
           unidad = UnidadesOrganizacionalesSecSubVentanillaGetSerializer(obj.id_und_org_seccion_asignada)
           data = unidad.data
           return data['nombre_unidad']
        
#ENTREGA 99

class PQRSDFTitularGetSerializer(serializers.ModelSerializer):
    nombres = serializers.SerializerMethodField()
    apellidos = serializers.SerializerMethodField() 
    tipo_documento = serializers.ReadOnlyField(source='id_persona_titular.tipo_documento.nombre',default=None)
    numero_documento = serializers.ReadOnlyField(source='id_persona_titular.numero_documento',default=None)
    class Meta:
        model = PQRSDF
        fields = ['id_PQRSDF','nombres','apellidos','tipo_documento','numero_documento']
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
        if obj.id_persona_titular:
            return self.obtener_nombres(obj.id_persona_titular)
        return None

    def get_apellidos(self, obj):
        if obj.id_persona_titular:
            return self.obtener_apellidos(obj.id_persona_titular)
        return None
    

class PQRSDFTitularGetSerializer(serializers.ModelSerializer):
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
    

class PQRSDFDetalleSolicitud(serializers.ModelSerializer):
    #tipo_activo = serializers.CharField(source='id_bien.get_cod_tipo_bien_display')
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
        

class AnexosCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos
        fields = '__all__'

class MetadatosAnexosTmpCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadatosAnexosTmp
        fields = '__all__'
class SolicitudAlUsuarioSobrePQRSDFCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudAlUsuarioSobrePQRSDF
        fields = '__all__'

class Anexos_PQRCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos_PQR
        fields = '__all__'

class SolicitudAlUsuarioSobrePQRSDFGetSerializer(serializers.ModelSerializer):
    tipo_tramite = serializers.SerializerMethodField()
    numero_radicado = serializers.SerializerMethodField()
    estado = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre',default=None)
    class Meta:
        model = SolicitudAlUsuarioSobrePQRSDF
        # fields = ['id_solicitud_al_usuario_sobre_pqrsdf']
        fields = ['id_solicitud_al_usuario_sobre_pqrsdf','tipo_tramite','fecha_radicado_salida','numero_radicado','estado']

    def get_tipo_tramite(self,obj):
        return "Solicitud de Complemento de Información al Usuario"
    def get_numero_radicado(self,obj):
        cadena = ""
        if obj.id_radicado_salida:
            cadena= str(obj.id_radicado_salida.prefijo_radicado)+'-'+str(obj.id_radicado_salida.agno_radicado)+'-'+str(obj.id_radicado_salida.nro_radicado)
            return cadena
        return 'SIN RADICAR'
    
class Anexos_PQRAnexosGetSerializer(serializers.ModelSerializer):
   
    archivo = serializers.SerializerMethodField()
    numero = serializers.ReadOnlyField(source='id_anexo.orden_anexo_doc',default=None)
    nombre = serializers.ReadOnlyField(source='id_anexo.nombre_anexo',default=None)
    n_folios= serializers.ReadOnlyField(source='id_anexo.numero_folios',default=None)
    medio_almacenamiento = serializers.ReadOnlyField(source='id_anexo.get_cod_medio_almacenamiento_display',default=None)
    class Meta:
        model = Anexos_PQR
        fields = ['id_anexo_PQR','id_anexo','numero','nombre','n_folios','medio_almacenamiento','archivo']

    def get_archivo(self,obj):
        id_anexo = obj.id_anexo
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=id_anexo).first()
        if meta_data:
            data_archivo  = AnexoArchivosDigitalesSerializer(meta_data.id_archivo_sistema)
            return data_archivo.data['ruta_archivo']
        return "Archivo"
    

class SolicitudAlUsuarioSobrePQRSDFGetDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudAlUsuarioSobrePQRSDF
        fields = ['id_solicitud_al_usuario_sobre_pqrsdf','asunto','descripcion','fecha_solicitud']


class MetadatosAnexosTmpGetSerializer(serializers.ModelSerializer):
    categoria_archivo = serializers.ReadOnlyField(source='get_cod_categoria_archivo_display',default=None)
    origen_archivo = serializers.ReadOnlyField(source='get_cod_origen_archivo_display',default=None)
    nombre_tipologia_documental = serializers.ReadOnlyField(source='id_tipologia_doc.nombre',default=None)
    palabras_clave_doc = serializers.SerializerMethodField()
    class Meta:
        model = MetadatosAnexosTmp
        fields = ['id_metadatos_anexo_tmp','categoria_archivo','tiene_replica_fisica','origen_archivo','id_tipologia_doc','nombre_tipologia_documental','asunto','descripcion','palabras_clave_doc']
    
    
    def get_palabras_clave_doc(self, obj):
        if obj.palabras_clave_doc:
            lista_datos =  obj.palabras_clave_doc.split("|")
            return lista_datos
        return None
    


#ENTREGA 109 

class InfoDenuncias_PQRSDFGetByPqrsdfSerializer(serializers.ModelSerializer):
    municipio_localizacion_hecho = serializers.ReadOnlyField(source='cod_municipio_cocalizacion_hecho.nombre',default=None)
    #es un choices 
    nombre_zona_localizacion = serializers.ReadOnlyField(source='get_Cod_zona_localizacion_display',default=None)
    nombre_recursos_afectados_presuntos = serializers.SerializerMethodField()
    class Meta:
        model = InfoDenuncias_PQRSDF
        fields = ['id_info_denuncia_PQRSDF','municipio_localizacion_hecho','Cod_zona_localizacion','nombre_zona_localizacion',
                  'barrio_vereda_localizacion','direccion_localizacion','cod_recursos_fectados_presuntos','nombre_recursos_afectados_presuntos',
                  'otro_recurso_Afectado_cual','nombre_completo_presunto_infractor'
                ,'telefono_presunto_infractor'
                ,'direccion_presunto_infractor'
                ,'ya_habia_puesto_en_conocimiento'
                ,'ante_que_autoridad_había_interpuesto','evidencias_soportan_hecho']
        
    def get_nombre_recursos_afectados_presuntos(self, obj):
        cadena = obj.cod_recursos_fectados_presuntos
        CHOICES = [
            ('Su', 'Suelo'),
            ('Ag', 'Agua'),
            ('Ai', 'Aire'),
            ('Fl', 'Flora'),
            ('Fs', 'Fauna silvestre'),
            ('Ot', 'Otros'),
        ]

        valores_legibles = cadena.split('|')
        arreglo = []

        for codigo in valores_legibles:
            for code, nombre in CHOICES:
                if codigo == code:
                    arreglo.append(nombre)

        return arreglo
    

#OPAS
class OPAGetSerializer(serializers.ModelSerializer):
    id_persona_titular = serializers.ReadOnlyField(source='id_solicitud_tramite.id_persona_titular.id_persona', default=None)
    nombre_completo_titular = serializers.SerializerMethodField()
    tipo_solicitud = serializers.SerializerMethodField()
    id_persona_interpone = serializers.ReadOnlyField(source='id_solicitud_tramite.id_persona_interpone.id_persona', default=None)
    nombre_persona_interpone = serializers.SerializerMethodField()
    cod_relacion_con_el_titular = serializers.ReadOnlyField(source='id_solicitud_tramite.cod_relacion_con_el_titular', default=None)
    relacion_con_el_titular = serializers.CharField(source='id_solicitud_tramite.get_cod_relacion_con_el_titular_display')
    cod_tipo_operacion_tramite = serializers.ReadOnlyField(source='id_solicitud_tramite.cod_tipo_operacion_tramite', default=None)
    tipo_operacion_tramite = serializers.CharField(source='id_solicitud_tramite.get_cod_tipo_operacion_tramite_display')
    nombre_proyecto = serializers.ReadOnlyField(source='id_solicitud_tramite.nombre_proyecto', default=None)
    costo_proyecto = serializers.ReadOnlyField(source='id_solicitud_tramite.costo_proyecto', default=None)
    id_estado_actual_solicitud = serializers.ReadOnlyField(source='id_solicitud_tramite.id_estado_actual_solicitud.id_estado_solicitud', default=None)
    estado_actual_solicitud = serializers.ReadOnlyField(source='id_solicitud_tramite.id_estado_actual_solicitud.nombre', default=None)
    fecha_ini_estado_actual = serializers.ReadOnlyField(source='id_solicitud_tramite.fecha_ini_estado_actual', default=None)
    cod_tipo_permiso_ambiental = serializers.ReadOnlyField(source='id_permiso_ambiental.cod_tipo_permiso_ambiental', default=None)
    tipo_permiso_ambiental = serializers.CharField(source='id_permiso_ambiental.get_cod_tipo_permiso_ambiental_display')
    permiso_ambiental = serializers.ReadOnlyField(source='id_permiso_ambiental.nombre', default=None)
    asunto = serializers.SerializerMethodField()
    cantidad_anexos = serializers.SerializerMethodField()
    radicado = serializers.SerializerMethodField()
    fecha_radicado = serializers.ReadOnlyField(source='id_solicitud_tramite.fecha_radicado', default=None)
    nombre_sucursal = serializers.SerializerMethodField()
    requiere_digitalizacion = serializers.ReadOnlyField(source='id_solicitud_tramite.requiere_digitalizacion', default=None)
    def get_nombre_sucursal(self, obj):
        return 'NO APLICA'
    

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
        return 'NO APLICA'
    def get_asunto(self, obj):
        return 'No APLICA'
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
    
    def get_nombre_persona_interpone(self, obj):
        nombre_persona_interpone = None
        if obj.id_solicitud_tramite.id_persona_interpone:
            if obj.id_solicitud_tramite.id_persona_interpone.tipo_persona == 'J':
                nombre_persona_interpone = obj.id_solicitud_tramite.id_persona_interpone.razon_social
            else:
                nombre_list = [obj.id_solicitud_tramite.id_persona_interpone.primer_nombre, obj.id_solicitud_tramite.id_persona_interpone.segundo_nombre,
                                obj.id_solicitud_tramite.id_persona_interpone.primer_apellido, obj.id_solicitud_tramite.id_persona_interpone.segundo_apellido]
                nombre_persona_interpone = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_interpone = nombre_persona_interpone if nombre_persona_interpone != "" else None
        return nombre_persona_interpone
    def get_tipo_solicitud(self, obj):
        return "OPA"
    # SERIALIZERMETHODFIELD ARCHIVOS
    
    class Meta:
        model = PermisosAmbSolicitudesTramite
        fields = [
            'id_solicitud_tramite',
            'id_persona_titular',
            'nombre_completo_titular',
            'tipo_solicitud',
            'asunto',
            'cantidad_anexos',
            'radicado',
            'fecha_radicado',
            'nombre_sucursal',
            'requiere_digitalizacion',
            'id_estado_actual_solicitud',
            'estado_actual_solicitud',
            'id_persona_interpone',
            'nombre_persona_interpone',
            'cod_relacion_con_el_titular',
            'relacion_con_el_titular',
            'cod_tipo_operacion_tramite',
            'tipo_operacion_tramite',
            'nombre_proyecto',
            'costo_proyecto',
            'fecha_ini_estado_actual',
            'id_permiso_ambiental',
            'cod_tipo_permiso_ambiental',
            'tipo_permiso_ambiental',
            'permiso_ambiental',
            # 'cod_departamento',
            # 'departamento',
            # 'cod_municipio',
            # 'municipio',
            # 'direccion',
            'descripcion_direccion',
            'coordenada_x',
            'coordenada_y'
        ]

class OPAGetRefacSerializer(serializers.ModelSerializer):
    
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
        fields = ['id_solicitud_tramite','tipo_solicitud','nombre_proyecto','nombre_completo_titular','costo_proyecto','pagado','cantidad_predios','cantidad_anexos','radicado','fecha_radicado','id_sede','sede','requiere_digitalizacion','estado_actual','estado_asignacion_grupo','persona_asignada','unidad_asignada','tiene_anexos']

class AsignacionTramiteOpaGetSerializer(serializers.ModelSerializer):
    accion = serializers.SerializerMethodField()
    asignado_para = serializers.SerializerMethodField()
    estado_asignado = serializers.SerializerMethodField()
    grupo = serializers.SerializerMethodField()
    sec_sub = serializers.SerializerMethodField()
    class Meta:
        model = AsignacionTramites
        fields = ['id_solicitud_tramite','consecutivo_asign_x_tramite','accion','fecha_asignacion','fecha_eleccion_estado','asignado_para','sec_sub','grupo','estado_asignado','justificacion_rechazo']
    def get_accion(self,obj):
        return "ASIGNACION DE Opa"
    def get_asignado_para(self,obj):
          if obj.id_persona_asignada:
            nombre_completo_responsable = None
            nombre_list = [obj.id_persona_asignada.primer_nombre, obj.id_persona_asignada.segundo_nombre,
                            obj.id_persona_asignada.primer_apellido, obj.id_persona_asignada.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
            return nombre_completo_responsable
          else:
              
              return None
    def get_estado_asignado(self,obj):
        estado = obj.cod_estado_asignacion
        if not estado:
            return "EN ESPERA"
        if estado == 'Ac':
            return "ACEPTADO"
        if estado == 'Re':
            return "RECHAZADO"
    def get_grupo(self,obj):
        return ''
    
    def get_sec_sub(self,obj):
        if obj.id_und_org_seccion_asignada:
           unidad = UnidadesOrganizacionalesSecSubVentanillaGetSerializer(obj.id_und_org_seccion_asignada)
           data = unidad.data
           return data['nombre_unidad']
        
#ENTREGA 99


class TramitePutSerializer(serializers.ModelSerializer):

    class Meta:
        model = SolicitudesTramites
        fields = '__all__'

class OPADetalleHistoricoSerializer(serializers.ModelSerializer):
    id_tramite = serializers.ReadOnlyField(source='id_solicitud_tramite.id_solicitud_tramite')
    titular = serializers.SerializerMethodField()
    nombre_proyecto = serializers.ReadOnlyField(source='id_solicitud_tramite.nombre_proyecto', default=None)
    costo_proyecto = serializers.ReadOnlyField(source='id_solicitud_tramite.costo_proyecto', default=None)
    cantidad_predios = serializers.ReadOnlyField(source='id_solicitud_tramite.cantidad_predios', default=None)
    solicitud_actual = serializers.SerializerMethodField()
    registros = serializers.SerializerMethodField()
    class Meta:
        model = PermisosAmbSolicitudesTramite
        fields = ['id_tramite','titular','nombre_proyecto','costo_proyecto','cantidad_predios','solicitud_actual','registros']
    

    def get_solicitud_actual(self, obj):
        id_tramite = obj.id_solicitud_tramite.id_solicitud_tramite
        data = []
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_tramite=id_tramite)
        for solicitud in solicitudes:
            
          
            estado = Estados_PQR.objects.filter(fecha_iniEstado=solicitud.fecha_solicitud,estado_solicitud=9).first()
            data.append({'id_solicitud_de_digitalizacion':solicitud.id_solicitud_de_digitalizacion,'accion':estado.estado_solicitud.nombre,'fecha_solicitud':solicitud.fecha_solicitud})
           
        return data
    
    def get_registros(self,obj):
        id_tramite = obj.id_solicitud_tramite.id_solicitud_tramite
        data = []
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_tramite=id_tramite)
        for solicitud in solicitudes:
            data.append({'id':solicitud.id_solicitud_de_digitalizacion,'accion':'SOLICITUD DIGITALIZACIÓN RESPONDIDA','digitalizacion_completada':solicitud.digitalizacion_completada,'fecha_rta_solicitud':solicitud.fecha_rta_solicitud,'observacio':solicitud.observacion_digitalizacion})
        return data
        
    def get_titular(self, obj):
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

class OPAGetHistoricoSerializer(serializers.ModelSerializer):


    
   
    cabecera = serializers.SerializerMethodField()
    detalle = serializers.SerializerMethodField()
    class Meta:
        model = PermisosAmbSolicitudesTramite
        fields = ['cabecera','detalle']
        
    def get_cabecera(self, obj):
        cadena = ""
        if obj.id_solicitud_tramite.id_radicado:
            cadena= str(obj.id_solicitud_tramite.id_radicado.prefijo_radicado)+'-'+str(obj.id_solicitud_tramite.id_radicado.agno_radicado)+'-'+str(obj.id_solicitud_tramite.id_radicado.nro_radicado)
            #return cadena
            return {'id_solicitud_tramite':obj.id_solicitud_tramite.id_solicitud_tramite,'radicado':cadena}
        return None
        return serializer.data
    def get_tipo_solicitud(self, obj):
        return "OPA"
    

    def get_radicado(self, obj):
        cadena = ""
        radicado = obj.id_solicitud_tramite.id_radicado
        if radicado:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=radicado.agno_radicado,cod_tipo_radicado=radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(instance_config_tipo_radicado.consecutivo_actual).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
            print(instance_config_tipo_radicado.cantidad_digitos)
            return cadena
        else: 
            return 'SIN RADICAR'

    def get_detalle(self, obj):
        serializer = OPADetalleHistoricoSerializer(obj)
        return serializer.data
    # SERIALIZERMETHODFIELD ARCHIVOS


class AsignacionTramitesPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsignacionTramites
        fields = '__all__'
# OTROS

class OtrosGetSerializer(serializers.ModelSerializer):
    tipo_solicitud = serializers.SerializerMethodField()
    nombre_completo_titular = serializers.SerializerMethodField()
    estado_solicitud = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre',default=None)
    nombre_sucursal = serializers.ReadOnlyField(source='id_sucursal_recepcion_fisica.descripcion_sucursal',default=None)
    radicado = serializers.SerializerMethodField()
    estado_asignacion_grupo = serializers.SerializerMethodField()
    numero_solicitudes_digitalizacion = serializers.SerializerMethodField()
    medio_solicitud = serializers.ReadOnlyField(source='id_medio_solicitud.nombre',default=None)
    forma_presentacion = serializers.CharField(source='get_cod_forma_presentacion_display', default=None)
    persona_recibe = serializers.SerializerMethodField()
    nombre_sucursal_recepcion_fisica = serializers.ReadOnlyField(source='id_sucursal_recepcion_fisica.descripcion',default=None)
    es_pqrsdf = serializers.SerializerMethodField()
    persona_asignada = serializers.SerializerMethodField()
    persona_interpone = serializers.SerializerMethodField()
    unidad_asignada = serializers.SerializerMethodField()
    relacion_titular = serializers.CharField(source='get_cod_relacion_titular_display', default=None)
    
    def get_tipo_solicitud(self, obj):
        return "OTROS"
    
    def get_nombre_completo_titular(self, obj):
        nombre_completo_responsable = None
        if obj.id_persona_titular:
            if obj.id_persona_titular.tipo_persona == 'N':
                nombre_list = [obj.id_persona_titular.primer_nombre, obj.id_persona_titular.segundo_nombre,
                                obj.id_persona_titular.primer_apellido, obj.id_persona_titular.segundo_apellido]
                nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
                nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
            else:
                nombre_completo_responsable = obj.id_persona_titular.razon_social
                
        return nombre_completo_responsable
    
    def get_radicado(self, obj):
        cadena = ""
        if obj.id_radicados:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=obj.id_radicados.agno_radicado,cod_tipo_radicado=obj.id_radicados.cod_tipo_radicado).first()
            numero_con_ceros = str(obj.id_radicados.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            return cadena
    
    def get_estado_asignacion_grupo(self, obj):
        estado_asignacion_grupo = AsignacionOtros.objects.filter(id_otros=obj.id_otros).first()
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
        estado_asignacion_grupo = AsignacionOtros.objects.filter(id_otros=obj.id_otros).first()
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

        else:
            return None
    
    def get_unidad_asignada (self,obj):
        estado_asignacion_grupo = AsignacionOtros.objects.filter(id_otros=obj.id_otros).first()

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
        
    def get_persona_recibe(self, obj):
        nombre_persona_recibe = None
        if obj.id_persona_recibe:
            if obj.id_persona_recibe.tipo_persona == 'N':
                nombre_list = [obj.id_persona_recibe.primer_nombre, obj.id_persona_recibe.segundo_nombre,
                                obj.id_persona_recibe.primer_apellido, obj.id_persona_recibe.segundo_apellido]
                nombre_persona_recibe = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_recibe = nombre_persona_recibe if nombre_persona_recibe != "" else None
            else:
                nombre_persona_recibe = obj.id_persona_recibe.razon_social
                
        return nombre_persona_recibe
    
    # VALIDAR COMO OBTENER ESTE VALOR PARA OTROS
    def get_numero_solicitudes_digitalizacion(self, obj):
        numero_solicitudes = SolicitudDeDigitalizacion.objects.filter(id_otro=obj.id_otros).count()
        return numero_solicitudes
    
    def get_es_pqrsdf(self, obj):
        return False
        
    def get_persona_interpone(self, obj):
        nombre_persona_interpone = None
        if obj.id_persona_interpone:
            if obj.id_persona_interpone.tipo_persona == 'N':
                nombre_list = [obj.id_persona_interpone.primer_nombre, obj.id_persona_interpone.segundo_nombre,
                                obj.id_persona_interpone.primer_apellido, obj.id_persona_interpone.segundo_apellido]
                nombre_persona_interpone = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_interpone = nombre_persona_interpone if nombre_persona_interpone != "" else None
            else:
                nombre_persona_interpone = obj.id_persona_interpone.razon_social
                
        return nombre_persona_interpone
    
    class Meta:
        model = Otros
        fields = [
            'id_otros',
            'tipo_solicitud',
            'id_persona_titular',
            'nombre_completo_titular',
            'asunto',
            'cantidad_anexos',
            'id_radicados',
            'radicado',
            'fecha_radicado',
            'requiere_digitalizacion',
            'id_estado_actual_solicitud',
            'estado_solicitud',
            'estado_asignacion_grupo',
            'persona_asignada',
            'id_persona_recibe',
            'persona_recibe',
            'numero_solicitudes_digitalizacion',
            'nro_folios_totales',
            'unidad_asignada',
            'es_pqrsdf',
            'id_persona_interpone',
            'persona_interpone',
            'cod_relacion_titular',
            'relacion_titular',
            'id_medio_solicitud',
            'medio_solicitud',
            'cod_forma_presentacion',
            'forma_presentacion',
            'fecha_registro',
            'descripcion',
            'id_sucursal_recepciona_fisica',
            'nombre_sucursal',
            'nombre_sucursal_recepcion_fisica',
            'fecha_envio_definitivo_digitalizacion',
            'fecha_digitalizacion_completada',
            'fecha_inicial_estado_actual',
            'id_documento_archivo_expediente',
            'id_expediente_documental',
            'numero_solicitudes_digitalizacion'
        ]

class OtrosPutSerializer(serializers.ModelSerializer):

    class Meta:
        model = Otros
        fields = '__all__'
        
class AsignacionOtrosPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsignacionOtros
        fields = '__all__'

class AsignacionOtrosGetSerializer(serializers.ModelSerializer):
    accion = serializers.SerializerMethodField()
    asignado_para = serializers.SerializerMethodField()
    estado_asignado = serializers.SerializerMethodField()
    grupo = serializers.SerializerMethodField()
    sec_sub = serializers.SerializerMethodField()
    
    def get_accion(self,obj):
        return "ASIGNACION DE OTROS"
    
    def get_asignado_para(self,obj):
        if obj.id_persona_asignada:
            nombre_completo_responsable = None
            nombre_list = [obj.id_persona_asignada.primer_nombre, obj.id_persona_asignada.segundo_nombre,
                            obj.id_persona_asignada.primer_apellido, obj.id_persona_asignada.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
            return nombre_completo_responsable
        else:
            return None
        
    def get_estado_asignado(self,obj):
        estado = obj.cod_estado_asignacion
        if not estado:
            return "EN ESPERA"
        if estado == 'Ac':
            return "ACEPTADO"
        if estado == 'Re':
            return "RECHAZADO"
        
    def get_grupo(self,obj):
        return ''
    
    def get_sec_sub(self,obj):
        if obj.id_und_org_seccion_asignada:
           unidad = UnidadesOrganizacionalesSecSubVentanillaGetSerializer(obj.id_und_org_seccion_asignada)
           data = unidad.data
           return data['nombre_unidad']
    
    class Meta:
        model = AsignacionOtros
        fields = [
            'id_asignacion_otros',
            'consecutivo_asign_x_otros',
            'accion',
            'fecha_asignacion',
            'fecha_eleccion_estado',
            'asignado_para',
            'sec_sub',
            'grupo',
            'estado_asignado',
            'justificacion_rechazo'
        ]
        
class OtrosDetalleHistoricoSerializer(serializers.ModelSerializer):
    titular = serializers.SerializerMethodField()
    solicitud_actual = serializers.SerializerMethodField()
    registros = serializers.SerializerMethodField()
    
    def get_solicitud_actual(self, obj):
        data = []
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_otro=obj.id_otros)
        for solicitud in solicitudes:
            estado = Estados_PQR.objects.filter(fecha_iniEstado=solicitud.fecha_solicitud,estado_solicitud=9).first()
            data.append({'id_solicitud_de_digitalizacion':solicitud.id_solicitud_de_digitalizacion,'accion':estado.estado_solicitud.nombre,'fecha_solicitud':solicitud.fecha_solicitud})
           
        return data
    
    def get_registros(self,obj):
        data = []
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_otro=obj.id_otros)
        for solicitud in solicitudes:
            data.append({'id':solicitud.id_solicitud_de_digitalizacion,'accion':'SOLICITUD DIGITALIZACIÓN RESPONDIDA','digitalizacion_completada':solicitud.digitalizacion_completada,'fecha_rta_solicitud':solicitud.fecha_rta_solicitud,'observacion':solicitud.observacion_digitalizacion})
        return data
        
    def get_titular(self, obj):
        nombre_persona_titular = None
        if obj.id_persona_titular:
            if obj.id_persona_titular.tipo_persona == 'J':
                nombre_persona_titular = obj.id_persona_titular.razon_social
            else:
                nombre_list = [obj.id_persona_titular.primer_nombre, obj.id_persona_titular.segundo_nombre,
                                obj.id_persona_titular.primer_apellido, obj.id_persona_titular.segundo_apellido]
                nombre_persona_titular = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_titular = nombre_persona_titular if nombre_persona_titular != "" else None
        return nombre_persona_titular
    
    class Meta:
        model = Otros
        fields = [
            'id_otros',
            'titular',
            'cantidad_anexos',
            'asunto',
            'solicitud_actual',
            'registros'
        ]
        
class OtrosGetHistoricoSerializer(serializers.ModelSerializer):
    cabecera = serializers.SerializerMethodField()
    detalle = serializers.SerializerMethodField()
    
    def get_cabecera(self, obj):
        cadena = ""
        if obj.id_radicados:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=obj.id_radicados.agno_radicado,cod_tipo_radicado=obj.id_radicados.cod_tipo_radicado).first()
            numero_con_ceros = str(obj.id_radicados.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
            
            return {'id_otros':obj.id_otros, 'radicado':cadena}
        return None

    def get_detalle(self, obj):
        serializer = OtrosDetalleHistoricoSerializer(obj)
        return serializer.data
    
    class Meta:
        model = Otros
        fields = ['cabecera','detalle']
    

class UnidadesOrganizacionalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadesOrganizacionales
        fields = '__all__'

#PANEL DE VENTANILLA TRAMITES
        
class SolicitudesTramitesGetSerializer(serializers.ModelSerializer):
    nombre_cod_tipo_operacion_tramite = serializers.ReadOnlyField(source='get_cod_tipo_operacion_tramite_display',default=None)
    nombre_cod_relacion_con_el_titular = serializers.ReadOnlyField(source='get_cod_relacion_con_el_titular_display', default=None)
    estado_actual_solicitud = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre', default=None)
    nombre_sucursal = serializers.ReadOnlyField(source='id_sucursal_recepcion_fisica.descripcion_sucursal',default=None)
    medio_solicitud = serializers.ReadOnlyField(source='id_medio_solicitud.nombre',default=None)
    nombre_completo_titular = serializers.SerializerMethodField()
    radicado = serializers.SerializerMethodField()
    tipo_solicitud = serializers.SerializerMethodField()
    nombre_tramite = serializers.SerializerMethodField()
    cantidad_anexos = serializers.SerializerMethodField()
    estado_asignacion_grupo = serializers.SerializerMethodField()
    persona_asignada = serializers.SerializerMethodField()
    unidad_asignada = serializers.SerializerMethodField()
    
    def get_cantidad_anexos(self, obj):
        conteo_anexos = AnexosTramite.objects.filter(id_solicitud_tramite=obj.id_solicitud_tramite).count()
        return conteo_anexos

    def get_tipo_solicitud(self, obj):
        return 'TRAMITE'
    
    def get_nombre_completo_titular(self, obj):
        if obj.id_persona_titular:
            
            if obj.id_persona_titular.tipo_persona == 'J':
                nombre_completo_titular = obj.id_persona_titular.razon_social
                return nombre_completo_titular
            else:
                nombre_completo_titular = None
                nombre_list = [obj.id_persona_titular.primer_nombre, obj.id_persona_titular.segundo_nombre,
                                obj.id_persona_titular.primer_apellido, obj.id_persona_titular.segundo_apellido]
                nombre_completo_titular = ' '.join(item for item in nombre_list if item is not None)
                nombre_completo_titular = nombre_completo_titular if nombre_completo_titular != "" else None
                return nombre_completo_titular
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
            if estado_asignacion_grupo.cod_estado_asignacion == 'Ac':
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
    
    def get_nombre_tramite(self, obj):
        nombre_tramite = None
        permiso_ambiental = obj.permisosambsolicitudestramite_set.first()
        if permiso_ambiental:
            nombre_tramite = permiso_ambiental.id_permiso_ambiental.nombre
        return nombre_tramite
    
    class Meta:
        model = SolicitudesTramites
        fields = '__all__'
        
class AsignacionTramiteGetSerializer(serializers.ModelSerializer):
    accion = serializers.SerializerMethodField()
    asignado_para = serializers.SerializerMethodField()
    estado_asignado = serializers.SerializerMethodField()
    grupo = serializers.SerializerMethodField()
    sec_sub = serializers.SerializerMethodField()
    class Meta:
        model = AsignacionTramites
        fields = ['id_solicitud_tramite','consecutivo_asign_x_tramite','accion','fecha_asignacion','fecha_eleccion_estado','asignado_para','sec_sub','grupo','estado_asignado','justificacion_rechazo']
    def get_accion(self,obj):
        return "ASIGNACION DE TRAMITE"
    def get_asignado_para(self,obj):
          if obj.id_persona_asignada:
            nombre_completo_responsable = None
            nombre_list = [obj.id_persona_asignada.primer_nombre, obj.id_persona_asignada.segundo_nombre,
                            obj.id_persona_asignada.primer_apellido, obj.id_persona_asignada.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
            return nombre_completo_responsable
          else:
              
              return None
    def get_estado_asignado(self,obj):
        estado = obj.cod_estado_asignacion
        if not estado:
            return "EN ESPERA"
        if estado == 'Ac':
            return "ACEPTADO"
        if estado == 'Re':
            return "RECHAZADO"
    def get_grupo(self,obj):
        return ''
    
    def get_sec_sub(self,obj):
        if obj.id_und_org_seccion_asignada:
           unidad = UnidadesOrganizacionalesSecSubVentanillaGetSerializer(obj.id_und_org_seccion_asignada)
           data = unidad.data
           return data['nombre_unidad']

class TramitesDetalleHistoricoSerializer(serializers.ModelSerializer):
    solicitud_actual = serializers.SerializerMethodField()
    nombre_tramite = serializers.SerializerMethodField()
    registros = serializers.SerializerMethodField()
    titular = serializers.SerializerMethodField()
    
    def get_nombre_tramite(self, obj):
        nombre_tramite = None
        permiso_ambiental = obj.permisosambsolicitudestramite_set.first()
        if permiso_ambiental:
            nombre_tramite = permiso_ambiental.id_permiso_ambiental.nombre
        return nombre_tramite
    
    def get_solicitud_actual(self, obj):
        id_tramite = obj.id_solicitud_tramite
        data = []
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_tramite=id_tramite)
        for solicitud in solicitudes:
            estado = Estados_PQR.objects.filter(id_tramite=solicitud.id_tramite.id_solicitud_tramite,estado_solicitud=9).first()
            data.append({'id_solicitud_de_digitalizacion':solicitud.id_solicitud_de_digitalizacion,'accion':estado.estado_solicitud.nombre,'fecha_solicitud':solicitud.fecha_solicitud})
           
        return data
    
    def get_registros(self,obj):
        id_tramite = obj.id_solicitud_tramite
        data = []
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_tramite=id_tramite)
        for solicitud in solicitudes:
            data.append(
                {
                    'id':solicitud.id_solicitud_de_digitalizacion,
                    'accion':'SOLICITUD DIGITALIZACIÓN RESPONDIDA',
                    'digitalizacion_completada':solicitud.digitalizacion_completada,
                    'fecha_rta_solicitud':solicitud.fecha_rta_solicitud,
                    'observacion':solicitud.observacion_digitalizacion
                }
            )
        return data
        
    def get_titular(self, obj):
        nombre_persona_titular = None
        if obj.id_persona_titular:
            if obj.id_persona_titular.tipo_persona == 'J':
                nombre_persona_titular = obj.id_persona_titular.razon_social
            else:
                nombre_list = [obj.id_persona_titular.primer_nombre, obj.id_persona_titular.segundo_nombre,
                                obj.id_persona_titular.primer_apellido, obj.id_persona_titular.segundo_apellido]
                nombre_persona_titular = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_titular = nombre_persona_titular if nombre_persona_titular != "" else None
        return nombre_persona_titular
    
    class Meta:
        model = SolicitudesTramites
        fields = [
            'id_solicitud_tramite',
            'titular',
            'nombre_proyecto',
            'nombre_tramite',
            'costo_proyecto',
            'cantidad_predios',
            'solicitud_actual',
            'registros'
        ]

class TramitesGetHistoricoSerializer(serializers.ModelSerializer):
    cabecera = serializers.SerializerMethodField()
    detalle = serializers.SerializerMethodField()
        
    def get_cabecera(self, obj):
        cadena = ""
        radicado = obj.id_radicado
       
        if radicado:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=radicado.agno_radicado,cod_tipo_radicado=radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
            
            return {
                'id_solicitud_tramite':obj.id_solicitud_tramite,
                'radicado':cadena
            }
           
        else: 
            return 'SIN RADICAR'

    def get_detalle(self, obj):
        serializer = TramitesDetalleHistoricoSerializer(obj)
        return serializer.data
    
    class Meta:
        model = SolicitudesTramites
        fields = ['cabecera','detalle']

class TramitesComplementosUsu_PQRGetSerializer(serializers.ModelSerializer):
    tipo = serializers.SerializerMethodField()
    nombre_completo_titular = serializers.SerializerMethodField()
    radicado = serializers.SerializerMethodField()
    numero_solicitudes = serializers.SerializerMethodField()
    es_complemento = serializers.SerializerMethodField()
    id_solicitud_tramite = serializers.ReadOnlyField(source='id_solicitud_usu_PQR.id_solicitud_tramite.id_solicitud_tramite', default=None)
    medio_solicitud = serializers.ReadOnlyField(source='id_medio_solicitud.nombre', default=None)
    nombre_completo_recibe = serializers.SerializerMethodField()
    
    def get_es_complemento(self, obj):
        return True
    
    def get_tipo(self, obj):
        return "Complemento de Trámite - Respuesta a Requerimiento"
    
    def get_nombre_completo_recibe(self, obj):
        nombre_persona_titular = None
        if obj.id_persona_recibe:
            if obj.id_persona_recibe.tipo_persona == 'J':
                nombre_persona_titular = obj.id_persona_recibe.razon_social
            else:
                nombre_list = [obj.id_persona_recibe.primer_nombre, obj.id_persona_recibe.segundo_nombre,
                                obj.id_persona_recibe.primer_apellido, obj.id_persona_recibe.segundo_apellido]
                nombre_persona_titular = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_titular = nombre_persona_titular if nombre_persona_titular != "" else None
        else:
            nombre_persona_titular = 'No Identificado'
        return nombre_persona_titular
        
    def get_nombre_completo_titular(self, obj):
        nombre_persona_titular = None
        if obj.id_persona_interpone:
            if obj.id_persona_interpone.tipo_persona == 'J':
                nombre_persona_titular = obj.id_persona_interpone.razon_social
            else:
                nombre_persona_titular = None
                nombre_list = [obj.id_persona_interpone.primer_nombre, obj.id_persona_interpone.segundo_nombre,
                                obj.id_persona_interpone.primer_apellido, obj.id_persona_interpone.segundo_apellido]
                nombre_persona_titular = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_titular = nombre_persona_titular if nombre_persona_titular != "" else None
        else:
            nombre_persona_titular = 'No Identificado'
        return nombre_persona_titular
            
    def get_radicado(self, obj):
        cadena = ""
        if obj.id_radicado:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=obj.id_radicado.agno_radicado,cod_tipo_radicado=obj.id_radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(obj.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            return cadena
        
    def get_numero_solicitudes(self, obj):
        id= obj.idComplementoUsu_PQR
        numero_solicitudes = SolicitudDeDigitalizacion.objects.filter(id_complemento_usu_pqr=id).count()
        return numero_solicitudes
    
    class Meta:
        model = ComplementosUsu_PQR
        fields = [
            'idComplementoUsu_PQR',
            'id_solicitud_tramite',
            'tipo',
            'nombre_completo_titular',
            'asunto',
            'cantidad_anexos',
            'radicado',
            'fecha_radicado',
            'requiere_digitalizacion',
            'numero_solicitudes',
            'es_complemento',
            'complemento_asignado_unidad',
            'fecha_complemento',
            'medio_solicitud',
            'nro_folios_totales',
            'nombre_completo_recibe',
            'descripcion'
        ]
    
class TramitesDetalleHistoricoComplementoSerializer(serializers.ModelSerializer):
    id_solicitud_tramite = serializers.ReadOnlyField(source='id_solicitud_usu_PQR.id_solicitud_tramite.id_solicitud_tramite', default=None)
    solicitud_actual = serializers.SerializerMethodField()
    registros = serializers.SerializerMethodField()
    titular = serializers.SerializerMethodField()
    
    def get_solicitud_actual(self, obj):
        idComplementoUsu_PQR = obj.idComplementoUsu_PQR
        data = []
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_complemento_usu_pqr=idComplementoUsu_PQR)
        for solicitud in solicitudes:
            estado = Estados_PQR.objects.filter(solicitud_usu_sobre_PQR=solicitud.id_complemento_usu_pqr.id_solicitud_usu_PQR.id_solicitud_al_usuario_sobre_pqrsdf,estado_solicitud=9).first()
            accion = estado.estado_solicitud.nombre if estado else None
            data.append({'id_solicitud_de_digitalizacion':solicitud.id_solicitud_de_digitalizacion,'accion':accion,'fecha_solicitud':solicitud.fecha_solicitud})
           
        return data
    
    def get_registros(self,obj):
        idComplementoUsu_PQR = obj.idComplementoUsu_PQR
        data = []
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_complemento_usu_pqr=idComplementoUsu_PQR)
        for solicitud in solicitudes:
            data.append(
                {
                    'id':solicitud.id_solicitud_de_digitalizacion,
                    'accion':'SOLICITUD DIGITALIZACIÓN RESPONDIDA',
                    'digitalizacion_completada':solicitud.digitalizacion_completada,
                    'fecha_rta_solicitud':solicitud.fecha_rta_solicitud,
                    'observacion':solicitud.observacion_digitalizacion
                }
            )
        return data
        
    def get_titular(self, obj):
        nombre_persona_titular = None
        if obj.id_persona_interpone:
            if obj.id_persona_interpone.tipo_persona == 'J':
                nombre_persona_titular = obj.id_persona_interpone.razon_social
            else:
                nombre_list = [obj.id_persona_interpone.primer_nombre, obj.id_persona_interpone.segundo_nombre,
                                obj.id_persona_interpone.primer_apellido, obj.id_persona_interpone.segundo_apellido]
                nombre_persona_titular = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_titular = nombre_persona_titular if nombre_persona_titular != "" else None
        return nombre_persona_titular
    
    class Meta:
        model = ComplementosUsu_PQR
        fields = [
            'id_solicitud_usu_PQR',
            'id_solicitud_tramite',
            'titular',
            'cantidad_anexos',
            'asunto',
            'solicitud_actual',
            'registros'
        ]

class TramitesGetHistoricoComplementoSerializer(serializers.ModelSerializer):
    cabecera = serializers.SerializerMethodField()
    detalle = serializers.SerializerMethodField()
        
    def get_cabecera(self, obj):
        cadena = ""
        radicado = obj.id_radicado
       
        if radicado:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=radicado.agno_radicado,cod_tipo_radicado=radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
            
            return {
                'idComplementoUsu_PQR':obj.idComplementoUsu_PQR,
                'radicado':cadena
            }
           
        else: 
            return 'SIN RADICAR'

    def get_detalle(self, obj):
        serializer = TramitesDetalleHistoricoComplementoSerializer(obj)
        return serializer.data
    
    class Meta:
        model = ComplementosUsu_PQR
        fields = ['cabecera','detalle']
