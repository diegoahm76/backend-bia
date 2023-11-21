from rest_framework import serializers

from gestion_documental.models.radicados_models import PQRSDF, AsignacionPQR, ComplementosUsu_PQR, Estados_PQR, EstadosSolicitudes, SolicitudDeDigitalizacion, TiposPQR, MediosSolicitud



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
    class Meta:
        model = PQRSDF
        fields = ['id_PQRSDF','tipo_solicitud','nombre_completo_titular','asunto','cantidad_anexos','radicado','fecha_radicado','requiere_digitalizacion','estado_solicitud','estado_asignacion_grupo','nombre_sucursal','numero_solicitudes_digitalizacion','numero_solicitudes_usuario']

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
    estado_asociado = serializers.SerializerMethodField()
    class Meta:
        model = SolicitudDeDigitalizacion
        fields = ['id_solicitud_de_digitalizacion','fecha_solicitud','fecha_rta_solicitud','estado_digitalizacion','observacion_digitalizacion','estado_asociado']

    def get_estado_asociado(self,obj):
        id = obj.id_pqrsdf
        fecha = obj.fecha_solicitud
        solicitud = Estados_PQR.objects.filter(PQRSDF=id,fecha_iniEstado=fecha).first()
        print(solicitud.estado_solicitud.nombre)
        return solicitud.estado_solicitud.nombre
    def get_estado_digitalizacion(self, obj):
        if obj.digitalizacion_completada and not obj.devuelta_sin_completar:
            return "COMPLETA"
        else:
            return "PENDIENTE"


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
    solicitudes = serializers.SerializerMethodField()
    titular = serializers.SerializerMethodField()
    estado_actual_solicitud = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre',default=None)#id_estado_actual_solicitud
    solicitud_actual = serializers.SerializerMethodField()
   # solicitud_actual = serializers.SerializerMethodField()
    class Meta:
        model = PQRSDF
        fields = ['id_PQRSDF','cantidad_anexos','asunto','titular','estado_actual_solicitud','solicitud_actual','solicitudes']

    def get_solicitudes(self,obj):
        id = obj.id_PQRSDF
        if id:
            solicitudes = SolicitudDeDigitalizacion.objects.filter(id_pqrsdf=id)
            respuesta = SolicitudDeDigitalizacionGetSerializer(solicitudes,many=True)
            return respuesta.data
    def get_solicitud_actual(self,obj):
        id = obj.id_PQRSDF
        if id:

            estado_actual = obj.id_estado_actual_solicitud
            
            if estado_actual:
                estados = Estados_PQR.objects.filter(PQRSDF=obj,estado_solicitud=estado_actual).order_by('-fecha_iniEstado').first()
                
                if estados:
                    estados_asociados = Estados_PQR.objects.filter(PQRSDF=obj,estado_PQR_asociado=estados).order_by('-fecha_iniEstado').first()
                    
                    if estados_asociados:
                        solicitud = SolicitudDeDigitalizacion.objects.filter(id_pqrsdf=id,fecha_solicitud=estados_asociados.fecha_iniEstado).first()
                        if solicitud:
                            solicitud_serializada = SolicitudDeDigitalizacionGetSerializer(solicitud)
                            print("chi")
                     
                            return {'accion':estados_asociados.estado_solicitud.nombre,**solicitud_serializada.data}
        
                    
            
            return {}
            #return data_estado_actual.data
        
    def get_titular(self, obj):

        if obj.id_persona_titular:
            nombre_completo_responsable = None
            nombre_list = [obj.id_persona_titular.primer_nombre, obj.id_persona_titular.segundo_nombre,
                            obj.id_persona_titular.primer_apellido, obj.id_persona_titular.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
            return nombre_completo_responsable