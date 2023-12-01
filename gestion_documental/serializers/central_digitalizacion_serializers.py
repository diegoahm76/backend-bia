from rest_framework import serializers
from gestion_documental.choices.central_digitalizacion_choices import TIPO_SOLICITUD_CHOICES

from gestion_documental.models.radicados_models import SolicitudDeDigitalizacion
from gestion_documental.serializers.pqr_serializers import AnexosPqrsdfPanelSerializer
from transversal.models.personas_models import Personas

class SolicitudesPendientesSerializer(serializers.ModelSerializer):
    nombre_tipo_solicitud = serializers.SerializerMethodField()
    numero_radicado = serializers.SerializerMethodField()
    asunto = serializers.SerializerMethodField()
    titular = serializers.SerializerMethodField()
    numero_anexos = serializers.SerializerMethodField()
    estado_digitalizacion = serializers.SerializerMethodField()
    anexos = serializers.SerializerMethodField()

    def get_nombre_tipo_solicitud(self, obj):
        nombre_tipo_solicitud = ''
        for choice in TIPO_SOLICITUD_CHOICES:
            if choice[0] == obj['cod_tipo_solicitud']:
                nombre_tipo_solicitud = choice[1]
                break
        
        return nombre_tipo_solicitud

    def get_numero_radicado(self, obj):
        return f"{obj['radicado'].prefijo_radicado}-{obj['radicado'].agno_radicado}-{obj['radicado'].nro_radicado}"
    
    def get_asunto(self, obj):
        return obj['asunto']

    def get_titular(self, obj):
        nombre_persona_titular = ""
        if obj['id_persona_titular']:
            persona_titular = Personas.objects.filter(id_persona = obj['id_persona_titular']).first()
            nombre_persona_titular = f"{persona_titular.primer_nombre} {persona_titular.segundo_nombre} {persona_titular.primer_apellido} {persona_titular.segundo_apellido}"
        elif obj['id_persona_titular'] == 0:
            nombre_persona_titular = "Anonimo"
        
        return nombre_persona_titular

    def get_numero_anexos(self, obj):
        return obj['numero_anexos']
    
    def get_estado_digitalizacion(self, obj):
        validate_anexos_SH =  all(not anexo.ya_digitalizado for anexo in obj['anexos'])
        return 'Sin Hacer' if validate_anexos_SH else 'En Proceso'
    
    def get_anexos(self, obj):
        anexos = []
        for anexo in obj['anexos']:
            anexos.append(AnexosPqrsdfPanelSerializer(anexo).data)
        return anexos

    class Meta:
        model = SolicitudDeDigitalizacion
        fields = [
            'id_solicitud_de_digitalizacion',
            'fecha_solicitud',
            'nombre_tipo_solicitud',
            'numero_radicado',
            'asunto',
            'titular',
            'numero_anexos',
            'estado_digitalizacion',
            'anexos'
        ]

class SolicitudesPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudDeDigitalizacion
        fields = '__all__'