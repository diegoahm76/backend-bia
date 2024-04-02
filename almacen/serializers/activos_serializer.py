from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen, ItemEntradaAlmacen
from almacen.models.inventario_models import Inventario, TiposEntradas
from almacen.models.generics_models import Bodegas, Marcas, UnidadesMedida
from almacen.models.activos_models import ActivosDevolucionados, AnexosDocsAlma, BajaActivos, DespachoActivos, DevolucionActivos, ItemsBajaActivos, ArchivosDigitales, ItemsDespachoActivos, ItemsSolicitudActivos, SalidasEspecialesArticulos, SolicitudesActivos
from transversal.models.base_models import ClasesTerceroPersona
from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen, Bodegas, EstadosArticulo
from almacen.models.hoja_de_vida_models import HojaDeVidaComputadores, HojaDeVidaOtrosActivos, HojaDeVidaVehiculos, DocumentosVehiculo
from seguridad.models import Personas
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
    primer_nombre_persona_solicita = serializers.ReadOnlyField(source='id_persona_solicita.primer_nombre', default=None)
    primer_apellido_persona_solicita = serializers.ReadOnlyField(source='id_persona_solicita.primer_apellido', default=None)
    tipo_documento_persona_solicita = serializers.ReadOnlyField(source='id_persona_solicita.tipo_documento.cod_tipo_documento', default=None)
    numero_documento_persona_solicita = serializers.ReadOnlyField(source='id_persona.numero_documento', default=None)
    #///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    primer_nombre_funcionario_resp_unidad = serializers.ReadOnlyField(source='id_funcionario_resp_unidad.primer_nombre', default=None)
    primer_apellido_funcionario_resp_unidad = serializers.ReadOnlyField(source='id_funcionario_resp_unidad.primer_apellido', default=None)
    tipo_documento_funcionario_resp_unidad = serializers.ReadOnlyField(source='id_funcionario_resp_unidad.tipo_documento.cod_tipo_documento', default=None)
    numero_documento_funcionario_resp_unidad = serializers.ReadOnlyField(source='id_funcionario_resp_unidad.numero_documento', default=None)
    #///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    primer_nombre_persona_operario = serializers.ReadOnlyField(source='id_persona_operario.primer_nombre', default=None)
    primer_apellido_persona_operario = serializers.ReadOnlyField(source='id_persona_operario.primer_apellido', default=None)
    tipo_documento_persona_operario = serializers.ReadOnlyField(source='id_persona_operario.tipo_documento.cod_tipo_documento', default=None)
    numero_documento_persona_operario = serializers.ReadOnlyField(source='id_persona_operario.numero_documento', default=None)

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
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    cod_tipo_bien = serializers.ReadOnlyField(source='id_bien.cod_tipo_bien', default=None)
    descripcion_bien = serializers.ReadOnlyField(source='id_bien.descripcion', default=None)
   
    
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


class SalidasEspecialesArticulosSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalidasEspecialesArticulos
        fields = '__all__'

    def create(self, validated_data):
        return SalidasEspecialesArticulos.objects.create(**validated_data)
    

class AlmacenistaLogueadoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Personas
        fields = ['id_persona', 
                  'tipo_documento', 
                  'numero_documento', 
                  'primer_nombre',
                  'segundo_nombre',
                  'primer_apellido',
                  'segundo_apellido', 
                  'tipo_persona',
                  'telefono_celular',  
                  'telefono_empresa',  
                  'email',  
                  'email_empresarial']
        

class DespachoActivosSerializer(serializers.ModelSerializer):
    persona_despacha = serializers.SerializerMethodField()
    bodega = serializers.SerializerMethodField()
    tipo_solicitud = serializers.SerializerMethodField()
    fecha_solicitud = serializers.SerializerMethodField()

    class Meta:
        model = DespachoActivos
        fields = ['id_despacho_activo', 'fecha_despacho', 'persona_despacha', 'bodega', 'observacion', 'tipo_solicitud', 'fecha_solicitud']

    def get_persona_despacha(self, obj):
        persona_despacha = obj.id_persona_despacha
        if persona_despacha:
            return f"{persona_despacha.primer_nombre} {persona_despacha.segundo_nombre} {persona_despacha.primer_apellido} {persona_despacha.segundo_apellido}"
        return "Desconocido"

    def get_bodega(self, obj):
        bodega = obj.id_bodega
        if bodega:
            return bodega.nombre
        return "Desconocido"

    def get_tipo_solicitud(self, obj):
        if obj.despacho_sin_solicitud:
            return "Despacho sin solicitud"
        else:
            if obj.id_solicitud_activo:
                if obj.id_solicitud_activo.solicitud_prestamo:
                    return "Despacho con solicitud de préstamo"
                else:
                    return "Despacho con solicitud ordinaria"
        return "Desconocido"

    def get_fecha_solicitud(self, obj):
        if obj.despacho_sin_solicitud:
            return "No aplica"
        else:
            if obj.id_solicitud_activo:
                return obj.id_solicitud_activo.fecha_solicitud
        return None
        

class ActivosDespachadosDevolucionSerializer(serializers.ModelSerializer):
    codigo_activo = serializers.SerializerMethodField()
    nombre_activo = serializers.SerializerMethodField()
    marca_activo = serializers.SerializerMethodField()
    identificador_activo = serializers.SerializerMethodField()
    nombre_bodega = serializers.SerializerMethodField()

    class Meta:
        model = ItemsDespachoActivos
        fields = (
            'codigo_activo',
            'nombre_activo',
            'marca_activo',
            'identificador_activo',
            'nombre_bodega',
            'nro_posicion_en_despacho',
            'cantidad_solicitada',
            'cantidad_despachada',
            'fecha_devolucion',
            'observacion',
        )

    def get_codigo_activo(self, obj):
        return obj.id_bien_despachado.codigo_bien if obj.id_bien_despachado else None

    def get_nombre_activo(self, obj):
        return obj.id_bien_despachado.nombre if obj.id_bien_despachado else None

    def get_marca_activo(self, obj):
        if obj.id_bien_despachado and obj.id_bien_despachado.id_marca:
            return obj.id_bien_despachado.id_marca.nombre
        else:
            return None

    def get_identificador_activo(self, obj):
        return obj.id_bien_despachado.doc_identificador_nro if obj.id_bien_despachado else None

    def get_nombre_bodega(self, obj):
        return obj.id_bodega.nombre if obj.id_bodega else None
    
class EstadosArticuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadosArticulo
        fields = '__all__'


class ActivosDevolucionadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivosDevolucionados
        fields = '__all__'

class DevolucionActivosSerializer(serializers.ModelSerializer):
    activos_devueltos = ActivosDevolucionadosSerializer(many=True)

    class Meta:
        model = DevolucionActivos
        fields = '__all__'

    def create(self, validated_data):
        activos_devueltos_data = validated_data.pop('activos_devueltos')
        devolucion = DevolucionActivos.objects.create(**validated_data)
        for activo_devuelto_data in activos_devueltos_data:
            ActivosDevolucionados.objects.create(devolucion_activo=devolucion, **activo_devuelto_data)
        return devolucion