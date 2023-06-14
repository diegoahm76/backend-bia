from rest_framework import serializers

from transversal.models.entidades_models import ConfiguracionEntidad

class ConfiguracionEntidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionEntidad
        fields = '__all__'
