from datetime import datetime
from estaciones.models.estaciones_models import Estaciones, PersonasEstacionesEstacion
from rest_framework import serializers
from estaciones.serializers.personas_estaciones_serializers import PersonasEstacionesSerializer
from transversal.models.personas_models import Personas


class EstacionesSerializer(serializers.ModelSerializer):
    personas = serializers.SerializerMethodField()
    nombre_persona_modifica = serializers.SerializerMethodField()

    def get_personas(self, obj):
        personas = PersonasEstacionesEstacion.objects.filter(
            id_estacion=obj.id_estacion).using('bia-estaciones')
        personas_instancias = [
            persona.id_persona_estaciones for persona in personas]
        serializador = PersonasEstacionesSerializer(
            personas_instancias, many=True)
        return serializador.data
    
    def get_nombre_persona_modifica(self, obj):
        nombre_persona_modifica = None

        persona = Personas.objects.filter(id_persona=obj.id_persona_modifica).first()
        if persona:
            nombre_list = [persona.primer_nombre, persona.segundo_nombre, persona.primer_apellido, persona.segundo_apellido]
            nombre_persona_modifica = ' '.join(item for item in nombre_list if item is not None)
        return nombre_persona_modifica

    def create(self, validated_data):
        Modelclass = Estaciones
        try:
            instance = Modelclass.objects.db_manager(
                "bia-estaciones").create(**validated_data)
        except TypeError:
            raise TypeError()
        return instance

    def update(self, instance, validated_data):
        # Verificar si se está actualizando algún campo
        if validated_data:
        # Actualizar el campo fecha_modificacion con la fecha y hora actuales
            instance.fecha_modificacion = datetime.now()

            # Verificar si se está actualizando la latitud o longitud
            latitud = validated_data.get('latitud', instance.latitud)
            longitud = validated_data.get('longitud', instance.longitud)
            if latitud != instance.latitud or longitud != instance.longitud:
                # Actualizar el campo fecha_modificacion_coordenadas con la fecha y hora actuales
                instance.fecha_modificacion_coordenadas = datetime.now()

            # Actualizar la instancia con los datos validados
            instance.nombre_estacion = validated_data.get(
                'nombre_estacion', instance.nombre_estacion)
            instance.cod_tipo_estacion = validated_data.get(
                'cod_tipo_estacion', instance.cod_tipo_estacion)
            instance.latitud = latitud
            instance.longitud = longitud
            instance.cod_municipio = validated_data.get(
                'cod_municipio', instance.cod_municipio)
            instance.indicaciones_ubicacion = validated_data.get(
                'indicaciones_ubicacion', instance.indicaciones_ubicacion)
            instance.id_persona_modifica = validated_data.get(
                'id_persona_modifica', instance.id_persona_modifica)

            # Guardar los cambios en la base de datos usando el nombre de la base de datos 'bia-estaciones'
            instance.save(using='bia-estaciones')
            # Retornar la instancia actualizada
            return instance

    class Meta:
        model = Estaciones
        fields = '__all__'
