
from rest_framework import serializers

from transversal.models.alertas_models import ConfiguracionClaseAlerta, FechaClaseAlerta



class ConfiguracionClaseAlertaGetSerializer(serializers.ModelSerializer):
        class Meta:
            model=ConfiguracionClaseAlerta
            fields='__all__'

class FechaClaseAlertaPostSerializer(serializers.ModelSerializer):
        class Meta:
            model=FechaClaseAlerta
            #fields=('__all__')
            fields=[    "cod_clase_alerta",
            "dia_cumplimiento",
            "mes_cumplimiento",]


class FechaClaseAlertaGetSerializer(serializers.ModelSerializer):
        class Meta:
            model=FechaClaseAlerta
            fields='__all__'

class FechaClaseAlertaDeleteSerializer(serializers.ModelSerializer):
        class Meta:
            model=FechaClaseAlerta
            fields='__all__'