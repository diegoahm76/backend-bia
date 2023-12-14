from rest_framework import serializers
from transversal.models.base_models import (
    Municipio,
    Departamento,
    Paises,
    Sexo
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
    
class PaisesSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='nombre')
    value = serializers.CharField(source='cod_pais')

    class Meta:
        model = Paises
        fields = ['label', 'value']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'cod_pais' in data:
            del data['cod_pais']
        return data

class SexoSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='nombre')
    value = serializers.CharField(source='cod_sexo')

    class Meta:
        model = Sexo
        fields = ['label', 'value']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'cod_sexo' in data:
            del data['cod_sexo']
        return data