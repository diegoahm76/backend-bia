from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from gestion_documental.models.depositos_models import Deposito, EstanteDeposito


class DepositoCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  Deposito
        fields = '__all__'

class DepositoDeleteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  Deposito
        fields = '__all__'

class DepositoUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  Deposito
        fields = '__all__'

class DepositoGetSerializer(serializers.ModelSerializer):
    nombre_sucursal = serializers.ReadOnlyField(source='id_sucursal_entidad.descripcion_sucursal', default=None)
    municipio=serializers.ReadOnlyField(source='id_sucursal_entidad.municipio', default=None)
    class Meta:
        model =  Deposito
        fields = ['nombre_deposito','identificacion_por_entidad','orden_ubicacion_por_entidad','direccion_deposito','cod_municipio_nal','cod_pais_exterior','id_sucursal_entidad','nombre_sucursal','municipio','activo']


class EstanteDepositoCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  EstanteDeposito
        fields = '__all__'