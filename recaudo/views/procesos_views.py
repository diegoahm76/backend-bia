from recaudo.models.procesos_models import (
    EtapasProceso,
    TiposAtributos,
    AtributosEtapas,
    FlujoProceso
)
from recaudo.serializers.procesos_serializers import (
    EtapasProcesoSerializer,
    TiposAtributosSerializer,
    AtributosEtapasSerializer,
    FlujoProcesoSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response


class EtapasProcesoView(generics.ListAPIView):
    queryset = EtapasProceso.objects.all()
    serializer_class = EtapasProcesoSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class TiposAtributosView(generics.ListAPIView):
    queryset = TiposAtributos.objects.all()
    serializer_class = TiposAtributosSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class AtributosEtapasView(generics.ListAPIView):
    queryset = AtributosEtapas.objects.all()
    serializer_class = AtributosEtapasSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, etapa):
        queryset = AtributosEtapas.objects.filter(id_etapa=etapa)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class FlujoProcesoView(generics.ListAPIView):
    queryset = FlujoProceso.objects.all()
    serializer_class = FlujoProcesoSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

