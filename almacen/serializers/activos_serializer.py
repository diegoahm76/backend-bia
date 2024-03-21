from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen, ItemEntradaAlmacen
from almacen.models.inventario_models import Inventario, TiposEntradas
from almacen.models.generics_models import Marcas, UnidadesMedida
from almacen.models.activos_models import AnexosDocsAlma, BajaActivos, ItemsBajaActivos, ArchivosDigitales, ItemsSolicitudActivos, SalidasEspecialesArticulos, SolicitudesActivos
from transversal.models.base_models import ClasesTerceroPersona
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
        fields = '__all__' 

class AnexosOpcionalesDocsAlmaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnexosDocsAlma
        fields = '__all__'  

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


class BusquedaSolicitudActivoSerializer(serializers.ModelSerializer):
    numero_activos = serializers.SerializerMethodField()  # Campo adicional para el cálculo del número de activos
    primer_nombre_persona_solicita = serializers.ReadOnlyField(source='id_persona_solicita.primer_nombre', default=None)
    primer_apellido_persona_solicita = serializers.ReadOnlyField(source='id_persona_solicita.primer_apellido', default=None)
    primer_nombre_funcionario_resp_unidad = serializers.ReadOnlyField(source='id_funcionario_resp_unidad.primer_nombre', default=None)
    primer_apellido_funcionario_resp_unidad = serializers.ReadOnlyField(source='id_funcionario_resp_unidad.primer_apellido', default=None)

    

    class Meta:
        model = SolicitudesActivos
        fields = (
            'id_solicitud_activo',
            'fecha_solicitud',
            'motivo',
            'estado_solicitud',
            'id_persona_solicita',
            'primer_nombre_persona_solicita',
            'primer_apellido_persona_solicita',
            'id_funcionario_resp_unidad',
            'primer_nombre_funcionario_resp_unidad',
            'primer_apellido_funcionario_resp_unidad',
            'numero_activos',  # Campo adicional para el cálculo del número de activos
        )

    def get_numero_activos(self, instance):
        # Obtener el número de activos relacionados con esta solicitud
        return ItemsSolicitudActivos.objects.filter(id_solicitud_activo=instance).count()
    


class ClasesTerceroPersonaSerializer(serializers.ModelSerializer):
    primer_nombre = serializers.ReadOnlyField(source='id_persona.primer_nombre', default=None)
    segundo_nombre = serializers.ReadOnlyField(source='id_persona.segundo_nombre', default=None)
    primer_apellido = serializers.ReadOnlyField(source='id_persona.primer_apellido', default=None)
    segundo_apellido = serializers.ReadOnlyField(source='id_persona.segundo_apellido', default=None)
    tipo_documento = serializers.ReadOnlyField(source='id_persona.tipo_documento.cod_tipo_documento', default=None)
    numero_documento = serializers.ReadOnlyField(source='id_persona.numero_documento', default=None)
    tipo_persona = serializers.ReadOnlyField(source='id_persona.tipo_persona', default=None)
    nombre_clase_tercero = serializers.ReadOnlyField(source='id_clase_tercero.nombre', default=None)
    class Meta:
        model = ClasesTerceroPersona
        fields = '__all__'


class EntradasAlmacenSerializer(serializers.ModelSerializer):
    tipo_entrada = serializers.SerializerMethodField()
    consecutivo = serializers.IntegerField(source='numero_entrada_almacen')
    fecha_registro = serializers.DateTimeField(source='fecha_real_registro')

    class Meta:
        model = EntradasAlmacen
        fields = '__all__'

    def get_tipo_entrada(self, obj):
        tipo_entrada_id = obj.id_tipo_entrada.cod_tipo_entrada
        tipo_entrada = TiposEntradas.objects.filter(cod_tipo_entrada=tipo_entrada_id).values('nombre').first()
        return tipo_entrada['nombre'] if tipo_entrada else None



class SalidasEspecialesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalidasEspecialesArticulos
        fields = '__all__'