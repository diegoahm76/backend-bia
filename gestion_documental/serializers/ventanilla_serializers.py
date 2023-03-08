from seguridad.models import Personas
from rest_framework import serializers


class PersonasSerializer(serializers.ModelSerializer):
    class Meta:
        
        fields = '__all__'
        model = Personas
        
class PersonasUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        
        exclude = ['primer_nombre','segundo_nombre','primer_apellido','segundo_apellido','tipo_documento','numero_documento','tipo_persona']
        model = Personas
        
class ActualizarAutorizacionesPersona(serializers.ModelSerializer):
    
    fields = ['acepta_notificacion_sms','acepta_notificacion_email','acepta_tratamiento_datos']
    model = Personas