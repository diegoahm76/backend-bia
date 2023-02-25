from estaciones.models.estaciones_models import ConfiguracionAlertaPersonas
from rest_framework import serializers

class ConfiguracionAlertasCreateSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        Modelclass= ConfiguracionAlertaPersonas
        try:
            instance=Modelclass.objects.db_manager('bia-estaciones').create(**validated_data)
        except TypeError:
            raise TypeError()
        return instance

    class Meta:
        model=ConfiguracionAlertaPersonas
        fields='__all__'

class ConfiguracionAlertasUpdateSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        Modelclass= ConfiguracionAlertaPersonas
        try:
            instance.nombre_variable_alarma=validated_data.get('nombre_variable_alarma',instance.nombre_variable_alarma)
            instance.mensaje_alarma_maximo=validated_data.get('mensaje_alarma_maximo',instance.mensaje_alarma_maximo)
            instance.mensaje_alarma_minimo=validated_data.get('mensaje_alarma_minimo',instance.mensaje_alarma_minimo)
            instance.mensaje_no_alarma=validated_data.get('mensaje_no_alarma',instance.mensaje_no_alarma)
            instance.frecuencia_alarma=validated_data.get('frecuencia_alarma',instance.frecuencia_alarma)

            instance.save(using='bia-estaciones')
        except TypeError:
            raise TypeError()
        return instance

    class Meta:
        model=ConfiguracionAlertaPersonas
        fields=['nombre_variable_alarma', 'mensaje_alarma_maximo', 'mensaje_alarma_minimo', 'mensaje_no_alarma', 'frecuencia_alarma']