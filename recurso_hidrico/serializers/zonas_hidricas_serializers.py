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
    nombre_tipo_agua = serializers.ReadOnlyField(source='id_tipo_zona_hidrica.nombre_tipo_agua_zona_hidrica')
    nombre_tipo_zona_hidrica  = serializers.ReadOnlyField(source='id_tipo_zona_hidrica.nombre_tipo_zona_hidrica')
    nombre_macrocuenca = serializers.ReadOnlyField(source='id_zona_hidrica.id_macro_cuenca.nombre_macro_cuenca')
    class Meta:
        model = SubZonaHidrica
        fields = '__all__'



class SubZonaHidricaSerializerr(serializers.ModelSerializer):
    nombre_zona_hidrica_macrocuenca = serializers.ReadOnlyField(source='id_zona_hidrica.id_macro_cuenca.nombre_macro_cuenca')
    id_zona_hidrica_macrocuenca = serializers.ReadOnlyField(source='id_zona_hidrica.id_macro_cuenca.id_macro_cuenca')
    nombre_zona_hidirca= serializers.ReadOnlyField(source='id_zona_hidrica.nombre_zona_hidrica')


    class Meta:
        model = SubZonaHidrica
        fields = '__all__'