from almacen.models.generics_models import UnidadesMedida
from transversal.serializers.personas_serializers import PersonasSerializer
from almacen.models.generics_models import Magnitudes
from almacen.models.inventario_models import Inventario
from almacen.models.solicitudes_models import DespachoConsumo, ItemDespachoConsumo, SolicitudesConsumibles, ItemsSolicitudConsumible
from rest_framework import serializers
from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen, ItemEntradaAlmacen
from conservacion.models.despachos_models import DespachoEntrantes, ItemsDespachoEntrante
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

class SerializersDespachoViverosConsumo(serializers.ModelSerializer):
    class Meta:
        model=DespachoConsumo
        fields=('__all__')
class SerializersDespachoConsumoViverosActualizar(serializers.ModelSerializer):
    class Meta:
        model=DespachoConsumo
        exclude=('numero_despacho_consumo', 'fecha_despacho', 'id_persona_despacha',)
class SerializersItemDespachoViverosConsumo(serializers.ModelSerializer):
    class Meta:
        model=ItemDespachoConsumo
        fields=('__all__')
        
class SerializersDespachoEntrantes(serializers.ModelSerializer):
    class Meta:
        model=DespachoEntrantes
        fields=('__all__')

class SerializersItemsDespachoEntrantes(serializers.ModelSerializer):
    class Meta:
        model=ItemsDespachoEntrante
        fields=('__all__')