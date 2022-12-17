from almacen.models.generics_models import UnidadesMedida
from seguridad.serializers.personas_serializers import PersonasSerializer
from almacen.models.generics_models import Magnitudes
from rest_framework import serializers
from almacen.models.generics_models import Marcas,Bodegas,PorcentajesIVA
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from almacen.models.inventario_models import Inventario

class SerializerUpdateInventariosActivosFijos(serializers.ModelSerializer):
    valor_total_item = serializers.FloatField(source='valor_ingreso')
    cod_estado = serializers.CharField(source='cod_estado_activo')
    class Meta:
        model= Inventario
        fields = ['id_bodega', 'valor_total_item', 'cod_estado']