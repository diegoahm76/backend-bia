from recaudo.models.procesos_models import (
    EtapasProceso,
    TiposAtributos,
    AtributosEtapas,
    FlujoProceso,
    ValoresProceso,
    Procesos,
    CategoriaAtributo,
    Bienes,
    Avaluos
)
from recaudo.serializers.procesos_serializers import (
    EtapasProcesoSerializer,
    TiposAtributosSerializer,
    AtributosEtapasSerializer,
    FlujoProcesoSerializer,
    FlujoProcesoPostSerializer,
    ValoresProcesoSerializer,
    ValoresProcesoPostSerializer,
    ProcesosSerializer,
    ProcesosPostSerializer,
    AtributosEtapasPostSerializer,
    AvaluosSerializer,
    CategoriaAtributoSerializer
)
from recaudo.models.base_models import TiposBien

from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response
import datetime
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied


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

    def post(self, request):
        serializer = AtributosEtapasPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlujoProcesoView(generics.ListAPIView):
    queryset = FlujoProceso.objects.all()
    serializer_class = FlujoProcesoSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = FlujoProcesoPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GraficaView(generics.ListAPIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        querysetEtapas = EtapasProceso.objects.all()
        querysetFlujos = FlujoProceso.objects.all()
        nuevasEtapas = []
        nuevoFlujo = []
        for item in querysetEtapas:
            nuevasEtapas.append({'id': item.pk, 'data': {'etapa': item.etapa, 'descripcion': item.descripcion}})
        for item in querysetFlujos:
            data = {'fecha_flujo': item.fecha_flujo, 'descripcion': item.descripcion, 'requisitos': item.requisitos}
            nuevoFlujo.append({'id': item.pk, 'source': item.id_etapa_origen.pk, 'target': item.id_etapa_destino.pk, 'data': data})
        response = {
            'nodes': nuevasEtapas,
            'edges': nuevoFlujo
        }
        return Response(response, status=status.HTTP_200_OK)


class ValoresProcesoView(generics.ListAPIView):
    queryset = ValoresProceso.objects.all()
    serializer_class = ValoresProcesoSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, proceso):
        queryset = ValoresProceso.objects.filter(id_proceso=proceso)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ValoresProcesoPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActualizarEtapaProceso(generics.ListAPIView):
    serializer_class = ProcesosSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, proceso):
        procesoFilter = Procesos.objects.filter(pk=proceso).filter(fin__isnull=True)
        if len(procesoFilter) == 0:
            return Response({'success': False, 'detail': 'No existen etapas sin finalizar en el proceso con el id enviado'}, status=status.HTTP_200_OK)
        else:
            procesoActual = procesoFilter.get()
            procesoActual.fin = datetime.date.today()
            procesoActual.save()
            flujo_siguiente = FlujoProceso.objects.filter(id_etapa_origen=procesoActual.id_etapa.pk)
            if len(flujo_siguiente) == 0:
                serializer = self.serializer_class(procesoActual, many=False)
                return Response({'success': True, 'detail': 'Esta era la ultima etapa en el flujo, fecha fin actualizada correctamente', 'data': serializer.data}, status=status.HTTP_200_OK)
            else:
                flujo_nuevo = flujo_siguiente.first()
                proceso_nuevo = Procesos(
                    id_cartera=procesoActual.id_cartera,
                    id_etapa=flujo_nuevo.id_etapa_destino,
                    id_funcionario=procesoActual.id_funcionario,
                    inicio=datetime.date.today()
                )
                proceso_nuevo.save()
                serializer = self.serializer_class(proceso_nuevo, many=False)
                return Response({'success': True, 'detail': 'Se creo la siguiente etapa de manera exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)


class ProcesosView(generics.ListAPIView):
    queryset = Procesos.objects.filter(fin__isnull=True)
    serializer_class = ProcesosSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProcesosPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class AvaluosBienesView(generics.CreateAPIView):
    serializer_class = AvaluosSerializer
    
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail':'Se agregar los avaluos del bien que da el deudor', 'data':serializer.data},status=status.HTTP_200_OK)


class CategoriaAtributoView(generics.ListAPIView):
    queryset = CategoriaAtributo.objects.all()
    serializer_class = CategoriaAtributoSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)