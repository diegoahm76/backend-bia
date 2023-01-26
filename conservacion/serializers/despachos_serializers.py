from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from conservacion.models.despachos_models import (
    DespachoEntrantes,
    ItemsDespachoEntrante,
    DistribucionesItemDespachoEntrante
)
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

class DespachosEntrantesSerializer(serializers.ModelSerializer):
    numero_despacho_consumo = serializers.ReadOnlyField(source='id_despacho_consumo_alm.numero_despacho_consumo', default=None)
    
    class Meta:
        model = DespachoEntrantes
        fields = '__all__'
        
class ItemsDespachosEntrantesSerializer(serializers.ModelSerializer):
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    tipo_documento = serializers.ReadOnlyField(source='id_entrada_alm_del_bien.id_tipo_entrada.nombre', default=None)
    numero_documento = serializers.ReadOnlyField(source='id_entrada_alm_del_bien.numero_entrada_almacen', default=None)
    cantidad_restante = serializers.IntegerField(read_only=True, default=None)
    class Meta:
        model = ItemsDespachoEntrante
        fields = '__all__'
        
class DistribucionesItemDespachoEntranteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistribucionesItemDespachoEntrante
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=DistribucionesItemDespachoEntrante.objects.all(),
                fields=['id_item_despacho_entrante', 'id_vivero'],
                message='El item despacho entrante y el vivero deben ser una pareja única'
            )
        ]
        
class DistribucionesItemPreDistribuidoSerializer(serializers.ModelSerializer):
    vivero_nombre=serializers.ReadOnlyField(source='id_vivero.nombre', default=None)
    nombre_bien=serializers.ReadOnlyField(source='id_item_despacho_entrante.id_bien.nombre', default=None)
    codigo_bien=serializers.ReadOnlyField(source='id_item_despacho_entrante.id_bien.codigo_bien', default=None)
    unidad_medida=serializers.ReadOnlyField(source='id_item_despacho_entrante.id_bien.id_unidad_medida.abreviatura', default=None)
    id_bien=serializers.ReadOnlyField(source='id_item_despacho_entrante.id_bien.id_bien', default=None)
    
    class Meta:
        model = DistribucionesItemDespachoEntrante
        fields = ['id_distribucion_item_despacho_entrante','id_vivero','id_bien','cantidad_asignada','cod_etapa_lote_al_ingresar','id_item_despacho_entrante','vivero_nombre','unidad_medida','codigo_bien','nombre_bien']
      