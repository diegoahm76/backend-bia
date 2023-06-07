from rest_framework import serializers

from recaudo.models.notificaciones_models import (
    MedioNotificacion
)

from seguridad.models import Personas

from recaudo.models.liquidaciones_models import Deudores


class MedioNotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedioNotificacion
        fields = '__all__'


class DatosRemitenteSerializer(serializers.ModelSerializer):
    ubicacion = serializers.SerializerMethodField()
    
    def get_ubicacion(self, obj):
        ubicacion = obj.ubicacion_id.nombre
        return ubicacion

    class Meta:
        model = Deudores
        fields = ('codigo', 'identificacion', 'nombres', 'apellidos', 'email', 'ubicacion')


