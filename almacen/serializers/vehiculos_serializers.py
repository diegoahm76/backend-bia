from rest_framework import serializers
from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from almacen.models.hoja_de_vida_models import HojaDeVidaComputadores, HojaDeVidaOtrosActivos, HojaDeVidaVehiculos, DocumentosVehiculo
from transversal.models.base_models import Municipio, ApoderadoPersona, ClasesTerceroPersona, Personas
from almacen.models.vehiculos_models import  InspeccionesVehiculosDia, VehiculosAgendables_Conductor, VehiculosArrendados, Marcas



from almacen.models.vehiculos_models import (
    PeriodoArriendoVehiculo,
    VehiculosAgendadosDiaDisponible,
    VehiculosArrendados,
    VehiculosAgendables_Conductor,
    SolicitudesViajes
    # ViajesAgendados
    )

class RegistrarVehiculoArrendadoSerializer(serializers.ModelSerializer):
    nombre_marca = serializers.ReadOnlyField(source='id_marca.nombre')
    
    class Meta:
        model = VehiculosArrendados
        fields = ['id_vehiculo_arrendado', 'nombre', 'descripcion', 'placa', 'nombre_marca', 'empresa_contratista', 'tiene_hoja_de_vida']

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
    marca = serializers.SerializerMethodField()
    placa = serializers.SerializerMethodField()
    tipo_conductor = serializers.SerializerMethodField()
    nombre_conductor = serializers.SerializerMethodField()
    nro_documento_conductor = serializers.CharField(source='id_persona_conductor.numero_documento')
    id_asignacion = serializers.IntegerField(source='id_vehiculo_conductor')  # Aquí incluimos el ID de la asignación

    class Meta:
        model = VehiculosAgendables_Conductor
        fields = ['id_asignacion', 'tipo_vehiculo', 'marca', 'placa', 'tipo_conductor', 'nombre_conductor', 'nro_documento_conductor', 'fecha_inicio_asignacion', 'fecha_final_asignacion']

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

    def get_marca(self, obj):
        if obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado:
            return obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado.id_marca.nombre
        return None

    def get_placa(self, obj):
        if obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado:
            return obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado.placa
        return None

    


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

    
class VehiculoPersonaLogueadaSerializer(serializers.ModelSerializer):
    marca = serializers.SerializerMethodField()
    contratista = serializers.CharField(source='id_hoja_vida_vehiculo.id_vehiculo_arrendado.empresa_contratista', read_only=True)
    placa = serializers.CharField(source='id_hoja_vida_vehiculo.id_vehiculo_arrendado.placa', read_only=True)

    class Meta:
        model = VehiculosAgendables_Conductor
        fields = ['id_vehiculo_conductor', 'id_hoja_vida_vehiculo', 'id_persona_conductor', 'marca', 'contratista', 'placa']

    def get_marca(self, obj):
        if obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado:
            return obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado.id_marca.nombre
        return None

    def to_representation(self, instance):
        persona_logueada = self.context['request'].user.persona
        vehiculos_asociados = VehiculosAgendables_Conductor.objects.filter(id_persona_conductor=persona_logueada)
        serialized_data = []
        for vehiculo in vehiculos_asociados:
            vehiculo_data = {
                'id_vehiculo_conductor': vehiculo.id_vehiculo_conductor,
                'id_hoja_vida_vehiculo': vehiculo.id_hoja_vida_vehiculo.id_hoja_de_vida,
                'id_persona_conductor': vehiculo.id_persona_conductor.id_persona,
                'marca': self.get_marca(vehiculo),
                'contratista': vehiculo.id_hoja_vida_vehiculo.id_vehiculo_arrendado.empresa_contratista if vehiculo.id_hoja_vida_vehiculo.id_vehiculo_arrendado else None,
                'placa': vehiculo.id_hoja_vida_vehiculo.id_vehiculo_arrendado.placa if vehiculo.id_hoja_vida_vehiculo.id_vehiculo_arrendado else None
            }
            serialized_data.append(vehiculo_data)
        return serialized_data


class InspeccionesVehiculosDiaCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = InspeccionesVehiculosDia
        fields = '__all__'
        extra_kwargs = {
            'dia_inspeccion': {'required': False},
            'fecha_registro': {'required': False},
            'id_persona_inspecciona': {'required': False},
            'observaciones': {'required': False},
        }

    
    def validate(self, data):
        # Realizamos las validaciones personalizadas

        # Si es_agendable no está presente o es True, no se actualiza el kilometraje ni la fecha
        if 'es_agendable' in data and not data['es_agendable']:
            # Si el vehículo no es agendable, actualizamos el kilometraje y la fecha solo para vehículos NO arrendados
            hoja_de_vida_vehiculo = data.get('id_hoja_vida_vehiculo')
            if hoja_de_vida_vehiculo and not hoja_de_vida_vehiculo.id_vehiculo_arrendado:
                # Actualizamos el kilometraje y la fecha
                hoja_de_vida_vehiculo.ultimo_kilometraje = data.get('kilometraje')
                hoja_de_vida_vehiculo.fecha_ultimo_kilometraje = data.get('dia_inspeccion')
                hoja_de_vida_vehiculo.save()

        # Verificamos si algún elemento de la inspección está mal
        campos_booleanos = [
            'dir_llantas_delanteras', 'dir_llantas_traseras', 'limpiabrisas_delantero',
            'limpiabrisas_traseros', 'nivel_aceite', 'estado_frenos', 'nivel_refrigerante',
            'apoyo_cabezas_piloto', 'apoyo_cabezas_copiloto', 'apoyo_cabezas_traseros',
            'frenos_generales', 'freno_emergencia', 'llantas_delanteras', 'llantas_traseras',
            'llanta_repuesto', 'espejos_laterales', 'espejo_retrovisor', 'cinturon_seguridad_delantero',
            'cinturon_seguridad_trasero', 'luces_altas', 'luces_media', 'luces_bajas', 'luces_parada',
            'luces_parqueo', 'luces_reversa', 'kit_herramientas', 'botiquin_completo', 'pito'
        ]

        if any(data.get(campo) == False for campo in campos_booleanos):
            # Si algún elemento está mal, marcamos el atributo requiere_verificacion como True
            data['requiere_verificacion'] = True

            # Si algún elemento está mal, se permite adjuntar una observación
            if 'observaciones' not in data or not data['observaciones']:
                raise serializers.ValidationError("Se requiere una observación debido a que hay elementos de inspección que están mal")

        # Si no hay elementos de inspección malos, requiere_verificacion se establece en False
        else:
            data['requiere_verificacion'] = False

        # verificacion_superior_realizada se establece en False por defecto
        data['verificacion_superior_realizada'] = False

        return data
    


class InspeccionVehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspeccionesVehiculosDia
        fields = '__all__'