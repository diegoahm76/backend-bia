from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from almacen.models.solicitudes_models import (
    DespachoConsumo,
    ItemDespachoConsumo
)
from almacen.models.bienes_models import (
    EntradasAlmacen,
    ItemEntradaAlmacen
) 

class GetNumeroEntregas(serializers.ModelSerializer):
    class Meta:
        model = DespachoConsumo
        fields = ['numero_despacho_consumo']

class GetEntregasSerializer(serializers.ModelSerializer):
    cod_tipo_entrada = serializers.ReadOnlyField(source='id_entrada_almacen_cv.id_tipo_entrada.cod_tipo_entrada', default=None)
    tipo_entrada = serializers.ReadOnlyField(source='id_entrada_almacen_cv.id_tipo_entrada.nombre', default=None)
    
    class Meta:
        model = DespachoConsumo
        fields = '__all__'

class CreateEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DespachoConsumo
        exclude = (
            'id_solicitud_consumo', 
            'numero_solicitud_por_tipo', 
            'fecha_solicitud', 
            'id_persona_solicita',
            'id_unidad_para_la_que_solicita',
            'id_funcionario_responsable_unidad',
            'despacho_anulado',
            'justificacion_anulacion',
            'fecha_anulacion',
            'id_persona_anula',
        )
        extra_kwargs = {
            'id_bien_despachado': {'required': True},
            'cantidad_despachada': {'required': True},
            'id_entrada_almacen_bien': {'required': True},
            'id_bodega': {'required': True}
        }

class CreateItemsEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemDespachoConsumo
        exclude = (
            'id_bien_solicitado',
            'cantidad_solicitada',
            'id_unidad_medida_solicitada',   
        )

class GetEntradasEntregasSerializer(serializers.ModelSerializer):
    cod_tipo_entrada = serializers.ReadOnlyField(source='id_tipo_entrada.cod_tipo_entrada', default=None)
    tipo_entrada = serializers.ReadOnlyField(source='id_tipo_entrada.nombre', default=None)
    
    class Meta:
        model = EntradasAlmacen
        fields = '__all__'

class GetItemsEntradasEntregasSerializer(serializers.ModelSerializer):
    tiene_cantidad_disponible = serializers.BooleanField(read_only=True, default=None)
    cantidad_disponible = serializers.IntegerField(read_only=True, default=0)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    observaciones = serializers.ReadOnlyField(source='id_entrada_almacen.observacion', default=None)
    class Meta:
        model = ItemEntradaAlmacen
        fields = (
            'id_entrada_almacen',
            'codigo_bien',
            'nombre_bien',
            'id_bien',
            'tiene_cantidad_disponible',
            'cantidad_disponible',
            'observaciones'
        )


class AnularEntregaSerializer(serializers.ModelSerializer):
    descripcion_anulacion = serializers.CharField(read_only=True)
    class Meta:
        model = DespachoConsumo
        fields = (
            'id_despacho_consumo',
            'descripcion_anulacion',
            'despacho_anulado',
            'fecha_anulacion',
            'id_persona_anula',
        )

class ActualizarEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DespachoConsumo
        fields = (
            'motivo',
        )

class GetItemsEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemDespachoConsumo
        fields = '__all__'

class DeleteItemsEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemDespachoConsumo
        fields = '__all__'