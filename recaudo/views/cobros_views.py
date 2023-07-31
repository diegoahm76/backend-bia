from recaudo.models.cobros_models import (
    Cartera
)
from recaudo.serializers.cobros_serializers import (
    CarteraGeneralSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response


class CarteraView(generics.ListAPIView):
    queryset = Cartera.objects.all()
    serializer_class = CarteraGeneralSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
