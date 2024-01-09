import os
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import generics,status

from rest_framework.permissions import IsAuthenticated
from seguridad.utils import Util
from rest_framework.response import Response

class EnviarSMSView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        telefono = request.data.get('telefono')
        mensaje = request.data.get('mensaje')

        if not telefono or not mensaje:
            raise ValidationError('Por favor, proporciona el teléfono y el mensaje que desea enviar.')

        Util.send_sms(telefono, mensaje)
        
        return Response({
            'success': True,
            'detail': 'SMS enviado correctamente'
        }, status=status.HTTP_200_OK)