from rest_framework import serializers

from transversal.models.notificaciones_models import (
    MedioNotificacion,
    Notificacion,
    DespachoNotificacion,
    RespuestaNotificacion
)

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


class NotificacionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notificacion
        fields = '__all__'


class DespachoNotificacionSerializer(serializers.ModelSerializer):

    class Meta:
        model = DespachoNotificacion
        fields = '__all__'

    
class RespuestaNotificacionSerializer(serializers.ModelSerializer):

    class Meta:
        model = RespuestaNotificacion
        fields = '__all__'


