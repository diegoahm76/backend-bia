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
from conservacion.models.inventario_models import (
    InventarioViveros
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
            'id_siembra',
        )
    
class CreateSiembraInventarioViveroSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventarioViveros
        fields = (
            'id_vivero',
            'id_bien',
            'agno_lote',
            'cod_etapa_lote',
            'es_produccion_propia_lote',
            'fecha_ingreso_lote_etapa',
            'id_siembra_lote_germinacion',
            'siembra_lote_cerrada',
        )

class GetNumeroLoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Siembras
        fields = 'nro_lote'

class GetBienSembradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogoBienes
        fields = '__all__'