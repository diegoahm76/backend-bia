from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from recurso_hidrico.models.zonas_hidricas_models import ZonaHidrica, MacroCuencas

from recurso_hidrico.serializers.zonas_hidricas_serializers import ZonaHidricaSerializer, MacroCuencasSerializer

class MacroCuencasListView (generics.ListAPIView):
    queryset = ZonaHidrica.objects.all()
    serializer_class = MacroCuencasSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cuencas = MacroCuencas.objects.all()
        serializer = self.serializer_class(cuencas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    

class ZonaHidricaListView (generics.ListCreateAPIView):
    queryset = ZonaHidrica.objects.all()
    serializer_class = ZonaHidricaSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request):
        zonas = ZonaHidrica.objects.all()
        serializer = self.serializer_class(zonas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)