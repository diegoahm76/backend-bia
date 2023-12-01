from rest_framework import serializers

from recaudo.models.base_models import RegistrosConfiguracion



class RegistrosConfiguracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrosConfiguracion
        fields = '__all__'
