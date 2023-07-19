from rest_framework import serializers
from recaudo.models.garantias_models import Garantias, RolesGarantias


class RolesGarantiasSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolesGarantias
        fields = '__all__'


class GarantiasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garantias
        fields = '__all__'


