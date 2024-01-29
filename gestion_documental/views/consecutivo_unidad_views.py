from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from gestion_documental.models.consecutivo_unidad_models import ConfigTipoConsecAgno
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied

from gestion_documental.serializers.consecutivo_unidad_serializers import ConfigTipoConsecAgnoGetSerializer


class ConfigTipoConsecAgnoGetView(generics.ListAPIView):
    serializer_class = ConfigTipoConsecAgnoGetSerializer
    permission_classes = [IsAuthenticated]
    queryset = ConfigTipoConsecAgno.objects.all()
    
    def get(self, request):
        instance = self.get_queryset()

        if not instance:
            raise NotFound('No existe registro')
        
        serializer = self.serializer_class(instance,many=True)
        
        return Response({'success':True, 'detail':'se encontraron los siguientes registros', 'data': serializer.data}, status=status.HTTP_200_OK)
