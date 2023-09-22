from rest_framework import serializers
from almacen.models.bienes_models import CatalogoBienes
from almacen.models.inventario_models import Inventario

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
            'cod_tipo_entrada',
            'nombre_tipo_entrada',
            'constituye_propiedad',
            'propiedad',
            'fecha_ingreso',
            'ubicacion',
            'responsable_actual',
            'cod_estado_activo',
            'estado_activo',
            'fecha_ultimo_movimiento'
        ]
        model = Inventario