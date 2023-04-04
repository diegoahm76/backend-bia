from estaciones.models.estaciones_models import Migracion
from rest_framework import serializers


class MigracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Migracion
        fields = '__all__'
