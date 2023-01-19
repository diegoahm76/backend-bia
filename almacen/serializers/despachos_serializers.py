from almacen.models.generics_models import UnidadesMedida
from seguridad.serializers.personas_serializers import PersonasSerializer
from almacen.models.generics_models import Magnitudes
from almacen.models.inventario_models import Inventario
from almacen.models.solicitudes_models import DespachoConsumo, ItemDespachoConsumo, SolicitudesConsumibles, ItemsSolicitudConsumible
from rest_framework import serializers
from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen, ItemEntradaAlmacen
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

class SerializersDespachoConsumo(serializers.ModelSerializer):
    #nombre = serializers.CharField(validators=[UniqueValidator(queryset=Marcas.objects.all())])
    class Meta:
        model=DespachoConsumo
        fields=('__all__')
class SerializersDespachoConsumoActualizar(serializers.ModelSerializer):
    #nombre = serializers.CharField(validators=[UniqueValidator(queryset=Marcas.objects.all())])
    class Meta:
        model=DespachoConsumo
        exclude=('numero_despacho_consumo', 'fecha_despacho', 'id_persona_despacha',)
class SerializersItemDespachoConsumo(serializers.ModelSerializer):
    #nombre = serializers.CharField(validators=[UniqueValidator(queryset=Marcas.objects.all())])
    class Meta:
        model=ItemDespachoConsumo
        exclude=('id_entrada_almacen_bien',)

class SerializersSolicitudesConsumibles(serializers.ModelSerializer):
    #nombre = serializers.CharField(validators=[UniqueValidator(queryset=Marcas.objects.all())])
    nombre_completo_responsable = serializers.SerializerMethodField()
    nombre_completo_solicitante = serializers.SerializerMethodField()
    unidad_para_la_que_solicita=serializers.ReadOnlyField(source='id_unidad_para_la_que_solicita.nombre',default=None)
    unidad_org_del_responsable=serializers.ReadOnlyField(source='id_unidad_org_del_responsable.nombre',default=None)
    unidad_org_del_solicitante=serializers.ReadOnlyField(source='id_unidad_org_del_solicitante.nombre',default=None)
    def get_nombre_completo_responsable(self, obj):
        nombre_completo_responsable = None
        nombre_list = [obj.id_funcionario_responsable_unidad.primer_nombre, obj.id_funcionario_responsable_unidad.segundo_nombre,
                        obj.id_funcionario_responsable_unidad.primer_apellido, obj.id_funcionario_responsable_unidad.segundo_apellido]
        nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
        return nombre_completo_responsable
    def get_nombre_completo_solicitante(self, obj):
        nombre_completo_solicitante = None
        nombre_list = [obj.id_persona_solicita.primer_nombre, obj.id_persona_solicita.segundo_nombre,
                        obj.id_persona_solicita.primer_apellido, obj.id_persona_solicita.segundo_apellido]
        nombre_completo_solicitante = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo_solicitante = nombre_completo_solicitante if nombre_completo_solicitante != "" else None
        return nombre_completo_solicitante
    
        

    class Meta:
        model=SolicitudesConsumibles
        fields=('__all__')

class SerializersItemsSolicitudConsumible(serializers.ModelSerializer):
   # nombre = serializers.CharField(validators=[UniqueValidator(queryset=Marcas.objects.all())])
    class Meta:
        model=ItemsSolicitudConsumible
        fields=('__all__')


class CerrarSolicitudDebidoInexistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesConsumibles
        fields = (
            'observacion_cierre_no_dispo_alm',
            'fecha_cierre_no_dispo_alm',
            'id_persona_cierre_no_dispo_alm',
            'solicitud_abierta',
            'fecha_cierre_solicitud',
            'gestionada_almacen'
        )
        extra_kwargs = {
            'observacion_cierre_no_dispo_alm': {'required': True},
        }

class SearchBienInventarioSerializer(serializers.ModelSerializer):
    codigo_bien=serializers.ReadOnlyField(source='id_bien.codigo_bien',default=None)
    nombre=serializers.ReadOnlyField(source='id_bien.nombre',default=None)
    bodega=serializers.ReadOnlyField(source='id_bodega.nombre',default=None)
    cantidad_disponible = serializers.IntegerField(read_only=True, default=None)
    disponible= serializers.BooleanField(read_only=True,default=None)
    unidad_medida= serializers.ReadOnlyField(source='id_bien.id_unidad_medida.abreviatura')
    class Meta:
        model=Inventario
        fields=('id_inventario', 'id_bien', 'codigo_bien', 'nombre', 'id_bodega', 'bodega', 'cantidad_disponible','disponible','unidad_medida')

class AgregarBienesConsumoConservacionSerializer(serializers.ModelSerializer):
    codigo_bien=serializers.ReadOnlyField(source='id_bien.codigo_bien',default=None)
    nombre=serializers.ReadOnlyField(source='id_bien.nombre',default=None)
    bodega=serializers.ReadOnlyField(source='id_bodega.nombre',default=None)
    tipo_documento=serializers.CharField(default='Todos')
    cantidad_disponible=serializers.IntegerField(read_only=True,default=None)
    origen=serializers.CharField(read_only=True,default='Todos')
    disponible= serializers.BooleanField(read_only=True,default=None)
    unidad_medida= serializers.ReadOnlyField(source='id_bien.id_unidad_medida.abreviatura')
    class Meta:
        model=Inventario
        fields=('id_inventario', 'id_bien', 'codigo_bien', 'nombre', 'id_bodega', 'bodega','tipo_documento','cantidad_disponible','origen','disponible','unidad_medida')

class GetItemOtrosOrigenesSerializers(serializers.ModelSerializer):
    codigo_bien_desp=serializers.ReadOnlyField(source='id_bien.codigo_bien',default=None)
    nombre=serializers.ReadOnlyField(source='id_bien.nombre',default=None)
    tipo_documento=serializers.CharField(read_only=True,default=None)
    cantidad_por_distribuir=serializers.IntegerField(read_only=True,default=None)
    numero_documento=serializers.CharField(read_only=True,default=None)
    class Meta:
        model=ItemEntradaAlmacen
        fields=('id_bien', 'nombre','tipo_documento','numero_documento','cantidad_por_distribuir','codigo_bien_desp')
