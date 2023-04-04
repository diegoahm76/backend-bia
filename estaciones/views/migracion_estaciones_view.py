from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from estaciones.serializers.migracion_estaciones_serializer import MigracionSerializer
from estaciones.models.estaciones_models import  Migracion
# Listar Estaciones

class ConsultarMigracion(generics.ListAPIView):
    serializer_class = MigracionSerializer
    queryset = Migracion.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, request):
        estaciones = self.queryset.all()
        serializador = self.serializer_class(estaciones, many=True)
        return Response({'success': True, 'detail': 'Se encontraron las siguientes estaciones', 'data': serializador.data}, status=status.HTTP_200_OK)
