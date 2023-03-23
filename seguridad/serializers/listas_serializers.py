from rest_framework import serializers
from conservacion.models.mezclas_models import Mezclas, PreparacionMezclas, ItemsPreparacionMezcla
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from seguridad.models import (
    Municipio,
    Departamento,
)

class MunicipiosSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='nombre')
    value = serializers.CharField(source='cod_municipio')

    class Meta:
        model = Municipio
        fields = ['label', 'value']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'cod_municipio' in data:
            del data['cod_municipio']
        return data
    
class DepartamentosSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='nombre')
    value = serializers.CharField(source='cod_departamento')

    class Meta:
        model = Departamento
        fields = ['label', 'value']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'cod_departamento' in data:
            del data['cod_departamento']
        return data
