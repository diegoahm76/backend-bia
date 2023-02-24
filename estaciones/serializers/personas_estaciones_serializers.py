from estaciones.models.estaciones_models import PersonasEstaciones
from rest_framework import serializers

class PersonasEstacionesSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        Modelclass= PersonasEstaciones
        try:
            instance=Modelclass.objects.db_manager("bia-estaciones").create(**validated_data)
        except TypeError:
            raise TypeError()
        return instance

    class Meta:
        model=PersonasEstaciones
        fields='__all__'

class PersonasEstacionesCreateSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        Modelclass = PersonasEstaciones
        try:
            instance = Modelclass.objects.using('bia-estaciones').create(**validated_data)
        except TypeError:
            raise TypeError()
        return instance

    class Meta:
        model = PersonasEstaciones
        fields = ['id_persona', 'cod_tipo_documento_id', 'numero_documento_id', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'entidad', 'cargo', 'email_notificacion', 'nro_celular_notificacion', 'observacion']

class PersonasEstacionesUpdateSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        Modelclass= PersonasEstaciones
        try:
            instance.primer_nombre=validated_data.get('primer_nombre',instance.primer_nombre)
            instance.segundo_nombre=validated_data.get('segundo_nombre',instance.segundo_nombre)
            instance.primer_apellido=validated_data.get('primer_apellido',instance.primer_apellido)
            instance.segundo_apellido=validated_data.get('segundo_apellido',instance.segundo_apellido)
            instance.entidad=validated_data.get('entidad',instance.entidad)
            instance.cargo=validated_data.get('cargo',instance.cargo)
            instance.email_notificacion=validated_data.get('email_notificacion',instance.email_notificacion)
            instance.nro_celular_notificacion=validated_data.get('nro_celular_notificacion',instance.nro_celular_notificacion)
            instance.observacion=validated_data.get('observacion',instance.observacion)

            instance.save(using='bia-estaciones')
        except TypeError:
            raise TypeError()
        return instance

    class Meta:
        model=PersonasEstaciones
        fields=['primer_nombre', 'primer_apellido', 'entidad', 'email_notificacion', 'nro_celular_notificacion','observacion']