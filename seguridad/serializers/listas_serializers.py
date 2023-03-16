from rest_framework import serializers
from conservacion.models.mezclas_models import Mezclas, PreparacionMezclas, ItemsPreparacionMezcla
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from seguridad.models import (
    Municipio,
    Departamento,
    Paises,
    TipoDocumento
)

class MunicipiosSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Municipio
        fields = '__all__'

class DepartamentosSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Departamento
        fields = '__all__'

class TipoDocumentoSerializer(serializers.ModelSerializer):

    class Meta:
        model=TipoDocumento
        fields = '__all__'

class PaisSerializer(serializers.ModelSerializer):

    class Meta:
        model=Paises
        fields = '__all__'