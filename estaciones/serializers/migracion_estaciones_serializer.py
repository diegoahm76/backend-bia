from estaciones.models.estaciones_models import Migracion
from rest_framework import serializers


class MigracionSerializer(serializers.ModelSerializer):
    temperatura = serializers.CharField(source='sensor1_data')
    temperatura_max = serializers.CharField(source='sensor2_data')
    temperatura_min = serializers.CharField(source='sensor3_data')
    humedad_relativa = serializers.CharField(source='sensor4_data')
    punto_de_rocio = serializers.CharField(source='sensor5_data')
    fecha = serializers.DateField()
    presion_atm_abs = serializers.CharField(source='sensor6_data')
    presion_atm_rel = serializers.CharField(source='sensor7_data')
    intensidad = serializers.CharField(source='sensor8_data')
    precipitacion = serializers.CharField(source='sensor9_data')
    nivel_agua = serializers.CharField(source='sensor10_data')
    nivel_agua_max = serializers.CharField(source='sensor11_data')
    nivel_agua_min = serializers.CharField(source='sensor12_data')
    velocidad_rio = serializers.CharField(source='sensor13_data')
    caudal = serializers.CharField(source='sensor14_data')
    voltaje  = serializers.CharField(source='sensor15_data')

    class Meta:
        model = Migracion
        fields = ('id_migracion_estacion', 'id_estacion', 'nombre',
                  'fecha', 'temperatura', 'temperatura_max', 'temperatura_min', 'humedad_relativa', 'punto_de_rocio', 'presion_atm_abs', 'presion_atm_rel', 'intensidad', 'precipitacion', 'nivel_agua', 'nivel_agua_max' , 'nivel_agua_min' , 'velocidad_rio', 'caudal', 'voltaje')
