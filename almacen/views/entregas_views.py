from rest_framework import generics,status
from rest_framework.response import Response
from seguridad.models import Personas, User
from seguridad.utils import Util
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from datetime import datetime, date
import copy

from almacen.serializers.entregas_serializers import (
    GetNumeroEntregas,
    GetEntregasSerializer
)
from almacen.models.solicitudes_models import (
    DespachoConsumo,
)

class GetNumeroDespachoView(generics.RetrieveAPIView):
    serializer_class = GetNumeroEntregas
    queryset = DespachoConsumo.objects.all()

    def get(self, request):
        despacho = DespachoConsumo.objects.all().order_by('-numero_despacho_consumo').first()
        if despacho:
            numero_despacho = despacho.numero_despacho_consumo + 1
            return Response({'success': True, 'detail': 'Resultado exitoso', 'data': numero_despacho}, status=status.HTTP_200_OK)
        numero_despacho = 1
        return Response({'success': True, 'detail': 'Resultado exitoso', 'data': numero_despacho}, status=status.HTTP_200_OK)


class GetEntregasView(generics.ListAPIView):
    serializer_class = GetEntregasSerializer
    queryset = DespachoConsumo.objects.all()
            
        

