from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from estaciones.serializers.datos_serializers import DatosSerializer
from estaciones.models.estaciones_models import Datos

# Listar Estaciones


class ConsultarDatos(generics.ListAPIView):
    serializer_class = DatosSerializer
    queryset = Datos.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, request):
        datos = self.queryset.all()
        if datos:
            serializador = self.serializer_class(datos, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguentes datos', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'No se encontraron datos'}, status=status.HTTP_404_NOT_FOUND)

# Craer estacioens