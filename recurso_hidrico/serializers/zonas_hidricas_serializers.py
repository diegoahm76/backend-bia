from rest_framework import serializers

from recurso_hidrico.models.zonas_hidricas_models import MacroCuencas, SubZonaHidrica, TipoAguaZonaHidrica, TipoZonaHidrica, ZonaHidrica


class MacroCuencasSerializer(serializers.ModelSerializer):
    class Meta:
        model = MacroCuencas
        fields = '__all__'

class ZonaHidricaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonaHidrica
        fields = '__all__'


class TipoZonaHidricaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoZonaHidrica
        fields = '__all__'


class TipoAguaZonaHidricaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAguaZonaHidrica
        fields = '__all__'

class SubZonaHidricaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubZonaHidrica
        fields = '__all__'



