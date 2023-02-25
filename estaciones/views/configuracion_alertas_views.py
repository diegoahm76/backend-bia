from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from estaciones.serializers.configuracion_alertas_serializers import ConfiguracionAlertasCreateSerializer ,ConfiguracionAlertasUpdateSerializer
from estaciones.models.estaciones_models import ConfiguracionAlertaPersonas

# Listar Alerta

class ConsultarAlertaEstacion(generics.ListAPIView):
    serializer_class = ConfiguracionAlertasCreateSerializer
    queryset = ConfiguracionAlertaPersonas.objects.all().using('bia-estaciones')
    permission_classes = [IsAuthenticated]

    def get(self, requet):
        alertas = self.queryset.all()
        serializador = self.serializer_class(alertas, many=True)
        return Response({'success': True, 'detail': 'Se encontraron las siguientes Alertas', 'data': serializador.data}, status=status.HTTP_200_OK)

# Craer Alerta

class CrearAlertaEstacion(generics.CreateAPIView):
    serializer_class = ConfiguracionAlertasCreateSerializer
    queryset = ConfiguracionAlertaPersonas.objects.all().using('bia-estaciones')
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data=request.data
        serializador=self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Se creo la Alerta de manera exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)
        

#Actualziar Alerta
class ActualizarAlertaEstacion(generics.UpdateAPIView):
    serializer_class = ConfiguracionAlertasUpdateSerializer
    queryset = ConfiguracionAlertaPersonas.objects.all().using('bia-estaciones')
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data=request.data
        alerta=self.queryset.all().filter(id_confi_alerta_persona=pk).first()
        if alerta:
            serializador=self.serializer_class(alerta, data=data)
            serializador.is_valid(raise_exception=True)
            serializador.save()
            return Response({'success': True, 'detail': 'Se Actualizo la Alerta de manera exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'detail': 'La Alerta ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
        
#Eliminar Alerta

class EliminarAlertaEstacion(generics.DestroyAPIView):
    serializer_class = ConfiguracionAlertasCreateSerializer
    queryset = ConfiguracionAlertaPersonas.objects.all().using('bia-estaciones')
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        alerta=self.queryset.all().filter(id_confi_alerta_persona=pk).first()
        if alerta:
            alerta.delete()
            return Response({'success': True, 'detail': 'Se Elimino la Alerta de manera exitosa'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'La Alerta ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
        
#Consultar Alerta Id
class ConsultarAlertaEstacionId(generics.ListAPIView):
    serializer_class = ConfiguracionAlertasCreateSerializer
    queryset = ConfiguracionAlertaPersonas.objects.all().using('bia-estaciones')
    permission_classes = [IsAuthenticated]

    def get(self, requet, pk):
        alerta=self.queryset.all().filter(id_confi_alerta_persona=pk).first()
        if alerta:
            serializador = self.serializer_class(alerta, many=False)
            return Response({'success': True, 'detail': 'Se encontró la siguiente Alerta', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'La Alerta ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)