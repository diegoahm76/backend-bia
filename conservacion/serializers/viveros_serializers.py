from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from conservacion.models.viveros_models import (
    Vivero,
    HistorialAperturaViveros,
    HistorialCuarentenaViveros
)

class ViveroSerializer(serializers.Serializer):
    class Meta:
        model = Vivero
        fields = '__all__'


class ActivarDesactivarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vivero
        fields = ['justificacion_apertura', 'fecha_ultima_apertura', 'en_funcionamiento', 'item_ya_usado', 'id_persona_abre']
        extra_kwargs = {
            'justificacion_apertura': {'required': True},
        }


