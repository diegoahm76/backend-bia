from estaciones.models.estaciones_models import ParametrosReferencia
from rest_framework import serializers

class ParametrosEstacionesSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        Modelclass= ParametrosReferencia
        try:
            instance=Modelclass.objects.db_manager("bia-estaciones").create(**validated_data)
        except TypeError:
            raise TypeError()
        return instance

    class Meta:
        model=ParametrosReferencia
        fields='__all__'

class ParametrosEstacionesUpdateSerializer(serializers.ModelSerializer):
   
    def update(self, instance, validated_data):
        try:
           
            instance.fecha_modificacion=validated_data.get('fecha_modificacion', instance.fecha_modificacion)
            instance.frecuencia_solicitud_datos=validated_data.get('frecuencia_solicitud_datos',instance.frecuencia_solicitud_datos)
            instance.temperatura_ambiente_max=validated_data.get('temperatura_ambiente_max',instance.temperatura_ambiente_max)
            instance.temperatura_ambiente_min=validated_data.get('temperatura_ambiente_min',instance.temperatura_ambiente_min)
            instance.humedad_ambiente_max=validated_data.get('humedad_ambiente_max',instance.humedad_ambiente_max)
            instance.humedad_ambiente_min=validated_data.get('humedad_ambiente_min',instance.humedad_ambiente_min)
            instance.presion_barometrica_max=validated_data.get('presion_barometrica_max',instance.presion_barometrica_max)
            instance.presion_barometrica_min=validated_data.get('presion_barometrica_min',instance.presion_barometrica_min)
            instance.velocidad_viento_max=validated_data.get('velocidad_viento_max',instance.velocidad_viento_max)
            instance.velocidad_viento_min=validated_data.get('velocidad_viento_min',instance.velocidad_viento_min)
            instance.direccion_viento_max=validated_data.get('direccion_viento_max',instance.direccion_viento_max)
            instance.direccion_viento_min=validated_data.get('direccion_viento_min',instance.direccion_viento_min)
            instance.precipitacion_max=validated_data.get('precipitacion_max', instance.precipitacion_max)
            instance.precipitacion_min=validated_data.get('precipitacion_min', instance.precipitacion_min)
            instance.luminosidad_max=validated_data.get('luminosidad_max', instance.luminosidad_max)
            instance.luminosidad_min=validated_data.get('luminosidad_min', instance.luminosidad_min)
            instance.nivel_agua_max=validated_data.get('nivel_agua_max', instance.nivel_agua_max)
            instance.nivel_agua_min=validated_data.get('nivel_agua_min',instance.nivel_agua_min)
            instance.velocidad_agua_max=validated_data.get('velocidad_agua_max', instance.velocidad_agua_max)
            instance.velocidad_agua_min=validated_data.get('velocidad_agua_min', instance.velocidad_agua_min)
            instance.id_persona_modifica=validated_data.get('id_persona_modifica', instance.id_persona_modifica)

            instance.save(using='bia-estaciones')
        except TypeError:
            raise TypeError()
        return instance

    class Meta:
        model=ParametrosReferencia
        fields=['fecha_modificacion','frecuencia_solicitud_datos', 'temperatura_ambiente_max', 'temperatura_ambiente_min', 'humedad_ambiente_max', 'humedad_ambiente_min','presion_barometrica_max', 'presion_barometrica_min', 'velocidad_viento_max', 'velocidad_viento_min', 'direccion_viento_max', 'direccion_viento_min', 'precipitacion_max', 'precipitacion_min', 'luminosidad_max', 'luminosidad_min', 'nivel_agua_max', 'nivel_agua_min', 'velocidad_agua_max', 'velocidad_agua_min', 'id_persona_modifica']