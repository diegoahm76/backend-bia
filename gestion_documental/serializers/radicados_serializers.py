from rest_framework import serializers
from gestion_documental.choices.tipo_radicado_choices import TIPOS_RADICADO_CHOICES

from gestion_documental.models.radicados_models import T262Radicados
from transversal.models.personas_models import Personas

class RadicadosImprimirSerializer(serializers.ModelSerializer):
    nombre_tipo_radicado = serializers.SerializerMethodField()
    numero_radicado_completo = serializers.SerializerMethodField()
    asunto = serializers.SerializerMethodField()
    titular = serializers.SerializerMethodField()
    fecha_radicado = serializers.SerializerMethodField()
    agno_radicado = serializers.SerializerMethodField()
    

    def get_nombre_tipo_radicado(self, obj):
        nombre_tipo_radicado = ''
        for choice in TIPOS_RADICADO_CHOICES:
            if choice[0] == obj['cod_tipo_radicado']:
                nombre_tipo_radicado = choice[1]
                break
        
        return nombre_tipo_radicado
    
    def get_numero_radicado_completo(self, obj):
        return f"{obj['prefijo_radicado']}-{obj['agno_radicado']}-{obj['nro_radicado']}"

    def get_asunto(self, obj):
        return obj['asunto']
            
    def get_titular(self, obj):
        nombre_persona_titular = ""
        if obj['id_persona_titular']:
            persona_titular = Personas.objects.filter(id_persona = obj['id_persona_titular']).first()
            nombre_persona_titular = f"{persona_titular.primer_nombre} {persona_titular.segundo_nombre} {persona_titular.primer_apellido} {persona_titular.segundo_apellido}"
        
        return nombre_persona_titular

    def get_agno_radicado(self, obj):
        return obj['agno_radicado']
    
    def get_fecha_radicado(self, obj):
        return obj['fecha_radicado']
    
    class Meta:
        model = T262Radicados
        fields = [
            'nombre_tipo_radicado',
            'numero_radicado_completo',
            'titular',
            'asunto',
            'fecha_radicado',
            'agno_radicado'
        ]