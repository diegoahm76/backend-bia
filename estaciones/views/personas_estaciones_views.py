from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from estaciones.serializers.personas_estaciones_serializers import PersonasEstacionesCreateSerializer ,PersonasEstacionesUpdateSerializer, PersonasEstacionesSerializer
from estaciones.models.estaciones_models import PersonasEstaciones, PersonasEstacionesEstacion, Estaciones
from seguridad.permissions.permissions_recurso_hidrico import PermisoActualizarUsuariosEstacion, PermisoBorrarUsuariosEstacion, PermisoCrearUsuariosEstacion

# Listar persona

class ConsultarPersonaEstacion(generics.ListAPIView):
    serializer_class = PersonasEstacionesSerializer
    queryset = PersonasEstaciones.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, requet):
        personas = self.queryset.all()
        serializador = self.serializer_class(personas, many=True)
        return Response({'success': True, 'detail': 'Se encontraron las siguientes Personas', 'data': serializador.data}, status=status.HTTP_200_OK)

# Craer persona

class CrearPersonaEstacion(generics.CreateAPIView):
    serializer_class = PersonasEstacionesCreateSerializer
    queryset = PersonasEstaciones.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated, PermisoCrearUsuariosEstacion]

    def post(self, request):
        data=request.data
        
        # CREAR ASOCIACIO CON ESTACION
        estacion = Estaciones.objects.filter(id_estacion=data['id_estacion']).using("bia-estaciones").first()
        if not estacion:
            return Response({'success': False, 'detail': 'La estación elegida no existe'}, status=status.HTTP_400_BAD_REQUEST)
        
        del data['id_estacion']
        
        serializador=self.serializer_class(data=data, many=False)
        serializador.is_valid(raise_exception=True)
        guardar = serializador.save()
        
        PersonasEstacionesEstacion.objects.using("bia-estaciones").create(
            id_estacion = estacion,
            id_persona_estaciones = guardar
        )

        return Response({'success': True, 'detail': 'Se creo la persona de manera exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)
        

#Actualziar persona
class ActualizarPersonaEstacion(generics.UpdateAPIView):
    serializer_class = PersonasEstacionesUpdateSerializer
    queryset = PersonasEstaciones.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated, PermisoActualizarUsuariosEstacion]

    def put(self, request, pk):
        data=request.data
        persona=self.queryset.all().filter(id_persona=pk).first()
        if persona:
            serializador=self.serializer_class(persona, data=data)
            serializador.is_valid(raise_exception=True)
            serializador.save()
            return Response({'success': True, 'detail': 'Se Actualizo la persona de manera exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'detail': 'La persona ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
        
#Eliminar persona

class EliminarPersonaEstacion(generics.DestroyAPIView):
    serializer_class = PersonasEstacionesSerializer
    queryset = PersonasEstaciones.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated, PermisoBorrarUsuariosEstacion]

    def delete(self, request, pk):
        persona=self.queryset.all().filter(id_persona=pk).first()
        if persona:
            persona.delete()
            return Response({'success': True, 'detail': 'Se Elimino la persona de manera exitosa'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'La persona ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
        
#Consultar Persona Id
class ConsultarPersonaEstacionId(generics.ListAPIView):
    serializer_class = PersonasEstacionesSerializer
    queryset = PersonasEstaciones.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, requet, pk):
        persona=self.queryset.all().filter(id_persona=pk).first()
        if persona:
            serializador = self.serializer_class(persona, many=False)
            return Response({'success': True, 'detail': 'Se encontró la siguiente Persona', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'La Persona ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)