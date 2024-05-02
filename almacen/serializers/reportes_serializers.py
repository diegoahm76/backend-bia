from rest_framework import serializers
from almacen.models.bienes_models import ItemEntradaAlmacen
from almacen.models.mantenimientos_models import RegistroMantenimientos
from almacen.models.inventario_models import Inventario
from almacen.models.hoja_de_vida_models import HojaDeVidaVehiculos
from almacen.models.vehiculos_models import  InspeccionesVehiculosDia, PersonasSolicitudViaje, VehiculosAgendables_Conductor, VehiculosArrendados, Marcas, ViajesAgendados,BitacoraViaje
from transversal.models.base_models import Municipio, ApoderadoPersona, ClasesTerceroPersona, Personas
from almacen.models.solicitudes_models import DespachoConsumo, ItemDespachoConsumo, SolicitudesConsumibles, ItemsSolicitudConsumible


class EntradasInventarioGetSerializer(serializers.ModelSerializer):
    nombre_bodega = serializers.ReadOnlyField(source='id_bodega.nombre', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    fecha_entrada = serializers.ReadOnlyField(source='id_entrada_almacen.fecha_entrada', default=None)
    responsable_bodega = serializers.SerializerMethodField()
    entrada = serializers.SerializerMethodField()
    
    def get_responsable_bodega(self, obj):
        nombre_completo_responsable = None
        if obj.id_bodega.id_responsable:
            nombre_list = [obj.id_bodega.id_responsable.primer_nombre, obj.id_bodega.id_responsable.segundo_nombre,
                            obj.id_bodega.id_responsable.primer_apellido, obj.id_bodega.id_responsable.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
        return nombre_completo_responsable
    
    def get_entrada(self, obj):
        tipo_numero_origen = None
        if obj.id_entrada_almacen.id_tipo_entrada:
            tipo_numero_origen = obj.id_entrada_almacen.id_tipo_entrada.nombre + ' - ' + str(obj.id_entrada_almacen.numero_entrada_almacen)
        return tipo_numero_origen
    
    class Meta:
        fields = [
            'id_bodega',
            'nombre_bodega',
            'id_bien',
            'nombre_bien',
            'codigo_bien',
            'cantidad',
            'entrada',
            'fecha_entrada',
            'responsable_bodega'
        ]
        model = ItemEntradaAlmacen
        
class MovimientosIncautadosGetSerializer(serializers.ModelSerializer):
    nombre_bodega = serializers.ReadOnlyField(source='id_bodega.nombre', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    codigo_activo = serializers.ReadOnlyField(source='id_bien.cod_tipo_activo.cod_tipo_activo', default=None)
    tipo_activo = serializers.CharField(source='id_bien.get_cod_tipo_bien_display')
    
    class Meta:
        fields = [
            'id_bodega',
            'nombre_bodega',
            'id_bien',
            'nombre_bien',
            'codigo_bien',
            'codigo_activo',
            'tipo_activo',
            'cantidad',
        ]
        model = ItemEntradaAlmacen

class MantenimientosRealizadosGetSerializer(serializers.ModelSerializer):
    nombre_bien = serializers.ReadOnlyField(source='id_articulo.nombre', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_articulo.codigo_bien', default=None)
    serial_placa = serializers.ReadOnlyField(source='id_articulo.doc_identificador_nro', default=None)
    estado_final = serializers.ReadOnlyField(source='cod_estado_final.nombre', default=None)
    tipo_mantenimiento = serializers.ReadOnlyField(source='get_cod_tipo_mantenimiento_display', default=None)
    realizado_por = serializers.SerializerMethodField()
    
    def get_realizado_por(self, obj):
        nombre_completo_responsable = None
        if obj.id_persona_realiza:
            nombre_list = [obj.id_persona_realiza.primer_nombre, obj.id_persona_realiza.segundo_nombre,
                            obj.id_persona_realiza.primer_apellido, obj.id_persona_realiza.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
        return nombre_completo_responsable
    
    class Meta:
        fields = [
            'id_articulo',
            'nombre_bien',
            'codigo_bien',
            'serial_placa',
            'cod_tipo_mantenimiento',
            'tipo_mantenimiento',
            'fecha_ejecutado',
            'realizado_por',
            'cod_estado_final',
            'estado_final'
        ]
        model = RegistroMantenimientos


class InventarioSerializer(serializers.ModelSerializer):
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    identificador_bien = serializers.ReadOnlyField(source='id_bien.doc_identificador_nro', default=None)
    id_marca = serializers.ReadOnlyField(source='id_bien.id_marca.id_marca', default=None)
    nombre_marca = serializers.ReadOnlyField(source='id_bien.id_marca.nombre', default=None)
    nombre_bodega = serializers.ReadOnlyField(source='id_bodega.nombre', default=None)
    estado = serializers.ReadOnlyField(source='cod_estado_activo.nombre', default=None)
    valor_unitario = serializers.SerializerMethodField()
    id_item_entrada_almacen = serializers.SerializerMethodField()
    cantidad = serializers.SerializerMethodField()
    ubicacion = serializers.SerializerMethodField()
    tipo_movimiento = serializers.SerializerMethodField()
    nombre_persona_responsable = serializers.SerializerMethodField()
    nombre_persona_origen = serializers.SerializerMethodField()

    def get_nombre_persona_origen(self, obj):
        nombre_persona_origen = None
        if obj.id_persona_origen:
            nombre_list = [obj.id_persona_origen.primer_nombre, obj.id_persona_origen.segundo_nombre,
                            obj.id_persona_origen.primer_apellido, obj.id_persona_origen.segundo_apellido]
            nombre_persona_origen = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_origen = nombre_persona_origen if nombre_persona_origen != "" else None
        return nombre_persona_origen
    
    def get_nombre_persona_responsable(self, obj):
        nombre_persona_responsable = None
        if obj.id_persona_responsable:
            nombre_list = [obj.id_persona_responsable.primer_nombre, obj.id_persona_responsable.segundo_nombre,
                            obj.id_persona_responsable.primer_apellido, obj.id_persona_responsable.segundo_apellido]
            nombre_persona_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_responsable = nombre_persona_responsable if nombre_persona_responsable != "" else None
        return nombre_persona_responsable

    def get_tipo_movimiento(self, obj):
        tipo_movimiento = obj.tipo_doc_ultimo_movimiento
        tipo_movimiento_choices = dict(Inventario.tipo_doc_ultimo_movimiento.field.choices)
        return tipo_movimiento_choices.get(tipo_movimiento, tipo_movimiento)
    
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

    def get_cantidad(self, obj):
        return 1  

    def get_ubicacion(self, obj):
        if obj.ubicacion_en_bodega:
            return 'En Bodega'
        elif obj.ubicacion_asignado:
            return 'Asignado a Funcionario'
        elif obj.ubicacion_prestado:
            return 'Prestado a Funcionario'
   
    
    class Meta:
        model = Inventario
        fields = '__all__'

class InventarioReporteSerializer(serializers.ModelSerializer):
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    identificador_bien = serializers.ReadOnlyField(source='id_bien.doc_identificador_nro', default=None)
    id_marca = serializers.ReadOnlyField(source='id_bien.id_marca.id_marca', default=None)
    nombre_marca = serializers.ReadOnlyField(source='id_bien.id_marca.nombre', default=None)
    nombre_bodega = serializers.ReadOnlyField(source='id_bodega.nombre', default=None)
    estado = serializers.ReadOnlyField(source='cod_estado_activo.nombre', default=None)
    codigo_categoria = serializers.ReadOnlyField(source='id_bien.cod_tipo_activo.cod_tipo_activo', default=None)
    nombre_categoria = serializers.ReadOnlyField(source='id_bien.cod_tipo_activo.nombre', default=None)
    valor_unitario = serializers.SerializerMethodField()
    id_item_entrada_almacen = serializers.SerializerMethodField()
    cantidad = serializers.SerializerMethodField()
    ubicacion = serializers.SerializerMethodField()
    tipo_movimiento = serializers.SerializerMethodField()
    nombre_persona_responsable = serializers.SerializerMethodField()
    nombre_persona_origen = serializers.SerializerMethodField()

    def get_nombre_persona_origen(self, obj):
        nombre_persona_origen = None
        if obj.id_persona_origen:
            nombre_list = [obj.id_persona_origen.primer_nombre, obj.id_persona_origen.segundo_nombre,
                            obj.id_persona_origen.primer_apellido, obj.id_persona_origen.segundo_apellido]
            nombre_persona_origen = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_origen = nombre_persona_origen if nombre_persona_origen != "" else None
        return nombre_persona_origen
    
    def get_nombre_persona_responsable(self, obj):
        nombre_persona_responsable = None
        if obj.id_persona_responsable:
            nombre_list = [obj.id_persona_responsable.primer_nombre, obj.id_persona_responsable.segundo_nombre,
                            obj.id_persona_responsable.primer_apellido, obj.id_persona_responsable.segundo_apellido]
            nombre_persona_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_responsable = nombre_persona_responsable if nombre_persona_responsable != "" else None
        return nombre_persona_responsable

    def get_tipo_movimiento(self, obj):
        tipo_movimiento = obj.tipo_doc_ultimo_movimiento
        tipo_movimiento_choices = dict(Inventario.tipo_doc_ultimo_movimiento.field.choices)
        return tipo_movimiento_choices.get(tipo_movimiento, tipo_movimiento)
    
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

    def get_cantidad(self, obj):
        return 1  

    def get_ubicacion(self, obj):
        if obj.ubicacion_en_bodega:
            return 'En Bodega'
        elif obj.ubicacion_asignado:
            return 'Asignado a Funcionario'
        elif obj.ubicacion_prestado:
            return 'Prestado'
   
    
    class Meta:
        model = Inventario
        fields = '__all__'


class HojaDeVidaVehiculosSerializer(serializers.ModelSerializer):
    placa = serializers.SerializerMethodField()
    marca = serializers.SerializerMethodField()
    nombre = serializers.SerializerMethodField()
    tipo_vehiculo = serializers.CharField(source='get_cod_tipo_vehiculo_display', default=None)
    nombre_contratista = serializers.ReadOnlyField(source='id_vehiculo_arrendado.empresa_contratista', default=None)

    class Meta:
        model = HojaDeVidaVehiculos
        fields = '__all__'

    def get_placa(self, obj):
        if obj.es_arrendado:
            vehiculo_arrendado = obj.id_vehiculo_arrendado
            if vehiculo_arrendado:
                return vehiculo_arrendado.placa
        else:
            articulo = obj.id_articulo
            if articulo:
                return articulo.doc_identificador_nro
        
        return None


    def get_marca(self, obj):
        if obj.es_arrendado:
            if obj.id_vehiculo_arrendado and obj.id_vehiculo_arrendado.id_marca:
                return obj.id_vehiculo_arrendado.id_marca.nombre
        elif obj.id_articulo and obj.id_articulo.id_marca:
            return obj.id_articulo.id_marca.nombre
        return None

    def get_nombre(self, obj):
        if obj.es_arrendado:
            vehiculo_arrendado = obj.id_vehiculo_arrendado
            if vehiculo_arrendado:
                return vehiculo_arrendado.nombre
        else:
            articulo = obj.id_articulo
            if articulo:
                return articulo.nombre
        
        return None



class ViajesAgendadosSerializer(serializers.ModelSerializer):
    id_hoja_vida_vehiculo = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_hoja_vida_vehiculo.id_hoja_de_vida', default=None)
    Municipio_desplazamiento = serializers.ReadOnlyField(source='cod_municipio_destino.nombre', default=None)
    cod_tipo_vehiculo = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_hoja_vida_vehiculo.cod_tipo_vehiculo', default=None)
    es_arrendado = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_hoja_vida_vehiculo.es_arrendado', default=None)
    id_responsable_vehiculo = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_persona_conductor.id_persona', default=None)
    primer_nombre_responsable_vehiculo = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_persona_conductor.primer_nombre', default=None)
    primer_apellido_responsable_vehiculo = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_persona_conductor.primer_apellido', default=None)
    tipo_vehiculo = serializers.SerializerMethodField()
    funcionario_autorizo = serializers.SerializerMethodField()
    placa = serializers.SerializerMethodField()
    marca = serializers.SerializerMethodField()
    nombre = serializers.SerializerMethodField()

    class Meta:
        model = ViajesAgendados
        fields = '__all__'
    

    def get_funcionario_autorizo(self, obj):
        nombre_persona_autoriza = None
        if obj.id_persona_autoriza:
            nombre_list = [obj.id_persona_autoriza.primer_nombre, obj.id_persona_autoriza.segundo_nombre,
                            obj.id_persona_autoriza.primer_apellido, obj.id_persona_autoriza.segundo_apellido]
            nombre_persona_autoriza = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_autoriza = nombre_persona_autoriza if nombre_persona_autoriza != "" else None
        return nombre_persona_autoriza
    
    def get_placa(self, obj):
        if obj.id_vehiculo_conductor and obj.id_vehiculo_conductor.id_hoja_vida_vehiculo:
            vehiculo = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo
            if vehiculo.es_arrendado:
                return vehiculo.id_vehiculo_arrendado.placa
            else:
                return vehiculo.id_articulo.doc_identificador_nro
        return None

    def get_marca(self, obj):
        if obj.id_vehiculo_conductor and obj.id_vehiculo_conductor.id_hoja_vida_vehiculo:
            vehiculo = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo
            if vehiculo.es_arrendado:
                return vehiculo.id_vehiculo_arrendado.id_marca.nombre if vehiculo.id_vehiculo_arrendado.id_marca else None
            else:
                return vehiculo.id_articulo.id_marca.nombre if vehiculo.id_articulo.id_marca else None
        return None

    def get_nombre(self, obj):
        if obj.id_vehiculo_conductor and obj.id_vehiculo_conductor.id_hoja_vida_vehiculo:
            vehiculo = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo
            if vehiculo.es_arrendado:
                return vehiculo.id_vehiculo_arrendado.nombre
            else:
                return vehiculo.id_articulo.nombre
        return None

    def get_tipo_vehiculo(self, obj):
        if obj.id_vehiculo_conductor and obj.id_vehiculo_conductor.id_hoja_vida_vehiculo:
            vehiculo = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo
            return vehiculo.get_cod_tipo_vehiculo_display() if vehiculo.cod_tipo_vehiculo else None
        return None

    
    
class ItemDespachoConsumoSerializer(serializers.ModelSerializer):
    codigo_bien = serializers.ReadOnlyField(source='id_bien_despachado.codigo_bien')
    nombre_bien = serializers.ReadOnlyField(source='id_bien_despachado.nombre')
    cantidad = serializers.ReadOnlyField(source='cantidad_despachada')
    fecha_entrega = serializers.ReadOnlyField(source='id_despacho_consumo.fecha_despacho')
    responsable = serializers.SerializerMethodField()

    def get_responsable(self, obj):
        responsable = None
        if obj.id_despacho_consumo.id_funcionario_responsable_unidad:
            funcionario_responsable_unidad = obj.id_despacho_consumo.id_funcionario_responsable_unidad
            nombre_list = [funcionario_responsable_unidad.primer_nombre, funcionario_responsable_unidad.segundo_nombre,
                           funcionario_responsable_unidad.primer_apellido, funcionario_responsable_unidad.segundo_apellido]
            responsable = ' '.join(item for item in nombre_list if item is not None)
            responsable = responsable if responsable != "" else None
        return responsable

    class Meta:
        model = ItemDespachoConsumo
        fields = '__all__'