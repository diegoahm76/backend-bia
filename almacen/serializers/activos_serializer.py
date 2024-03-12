from almacen.models.bienes_models import CatalogoBienes, ItemEntradaAlmacen
from almacen.models.inventario_models import Inventario
from almacen.models.activos_models import AnexosDocsAlma, BajaActivos, ItemsBajaActivos
from rest_framework import serializers



class InventarioSerializer(serializers.ModelSerializer):
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    identificador_bien = serializers.ReadOnlyField(source='id_bien.doc_identificador_nro', default=None)
    nombre_marca = serializers.ReadOnlyField(source='id_bien.id_marca.nombre', default=None)
    valor_unitario = serializers.SerializerMethodField()
    id_item_entrada_almacen = serializers.SerializerMethodField()

    def get_valor_unitario(self, obj):
        id_bien = obj.id_bien
        item_entrada = ItemEntradaAlmacen.objects.filter(id_bien=id_bien).first()
        valor_unitario = item_entrada.valor_unitario if item_entrada else None
        return valor_unitario

    def get_id_item_entrada_almacen(self, obj):
        id_bien = obj.id_bien
        item_entrada = ItemEntradaAlmacen.objects.filter(id_bien=id_bien).first()
        id_item_entrada_almacen = item_entrada.id_item_entrada_almacen if item_entrada else None
        return id_item_entrada_almacen

    class Meta:
        model = Inventario
        fields = '__all__'


class RegistrarBajaCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = BajaActivos
        fields = '__all__'


class RegistrarBajaBienesCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ItemsBajaActivos
        fields = '__all__'


class RegistrarBajaAnexosCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnexosDocsAlma
        fields = '__all__'
        