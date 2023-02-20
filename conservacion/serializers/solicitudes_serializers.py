from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from conservacion.models.solicitudes_models import (
    SolicitudesViveros,
    ItemSolicitudViveros
)
from almacen.models.organigrama_models import (
    UnidadesOrganizacionales
)


class GetNumeroConsecutivoSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesViveros
        fields = '__all__'

class GetSolicitudByNumeroSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesViveros
        fields = '__all__'


class GetUnidadOrganizacionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadesOrganizacionales
        fields = '__all__'


class CreateSolicitudViverosSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesViveros
        fields = '__all__'