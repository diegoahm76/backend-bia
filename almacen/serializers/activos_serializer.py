from almacen.models.bienes_models import CatalogoBienes, ItemEntradaAlmacen
from almacen.models.inventario_models import Inventario
from almacen.models.generics_models import Marcas, UnidadesMedida
from almacen.models.activos_models import AnexosDocsAlma, BajaActivos, ItemsBajaActivos, ArchivosDigitales, ItemsSolicitudActivos, SolicitudesActivos
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
        
class AnexosDocsAlmaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnexosDocsAlma
        fields = '__all__'  # Incluir todos los campos del modelo AnexosDocsAlma

class ArchivosDigitalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivosDigitales
        fields = '__all__'  # Agrega aquí los campos que necesites para los archivos digitales

class BajaActivosSerializer(serializers.ModelSerializer):
    class Meta:
        model = BajaActivos
        fields = ('id_baja_activo', 'consecutivo_por_baja', 'concepto', 'fecha_baja', 'cantidad_activos_baja', 'id_persona_registro_baja', 'id_uni_org_registro_baja')



class AnexosDocsAlmaSerializer(serializers.ModelSerializer):
    id_baja_activo = BajaActivosSerializer()
    id_archivo_digital = ArchivosDigitalesSerializer()  # Agrega el serializador para los archivos digitales

    class Meta:
        model = AnexosDocsAlma
        fields = ('id_anexo_doc_alma', 'id_baja_activo', 'id_salida_espec_arti', 'nombre_anexo', 'nro_folios', 'descripcion_anexo', 'fecha_creacion_anexo', 'id_archivo_digital')


class ItemsBajaActivosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemsBajaActivos
        fields = '__all__'


class SolicitudesActivosSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesActivos
        fields = '__all__'

    
    
class ItemsSolicitudActivosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemsSolicitudActivos
        fields = '__all__'


class UnidadesMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadesMedida
        fields = '__all__'


class ItemSolicitudActivosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemsSolicitudActivos
        fields = '__all__'

class DetalleSolicitudActivosSerializer(serializers.ModelSerializer):
    items = ItemSolicitudActivosSerializer(many=True, read_only=True)

    class Meta:
        model = SolicitudesActivos
        fields = '__all__'
