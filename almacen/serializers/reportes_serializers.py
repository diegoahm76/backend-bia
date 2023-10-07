from rest_framework import serializers
from almacen.models.bienes_models import ItemEntradaAlmacen

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