from rest_framework import serializers
from recaudo.models.base_models import RegistrosConfiguracion,TipoCobro,TipoRenta,Variables,ValoresVariables



class RegistrosConfiguracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrosConfiguracion
        fields = '__all__'



class TipoCobroSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCobro
        fields = '__all__'

class TipoRentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRenta
        fields = '__all__'


class VariablesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variables
        fields = '__all__'


class ValoresVariablesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValoresVariables
        fields = '__all__'
