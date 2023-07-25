
from rest_framework import serializers

from transversal.models.alertas_models import ConfiguracionClaseAlerta, FechaClaseAlerta, PersonasAAlertar
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator


class ConfiguracionClaseAlertaGetSerializer(serializers.ModelSerializer):
        class Meta:
            model=ConfiguracionClaseAlerta
            fields='__all__'


class ConfiguracionClaseAlertaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionClaseAlerta
        fields = '__all__'
        
class FechaClaseAlertaPostSerializer(serializers.ModelSerializer):
        class Meta:
            model=FechaClaseAlerta
            fields=('__all__')

            validators = [
                UniqueTogetherValidator(
                queryset=FechaClaseAlerta.objects.all(),
                fields=['dia_cumplimiento', 'mes_cumplimiento','age_cumplimiento'],
                message='Ya existe esta fecha en la alerta.'
            )
        ]


class FechaClaseAlertaGetSerializer(serializers.ModelSerializer):
        class Meta:
            model=FechaClaseAlerta
            fields='__all__'

class FechaClaseAlertaDeleteSerializer(serializers.ModelSerializer):
        
        class Meta:
            model=FechaClaseAlerta
            fields='__all__'



#PERSONA ALERTA

class PersonasAAlertarPostSerializer(serializers.ModelSerializer):
        class Meta:
            model=PersonasAAlertar
            fields=('__all__')

class PersonasAAlertarGetSerializer(serializers.ModelSerializer):
        class Meta:
            model=PersonasAAlertar
            fields=('__all__')
            
class PersonasAAlertarDeleteSerializer(serializers.ModelSerializer):
        class Meta:
            model=PersonasAAlertar
            fields=('__all__')