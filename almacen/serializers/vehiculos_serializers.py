from rest_framework import serializers
from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from almacen.models.hoja_de_vida_models import HojaDeVidaComputadores, HojaDeVidaOtrosActivos, HojaDeVidaVehiculos, DocumentosVehiculo
from transversal.models.base_models import Municipio, ApoderadoPersona, ClasesTerceroPersona, Personas

from almacen.models.vehiculos_models import (
    PeriodoArriendoVehiculo,
    VehiculosAgendadosDiaDisponible,
    VehiculosArrendados,
    VehiculosAgendables_Conductor,
    SolicitudesViajes
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
        fields = '__all__'
        # Excluir el campo id_persona_que_asigna de la lista de campos requeridos
        extra_kwargs = {
            'id_persona_que_asigna': {'required': False}
        }

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


class SolicitudViajeSerializer(serializers.ModelSerializer):
    cod_departamento = serializers.ReadOnlyField(source='cod_municipio.cod_departamento.cod_departamento')

    class Meta:
        model = SolicitudesViajes
        fields = '__all__'

class HojaDeVidaVehiculosSerializer(serializers.ModelSerializer):
    class Meta:
        model = HojaDeVidaVehiculos
        fields = '__all__'


class ClaseTerceroPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClasesTerceroPersona
        fields = '__all__'


class AsignacionVehiculoSerializer(serializers.ModelSerializer):
    tipo_vehiculo = serializers.CharField(source='id_hoja_vida_vehiculo.cod_tipo_vehiculo')
    marca = serializers.CharField(source='id_hoja_vida_vehiculo.id_vehiculo_arrendado.id_marca.nombre')
    placa = serializers.CharField(source='id_hoja_vida_vehiculo.id_vehiculo_arrendado.placa')
    tipo_conductor = serializers.SerializerMethodField()
    nombre_conductor = serializers.SerializerMethodField()
    nro_documento_conductor = serializers.CharField(source='id_persona_conductor.numero_documento')
    id_asignacion = serializers.IntegerField(source='id_vehiculo_conductor')  # Aquí incluimos el ID de la asignación


    class Meta:
        model = VehiculosAgendables_Conductor
        fields = ['id_asignacion','tipo_vehiculo', 'marca', 'placa', 'tipo_conductor', 'nombre_conductor', 'nro_documento_conductor', 'fecha_inicio_asignacion', 'fecha_final_asignacion']

    def get_tipo_conductor(self, obj):
        # Verificar si el conductor es interno o externo
        clases_tercero_persona = ClasesTerceroPersona.objects.filter(id_persona=obj.id_persona_conductor)
        for ctp in clases_tercero_persona:
            if ctp.id_clase_tercero.nombre == "Conductor":
                return "Interno"
            elif ctp.id_clase_tercero.nombre == "Conductor Externo":
                return "Externo"
        return None

    def get_nombre_conductor(self, obj):
        return f"{obj.id_persona_conductor.primer_nombre} {obj.id_persona_conductor.primer_apellido}"
    


class PutSolicitudViajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesViajes
        fields = ['motivo_viaje', 'cod_municipio', 'tiene_expediente_asociado', 'id_expediente_asociado', 'direccion', 'nro_pasajeros', 'fecha_partida', 'hora_partida', 'fecha_retorno', 'hora_retorno', 'requiere_compagnia_militar', 'consideraciones_adicionales', 'indicaciones_destino']
        extra_kwargs = {
            'fecha_solicitud': {'required': False},
            'estado_solicitud': {'required': False},
            'id_persona_solicita': {'required': False},
            'id_unidad_org_solicita': {'required': False},
        }


class VehiculoConductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiculosAgendables_Conductor
        fields = '__all__'

class BusquedaVehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HojaDeVidaVehiculos
        fields = '__all__'