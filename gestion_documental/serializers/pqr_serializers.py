from rest_framework import serializers

from gestion_documental.models.radicados_models import PQRSDF, EstadosSolicitudes, TiposPQR, MediosSolicitud

class TiposPQRGetSerializer(serializers.ModelSerializer):
    cod_tipo_pqr_legible = serializers.SerializerMethodField()
    class Meta:
        model = TiposPQR
        fields = '__all__'

    def get_cod_tipo_pqr_legible(self, obj):
        return obj.get_cod_tipo_pqr_display()
    
class TiposPQRUpdateSerializer(serializers.ModelSerializer):
    cod_tipo_pqr_legible = serializers.SerializerMethodField()
    
    cod_tipo_pqr = serializers.ReadOnlyField(default=None)
    nombre = serializers.ReadOnlyField(default=None)
    class Meta:
        model = TiposPQR
        fields = '__all__'

    def get_cod_tipo_pqr_legible(self, obj):
        return obj.get_cod_tipo_pqr_display()
    



 ########################## MEDIOS DE SOLICITUD ##########################

class MediosSolicitudCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediosSolicitud
        fields = '__all__'


class MediosSolicitudSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediosSolicitud
        fields = '__all__'

class MediosSolicitudDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediosSolicitud
        fields = '__all__'

class MediosSolicitudUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediosSolicitud
        fields = '__all__'

class EstadosSolicitudesGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadosSolicitudes
        fields = '__all__'
class PQRSDFGetSerializer(serializers.ModelSerializer):
    estado_solicitud = serializers.ReadOnlyField(source='id_estado_actual_solicitud.estado_solicitud.nombre',default=None)
    radicado = serializers.SerializerMethodField()
    nombre_completo_titular = serializers.SerializerMethodField()
    tipo_solicitud = serializers.SerializerMethodField()
    estado_asignacion_grupo = serializers.SerializerMethodField()
    class Meta:
        model = PQRSDF
        fields = ['id_PQRSDF','tipo_solicitud','nombre_completo_titular','asunto','cantidad_anexos','radicado','requiere_digitalizacion','estado_solicitud','estado_asignacion_grupo']

    def get_radicado(self, obj):
        cadena = ""
        if obj.id_radicado:
            cadena= str(obj.id_radicado.prefijo_radicado)+'-'+str(obj.id_radicado.agno_radicado)+'-'+str(obj.id_radicado.nro_radicado)
            return cadena
    def get_estado_asignacion_grupo(self,obj):
        #pendiente entrega asignacion a grupo
        return "PENDIENTE"
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
            
        