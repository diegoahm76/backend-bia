from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from transversal.serializers.notificaciones_serializers import(
    DatosRemitenteSerializer,
    MedioNotificacionSerializer
)

from transversal.models.notificaciones_models import (
    MedioNotificacion
)


from recaudo.models import Deudores


class MedioNotificacionView(generics.ListAPIView):
    serializer_class = MedioNotificacionSerializer
    queryset = MedioNotificacion.objects.all() 

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail':'Se muestran los medios de las notificaciones', 'data': serializer.data}, status=status.HTTP_200_OK)
    



class DatosRemitenteView(generics.ListAPIView):
    queryset = Deudores.objects.all()
    serializer_class = DatosRemitenteSerializer

    def get(self, request, id):
        queryset = Deudores.objects.filter(codigo=id).first()
        if not queryset:
            raise NotFound('No se encontró ningun registro con el parámetro ingresado')
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'detail':'Se muestra los datos del remitente', 'data': serializer.data}, status=status.HTTP_200_OK)   
