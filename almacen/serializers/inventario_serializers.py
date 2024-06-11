from rest_framework import serializers
from almacen.models.bienes_models import CatalogoBienes
from almacen.models.inventario_models import Inventario, TiposEntradas
from almacen.models.solicitudes_models import ItemDespachoConsumo

class SerializerUpdateInventariosActivosFijos(serializers.ModelSerializer):
    valor_total_item = serializers.FloatField(source='valor_ingreso')
    cod_estado = serializers.ReadOnlyField(source='cod_estado_activo.cod_estado', default=None)
    class Meta:
        model= Inventario
        fields = ['id_bodega', 'valor_total_item', 'cod_estado']

class SerializerUpdateInventariosConsumo(serializers.ModelSerializer):
    class Meta:
        model= Inventario
        fields = ['id_bodega', 'cantidad_entrante_consumo']

class OrigenesListGetSerializer(serializers.ModelSerializer):
    class Meta:
        model= TiposEntradas
        fields = '__all__'
        
class BusquedaBienesSerializer(serializers.ModelSerializer):
    nombre_bien = serializers.ReadOnlyField(source='nombre', default=None)
    categoria = serializers.ReadOnlyField(source='cod_tipo_activo.nombre', default=None)
    nombre_marca = serializers.ReadOnlyField(source='id_marca.nombre', default=None)
    serial = serializers.ReadOnlyField(source='doc_identificador_nro', default=None)
    
    class Meta:
        fields = [
            'id_bien',
            'codigo_bien',
            'nombre_bien',
            'id_marca',
            'nombre_marca',
            'serial',
            'cod_tipo_activo',
            'categoria'
        ]
        model = CatalogoBienes
        
class BusquedaBienesConsumoSerializer(serializers.ModelSerializer):
    nombre_bien = serializers.ReadOnlyField(source='nombre', default=None)
    tipo_consumo_vivero = serializers.SerializerMethodField()
    
    def get_tipo_consumo_vivero(self, obj):
        tipo_bien = None
        if obj.cod_tipo_elemento_vivero == 'IN':
            tipo_bien = 'Insumo'
        elif obj.cod_tipo_elemento_vivero == 'HE':
            tipo_bien = 'Herramienta'
        elif obj.cod_tipo_elemento_vivero == 'MV' and obj.es_semilla_vivero == True:
            tipo_bien = 'Material Vegetal - Semilla'
        elif obj.cod_tipo_elemento_vivero == 'MV' and obj.es_semilla_vivero == False:
            tipo_bien = 'Material Vegetal - Planta'
            
        return tipo_bien
    
    class Meta:
        fields = [
            'id_bien',
            'codigo_bien',
            'nombre_bien',
            'stock_minimo',
            'stock_maximo',
            'cod_tipo_elemento_vivero',
            'es_semilla_vivero',
            'tipo_consumo_vivero',
            'solicitable_vivero'
        ]
        model = CatalogoBienes

class ControlInventarioTodoSerializer(serializers.ModelSerializer):
    nombre_bodega = serializers.ReadOnlyField(source='id_bodega.nombre', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    cod_tipo_activo = serializers.ReadOnlyField(source='id_bien.cod_tipo_activo.cod_tipo_activo', default=None)
    categoria = serializers.ReadOnlyField(source='id_bien.cod_tipo_activo.nombre', default=None)
    id_marca = serializers.ReadOnlyField(source='id_bien.id_marca.id_marca', default=None)
    nombre_marca = serializers.ReadOnlyField(source='id_bien.id_marca.nombre', default=None)
    serial = serializers.ReadOnlyField(source='id_bien.doc_identificador_nro', default=None)
    nombre_tipo_entrada = serializers.ReadOnlyField(source='cod_tipo_entrada.nombre', default=None)
    constituye_propiedad = serializers.ReadOnlyField(source='cod_tipo_entrada.constituye_propiedad', default=None)
    propiedad = serializers.SerializerMethodField()
    ubicacion = serializers.SerializerMethodField()
    responsable_actual = serializers.SerializerMethodField()
    tipo_numero_origen = serializers.SerializerMethodField()
    estado_activo = serializers.ReadOnlyField(source='cod_estado_activo.nombre', default=None)
    
    def get_propiedad(self, obj):
        propiedad = None
        if obj.cod_tipo_entrada.constituye_propiedad:
            propiedad = 'Propio'
        else:
            propiedad = 'No Propio'
        
        return propiedad
    
    def get_ubicacion(self, obj):
        ubicacion = None
        if obj.ubicacion_en_bodega:
            ubicacion = 'En Bodega'
        elif obj.ubicacion_asignado:
            ubicacion = 'Asignado a Persona'
        elif obj.ubicacion_prestado:
            ubicacion = 'Prestado a Persona'
        elif obj.realizo_baja:
            ubicacion = 'Dado de Baja'
        elif obj.realizo_salida:
            ubicacion = 'Se le registró Salida'
        
        return ubicacion
    
    def get_responsable_actual(self, obj):
        nombre_completo_responsable = None
        if obj.id_persona_responsable:
            nombre_list = [obj.id_persona_responsable.primer_nombre, obj.id_persona_responsable.primer_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
        return nombre_completo_responsable
    
    def get_tipo_numero_origen(self, obj):
        tipo_numero_origen = None
        if obj.cod_tipo_entrada:
            tipo_numero_origen = obj.numero_doc_origen + ' - ' + obj.cod_tipo_entrada.nombre
        return tipo_numero_origen
    
    class Meta:
        fields = [
            'id_inventario',
            'id_bodega',
            'nombre_bodega',
            'id_bien',
            'nombre_bien',
            'codigo_bien',
            'cod_tipo_activo',
            'categoria',
            'id_marca',
            'nombre_marca',
            'serial',
            'numero_doc_origen',
            'cod_tipo_entrada',
            'nombre_tipo_entrada',
            'constituye_propiedad',
            'propiedad',
            'fecha_ingreso',
            'ubicacion',
            'responsable_actual',
            'cod_estado_activo',
            'estado_activo',
            'fecha_ultimo_movimiento',
            'tipo_numero_origen'
        ]
        model = Inventario

class ControlInventarioByTipoSerializer(serializers.ModelSerializer):
    nombre_bodega = serializers.ReadOnlyField(source='id_bodega.nombre', default=None)
    id_bien_padre = serializers.ReadOnlyField(source='id_bien.id_bien_padre.id_bien', default=None)
    tipo_bien = serializers.ReadOnlyField(source='id_bien.id_bien_padre.nombre', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    id_marca = serializers.ReadOnlyField(source='id_bien.id_bien_padre.id_marca.id_marca', default=None)
    nombre_marca = serializers.ReadOnlyField(source='id_bien.id_bien_padre.id_marca.nombre', default=None)
    
    class Meta:
        fields = [
            'id_bodega',
            'nombre_bodega',
            'id_bien_padre',
            'tipo_bien',
            'codigo_bien',
            'id_marca',
            'nombre_marca'
        ]
        model = Inventario

class ControlBienesConsumoGetListSerializer(serializers.ModelSerializer):
    nombre_bodega = serializers.ReadOnlyField(source='id_bodega.nombre', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    cod_tipo_elemento_vivero = serializers.ReadOnlyField(source='id_bien.cod_tipo_elemento_vivero', default=None)
    es_semilla_vivero = serializers.ReadOnlyField(source='id_bien.es_semilla_vivero', default=None)
    id_unidad_medida = serializers.ReadOnlyField(source='id_bien.id_unidad_medida.id_unidad_medida', default=None)
    unidad_medida = serializers.ReadOnlyField(source='id_bien.id_unidad_medida.abreviatura', default=None)
    stock_minimo = serializers.ReadOnlyField(source='id_bien.stock_minimo', default=None)
    stock_maximo = serializers.ReadOnlyField(source='id_bien.stock_maximo', default=None)
    solicitable_vivero = serializers.ReadOnlyField(source='id_bien.solicitable_vivero', default=None)
    nombre_cientifico = serializers.ReadOnlyField(source='id_bien.nombre_cientifico', default=None)
    cantidad_existente = serializers.SerializerMethodField()
    tipo_consumo_vivero = serializers.SerializerMethodField()
    
    def get_cantidad_existente(self, obj):
        cantidad_entrante_consumo = obj.cantidad_entrante_consumo if obj.cantidad_entrante_consumo else 0
        cantidad_saliente_consumo = obj.cantidad_saliente_consumo if obj.cantidad_saliente_consumo else 0
        
        cantidad_existente = cantidad_entrante_consumo - cantidad_saliente_consumo
        return cantidad_existente
    
    def get_tipo_consumo_vivero(self, obj):
        tipo_bien = None
        if obj.id_bien.cod_tipo_elemento_vivero == 'IN':
            tipo_bien = 'Insumo'
        elif obj.id_bien.cod_tipo_elemento_vivero == 'HE':
            tipo_bien = 'Herramienta'
        elif obj.id_bien.cod_tipo_elemento_vivero == 'MV' and obj.id_bien.es_semilla_vivero == True:
            tipo_bien = 'Material Vegetal - Semilla'
        elif obj.id_bien.cod_tipo_elemento_vivero == 'MV' and obj.id_bien.es_semilla_vivero == False:
            tipo_bien = 'Material Vegetal - Planta'
            
        return tipo_bien
    
    class Meta:
        fields = [
            'id_inventario',
            'id_bodega',
            'nombre_bodega',
            'id_bien',
            'nombre_bien',
            'codigo_bien',
            'id_unidad_medida',
            'unidad_medida',
            'stock_minimo',
            'stock_maximo',
            'cantidad_existente',
            'solicitable_vivero',
            'cod_tipo_elemento_vivero',
            'es_semilla_vivero',
            'tipo_consumo_vivero',
            'nombre_cientifico'
        ]
        model = Inventario

class ControlConsumoBienesGetListSerializer(serializers.ModelSerializer):
    id_unidad_para_la_que_solicita = serializers.ReadOnlyField(source='id_despacho_consumo.id_unidad_para_la_que_solicita.id_unidad_organizacional', default=None)
    nombre_unidad_para_la_que_solicita = serializers.ReadOnlyField(source='id_despacho_consumo.id_unidad_para_la_que_solicita.nombre', default=None)
    es_despacho_conservacion = serializers.ReadOnlyField(source='id_despacho_consumo.es_despacho_conservacion', default=None)
    fecha_despacho = serializers.ReadOnlyField(source='id_despacho_consumo.fecha_despacho', default=None)
    nombre_bien_despachado = serializers.ReadOnlyField(source='id_bien_despachado.nombre', default=None)
    codigo_bien_despachado = serializers.ReadOnlyField(source='id_bien_despachado.codigo_bien', default=None)
    id_unidad_medida = serializers.ReadOnlyField(source='id_bien_despachado.id_unidad_medida.id_unidad_medida', default=None)
    unidad_medida = serializers.ReadOnlyField(source='id_bien_despachado.id_unidad_medida.abreviatura', default=None)
    
    class Meta:
        fields = [
            'id_unidad_para_la_que_solicita',
            'nombre_unidad_para_la_que_solicita',
            'id_bien_despachado',
            'nombre_bien_despachado',
            'codigo_bien_despachado',
            'cantidad_despachada',
            'id_unidad_medida',
            'unidad_medida',
            'es_despacho_conservacion',
            'fecha_despacho'
        ]
        model = ItemDespachoConsumo
        
class ControlStockGetSerializer(serializers.ModelSerializer):
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    stock_minimo = serializers.ReadOnlyField(source='id_bien.stock_minimo', default=None)
    stock_maximo = serializers.ReadOnlyField(source='id_bien.stock_maximo', default=None)
    id_unidad_medida = serializers.ReadOnlyField(source='id_bien.id_unidad_medida.id_unidad_medida', default=None)
    unidad_medida = serializers.ReadOnlyField(source='id_bien.id_unidad_medida.abreviatura', default=None)
    
    class Meta:
        fields = '__all__'
        model = Inventario