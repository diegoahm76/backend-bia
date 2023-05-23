from estaciones.models.estaciones_models import HistorialAlarmasEnviadasEstacion, AlertasEquipoEstacion, PersonasEstaciones
from rest_framework import serializers

class HistorialAlarmasEnviadasEstacionSerializer(serializers.ModelSerializer):
    nombre_persona_envio = serializers.SerializerMethodField()
    nombre_estacion = serializers.ReadOnlyField(source='id_estacion.nombre_estacion', default=None)
    
    def get_nombre_persona_envio(self, obj):
        nombre_persona_envio = None

        persona = obj.id_persona_estacion
        if persona:
            nombre_list = [persona.primer_nombre, persona.segundo_nombre, persona.primer_apellido, persona.segundo_apellido]
            nombre_persona_envio = ' '.join(item for item in nombre_list if item is not None)
        return nombre_persona_envio
    
    class Meta:
        model=HistorialAlarmasEnviadasEstacion
        fields='__all__'

class AlertasEquipoEstacionSerializer(serializers.ModelSerializer):

    nombre_estacion = serializers.ReadOnlyField(source='id_estacion.nombre_estacion', default=None)
    
    class Meta:
        model=AlertasEquipoEstacion
        fields='__all__'
