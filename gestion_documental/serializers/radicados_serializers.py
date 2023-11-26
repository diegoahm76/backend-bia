from rest_framework import serializers
from gestion_documental.choices.tipo_radicado_choices import TIPOS_RADICADO_CHOICES

from gestion_documental.models.radicados_models import T262Radicados
from transversal.models.personas_models import Personas

class RadicadosImprimir(serializers.ModelSerializer):
    nombre_tipo_radicado = serializers.SerializerMethodField()
    numero_radicado_completo = serializers.SerializerMethodField()
    asunto = serializers.SerializerMethodField()
    titular = serializers.SerializerMethodField()
    fecha_radicado = serializers.SerializerMethodField()
    agno_radicado = serializers.SerializerMethodField()
    

    def get_nombre_tipo_radicado(self, obj):
        nombre_tipo_radicado = ''
        for choice in TIPOS_RADICADO_CHOICES:
            if choice[0] == obj['radicado'].cod_tipo_radicado:
                nombre_tipo_radicado = choice[1]
                break
        
        return nombre_tipo_radicado
    
    def get_numero_radicado_completo(self, obj):
        radicado = obj['radicado']
        return f"{radicado.prefijo_radicado} {radicado.agno_radicado} {radicado.nro_radicado}"

    def get_asunto(self, obj):
        return obj['pqrsdf'].asunto
            
    def get_titular(self, obj):
        persona_titular = Personas.objects.filter(id_persona = obj['pqrsdf'].id_persona_titular_id).first()
        return f"{persona_titular.primer_nombre} {persona_titular.segundo_nombre} {persona_titular.primer_apellido} {persona_titular.segundo_apellido}"

    def get_agno_radicado(self, obj):
        return obj['radicado'].agno_radicado
    
    def get_fecha_radicado(self, obj):
        return obj['radicado'].fecha_radicado
    
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