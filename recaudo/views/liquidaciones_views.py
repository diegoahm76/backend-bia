from recaudo.models.liquidaciones_models import (
    OpcionesLiquidacionBase,
    Deudores,
    LiquidacionesBase,
    DetalleLiquidacionBase,
    Expedientes,
    VariablesBase
)
from recaudo.serializers.liquidaciones_serializers import (
    OpcionesLiquidacionBaseSerializer,
    DeudoresSerializer,
    LiquidacionesBaseSerializer,
    LiquidacionesBasePostSerializer,
    DetallesLiquidacionBaseSerializer,
    DetallesLiquidacionBasePostSerializer,
    ExpedientesSerializer,
    VariablesBaseSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response


class OpcionesLiquidacionBaseView(generics.ListAPIView):
    queryset = OpcionesLiquidacionBase.objects.all()
    serializer_class = OpcionesLiquidacionBaseSerializer
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


class DetalleOpcionesLiquidacionBaseView(generics.GenericAPIView):
    queryset = OpcionesLiquidacionBase.objects.all()
    serializer_class = OpcionesLiquidacionBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        queryset = OpcionesLiquidacionBase.objects.filter(pk=pk).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ningun registro con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class DeudoresView(generics.GenericAPIView):
    queryset = Deudores.objects.all()
    serializer_class = DeudoresSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class DeudoresIdentificacionView(generics.GenericAPIView):
    serializer_class = DeudoresSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, identificacion):
        queryset = Deudores.objects.filter(identificacion=identificacion).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ningun deudor con la identificación ingresada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class LiquidacionBaseView(generics.ListAPIView):
    queryset = LiquidacionesBase.objects.all()
    serializer_class = LiquidacionesBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = LiquidacionesBasePostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtenerLiquidacionBaseView(generics.GenericAPIView):
    serializer_class = LiquidacionesBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        queryset = LiquidacionesBase.objects.filter(pk=pk).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ninguna liquidación base con el id ingresado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class DetallesLiquidacionBaseView(generics.GenericAPIView):
    serializer_class = DetallesLiquidacionBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, liquidacion):
        queryset = DetalleLiquidacionBase.objects.filter(id_liquidacion__id=liquidacion)
        if len(queryset) == 0:
            return Response({'success': False, 'detail': 'No se encontró ningun detalle para la liquidación base'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        variable_serializer = VariablesBaseSerializer(data=self.request.data.get('id_variable'))
        if variable_serializer.is_valid(raise_exception=True):
            variable = variable_serializer.save()
            request.data['id_variable'] = variable.pk
            serializer = DetallesLiquidacionBasePostSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(id_variable=variable)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(variable_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpedientesView(generics.ListAPIView):
    queryset = Expedientes.objects.all()
    serializer_class = ExpedientesSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

