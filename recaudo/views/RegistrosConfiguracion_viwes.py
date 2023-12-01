from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from recaudo.serializers.registrosconfiguracion_serializer import RegistrosConfiguracionSerializer
from recaudo.models.base_models import RegistrosConfiguracion


# Vista get para las 4 tablas de zonas hidricas
class Vista_RegistrosConfiguracion (generics.ListAPIView):
    queryset = RegistrosConfiguracion.objects.all()
    serializer_class = RegistrosConfiguracionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cuencas = RegistrosConfiguracion.objects.all()
        serializer = self.serializer_class(cuencas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    



class Crear_RegistrosConfiguracion(generics.CreateAPIView):
    queryset = RegistrosConfiguracion.objects.all()
    serializer_class = RegistrosConfiguracionSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
           
            
            # Agregar lógica adicional si es necesario, por ejemplo, asignar valores antes de guardar
            # serializer.validated_data['campo_adicional'] = valor

            serializer.save()

            return Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({'error': 'Error al crear el registro', 'detail': e.detail})
        
    

class Borrar_RegistrosConfiguracion(generics.DestroyAPIView):
    queryset = RegistrosConfiguracion.objects.all()
    serializer_class = RegistrosConfiguracionSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'success': True, 'detail': 'Registro eliminado correctamente'},
                            status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({e.detail})
        



class Actualizar_RegistrosConfiguracion(generics.UpdateAPIView):
    queryset = RegistrosConfiguracion.objects.all()
    serializer_class = RegistrosConfiguracionSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene la instancia existente
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)  # Valida los datos
        serializer.save()  # Guarda la instancia con los datos actualizados

        return Response(serializer.data, status=status.HTTP_200_OK)
    

