from almacen.models.generics_models import UnidadesMedida
from transversal.serializers.personas_serializers import PersonasSerializer
from almacen.models.generics_models import Magnitudes
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from almacen.models.mantenimientos_models import (
    ProgramacionMantenimientos,
    RegistroMantenimientos
)
        
class SerializerProgramacionMantenimientos(serializers.ModelSerializer):
    id_persona_solicita = PersonasSerializer(read_only=True)
    id_persona_anula = PersonasSerializer(read_only=True)
    class Meta:
        model=ProgramacionMantenimientos
        fields=('__all__')

class AnularMantenimientoProgramadoSerializer(serializers.ModelSerializer):
    justificacion_anulacion = serializers.CharField(max_length=255, min_length=10)
    class Meta:
        model=ProgramacionMantenimientos
        fields=['justificacion_anulacion']

class UpdateMantenimientoProgramadoSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProgramacionMantenimientos
        fields=['cod_tipo_mantenimiento', 'observaciones']
        
class SerializerRegistroMantenimientos(serializers.ModelSerializer):
    id_persona_realiza = PersonasSerializer(read_only=True)
    id_persona_diligencia = PersonasSerializer(read_only=True)
    class Meta:
        model=RegistroMantenimientos
        fields=('__all__')
        
class SerializerUpdateRegistroMantenimientos(serializers.ModelSerializer):
    # id_persona_diligencia = PersonasSerializer(read_only=True)
    class Meta:
        model=RegistroMantenimientos
        fields=('cod_tipo_mantenimiento','acciones_realizadas','dias_empleados','observaciones','cod_estado_final','valor_mantenimiento','contrato_mantenimiento','id_persona_realiza','id_persona_diligencia','ruta_documentos_soporte')


class SerializerProgramacionMantenimientosPost(serializers.ModelSerializer):
    class Meta:
        model=ProgramacionMantenimientos
        fields=('__all__')
        extra_kwargs = {
            'id_articulo': {'required': True},
            'cod_tipo_mantenimiento': {'required': True},
            'fecha_generada': {'required': True},
            'fecha_programada': {'required': True},
            'motivo_mantenimiento': {'required': True},
            'ejecutado': {'required': True}
        }

class SerializerRegistroMantenimientosPost(serializers.ModelSerializer):
    class Meta:
        model=RegistroMantenimientos
        fields=('__all__')
