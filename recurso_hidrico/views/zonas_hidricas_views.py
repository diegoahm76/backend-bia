from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from recurso_hidrico.models.zonas_hidricas_models import ZonaHidrica, MacroCuencas,TipoZonaHidrica,SubZonaHidrica

from recurso_hidrico.serializers.zonas_hidricas_serializers import ZonaHidricaSerializer, MacroCuencasSerializer,TipoZonaHidricaSerializer,SubZonaHidricaSerializer

class MacroCuencasListView (generics.ListAPIView):
    queryset = MacroCuencas.objects.all()
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
    def get(self, request,pk):
        zonas = ZonaHidrica.objects.filter(id_macro_cuenca=pk)
        serializer = self.serializer_class(zonas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    
class TipoZonaHidricaListView (generics.ListCreateAPIView):
    queryset = TipoZonaHidrica.objects.all()
    serializer_class = TipoZonaHidricaSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request):
        zonas = TipoZonaHidrica.objects.all()
        serializer = self.serializer_class(zonas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    

 
class SubZonaHidricaListView (generics.ListCreateAPIView):
    queryset = SubZonaHidrica.objects.all()
    serializer_class = SubZonaHidricaSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        zonas = SubZonaHidrica.objects.filter(id_zona_hidrica=pk)
        serializer = self.serializer_class(zonas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    