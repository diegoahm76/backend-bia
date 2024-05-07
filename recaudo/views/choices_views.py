#PAGOS CHOICES
from recaudo.choices.pagos_tipo_id_choices import pagos_tipo_id_CHOICES
from recaudo.choices.estados_liquidacion_choices import estados_liquidacion_CHOICES

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
    
class PagosTipoId(APIView):
    def get(self, request):
        choices = pagos_tipo_id_CHOICES
        return Response({'success': True, 'detail':'Se encontraron los siguientes registros', 'data':choices}, status=status.HTTP_200_OK)

class EstadosLiquidacion(APIView):
    def get(self, request):
        choices = estados_liquidacion_CHOICES
        return Response({'success': True, 'detail':'Se encontraron los siguientes registros', 'data':choices}, status=status.HTTP_200_OK)