from estaciones.models.estaciones_models import Datos
from rest_framework import serializers


class DatosSerializer(serializers.ModelSerializer):

    # nombre_estacion = serializers.ReadOnlyField(source='id_estacion.nombre_estacion', default=None)

    class Meta:
        model = Datos
        fields = '__all__'

class DatosSerializerNombre(serializers.ModelSerializer):

    nombre_estacion = serializers.ReadOnlyField(source='id_estacion.nombre_estacion', default=None)

    class Meta:
        model = Datos
        fields = '__all__'
