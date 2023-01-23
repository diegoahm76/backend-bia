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
        despacho_entrante=DespachoEntrantes.objects.filter(id_despacho_entrante=id_despacho_entrante).first()
        if despacho_entrante:
            data = request.data
            user = request.user.persona
            observacion_distribucion = request.query_params.get('observaciones_distribucion')
            
            # VALIDAR EXISTENCIA DE ITEMS
            items_id_list = [item['id_item_despacho_entrante'] for item in data]
            items_despacho_entrante = ItemsDespachoEntrante.objects.filter(id_item_despacho_entrante__in=items_id_list)
            if len(items_id_list) != len(items_despacho_entrante):
                return Response({'success':True, 'detail':'Debe elegir items de despacho entrante existentes'}, status=status.HTTP_400_BAD_REQUEST)
            
            # VALIDAR EXISTENCIA DE VIVEROS
            viveros_id_list = [item['id_vivero'] for item in data]
            viveros = Vivero.objects.filter(id_vivero__in=viveros_id_list)
            if len(viveros_id_list) != len(viveros):
                return Response({'success':False, 'detail':'Debe elegir viveros existentes'}, status=status.HTTP_400_BAD_REQUEST)
            
            # VALIDAR CANTIDADES MAYOR A CERO
            cantidades = [item['cantidad_asignada'] for item in data]
            if cantidades.count(0) > 0:
                return Response({'success':False, 'detail':'Debe distribuir cantidades mayores a cero'}, status=status.HTTP_400_BAD_REQUEST)
            
            # VALIDAR CODIGOS ETAPA LOTE
            dict_cod_etapa_lote = [x for x,y in cod_etapa_lote_CHOICES]
            cod_etapa_lote_list = [item['cod_etapa_lote_al_ingresar'] for item in data]
            if not set(cod_etapa_lote_list).issubset(dict_cod_etapa_lote):
                return Response({'success':False, 'detail':'Debe seleccionar códigos de etapa lote existentes'}, status=status.HTTP_400_BAD_REQUEST)

            # ACTUALIZAR EN DESPACHO ENTRANTE
            despacho_entrante.observacion_distribucion = observacion_distribucion
            despacho_entrante.id_persona_distribuye = user
            
            items_create = []
            
            # ACTUALIZAR ITEMS DESPACHO ENTRANTE
            for item in data:
                item_despacho_entrante = ItemsDespachoEntrante.objects.filter(id_item_despacho_entrante=item['id_item_despacho_entrante']).first()
                item_despacho_entrante.cantidad_distribuida = item['cantidad_asignada']
                item_despacho_entrante.save()
                
                distribucion_item = DistribucionesItemDespachoEntrante.objects.filter(id_item_despacho_entrante=item['id_item_despacho_entrante']).first()
                if distribucion_item:
                    serializer_update = self.serializer_class(distribucion_item, data=item)
                    serializer_update.is_valid(raise_exception=True)
                    serializer_update.save()
                else:
                    items_create.append(item)
            
            # CREAR ITEMS DESPACHO ENTRANTE
            if items_create:
                serializer_create = self.serializer_class(data=items_create, many=True)
                serializer_create.is_valid(raise_exception=True)
                serializer_create.save()
            
            return Response({'success':True, 'detail':'Se realizó el guardado de las distribuciones correctamente'}, status=status.HTTP_201_CREATED)
            
        else:
            return Response({'success':False, 'detail':'El despacho entrante elegido no existe'}, status=status.HTTP_404_NOT_FOUND)
        