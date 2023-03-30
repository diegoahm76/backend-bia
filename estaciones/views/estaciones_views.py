from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from estaciones.serializers.estaciones_serializers import EstacionesSerializer
from estaciones.models.estaciones_models import Estaciones, Datos

# Listar Estaciones


class ConsultarEstacion(generics.ListAPIView):
    serializer_class = EstacionesSerializer
    queryset = Estaciones.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, request):
        estaciones = self.queryset.all()
        serializador = self.serializer_class(estaciones, many=True)
        return Response({'success': True, 'detail': 'Se encontraron las siguientes estaciones', 'data': serializador.data}, status=status.HTTP_200_OK)

# Craer estacioens


class CrearEstacion(generics.CreateAPIView):
    serializer_class = EstacionesSerializer
    queryset = Estaciones.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        print('PASOOOOOOOO')
        estaciones = self.queryset.all().filter(
            nombre_estacion=data["nombre_estacion"]).first()
        print('ESTACIONESSS', estaciones)
        if estaciones:
            return Response({'success': False, 'detail': 'La estacion ya existe'}, status=status.HTTP_403_FORBIDDEN)

        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Se creo la estación de manera exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)


# Actualziar estaciones

class ActualizarEstacion(generics.UpdateAPIView):
    serializer_class = EstacionesSerializer
    queryset = Estaciones.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data
        persona_logeada = request.user.persona.id_persona
        data['id_persona_modifica'] = persona_logeada

        estacion = self.queryset.all().filter(id_estacion=pk).first()
        if not estacion:
            return Response({'success': False, 'detail': 'La estación ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializador = self.serializer_class(estacion, data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Se Actualizo la estación de manera exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)


# Eliminar estación

class EliminarEstacion(generics.DestroyAPIView):
    serializer_class = EstacionesSerializer
    queryset = Estaciones.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        estacion = self.queryset.all().filter(id_estacion=pk).first()

        if estacion:
            # Verificar si la estación tiene registros en Datos
            tiene_registros = Datos.objects.filter(id_estacion=pk).using("bia-estaciones").exists()

            if tiene_registros:
                return Response({'success': False, 'detail': 'No se puede eliminar la estación porque tiene registros en Datos'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                estacion.delete()
                return Response({'success': True, 'detail': 'Se eliminó la estación de manera exitosa'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'La estación ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)


# Consultar Estacion Id
class ConsultarEstacionId(generics.ListAPIView):
    serializer_class = EstacionesSerializer
    queryset = Estaciones.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, requet, pk):
        estacion = self.queryset.all().filter(id_estacion=pk).first()
        if estacion:
            serializador = self.serializer_class(estacion, many=False)
            return Response({'success': True, 'detail': 'Se encontró la siguiente estación', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'La estación ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
