from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from conservacion.models.siembras_models import (
    Siembras,
    ConsumosSiembra,
    CamasGerminacionVivero,
    CamasGerminacionViveroSiembra,
    CambiosDeEstapa
)
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

class CamasGerminacionPost(serializers.ModelSerializer):
    class Meta:
        model = CamasGerminacionVivero
        fields = '__all__'