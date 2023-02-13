from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from conservacion.models.cuarentena_models import (
    BajasVivero,
    ItemsBajasVivero
)
from almacen.models.bienes_models import (
    CatalogoBienes
)
from conservacion.models.inventario_models import (
    InventarioViveros
)
from conservacion.models.viveros_models import (
    Vivero
)

class BajasViveroPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BajasVivero
        fields = '__all__'

class ItemsBajasActualizarViveroPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemsBajasVivero
        fields = (
            'observaciones',
            'cantidad_baja',
            'nro_posicion'
        )
            
        
class ItemsBajasViveroPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemsBajasVivero
        exclude = (
            'agno_lote',
            'nro_lote',
            'cod_etapa_lote',
            'consec_cuaren_por_lote_etapa'
            )

class ViveroBajasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vivero
        fields = (
            'id_vivero',
            'nombre',
        )

class CatalogoBienesBajasSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogoBienes
        fields = (
            'id_bien',
            'nombre',
            'es_semilla_vivero',
            'cod_tipo_elemento_vivero'
        )
    
class GetBajaByNumeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = BajasVivero
        fields = (
            'tipo_baja',
            'nro_baja_por_tipo',
            'fecha_baja',
            'baja_anulado',
            'justificacion_anulacion',
            'fecha_anulacion',
            'id_persona_anula'
        )

class CatalogoBienesSerializerBusquedaAvanzada(serializers.ModelSerializer):
    unidad_medida = serializers.ReadOnlyField(source='id_unidad_medida.abreviatura')
    saldo_disponible = serializers.IntegerField(default=0)
    tipo_bien = serializers.SerializerMethodField()
    
    def get_tipo_bien(self, obj):
        if obj.cod_tipo_elemento_vivero == 'HE':
            cod_tipo_elemento_vivero = 'Herramienta'
        elif obj.cod_tipo_elemento_vivero == 'IN':
            cod_tipo_elemento_vivero = 'Insumo'
        elif obj.cod_tipo_elemento_vivero == 'MV' and obj.es_semilla_vivero == True:
            cod_tipo_elemento_vivero = 'Semillas'
        return cod_tipo_elemento_vivero
    
    class Meta:
        model = CatalogoBienes
        fields = (
            'id_bien',
            'codigo_bien',
            'nombre',
            'tipo_bien',
            'saldo_disponible',
            'unidad_medida'
        )