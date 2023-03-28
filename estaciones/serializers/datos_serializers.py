from estaciones.models.estaciones_models import Datos, DatosGuamal
from rest_framework import serializers

class DatosSerializer(serializers.ModelSerializer):

    class Meta:
        model=Datos
        fields='__all__'

class DatosSerializerGuamal(serializers.ModelSerializer):

    class Meta:
        model=DatosGuamal
        fields='__all__'