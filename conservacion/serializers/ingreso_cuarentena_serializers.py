from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from conservacion.models.siembras_models import (
    Siembras,
    ConsumosSiembra,
    CamasGerminacionVivero,
    CamasGerminacionViveroSiembra,
    CambiosDeEtapa
)
from conservacion.models.cuarentena_models import (
    CuarentenaMatVegetal
)
from almacen.models.bienes_models import (
    CatalogoBienes
)
from conservacion.models.inventario_models import (
    InventarioViveros
)
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

class GetLotesEtapaSerializer(serializers.ModelSerializer):
    saldo_disponible = serializers.IntegerField(default=0)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    class Meta:
        model = InventarioViveros
        fields = (
            'id_inventario_vivero',
            'id_vivero',
            'id_bien',
            'agno_lote',
            'nro_lote',
            'cod_etapa_lote',
            'id_siembra_lote_germinacion',
            'id_mezcla',
            'saldo_disponible',
            'codigo_bien',
            'nombre_bien'
        )


class CreateIngresoCuarentenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuarentenaMatVegetal
        fields = '__all__'

class AnularIngresoCuarentenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuarentenaMatVegetal
        fields = '__all__'