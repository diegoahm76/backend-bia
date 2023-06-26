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
        fields = (
            'cuarentena_abierta',
            'cuarentena_anulada',
            'justificacion_anulacion',
            'fecha_anulacion',
            'cuarentena_abierta',
            'id_persona_anula'
        )
        extra_kwargs = {
            'justificacion_anulacion': {'required': True},
            'cuarentena_abierta': {'required': True},
            'cuarentena_anulada': {'required': True}
        }


class UpdateIngresoCuarentenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuarentenaMatVegetal
        fields = (
            'cantidad_cuarentena',
            'descrip_corta_diferenciable',
            'motivo',
            'ruta_archivo_soporte'
        )

class GetIngresoCuarentenaSerializer(serializers.ModelSerializer):
    saldo_disponible = serializers.SerializerMethodField()
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    
    def get_saldo_disponible(self, obj):
        inventario_vivero = InventarioViveros.objects.filter(id_bien=obj.id_bien, id_vivero=obj.id_vivero, agno_lote=obj.agno_lote, nro_lote=obj.nro_lote, cod_etapa_lote=obj.cod_etapa_lote, id_siembra_lote_germinacion=None).first()
        
        porc_cuarentena_lote_germinacion = inventario_vivero.porc_cuarentena_lote_germinacion if inventario_vivero.porc_cuarentena_lote_germinacion else 0
        cantidad_entrante = inventario_vivero.cantidad_entrante if inventario_vivero.cantidad_entrante else 0
        cantidad_bajas = inventario_vivero.cantidad_bajas if inventario_vivero.cantidad_bajas else 0
        cantidad_traslados_lote_produccion_distribucion = inventario_vivero.cantidad_traslados_lote_produccion_distribucion if inventario_vivero.cantidad_traslados_lote_produccion_distribucion else 0
        cantidad_salidas = inventario_vivero.cantidad_salidas if inventario_vivero.cantidad_salidas else 0
        cantidad_lote_cuarentena = inventario_vivero.cantidad_lote_cuarentena if inventario_vivero.cantidad_lote_cuarentena else 0
        
        saldo_disponible = 0
        
        if inventario_vivero.cod_etapa_lote == 'G':
            saldo_disponible = 100 - porc_cuarentena_lote_germinacion
        if inventario_vivero.cod_etapa_lote == 'P':
            saldo_disponible = cantidad_entrante - cantidad_bajas - cantidad_traslados_lote_produccion_distribucion - cantidad_salidas - cantidad_lote_cuarentena
        if inventario_vivero.cod_etapa_lote == 'D':
            saldo_disponible = cantidad_entrante - cantidad_bajas - cantidad_salidas - cantidad_lote_cuarentena
        
        return saldo_disponible
    
    class Meta:
        model = CuarentenaMatVegetal
        fields = '__all__'