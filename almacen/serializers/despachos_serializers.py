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

class SerializersItemDespachoConsumo(serializers.ModelSerializer):
    #nombre = serializers.CharField(validators=[UniqueValidator(queryset=Marcas.objects.all())])
    class Meta:
        model=ItemDespachoConsumo
        fields=('__all__')

class SerializersSolicitudesConsumibles(serializers.ModelSerializer):
    #nombre = serializers.CharField(validators=[UniqueValidator(queryset=Marcas.objects.all())])
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
