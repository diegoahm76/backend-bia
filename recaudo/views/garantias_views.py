from rest_framework import generics, status
from rest_framework.response import Response
from recaudo.models.garantias_models import RolesGarantias
from recaudo.serializers.garantias_serializers import RolesGarantiasSerializer


class RolesGarantiasView(generics.ListAPIView):
    serializer_class = RolesGarantiasSerializer
    queryset = RolesGarantias.objects.all() 

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail':'Se muestra los roles de garantias', 'data': serializer.data}, status=status.HTTP_200_OK)
