from estaciones.models.estaciones_models import Estaciones, PersonasEstacionesEstacion
from rest_framework import serializers
from estaciones.serializers.personas_estaciones_serializers import PersonasEstacionesSerializer

class EstacionesSerializer(serializers.ModelSerializer):
    personas = serializers.SerializerMethodField()

    def get_personas(self, obj):
        personas = PersonasEstacionesEstacion.objects.filter(id_estacion=obj.id_estacion).using('bia-estaciones')
        personas_instancias = [persona.id_persona_estaciones for persona in personas]
        serializador = PersonasEstacionesSerializer(personas_instancias, many=True)
        return serializador.data

    def create(self, validated_data):
        Modelclass= Estaciones
        try:
            instance=Modelclass.objects.db_manager("bia-estaciones").create(**validated_data)
        except TypeError:
            raise TypeError()
        return instance

    def update(self, instance, validated_data):
        Modelclass= Estaciones
        try:
            instance.fecha_modificacion=validated_data.get('fecha_modificacion',instance.fecha_modificacion)
            instance.nombre_estacion=validated_data.get('nombre_estacion',instance.nombre_estacion)
            instance.cod_tipo_estacion=validated_data.get('cod_tipo_estacion',instance.cod_tipo_estacion)
            instance.latitud=validated_data.get('latitud',instance.latitud)
            instance.longitud=validated_data.get('longitud',instance.longitud)
            instance.cod_municipio=validated_data.get('cod_municipio',instance.cod_municipio)
            instance.indicaciones_ubicacion=validated_data.get('indicaciones_ubicacion',instance.indicaciones_ubicacion)
            instance.fecha_modificacion_coordenadas=validated_data.get('fecha_modificacion_coordenadas',instance.fecha_modificacion_coordenadas)
            instance.id_persona_modifica=validated_data.get('id_persona_modifica',instance.id_persona_modifica)

            instance.save(using='bia-estaciones')
        except TypeError:
            raise TypeError()
        return instance

    class Meta:
        model=Estaciones
        fields='__all__'