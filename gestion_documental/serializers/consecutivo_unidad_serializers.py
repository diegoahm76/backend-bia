from rest_framework import serializers

from gestion_documental.models.consecutivo_unidad_models import ConfigTipoConsecAgno

class ConfigTipoConsecAgnoGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigTipoConsecAgno
        fields = '__all__'