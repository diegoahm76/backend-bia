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
    nombre_variable = serializers.ReadOnlyField(source='variables.nombre')
    id_tipo_renta = serializers.ReadOnlyField(source='variables.tipo_renta.id_tipo_renta')
    id_tipo_cobro = serializers.ReadOnlyField(source='variables.tipo_cobro.id_tipo_cobro')
    nombre_tipo_renta = serializers.ReadOnlyField(source='variables.tipo_renta.nombre_tipo_renta')
    nombre_tipo_cobro = serializers.ReadOnlyField(source='variables.tipo_cobro.nombre_tipo_cobro')

    class Meta:
        model = ValoresVariables
        fields = '__all__'
