from estaciones.models.estaciones_models import Migracion
from rest_framework import serializers


class MigracionSerializer(serializers.ModelSerializer):
    sensor1_data = serializers.CharField()
    sensor2_data = serializers.CharField()
    fecha = serializers.DateField()

    class Meta:
        model = Migracion
        fields = ('id_migracion_estacion', 'id_estacion', 'nombre', 'fecha', 'sensor1_data', 'sensor2_data')
