from rest_framework import generics, status
from rest_framework.views import APIView
from seguridad.utils import Util  
from django.db.models import Q, F, Sum
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from datetime import timezone
import copy

from seguridad.models import Personas
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from almacen.models.solicitudes_models import (
    DespachoConsumo
)
from conservacion.models.viveros_models import (
    Vivero
)
from conservacion.models.despachos_models import (
    DespachoEntrantes,
    ItemsDespachoEntrante,
    DistribucionesItemDespachoEntrante
)
from conservacion.serializers.despachos_serializers import (
    DespachosEntrantesSerializer,
    ItemsDespachosEntrantesSerializer,
    DistribucionesItemDespachoEntranteSerializer
)
from conservacion.utils import UtilConservacion

class GetDespachosEntrantes(generics.ListAPIView):
    serializer_class=DespachosEntrantesSerializer
    queryset=DespachoEntrantes.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        numero_despacho_consumo = request.query_params.get('numero_despacho')
        despachos_entrantes = self.queryset.all()
        
        if numero_despacho_consumo:
            despacho_consumo = DespachoConsumo.objects.filter(numero_despacho_consumo=numero_despacho_consumo).first()
            despachos_entrantes = despachos_entrantes.filter(id_despacho_consumo_alm=despacho_consumo.id_despacho_consumo)
        
        serializer=self.serializer_class(despachos_entrantes, many=True)
        if despachos_entrantes:
            return Response({'success':True,'detail':'Se encontraron despachos entrantes','data':serializer.data}, status=status.HTTP_200_OK)
        else: 
            return Response({'success':True,'detail':'No se encontraron despachos entrantes', 'data':[]}, status=status.HTTP_200_OK)

class GetItemsDespachosEntrantes(generics.ListAPIView):
    serializer_class=ItemsDespachosEntrantesSerializer
    queryset=ItemsDespachoEntrante.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request,pk):
        items_despacho = ItemsDespachoEntrante.objects.filter(id_despacho_entrante=pk).values(
            'id_item_despacho_entrante',
            'id_despacho_entrante',
            'id_bien',
            'id_entrada_alm_del_bien',
            'fecha_ingreso',
            'cantidad_entrante',
            'cantidad_distribuida',
            'observacion',
            codigo_bien=F('id_bien__codigo_bien'),
            nombre_bien=F('id_bien__nombre'),
            tipo_documento=F('id_entrada_alm_del_bien__id_tipo_entrada__nombre'),
            numero_documento=F('id_entrada_alm_del_bien__numero_entrada_almacen'),
        ).annotate(cantidad_restante=Sum('cantidad_entrante') - Sum('cantidad_distribuida'))
        
        if items_despacho:
            return Response({'success':True,'detail':'Se encontraron items de despachos entrantes','data':items_despacho}, status=status.HTTP_200_OK)
        else: 
            return Response({'success':True,'detail':'No se encontraron items de despachos entrantes', 'data':[]}, status=status.HTTP_200_OK)
        
class GuardarDistribucionBienes(generics.ListAPIView):
    serializer_class=DistribucionesItemDespachoEntranteSerializer
    queryset=DistribucionesItemDespachoEntrante.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,id_despacho_entrante):
        response_dict = UtilConservacion.guardar_distribuciones(id_despacho_entrante, request, self.queryset.all())
        return Response({'success':response_dict['success'], 'detail':response_dict['detail']}, status=response_dict['status'])