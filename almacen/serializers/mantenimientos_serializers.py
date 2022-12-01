from almacen.models.generics_models import UnidadesMedida
from seguridad.serializers.personas_serializers import PersonasSerializer
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