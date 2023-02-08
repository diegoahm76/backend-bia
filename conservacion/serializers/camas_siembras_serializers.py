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
        fields = '__all__'
    
class CreateSiembraInventarioViveroSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventarioViveros
        fields = (
            'id_vivero',
            'id_bien',
            'nro_lote',
            'agno_lote',
            'cod_etapa_lote',
            'es_produccion_propia_lote',
            'fecha_ingreso_lote_etapa',
            'id_siembra_lote_germinacion',
            'siembra_lote_cerrada',
        )

class CreateBienesConsumidosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumosSiembra
        fields = '__all__'

class GetNumeroLoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Siembras
        fields = 'nro_lote'

class GetBienSembradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogoBienes
        fields = '__all__'


class GetSiembraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Siembras
        fields = (
            'id_siembra',
            'id_vivero',
            'id_bien_sembrado',
            'agno_lote',
            'nro_lote',
            'fecha_siembra',
            'fecha_registro',
            'observaciones',
            'distancia_entre_semillas',
            'id_persona_siembra',
            'ruta_archivo_soporte'
        )


class GetBienesPorConsumirSerializer(serializers.ModelSerializer):
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    tipo_bien = serializers.SerializerMethodField()
    unidad_disponible = serializers.ReadOnlyField(source='id_bien.id_unidad_medida.nombre', default=None)
    cantidad_disponible_bien = serializers.IntegerField(default=None)

    def get_tipo_bien(self, obj):
        if obj.id_bien.cod_tipo_elemento_vivero == 'HE':
            cod_tipo_elemento_vivero = 'Herramienta'
        elif obj.id_bien.cod_tipo_elemento_vivero == 'IN':
            cod_tipo_elemento_vivero = 'Insumo'
        elif obj.id_bien.cod_tipo_elemento_vivero == 'MV' and obj.id_bien.es_semilla_vivero == True:
            cod_tipo_elemento_vivero = 'Semillas'
        return cod_tipo_elemento_vivero

    class Meta:
        model = InventarioViveros
        fields = (
            'id_inventario_vivero',
            'cantidad_entrante',
            'id_vivero',
            'id_bien',
            'codigo_bien',
            'nombre_bien',
            'tipo_bien',
            'cantidad_disponible_bien',
            'unidad_disponible'
        )


class UpdateSiembraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Siembras
        fields = (
            'observaciones',
            'distancia_entre_semillas',
            'id_persona_siembra'
        )

class UpdateBienesConsumidosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumosSiembra
        fields = '__all__'


class DeleteSiembraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Siembras
        fields = '__all__'


class DeleteBienesConsumidosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Siembras
        fields = '__all__'

class GetBienesConsumidosSiembraSerializer(serializers.ModelSerializer):
    codigo_bien = serializers.ReadOnlyField(source='id_bien_consumido.codigo_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien_consumido.nombre', default=None)
    tipo_bien = serializers.ReadOnlyField(source='id_bien_consumido.cod_tipo_elemento_vivero', default=None)
    class Meta:
        model = ConsumosSiembra
        fields = (
            'id_consumo_siembra',
            'id_siembra',
            'id_bien_consumido',
            'cantidad',
            'observaciones',
            'id_mezcla_consumida',
            'codigo_bien',
            'nombre_bien',
            'tipo_bien'
        )


class GetSiembrasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Siembras
        fields = '__all__'