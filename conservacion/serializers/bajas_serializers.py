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
        
class ItemsBajasViveroGetSerializer(serializers.ModelSerializer):
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    nombre = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    
    class Meta:
        model = ItemsBajasVivero
        fields = '__all__'

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
    nombre_vivero = serializers.ReadOnlyField(source='id_vivero.nombre', default=None)
    nombre_persona_anula = serializers.SerializerMethodField()
    nombre_persona_baja = serializers.SerializerMethodField()
    
    def get_nombre_persona_anula(self, obj):
        nombre_persona_anula = None
        if obj.id_persona_anula:
            nombre_list = [obj.id_persona_anula.primer_nombre, obj.id_persona_anula.segundo_nombre,
                            obj.id_persona_anula.primer_apellido, obj.id_persona_anula.segundo_apellido]
            nombre_persona_anula = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_anula = nombre_persona_anula if nombre_persona_anula != "" else None
        return nombre_persona_anula
    
    def get_nombre_persona_baja(self, obj):
        nombre_persona_baja = None
        nombre_list = [obj.id_persona_baja.primer_nombre, obj.id_persona_baja.segundo_nombre,
                        obj.id_persona_baja.primer_apellido, obj.id_persona_baja.segundo_apellido]
        nombre_persona_baja = ' '.join(item for item in nombre_list if item is not None)
        nombre_persona_baja = nombre_persona_baja if nombre_persona_baja != "" else None
        return nombre_persona_baja
    
    class Meta:
        model = BajasVivero
        fields = [
            'id_baja',
            'tipo_baja',
            'nro_baja_por_tipo',
            'fecha_baja',
            'baja_anulado',
            'justificacion_anulacion',
            'fecha_anulacion',
            'id_persona_anula',
            'nombre_persona_anula',
            'id_vivero',
            'nombre_vivero',
            'id_persona_baja',
            'nombre_persona_baja',
            'motivo',
            'ruta_archivo_soporte'
        ]

class CatalogoBienesSerializerBusquedaAvanzada(serializers.ModelSerializer):
    unidad_medida = serializers.ReadOnlyField(source='id_unidad_medida.abreviatura')
    saldo_disponible = serializers.IntegerField(default=0)
    tipo_bien = serializers.SerializerMethodField()
    
    def get_tipo_bien(self, obj):
        cod_tipo_elemento_vivero = None
        if obj.cod_tipo_elemento_vivero == 'HE':
            cod_tipo_elemento_vivero = 'Herramienta'
        elif obj.cod_tipo_elemento_vivero == 'IN':
            cod_tipo_elemento_vivero = 'Insumo'
        # elif obj.cod_tipo_elemento_vivero == 'MV' and obj.es_semilla_vivero == True:
        elif obj.cod_tipo_elemento_vivero == 'MV':
            cod_tipo_elemento_vivero = 'Material Vegetal'
        return cod_tipo_elemento_vivero
    
    class Meta:
        model = CatalogoBienes
        fields = (
            'id_bien',
            'codigo_bien',
            'nombre',
            'cod_tipo_elemento_vivero',
            'tipo_bien',
            'es_semilla_vivero',
            'saldo_disponible',
            'unidad_medida'
        )