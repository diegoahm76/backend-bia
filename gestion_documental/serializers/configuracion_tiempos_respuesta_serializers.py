from rest_framework import serializers

from gestion_documental.models.configuracion_tiempos_respuesta_models import ConfiguracionTiemposRespuesta


class ConfiguracionTiemposRespuestaGetSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = ConfiguracionTiemposRespuesta
        fields = '__all__'

class ConfiguracionTiemposRespuestaPutSerializer(serializers.ModelSerializer):
    id_configuracion_tiempo_respuesta = serializers.ReadOnlyField()
    nombre_configuracion = serializers.ReadOnlyField()
    class Meta:
        model = ConfiguracionTiemposRespuesta
        fields = '__all__'