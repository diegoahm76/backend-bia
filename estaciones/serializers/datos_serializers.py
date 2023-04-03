from estaciones.models.estaciones_models import Datos
from rest_framework import serializers

class DatosSerializer(serializers.ModelSerializer):

    class Meta:
        model=Datos
        fields='__all__'
