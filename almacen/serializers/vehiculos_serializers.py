from rest_framework import serializers
from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from almacen.models.vehiculos_models import (
    PeriodoArriendoVehiculo,
    VehiculosAgendadosDiaDisponible,
    VehiculosArrendados,
    VehiculosAgendables_Conductor,
    # ViajesAgendados
    )

class RegistrarVehiculoArrendadoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = VehiculosArrendados
        fields = '__all__'

class ActualizarVehiculoArrendadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiculosArrendados
        fields = ['descripcion','id_marca','empresa_contratista']
        
class VehiculosAgendablesConductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiculosAgendables_Conductor
        fields = ['id_hoja_vida_vehiculo','id_persona_conductor','fecha_inicio_asignacion','fecha_final_asignacion','id_persona_que_asigna']

class PeriodoVehiculoArrendadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoArriendoVehiculo
        fields = '__all__'
        
class CrearAgendaVehiculoDiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiculosAgendadosDiaDisponible
        fields = '__all__'
class UpdateArrendarVehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoArriendoVehiculo
        fields = ['id_vehiculo_arrendado','fecha_fin']
