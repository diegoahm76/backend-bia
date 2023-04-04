from estaciones.models.estaciones_models import HistorialAlarmasEnviadasEstacion, AlertasEquipoEstacion
from rest_framework import serializers

class HistorialAlarmasEnviadasEstacionSerializer(serializers.ModelSerializer):

    nombre_estacion = serializers.ReadOnlyField(source='id_estacion.nombre_estacion', default=None)
    
    class Meta:
        model=HistorialAlarmasEnviadasEstacion
        fields='__all__'

class AlertasEquipoEstacionSerializer(serializers.ModelSerializer):

    nombre_estacion = serializers.ReadOnlyField(source='id_estacion.nombre_estacion', default=None)
    
    class Meta:
        model=AlertasEquipoEstacion
        fields='__all__'
