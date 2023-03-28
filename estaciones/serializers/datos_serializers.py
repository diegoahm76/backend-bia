from estaciones.models.estaciones_models import Datos, DatosGuamal, DatosOcoa, DatosGuayuriba, DatosGaitan
from rest_framework import serializers

class DatosSerializer(serializers.ModelSerializer):

    class Meta:
        model=Datos
        fields='__all__'

class DatosSerializerGuamal(serializers.ModelSerializer):

    class Meta:
        model=DatosGuamal
        fields='__all__'

class DatosSerializerOcoa(serializers.ModelSerializer):

    class Meta:
        model=DatosOcoa
        fields='__all__'

class DatosSerializerGuayutiba(serializers.ModelSerializer):

    class Meta:
        model=DatosGuayuriba
        fields='__all__'

class DatosSerializerGaitan(serializers.ModelSerializer):

    class Meta:
        model=DatosGaitan
        fields='__all__'