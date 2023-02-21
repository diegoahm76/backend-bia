from rest_framework import serializers
from conservacion.models.mezclas_models import Mezclas, PreparacionMezclas, ItemsPreparacionMezcla
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from almacen.models.bienes_models import (
    CatalogoBienes
)
from conservacion.models.inventario_models import (
    InventarioViveros
)

class MezclasSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Mezclas
        fields = '__all__'

class PreparacionMezclasSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PreparacionMezclas
        fields = '__all__'

class ItemsPreparacionMezclasSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ItemsPreparacionMezcla
        fields = '__all__'

class CatalogoBienesInsumoSerializer(serializers.ModelSerializer):
    saldo_disponible = serializers.IntegerField(default=0)
    unidad_medida = serializers.ReadOnlyField(source='id_unidad_medida.abreviatura')
    
    class Meta:
        model = CatalogoBienes
        fields = (
            'id_bien',
            'codigo_bien',
            'nombre',
            'saldo_disponible',
            'unidad_medida'
        )

class CreateMezclaInventarioViveroSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventarioViveros
        fields = '__all__'
        
class ItemsPreparacionMezclaActualizarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemsPreparacionMezcla
        fields = (
            'observaciones',
            'cantidad_usada',
            'nro_posicion'
        )

class MezclasSerializador(serializers.ModelSerializer):
    class Meta:
        fields = ['nombre','id_unidad_medida']
        model = Mezclas
        extra_kwargs = {
            'nombre': {'required': True},
            'id_unidad_medida': {'required': True}
        }
        
class MezclasPutSerializador(serializers.ModelSerializer):
    class Meta:
        fields = ['nombre','id_unidad_medida','item_activo']
        model = Mezclas
        
class MezclasGetListSerializador(serializers.ModelSerializer):
    unidad_medida = serializers.ReadOnlyField(source='id_unidad_medida.abreviatura')
    class Meta:
        fields = '__all__'
        model = Mezclas