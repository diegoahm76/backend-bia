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

class EstanteDepositoCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  EstanteDeposito
        fields = '__all__'