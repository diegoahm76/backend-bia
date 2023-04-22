from recaudo.models.liquidaciones_models import OpcionesLiquidacionBase
from recaudo.serializers.liquidaciones_serializers import OpcionesLiquidacionBaseSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView


class OpcionesLiquidacionBaseView(generics.ListAPIView):
    queryset = OpcionesLiquidacionBase.objects.all()
    serializer_class = OpcionesLiquidacionBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        print(request)
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

