from almacen.models.generics_models import UnidadesMedida
from seguridad.serializers.personas_serializers import PersonasSerializer
from almacen.models.generics_models import Magnitudes
from rest_framework import serializers
from almacen.models.generics_models import Marcas,Bodegas,PorcentajesIVA
from almacen.models.bienes_models import CatalogoBienes
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

class CatalogoBienesSerializer(serializers.ModelSerializer):
    class Meta:
        model= CatalogoBienes
        fields='__all__'