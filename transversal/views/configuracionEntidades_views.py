from django.forms import ValidationError
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from transversal.serializers.entidades_serializers import ConfiguracionEntidadSerializer
from transversal.models import ConfiguracionEntidad


class GetConfiguracionEntidadByID(generics.GenericAPIView):

    serializer_class = ConfiguracionEntidadSerializer
    queryset = ConfiguracionEntidad.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        
        confEntidad = ConfiguracionEntidad.objects.filter(id_persona_entidad=pk)
        serializer = self.serializer_class(confEntidad,many=True)
        
        if not confEntidad:
            raise ValidationError("El registro de configuracion  que busca no existe")
        
        return Response({'success':True,'detail':"Se encontro el siguiente registro.",'data':serializer.data},status=status.HTTP_200_OK)
            

class UpdateConfiguracionEntidad(generics.UpdateAPIView):
    serializer_class = ConfiguracionEntidadSerializer
    queryset = ConfiguracionEntidad.objects.all()
    lookup_field = 'id_persona_entidad'

    def put(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtener la instancia del objeto a actualizar
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)