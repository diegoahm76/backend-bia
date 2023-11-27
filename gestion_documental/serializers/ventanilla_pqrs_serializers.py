from rest_framework import serializers
from gestion_documental.models.expedientes_models import ArchivosDigitales

from gestion_documental.models.radicados_models import PQRSDF, Anexos, AsignacionPQR, ComplementosUsu_PQR, Estados_PQR, EstadosSolicitudes, MetadatosAnexosTmp, SolicitudDeDigitalizacion, TiposPQR, MediosSolicitud
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.models.organigrama_models import UnidadesOrganizacionales




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
    class Meta:
        model = PQRSDF
        fields = ['id_PQRSDF','tipo_solicitud','nombre_completo_titular','asunto','cantidad_anexos','radicado','fecha_radicado','requiere_digitalizacion','estado_solicitud','estado_asignacion_grupo','nombre_sucursal','numero_solicitudes_digitalizacion','numero_solicitudes_usuario','tiene_complementos']

    def get_radicado(self, obj):
        cadena = ""
        if obj.id_radicado:
            cadena= str(obj.id_radicado.prefijo_radicado)+'-'+str(obj.id_radicado.agno_radicado)+'-'+str(obj.id_radicado.nro_radicado)
            return cadena

    def get_tipo_solicitud(self, obj):
        return "PQRSDF"
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
                    return "Pendiente"
            else:
                return "Pendiente"
        else:
            return "Pendiente"
    def get_numero_solicitudes_digitalizacion(self,obj):
        id= obj.id_PQRSDF
        numero_solicitudes = SolicitudDeDigitalizacion.objects.filter(id_pqrsdf=id).count()
        return numero_solicitudes
    def get_numero_solicitudes_usuario(self,obj):
        return 0
    
    def get_tiene_complementos(self,obj):
        id= obj.id_PQRSDF
        complementos = ComplementosUsu_PQR.objects.filter(id_PQRSDF=id).first()
        if complementos:
            return True
        else:
            return False
class ComplementosUsu_PQRGetSerializer(serializers.ModelSerializer):
    tipo = serializers.SerializerMethodField()
    nombre_completo_titular = serializers.SerializerMethodField()
    radicado = serializers.SerializerMethodField()
    numero_solicitudes = serializers.SerializerMethodField()
    class Meta:
        model = ComplementosUsu_PQR
        fields = ['idComplementoUsu_PQR','tipo','nombre_completo_titular','asunto','cantidad_anexos','radicado','requiere_digitalizacion','numero_solicitudes']
    def get_tipo(self, obj):
        return "Complemento de PQRSDF"
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
                    print(solicitudes)
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
    class Meta:
        model = Anexos
        fields = '__all__'  

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
    class Meta:
        model = MetadatosAnexosTmp
        fields = ['id_metadatos_anexo_tmp','asunto','fecha_creacion_doc','origen_archivo','categoria_archivo','tiene_replica_fisica','es_version_original','palabras_clave_doc','nombre_tipologia_documental','descripcion']


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

class AsignacionPQRPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsignacionPQR
        fields = '__all__'
        