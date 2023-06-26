from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from transversal.serializers.notificaciones_serializers import(
    DatosRemitenteSerializer,
    MedioNotificacionSerializer,
    NotificacionSerializer,
    DespachoNotificacionSerializer,
    RespuestaNotificacionSerializer
)

from transversal.models.notificaciones_models import (
    MedioNotificacion,
    Notificacion,
)


from recaudo.models import Deudores


class MedioNotificacionView(generics.ListAPIView):
    serializer_class = MedioNotificacionSerializer
    permission_classes = [IsAuthenticated]
    queryset = MedioNotificacion.objects.all() 

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail':'Se muestran los medios de las notificaciones', 'data': serializer.data}, status=status.HTTP_200_OK)


class DatosRemitenteView(generics.ListAPIView):
    queryset = Deudores.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = DatosRemitenteSerializer

    def get(self, request, id):
        queryset = Deudores.objects.filter(codigo=id).first()
        if not queryset:
            raise NotFound('No se encontró ningun registro con el parámetro ingresado')
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'detail':'Se muestra los datos del remitente', 'data': serializer.data}, status=status.HTTP_200_OK)   


class CrearNotificacionView(generics.CreateAPIView):
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        funcionario = request.user.persona.id_persona
        data = request.data
        data['id_funcionario'] = funcionario
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail':'Se crea la notificacion'},status=status.HTTP_200_OK)
    

class CrearDespachoNotificacionView(generics.CreateAPIView):
    serializer_class = DespachoNotificacionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        funcionario = request.user.persona.id_persona
        data = request.data
        #data['id_funcionario'] = funcionario
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail':'Se crea el despacho de la notificacion'},status=status.HTTP_200_OK)


class CrearRespuestaNotificacionView(generics.CreateAPIView):
    serializer_class = RespuestaNotificacionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        funcionario = request.user.persona.id_persona
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail':'Se crea la respuesta de la notificacion'},status=status.HTTP_200_OK)

