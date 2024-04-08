


from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from tramites.models.tramites_models import AnexosTramite, RespuestasRequerimientos


class RespuestaRequerimientoOPACreateserializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestasRequerimientos
        fields = '__all__'


class AnexosTramiteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnexosTramite
        fields = '__all__'