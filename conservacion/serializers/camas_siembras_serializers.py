from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from conservacion.models.siembras_models import (
    Siembras,
    ConsumosSiembra,
    CamasGerminacionVivero,
    CamasGerminacionViveroSiembra,
    CambiosDeEtapa
)
from almacen.models.bienes_models import (
    CatalogoBienes
)
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

class CamasGerminacionPost(serializers.ModelSerializer):
    class Meta:
        model = CamasGerminacionVivero
        fields = '__all__'

class GetCamasGerminacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CamasGerminacionVivero
        fields = '__all__'

class CreateSiembrasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Siembras
        exclude = (
            'id_cama_germinacion_vivero',
        )

class GetNumeroLoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Siembras
        fields = 'nro_lote'

class GetBienSembradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogoBienes
        fields = '__all__'