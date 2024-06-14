from rest_framework import serializers
from almacen.models.bienes_models import CatalogoBienes, ItemEntradaAlmacen
from almacen.models.inventario_models import HistoricoMovimientosInventario, Inventario, TiposEntradas
from almacen.models.solicitudes_models import ItemDespachoConsumo
from datetime import datetime
from django.db.models import F, Count, Sum
from django.db.models import F, Sum, Value, CharField

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
    consecutivo = serializers.ReadOnlyField(source='id_bien.nro_elemento_bien', default=None)
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
            'tipo_numero_origen',
            'consecutivo'
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
    valor_unitario = serializers.SerializerMethodField()
    valor_total = serializers.SerializerMethodField()
    valor_iva = serializers.SerializerMethodField()
    valor_residual = serializers.SerializerMethodField()
    depreciacion_valor  = serializers.SerializerMethodField()
    ubicacion = serializers.SerializerMethodField()
    
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
    
    def get_depreciacion_valor(self, obj):
        item_entrada = ItemEntradaAlmacen.objects.filter(id_bien=obj.id_bien).first()
        
        if item_entrada and item_entrada.cantidad_vida_util:
            valor_ingreso = obj.valor_ingreso
            cantidad_vida_util = item_entrada.cantidad_vida_util
                
            fecha_actual = datetime.now().date()
            dias_transcurridos = (fecha_actual - obj.fecha_ingreso).days
                
            valor_depreciado = valor_ingreso - ((valor_ingreso / cantidad_vida_util) * dias_transcurridos)
            
            # Validar si el valor depreciado es menor al valor residual
            if valor_depreciado < item_entrada.valor_residual:
                return item_entrada.valor_residual
            else:
                return valor_depreciado
        else:
            return None

    
    def get_valor_unitario(self, obj):
        id_bien = obj.id_bien
        item_entrada = ItemEntradaAlmacen.objects.filter(id_bien=id_bien).first()
        valor_unitario = item_entrada.valor_unitario if item_entrada else None
        return valor_unitario

    def get_valor_total(self, obj):
        id_bien = obj.id_bien
        item_entrada = ItemEntradaAlmacen.objects.filter(id_bien=id_bien).first()
        valor_iva = item_entrada.valor_iva if item_entrada else None
        return valor_iva
    
    def get_valor_iva(self, obj):
        id_bien = obj.id_bien
        item_entrada = ItemEntradaAlmacen.objects.filter(id_bien=id_bien).first()
        valor_total_item = item_entrada.valor_total_item if item_entrada else None
        return valor_total_item

    def get_id_item_entrada_almacen(self, obj):
        id_bien = obj.id_bien
        item_entrada = ItemEntradaAlmacen.objects.filter(id_bien=id_bien).first()
        id_item_entrada_almacen = item_entrada.id_item_entrada_almacen if item_entrada else None
        return id_item_entrada_almacen
    
    def get_valor_residual(self, obj):
        id_bien = obj.id_bien
        item_entrada = ItemEntradaAlmacen.objects.filter(id_bien=id_bien).first()
        valor_residual = item_entrada.valor_residual if item_entrada else None
        return valor_residual


    def get_ubicacion(self, obj):
        if obj.ubicacion_en_bodega:
            return 'En Bodega'
        elif obj.ubicacion_asignado:
            return 'Asignado a Funcionario'
        elif obj.ubicacion_prestado:
            return 'Prestado a Funcionario'
        else:
            return 'Ubicación desconocida'
    
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
            'nombre_cientifico',
            'fecha_ingreso',
            'valor_unitario',
            'valor_total',
            'valor_iva',
            'valor_residual',
            'depreciacion_valor',
            'ubicacion',
            'valor_ingreso'
        ]
        model = Inventario

class ControlConsumoBienesGetListSerializer(serializers.ModelSerializer):
    nombre_bodega = serializers.ReadOnlyField(source='id_bodega.nombre')
    nombre_bien_despachado = serializers.ReadOnlyField(source='id_bien_despachado.nombre')
    codigo_bien_despachado = serializers.ReadOnlyField(source='id_bien_despachado.codigo_bien')
    id_unidad_medida = serializers.ReadOnlyField(source='id_bien_despachado.id_unidad_medida.id_unidad_medida')
    unidad_medida = serializers.ReadOnlyField(source='id_bien_despachado.id_unidad_medida.abreviatura')
    cod_tipo_activo_bien_despachado = serializers.ReadOnlyField(source='id_bien_despachado.cod_tipo_activo')
    observacion_reporte = serializers.ReadOnlyField(source='observacion')
    cantidad_despachada_unidad = serializers.SerializerMethodField()
    cantidad_existente = serializers.SerializerMethodField()

    def get_cantidad_despachada_unidad(self, obj):
        return obj.cantidad_despachada

    def get_cantidad_existente(self, obj):
        # Filtrar el inventario para el bien despachado
        inventario = Inventario.objects.filter(id_bien=obj.id_bien_despachado)
        
        # Sumar las cantidades entrantes y salientes
        cantidad_entrante_consumo = inventario.aggregate(Sum('cantidad_entrante_consumo'))['cantidad_entrante_consumo__sum'] or 0
        cantidad_saliente_consumo = inventario.aggregate(Sum('cantidad_saliente_consumo'))['cantidad_saliente_consumo__sum'] or 0
        
        cantidad_existente = cantidad_entrante_consumo - cantidad_saliente_consumo
        return cantidad_existente

    class Meta:
        model = ItemDespachoConsumo
        fields = [
            'id_bien_despachado',
            'nombre_bodega',
            'nombre_bien_despachado',
            'codigo_bien_despachado',
            'id_unidad_medida',
            'unidad_medida',
            'cod_tipo_activo_bien_despachado',
            'id_bodega_reporte',
            'observacion_reporte',
            'cantidad_despachada_unidad',
            'cantidad_existente',
        ]

class ControlStockGetSerializer(serializers.ModelSerializer):
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    stock_minimo = serializers.ReadOnlyField(source='id_bien.stock_minimo', default=None)
    stock_maximo = serializers.ReadOnlyField(source='id_bien.stock_maximo', default=None)
    id_unidad_medida = serializers.ReadOnlyField(source='id_bien.id_unidad_medida.id_unidad_medida', default=None)
    unidad_medida = serializers.ReadOnlyField(source='id_bien.id_unidad_medida.abreviatura', default=None)
    
    class Meta:
        fields = '__all__'
        model = Inventario

class HistorialMovimientosSerializer(serializers.ModelSerializer):
    nombre_bodega = serializers.ReadOnlyField(source='id_inventario.id_bodega.nombre', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_inventario.id_bien.nombre', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_inventario.id_bien.codigo_bien', default=None)
    cod_tipo_activo = serializers.ReadOnlyField(source='id_inventario.id_bien.cod_tipo_activo.cod_tipo_activo', default=None)
    categoria = serializers.ReadOnlyField(source='id_inventario.id_bien.cod_tipo_activo.nombre', default=None)
    id_marca = serializers.ReadOnlyField(source='id_inventario.id_bien.id_marca.id_marca', default=None)
    nombre_marca = serializers.ReadOnlyField(source='id_inventario.id_bien.id_marca.nombre', default=None)
    serial = serializers.ReadOnlyField(source='id_inventario.id_bien.doc_identificador_nro', default=None)
    nombre_tipo_entrada = serializers.ReadOnlyField(source='id_inventario.cod_tipo_entrada.nombre', default=None)
    constituye_propiedad = serializers.ReadOnlyField(source='id_inventario.cod_tipo_entrada.constituye_propiedad', default=None)
    propiedad = serializers.SerializerMethodField()
    ubicacion = serializers.SerializerMethodField()
    responsable_actual = serializers.SerializerMethodField()
    estado_activo = serializers.ReadOnlyField(source='id_inventario.cod_estado_activo.nombre', default=None)
    tipo_doc_ultimo_movimiento_nombre = serializers.CharField(source='get_tipo_doc_ultimo_movimiento_display', read_only = True, default=None)
    
    def get_propiedad(self, obj):
        propiedad = None
        if obj.id_inventario.cod_tipo_entrada.constituye_propiedad:
            propiedad = 'Propio'
        else:
            propiedad = 'No Propio'
        
        return propiedad
    
    def get_ubicacion(self, obj):
        ubicacion = None
        if obj.id_inventario.ubicacion_en_bodega:
            ubicacion = 'En Bodega'
        elif obj.id_inventario.ubicacion_asignado:
            ubicacion = 'Asignado a Persona'
        elif obj.id_inventario.ubicacion_prestado:
            ubicacion = 'Prestado a Persona'
        elif obj.id_inventario.realizo_baja:
            ubicacion = 'Dado de Baja'
        elif obj.id_inventario.realizo_salida:
            ubicacion = 'Se le registró Salida'
        
        return ubicacion
    
    def get_responsable_actual(self, obj):
        nombre_completo_responsable = None
        if obj.id_inventario.id_persona_responsable:
            nombre_list = [obj.id_inventario.id_persona_responsable.primer_nombre, obj.id_inventario.id_persona_responsable.primer_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
        return nombre_completo_responsable
    
    class Meta:
        fields = '__all__'
        model = HistoricoMovimientosInventario