from rest_framework import serializers
from recaudo.models.base_models import  AdministraciondePersonal, ConfigaraicionInteres, IndicadoresSemestral, RegistrosConfiguracion,TipoCobro,TipoRenta,Variables,ValoresVariables  # Ajusta la ruta de importación según la estructura de tu proyecto



class RegistrosConfiguracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrosConfiguracion
        fields = '__all__'



class TipoCobroSerializer(serializers.ModelSerializer):
    nombre_renta_asociado = serializers.ReadOnlyField(source='tipo_renta_asociado.nombre_tipo_renta') 

    class Meta:
        model = TipoCobro
        fields = '__all__'

class TipoRentaSerializer(serializers.ModelSerializer):
    nombre_cobro = serializers.ReadOnlyField(source='tipo_cobro_asociado.nombre_tipo_cobro')

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



class AdministraciondePersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdministraciondePersonal
        fields = '__all__'
class ConfigaraicionInteresSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigaraicionInteres
        fields = '__all__'




class IndicadoresSemestralSerializer(serializers.ModelSerializer):

    class Meta:
        model = IndicadoresSemestral
        fields = '__all__'

 