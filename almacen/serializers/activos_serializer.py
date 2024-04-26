from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen, ItemEntradaAlmacen
from almacen.models.inventario_models import Inventario, TiposEntradas
from almacen.models.generics_models import Bodegas, Marcas, UnidadesMedida
from almacen.models.activos_models import ActivosDevolucionados, AnexosDocsAlma, AsignacionActivos, BajaActivos, DespachoActivos, DevolucionActivos, ItemsBajaActivos, ArchivosDigitales, ItemsDespachoActivos, ItemsSolicitudActivos, SalidasEspecialesArticulos, SolicitudesActivos
from transversal.models.base_models import ClasesTerceroPersona
from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen, Bodegas, EstadosArticulo
from almacen.models.hoja_de_vida_models import HojaDeVidaComputadores, HojaDeVidaOtrosActivos, HojaDeVidaVehiculos, DocumentosVehiculo
from gestion_documental.models.radicados_models import PQRSDF, Anexos
from seguridad.models import Personas
from rest_framework import serializers




class InventarioSerializer(serializers.ModelSerializer):
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    identificador_bien = serializers.ReadOnlyField(source='id_bien.doc_identificador_nro', default=None)
    id_marca = serializers.ReadOnlyField(source='id_bien.id_marca.id_marca', default=None)
    nombre_marca = serializers.ReadOnlyField(source='id_bien.id_marca.nombre', default=None)
    estado = serializers.ReadOnlyField(source='cod_estado_activo.nombre', default=None)
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
        fields = '__all__'  
class BajaActivosSerializer(serializers.ModelSerializer):
    class Meta:
        model = BajaActivos
        fields = ('id_baja_activo', 'consecutivo_por_baja', 'concepto', 'fecha_baja', 'cantidad_activos_baja', 'id_persona_registro_baja', 'id_uni_org_registro_baja')



class AnexosDocsAlmaSerializer(serializers.ModelSerializer):
    id_baja_activo = BajaActivosSerializer()
    id_archivo_digital = ArchivosDigitalesSerializer()  

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
        fields = '__all__'

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
    id_bodega = serializers.ReadOnlyField(source='id_bodega.id_bodega', default=None)
    nombre_bodega = serializers.ReadOnlyField(source='id_bodega.nombre', default=None)
    nombre_persona_despacha = serializers.SerializerMethodField()
    tipo_solicitud = serializers.SerializerMethodField()
    numero_activos = serializers.SerializerMethodField()
    id_funcionario_resp_asignado = serializers.SerializerMethodField()
    primer_nombre_funcionario_resp_asignado = serializers.SerializerMethodField()
    primer_apellido_funcionario_resp_asignado = serializers.SerializerMethodField()
    tipo_documento_funcionario_resp_asignado = serializers.SerializerMethodField()
    numero_documento_funcionario_resp_asignado = serializers.SerializerMethodField()
    id_persona_operario_asignado = serializers.SerializerMethodField()
    primer_nombre_persona_operario_asignado = serializers.SerializerMethodField()
    primer_apellido_persona_operario_asignado = serializers.SerializerMethodField()
    tipo_documento_persona_operario_asignado = serializers.SerializerMethodField()
    numero_documento_persona_operario_asignado = serializers.SerializerMethodField()
    class Meta:
        model = DespachoActivos
        fields = '__all__'

    def get_nombre_persona_despacha(self, obj):
        nombre_persona_despacha = None
        if obj.id_persona_despacha:
            nombre_list = [obj.id_persona_despacha.primer_nombre, obj.id_persona_despacha.segundo_nombre,
                            obj.id_persona_despacha.primer_apellido, obj.id_persona_despacha.segundo_apellido]
            nombre_persona_despacha = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_despacha = nombre_persona_despacha if nombre_persona_despacha != "" else None
        return nombre_persona_despacha
    
    def get_tipo_solicitud(self,obj):
        # Verificar si el despacho no tiene solicitud (despacho_sin_solicitud es True)
        if obj.despacho_sin_solicitud :
            return 'Despacho sin solicitud'

        if obj.id_solicitud_activo and not obj.despacho_sin_solicitud:

            solicitud_prestamo = obj.id_solicitud_activo.solicitud_prestamo
            if not solicitud_prestamo:
                return 'Despacho con solicitud ordinaria'
            else:
                return 'Despacho con solicitud de prestamo'
            
        if not obj.id_solicitud_activo:
            # Si no hay una solicitud asociada, retornar 'Despacho sin solicitud'
            return 'Despacho sin solicitud'
        
    def get_numero_activos(self, instance):
        # Obtener el número de activos relacionados con esta solicitud
        return ItemsDespachoActivos.objects.filter(id_despacho_activo=instance).count()
    
    #Persona_Responsable
    def get_id_funcionario_resp_asignado(self, obj):
        asignacion = AsignacionActivos.objects.filter(id_despacho_asignado=obj.id_despacho_activo).first()
        if asignacion:
            return asignacion.id_funcionario_resp_asignado.id_persona
        return None
    
    def get_primer_nombre_funcionario_resp_asignado(self, obj):
        asignacion = AsignacionActivos.objects.filter(id_despacho_asignado=obj.id_despacho_activo).first()
        if asignacion:
            return asignacion.id_funcionario_resp_asignado.primer_nombre
        return None
    
    def get_primer_apellido_funcionario_resp_asignado(self, obj):
        asignacion = AsignacionActivos.objects.filter(id_despacho_asignado=obj.id_despacho_activo).first()
        if asignacion:
            return asignacion.id_funcionario_resp_asignado.primer_apellido
        return None
    
    def get_tipo_documento_funcionario_resp_asignado(self, obj):
        asignacion = AsignacionActivos.objects.filter(id_despacho_asignado=obj.id_despacho_activo).first()
        if asignacion:
            return asignacion.id_funcionario_resp_asignado.tipo_documento.cod_tipo_documento
        return None
    
    def get_numero_documento_funcionario_resp_asignado(self, obj):
        asignacion = AsignacionActivos.objects.filter(id_despacho_asignado=obj.id_despacho_activo).first()
        if asignacion:
            return asignacion.id_funcionario_resp_asignado.numero_documento
        return None
    
    #Persona_Operario
    def get_id_persona_operario_asignado(self, obj):
        asignacion = AsignacionActivos.objects.filter(id_despacho_asignado=obj.id_despacho_activo).first()
        if asignacion:
            return asignacion.id_persona_operario_asignado.id_persona
        return None
    
    def get_primer_nombre_persona_operario_asignado(self, obj):
        asignacion = AsignacionActivos.objects.filter(id_despacho_asignado=obj.id_despacho_activo).first()
        if asignacion:
            return asignacion.id_persona_operario_asignado.primer_nombre
        return None
    
    def get_primer_apellido_persona_operario_asignado(self, obj):
        asignacion = AsignacionActivos.objects.filter(id_despacho_asignado=obj.id_despacho_activo).first()
        if asignacion:
            return asignacion.id_persona_operario_asignado.primer_apellido
        return None
    
    def get_tipo_documento_persona_operario_asignado(self, obj):
        asignacion = AsignacionActivos.objects.filter(id_despacho_asignado=obj.id_despacho_activo).first()
        if asignacion:
            return asignacion.id_persona_operario_asignado.tipo_documento.cod_tipo_documento
        return None
    
    def get_numero_documento_persona_operario_asignado(self, obj):
        asignacion = AsignacionActivos.objects.filter(id_despacho_asignado=obj.id_despacho_activo).first()
        if asignacion:
            return asignacion.id_persona_operario_asignado.numero_documento
        return None    

    


class ActivosDespachadosDevolucionSerializer(serializers.ModelSerializer):
    id_bodega = serializers.ReadOnlyField(source='id_bodega.id_bodega', default=None)
    nombre_bodega = serializers.ReadOnlyField(source='id_bodega.nombre', default=None)
    id_bien = serializers.ReadOnlyField(source='id_bien_despachado.id_bien', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien_despachado.codigo_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien_despachado.nombre', default=None)
    nombre_marca = serializers.ReadOnlyField(source='id_bien_despachado.id_marca.nombre', default=None)
    identificador_activo = serializers.ReadOnlyField(source='id_bien_despachado.doc_identificador_nro', default=None)

    class Meta:
        model = ItemsDespachoActivos
        fields = '__all__'


    
class EstadosArticuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadosArticulo
        fields = '__all__'


class ActivosDevolucionadosSerializer(serializers.ModelSerializer):
    cod_estado_nombre = serializers.ReadOnlyField(source='cod_estado_activo_devolucion.nombre', default=None)

    class Meta:
        model = ActivosDevolucionados
        fields = '__all__'

class AnexoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos
        fields = '__all__'

class DevolucionActivosSerializer(serializers.ModelSerializer):
    nombre_persona_devolucion = serializers.SerializerMethodField()
    nombre_persona_anulacion = serializers.SerializerMethodField()
    class Meta:
        model = DevolucionActivos
        fields = '__all__'
    
    def get_nombre_persona_devolucion(self, obj):
        nombre_persona_devolucion = None
        persona_devolucion = obj.id_persona_devolucion
        if persona_devolucion:
            nombre_list = [persona_devolucion.primer_nombre, persona_devolucion.segundo_nombre,
                           persona_devolucion.primer_apellido, persona_devolucion.segundo_apellido]
            nombre_persona_devolucion = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_devolucion = nombre_persona_devolucion if nombre_persona_devolucion != "" else None
        return nombre_persona_devolucion
    
    def get_nombre_persona_anulacion(self, obj):
        nombre_persona_anulacion = None
        persona_anulacion = obj.id_persona_anulacion
        if persona_anulacion:
            nombre_list = [persona_anulacion.primer_nombre, persona_anulacion.segundo_nombre,
                           persona_anulacion.primer_apellido, persona_anulacion.segundo_apellido]
            nombre_persona_anulacion = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_anulacion = nombre_persona_anulacion if nombre_persona_anulacion != "" else None
        return nombre_persona_anulacion
    
    

class EntradaAlmacenPersonaTerceroSerializer(serializers.ModelSerializer):
    nombre_proveedor = serializers.SerializerMethodField()

    class Meta:
        model = EntradasAlmacen
        fields = ['id_proveedor', 'nombre_proveedor']

    def get_nombre_proveedor(self, obj):
        nombre_proveedor = None
        proveedor = obj.id_proveedor
        if proveedor:
            nombre_list = [proveedor.primer_nombre, proveedor.segundo_nombre,
                           proveedor.primer_apellido, proveedor.segundo_apellido]
            nombre_proveedor = ' '.join(item for item in nombre_list if item is not None)
            nombre_proveedor = nombre_proveedor if nombre_proveedor != "" else None
        return nombre_proveedor

    
class ItemEntradaAlmacenSerializer(serializers.ModelSerializer):
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    serie_placa = serializers.ReadOnlyField(source='id_bien.doc_identificador_nro', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    id_marca = serializers.ReadOnlyField(source='id_bien.id_marca.id_marca', default=None)
    nombre_marca = serializers.ReadOnlyField(source='id_bien.id_marca.nombre', default=None)

    class Meta:
        model = ItemEntradaAlmacen
        fields = '__all__'

class BodegasSerializer(serializers.ModelSerializer):

    nombre_municipio = serializers.ReadOnlyField(source='cod_municipio.nombre', default=None)
    class Meta:
        model = Bodegas
        fields = '__all__'

class DespachoSinSolicitudSerializer(serializers.ModelSerializer):
    numero_activos = serializers.SerializerMethodField()
    fecha_despacho = serializers.ReadOnlyField(source='id_despacho_asignado.fecha_despacho', default=None)
    estado_despacho = serializers.ReadOnlyField(source='id_despacho_asignado.estado_despacho', default=None)
    observacion = serializers.ReadOnlyField(source='id_despacho_asignado.observacion', default=None)
    primer_nombre_persona_responsable = serializers.ReadOnlyField(source='id_funcionario_resp_asignado.primer_nombre', default=None)
    primer_apellido_persona_responsable = serializers.ReadOnlyField(source='id_funcionario_resp_asignado.primer_apellido', default=None)
    primer_nombre_persona_operario = serializers.ReadOnlyField(source='id_persona_operario_asignado.primer_nombre', default=None)
    primer_apellido_persona_operario = serializers.ReadOnlyField(source='id_persona_operario_asignado.primer_apellido', default=None)
    id_persona_despacha = serializers.ReadOnlyField(source='id_despacho_asignado.id_persona_despacha', default=None)
    primer_nombre_persona_despacha = serializers.ReadOnlyField(source='id_despacho_asignado.id_persona_despacha.primer_nombre', default=None)
    primer_apellido_persona_despacha = serializers.ReadOnlyField(source='id_despacho_asignado.id_persona_despacha.primer_apellido', default=None)


    class Meta:
        model = AsignacionActivos
        fields = '__all__'

    def get_numero_activos(self, instance):
            # Obtener el número de activos relacionados con esta solicitud
            return ItemsSolicitudActivos.objects.filter(id_solicitud_activo=instance).count()
    

class CatalogoBienesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogoBienes
        fields = '__all__'


class AsignacionActivosSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsignacionActivos
        fields = '__all__'
    

class ItemsDespachoActivosSerializer(serializers.ModelSerializer):
    codigo_bien_despachado = serializers.ReadOnlyField(source='id_bien_despachado.codigo_bien', default=None)
    nombre_bien_despachado = serializers.ReadOnlyField(source='id_bien_despachado.nombre', default=None)
    identificador_bien_despachado = serializers.ReadOnlyField(source='id_bien_despachado.doc_identificador_nro', default=None)
    nombre_bodega_despachado = serializers.ReadOnlyField(source='id_bodega.nombre', default=None)
    id_marca_despachado = serializers.ReadOnlyField(source='id_bien_despachado.id_marca.id_marca', default=None)
    nombre_marca_despachado = serializers.ReadOnlyField(source='id_bien_despachado.id_marca.nombre', default=None)
    nombre_uni_medida_solicitada = serializers.ReadOnlyField(source='id_uni_medida_solicitada.nombre', default=None)
    abreviatura_uni_medida_solicitada = serializers.ReadOnlyField(source='id_uni_medida_solicitada.abreviatura', default=None)

    class Meta:
        model = ItemsDespachoActivos
        fields = '__all__'


class BusquedaArticuloSubSerializer(serializers.ModelSerializer):
    id_bien = serializers.ReadOnlyField(source='id_bien.id_bien', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    id_bodega = serializers.ReadOnlyField(source='id_bodega.id_bodega', default=None)
    nombre_bodega = serializers.ReadOnlyField(source='id_bodega.nombre', default=None)
    class Meta:
        model = Inventario
        fields = '__all__'


class DespachoActivosCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DespachoActivos
        fields = '__all__'


