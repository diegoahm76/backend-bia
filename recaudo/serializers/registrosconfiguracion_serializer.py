from rest_framework import serializers
from recaudo.models.base_models import  AdministraciondePersonal, ConfigaraicionInteres, IndicadorValor, IndicadoresSemestral, RegistrosConfiguracion,TipoCobro,TipoRenta,Variables,ValoresVariables  # Ajusta la ruta de importación según la estructura de tu proyecto



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

class IndicadorValorSerializer(serializers.ModelSerializer):

    class Meta:
        model = IndicadorValor
        fields = '__all__'


# class IndicadoresSemestralSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = IndicadoresSemestral
#         fields = '__all__'

 
class IndicadorValorSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorValor
        fields = ['mes_id', 'valor', 'variable_1', 'variable_2']


class IndicadorValorSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorValor
        fields = ['mes_id', 'valor', 'variable_1', 'variable_2']

class IndicadoresSemestralSerializer(serializers.ModelSerializer):
    indicadorvalor_set = IndicadorValorSerializer(many=True)

    class Meta:
        model = IndicadoresSemestral
        fields = ['id_indicador', 'proceso', 'nombre_indicador', 'frecuencia_medicion', 'formula_indicador',
                  'vigencia_reporta', 'dependencia_grupo_regional', 'objetivo_indicador',
                  'unidad_medicion_reporte', 'descripcion_variable_1', 'descripcion_variable_2',
                  'origen_datos', 'fecha_creacion', 'responsable_creacion', 'tipo_indicador',
                  'formulario', 'indicadorvalor_set']

    def create(self, validated_data):
        indicador_valores_data = validated_data.pop('indicadorvalor_set')
        indicador_semestral = IndicadoresSemestral.objects.create(**validated_data)
        for indicador_valor_data in indicador_valores_data:
            IndicadorValor.objects.create(indicador=indicador_semestral, **indicador_valor_data)
        return indicador_semestral

    def update(self, instance, validated_data):
        indicador_valores_data = validated_data.pop('indicadorvalor_set', None)
        indicador_valores = instance.indicadorvalor_set.all()

        instance = super().update(instance, validated_data)

        if indicador_valores_data is not None:
            # Eliminar indicador_valores que no están presentes en los datos enviados
            for indicador_valor in indicador_valores:
                indicador_valor.delete()

            # Crear o actualizar indicador_valores que se encuentran en los datos enviados
            for indicador_valor_data in indicador_valores_data:
                IndicadorValor.objects.create(indicador=instance, **indicador_valor_data)

        return instance
