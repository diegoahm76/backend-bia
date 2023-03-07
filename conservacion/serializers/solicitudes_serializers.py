from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from conservacion.models.solicitudes_models import (
    SolicitudesViveros,
    ItemSolicitudViveros
)
from almacen.models.organigrama_models import (
    UnidadesOrganizacionales
)
from conservacion.models.inventario_models import (
    InventarioViveros
)
from almacen.models.bienes_models import (
    CatalogoBienes
)

class GetNumeroConsecutivoSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesViveros
        fields = '__all__'

class GetSolicitudByNumeroSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesViveros
        fields = '__all__'


class GetUnidadOrganizacionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadesOrganizacionales
        fields = '__all__'

class GetSolicitudesViverosSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesViveros
        fields = '__all__'

class ItemSolicitudViverosSerializer(serializers.ModelSerializer):
    class Meta:
        model= ItemSolicitudViveros
        fields = '__all__'

class ListarSolicitudIDSerializer(serializers.ModelSerializer):
    class Meta:
        model= SolicitudesViveros
        fields = '__all__'

class CreateSolicitudViverosSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesViveros
        fields = (
            'id_solicitud_vivero',
            'nro_solicitud',
            'fecha_solicitud',
            'id_vivero_solicitud',
            'nro_info_tecnico',
            'motivo',
            'observaciones',
            'id_unidad_para_la_que_solicita',
            'id_funcionario_responsable_und_destino',
            'id_unidad_org_del_responsable',
            'con_municipio_destino',
            'nombre_predio_destino',
            'direccion_destino',
            'fecha_retiro_material',
            'ruta_archivo_info_tecnico',
            'id_persona_solicita',
            'id_unidad_org_del_solicitante'
        )
        extra_kwargs = {
            'nro_solicitud': {'required': True},
            'fecha_solicitud': {'required': True},
            'id_vivero_solicitud': {'required': True},
            'nro_info_tecnico':  {'required': True},
            'motivo': {'required': True},
            'observaciones': {'required': True},
            'id_unidad_para_la_que_solicita': {'required': True},
            'id_funcionario_responsable_und_destino': {'required': True},
            'id_unidad_org_del_responsable': {'required': True},
            'con_municipio_destino': {'required': True},
            'nombre_predio_destino': {'required': True},
            'direccion_destino': {'required': True},
            'fecha_retiro_material': {'required': True},
            'ruta_archivo_info_tecnico': {'required': True},
            'id_persona_solicita': {'required': True},
            'id_unidad_org_del_solicitante': {'required': True},
        }


class GetBienByCodigoViveroSerializer(serializers.ModelSerializer):
    saldo_disponible = serializers.IntegerField(default=0)
    class Meta:
        model = CatalogoBienes
        fields = (
            'id_bien',
            'codigo_bien',
            'nombre',
            'cod_tipo_elemento_vivero',
            'saldo_disponible',
        )

class GetBienByFilterSerializer(serializers.ModelSerializer):
    saldo_disponible = serializers.IntegerField(default=0)
    class Meta:
        model = CatalogoBienes
        fields = (
            'id_bien',
            'codigo_bien',
            'nombre',
            'cod_tipo_elemento_vivero',
            'saldo_disponible',
        )


class DeleteItemsSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemSolicitudViveros
        fields = '__all__'

class AnulacionSolicitudesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesViveros
        fields = '__all__'


class UpdateSolicitudesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesViveros
        fields = (
            'id_solicitud_vivero',
            'motivo',
            'observaciones',
            'nombre_predio_destino',
            'direccion_destino',
            'con_municipio_destino',
            'fecha_retiro_material',
            'nro_info_tecnico',
            'ruta_archivo_info_tecnico',
            'id_funcionario_responsable_und_destino'
        )


class CreateItemsSolicitudSerializer(serializers.ModelSerializer):
    cod_tipo_elemento_vivero = serializers.ReadOnlyField(source='id_bien.cod_tipo_elemento_vivero', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    class Meta:
        model = ItemSolicitudViveros
        fields = (
            'id_item_solicitud_viveros',
            'id_solicitud_viveros',
            'id_bien',
            'cantidad',
            'observaciones',
            'nro_posicion',
            'cod_tipo_elemento_vivero',
            'codigo_bien'
        )