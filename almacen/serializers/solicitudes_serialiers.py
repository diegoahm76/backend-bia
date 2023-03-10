from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from almacen.models.solicitudes_models import (
    SolicitudesConsumibles,
    ItemsSolicitudConsumible
)

class CrearSolicitudesPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesConsumibles
        fields = '__all__'

class CrearItemsSolicitudConsumiblePostSerializer(serializers.ModelSerializer):
    #nro_posicion = serializers.IntegerField(validators=[UniqueValidator(queryset=ItemsSolicitudConsumible.objects.all())])
    class Meta:
        model = ItemsSolicitudConsumible
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ItemsSolicitudConsumible.objects.all(),
                fields=['id_bien', 'id_solicitud_consumibles'],
                message='No puede solicitar más de una vez el mismo bien en esta solicitud'
            )
        ]

