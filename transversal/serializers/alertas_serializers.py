
from rest_framework import serializers

from transversal.models.alertas_models import AlertasBandejaAlertaPersona, AlertasGeneradas, AlertasProgramadas, BandejaAlertaPersona, ConfiguracionClaseAlerta, FechaClaseAlerta, PersonasAAlertar
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
        nombre_completo = serializers.SerializerMethodField()
        nombre_unidad=serializers.ReadOnlyField(source='id_unidad_org_lider.nombre', default=None)
        class Meta:
            model=PersonasAAlertar
            fields=('__all__')

        def get_nombre_completo(self, obj):
            primer_nombre = obj.id_persona
            #primer_apellido = obj.id_persona.primer_apellido
            return f'{primer_nombre} '
            
class PersonasAAlertarDeleteSerializer(serializers.ModelSerializer):
        class Meta:
            model=PersonasAAlertar
            fields=('__all__')



class AlertasProgramadasPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertasProgramadas
        fields = '__all__'
class AlertasProgramadasUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertasProgramadas
        fields = '__all__'
class AlertasProgramadasDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertasProgramadas
        fields = '__all__'

class AlertasGeneradasPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertasGeneradas
        fields = '__all__'

class AlertasBandejaAlertaPersonaPostSerializer(serializers.ModelSerializer):
     class Meta:
          model=AlertasBandejaAlertaPersona
          fields= '__all__'

class BandejaAlertaPersonaGetSerializer(serializers.ModelSerializer):
     class Meta:
          model=BandejaAlertaPersona
          fields= '__all__'



class AlertasBandejaAlertaPersonaGetSerializer(serializers.ModelSerializer):
    nivel_prioridad=serializers.ReadOnlyField(source='id_alerta_generada.nivel_prioridad', default=None)
    tipo_alerta=serializers.ReadOnlyField(source='id_alerta_generada.cod_categoria_alerta', default=None)
    fecha_hora=serializers.ReadOnlyField(source='id_alerta_generada.fecha_generada', default=None)
    nombre_clase_alerta=serializers.ReadOnlyField(source='id_alerta_generada.nombre_clase_alerta', default=None)
    id_modulo=serializers.ReadOnlyField(source='id_alerta_generada.id_modulo_destino.id_modulo', default=None)
    nombre_modulo=serializers.ReadOnlyField(source='id_alerta_generada.id_modulo_destino.nombre_modulo', default=None)
    ultima_repeticion=serializers.ReadOnlyField(source='id_alerta_generada.es_ultima_repeticion', default=None)
    class Meta:
          model=AlertasBandejaAlertaPersona
          fields= '__all__'

