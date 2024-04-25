from django.shortcuts import render
from rest_framework.response import Response
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from estaciones.serializers.parametros_serializers import ParametrosEstacionesUpdateSerializer, ParametrosEstacionesSerializer
from estaciones.models.estaciones_models import ParametrosReferencia
from seguridad.permissions.permissions_recurso_hidrico import PermisoActualizarParametrosReferenciaSensoresRecu

class ConsultarParametroEstacion(generics.ListAPIView):
    serializer_class = ParametrosEstacionesSerializer
    queryset = ParametrosReferencia.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, requet):
        parametros = self.queryset.all()
        if parametros:
            serializador = self.serializer_class(parametros, many=True)
            return Response({'success': True, 'detail': 'Se encontraron las siguientes parametros', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'Error en el parametro'}, status=status.HTTP_404_NOT_FOUND)

class ActualizarParametro(generics.UpdateAPIView):
    serializer_class = ParametrosEstacionesUpdateSerializer
    queryset = ParametrosReferencia.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated, PermisoActualizarParametrosReferenciaSensoresRecu]

    def put(self, request, pk):
        data=request.data
        persona_logeada = request.user.persona.id_persona
        data['id_persona_modifica'] = persona_logeada
        fecha_modificacion=datetime.now()
        data['fecha_modificacion']= fecha_modificacion

        parametro=self.queryset.all().filter(id_parametro_referencia=pk).first()
        
        if parametro:
            serializador=self.serializer_class(parametro, data=data)
            serializador.is_valid(raise_exception=True)
            serializador.save()
            return Response({'success': True, 'detail': 'Se Actualizo el parametro de manera exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'detail': 'Error en el parametro'}, status=status.HTTP_404_NOT_FOUND)

    #CONSULTAR POR ID
class ConsultarParametroEstacionId(generics.ListAPIView):
    serializer_class = ParametrosEstacionesSerializer
    queryset = ParametrosReferencia.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, requet, pk):
        parametro=self.queryset.all().filter(id_parametro_referencia=pk).first()
        if parametro:
            serializador = self.serializer_class(parametro, many=False)
            return Response({'success': True, 'detail': 'Se encontró el siguiente parametro', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'El parametro ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)