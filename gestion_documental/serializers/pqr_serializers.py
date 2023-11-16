from rest_framework import serializers

from gestion_documental.models.radicados_models import PQRSDF, EstadosSolicitudes, SolicitudAlUsuarioSobrePQRSDF, T262Radicados, TiposPQR, MediosSolicitud
from transversal.models.personas_models import Personas

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

class SolicitudesSerializer(serializers.ModelSerializer):
    nombre_und_org_oficina_solicita = serializers.ReadOnlyField(source='id_und_org_oficina_solicita.nombre')
    numero_radicado_salida = serializers.SerializerMethodField()

    def get_numero_radicado_salida(self, obj):
        radicado = T262Radicados.objects.filter(id_radicado=obj.id_radicado_salida_id).first()
        numero_radicado_salida = ''
        if radicado:  
            data_radicado = [radicado.prefijo_radicado, str(radicado.fecha_radicado.year), str(radicado.nro_radicado)]
            numero_radicado_salida = '-'.join(data_radicado)
        return numero_radicado_salida
    class Meta:
        model = SolicitudAlUsuarioSobrePQRSDF
        fields = [
            'id_solicitud_al_usuario_sobre_pqrsdf',
            'id_pqrsdf',
            'id_und_org_oficina_solicita',
            'nombre_und_org_oficina_solicita',
            'fecha_solicitud',
            'asunto',
            'descripcion',
            'fecha_radicado_salida',
            'numero_radicado_salida'
        ]

class PQRSDFSerializer(serializers.ModelSerializer):
    nombre_estado_solicitud = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre')
    numero_radicado = serializers.ReadOnlyField(source='id_radicado.nro_radicado')
    numero_radicado_entrada = serializers.SerializerMethodField()
    nombre_completo_titular = serializers.SerializerMethodField()
    solicitudes_pqr = serializers.SerializerMethodField()

    def get_numero_radicado_entrada(self, obj):
        radicado = T262Radicados.objects.filter(id_radicado=obj.id_radicado_id).first()
        numero_radicado_entrada = ''
        if radicado:  
            data_radicado = [radicado.prefijo_radicado, str(radicado.fecha_radicado.year), str(radicado.nro_radicado)]
            numero_radicado_entrada = '-'.join(data_radicado)
        return numero_radicado_entrada

    def get_nombre_completo_titular(self, obj):
        persona = Personas.objects.filter(id_persona=obj.id_persona_titular_id).first()
        nombre_completo = None
        nombre_list = [persona.primer_nombre, persona.segundo_nombre, persona.primer_apellido, persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        return nombre_completo
    
    def get_solicitudes_pqr(self, obj):
        solicitudes = SolicitudAlUsuarioSobrePQRSDF.objects.filter(id_pqrsdf=obj.id_PQRSDF)
        solicitudes_titular = []
        if solicitudes:
            for solicitud in solicitudes:
                estado_solicitud = EstadosSolicitudes.objects.filter(id_estado_solicitud=solicitud.id_estado_actual_solicitud_id).first()
                if(estado_solicitud.nombre != "GUARDADA" and estado_solicitud.nombre != "RESPONDIDA"):
                    solicitudes_serializer = SolicitudesSerializer(solicitud)
                    solicitudes_titular.append(solicitudes_serializer.data)
        return solicitudes_titular

    class Meta:
        model = PQRSDF
        fields = '__all__'