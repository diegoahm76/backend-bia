from almacen.models.generics_models import UnidadesMedida
from seguridad.serializers.personas_serializers import PersonasSerializer
from almacen.models.generics_models import Magnitudes
from rest_framework import serializers
from almacen.models.bienes_models import CatalogoBienes
from almacen.models.hoja_de_vida_models import HojaDeVidaComputadores, HojaDeVidaOtrosActivos, HojaDeVidaVehiculos, DocumentosVehiculo
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

class SerializersHojaDeVidaComputadores(serializers.ModelSerializer):
    class Meta:
        model=HojaDeVidaComputadores
        fields=('__all__')
        
class SerializersPutHojaDeVidaComputadores(serializers.ModelSerializer):
    class Meta:
        model=HojaDeVidaComputadores
        fields=('sistema_operativo','suite_ofimatica','antivirus',
                'otras_aplicaciones','color','tipo_de_equipo',
                'tipo_almacenamiento','capacidad_almacenamiento','procesador',
                'memoria_ram','observaciones_adicionales','otras_aplicaciones')
        
class SerializersPutHojaDeVidaVehiculos(serializers.ModelSerializer):
    class Meta:
        model=HojaDeVidaVehiculos
        fields=('__all__')
        
class SerializersPutHojaDeVidaOtrosActivos(serializers.ModelSerializer):
    class Meta:
        model=HojaDeVidaOtrosActivos
        fields=('caracteristicas_fisicas','especificaciones_tecnicas','observaciones_adicionales')
        
class SerializersHojaDeVidaVehiculos(serializers.ModelSerializer):
    class Meta:
        model=HojaDeVidaVehiculos
        fields=('__all__')

class SerializersHojaDeVidaOtrosActivos(serializers.ModelSerializer):
    class Meta:
        model=HojaDeVidaOtrosActivos
        fields=('__all__')