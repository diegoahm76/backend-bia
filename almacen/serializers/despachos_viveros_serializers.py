from almacen.models.generics_models import UnidadesMedida
from seguridad.serializers.personas_serializers import PersonasSerializer
from almacen.models.generics_models import Magnitudes
from almacen.models.inventario_models import Inventario
from almacen.models.solicitudes_models import DespachoConsumo, ItemDespachoConsumo, SolicitudesConsumibles, ItemsSolicitudConsumible
from rest_framework import serializers
from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen, ItemEntradaAlmacen
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

class SerializersDespachoViverosConsumo(serializers.ModelSerializer):
    #nombre = serializers.CharField(validators=[UniqueValidator(queryset=Marcas.objects.all())])
    class Meta:
        model=DespachoConsumo
        fields=('__all__')
class SerializersDespachoConsumoViverosActualizar(serializers.ModelSerializer):
    #nombre = serializers.CharField(validators=[UniqueValidator(queryset=Marcas.objects.all())])
    class Meta:
        model=DespachoConsumo
        exclude=('numero_despacho_consumo', 'fecha_despacho', 'id_persona_despacha',)
class SerializersItemDespachoViverosConsumo(serializers.ModelSerializer):
    #nombre = serializers.CharField(validators=[UniqueValidator(queryset=Marcas.objects.all())])
    class Meta:
        model=ItemDespachoConsumo
        exclude=('id_entrada_almacen_bien',)