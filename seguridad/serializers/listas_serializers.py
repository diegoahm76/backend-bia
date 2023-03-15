from rest_framework import serializers
from conservacion.models.mezclas_models import Mezclas, PreparacionMezclas, ItemsPreparacionMezcla
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from seguridad.models import (
    Municipio,
    Departamento
)

class MunicipiosSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Municipio
        fields = '__all__'

class DepartamentosSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Departamento
        fields = '__all__'