from rest_framework import generics,status
from rest_framework.response import Response
from seguridad.models import Personas, User
from seguridad.utils import Util
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from datetime import datetime, date, timedelta
import copy
import json

from almacen.serializers.entregas_serializers import (
    GetNumeroEntregas,
    GetEntregasSerializer,
    CreateEntregaSerializer,
    GetEntradasEntregasSerializer,
    GetItemsEntradasEntregasSerializer
)
from almacen.models.solicitudes_models import (
    DespachoConsumo,
)
from almacen.models.bienes_models import (
    EntradasAlmacen,
    ItemEntradaAlmacen
)
from almacen.models.generics_models import (
    Bodegas,
)

class GetNumeroDespachoView(generics.RetrieveAPIView):
    serializer_class = GetNumeroEntregas
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entregas = DespachoConsumo.objects.filter(Q(id_solicitud_consumo=None) & ~Q(id_entrada_almacen_cv=None))
        serializer = self.serializer_class(entregas, many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)


class CrearEntregaView(generics.CreateAPIView):
    serializer_class = CreateEntregaSerializer
    queryset = DespachoConsumo.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data_entrega = json.loads(request.data['data_entrega'])
        data_entrega['ruta_archivo_doc_con_recibido'] = request.FILES.get('ruta_archivo_doc_con_recibido')
        persona_logeada = request.user.persona.id_persona
        data_entrega['id_persona_despacha'] = persona_logeada
        data_entrega['es_despacho_conservacion'] = True
        
        #REASIGNACIÓN DEL NUMERO DE DESPACHO
        numero_entrega_existente = DespachoConsumo.objects.filter(~Q(numero_despacho_consumo=None)).order_by('-numero_despacho_consumo').first()
        if numero_entrega_existente:
            data_entrega['numero_despacho_consumo'] = numero_entrega_existente.numero_despacho_consumo + 1
        else:
            data_entrega['numero_despacho_consumo'] = 1
        
        #VALIDACIÓN DE FECHA_DESPACHO
        fecha_entrega = data_entrega.get('fecha_despacho')
        fecha_actual = datetime.now()
        fecha_entrega_strptime = datetime.strptime(fecha_entrega, '%Y-%m-%d %H:%M:%S')
        if fecha_entrega_strptime > fecha_actual:
            return Response({'success': False, 'detail': 'La fecha de entrega seleccionada no debe ser superior a la actual'}, status=status.HTTP_400_BAD_REQUEST)
        if fecha_entrega_strptime < (fecha_actual - timedelta(days=8)):
            return Response({'success': False, 'detail': 'Las entregas pueden tener una fecha anterior hasta 8 días calendario'}, status=status.HTTP_400_BAD_REQUEST)           

        #VALIDACIÓN DE EXISTENCIA DE LA ENTRADA SELECCIONADA
        entrada_almacen = data_entrega.get('id_entrada_almacen_cv')
        entrada_almacen_instance = EntradasAlmacen.objects.filter(id_entrada_almacen=entrada_almacen).first()
        if not entrada_almacen_instance:
            return Response({'success': False, 'detail': 'No existe la entrada relacionada con esta entrega'}, status=status.HTTP_404_NOT_FOUND)

        #VALIDACIÓN DE EXISTENCIA DE LA BODEGA ENVIADA
        bodega_entrega = data_entrega.get('id_bodega_general')
        bodega_entrega_instance = Bodegas.objects.filter(id_bodega=bodega_entrega).first()
        if not bodega_entrega_instance:
            return Response({'success': False, 'detail': 'No existe la bodega relacionada con la entrega'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=data_entrega, many=False)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()
        return Response({'success': True, 'detail': 'Entrega creada exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)


class GetEntradasEntregasView(generics.ListAPIView):
    serializer_class = GetEntradasEntregasSerializer
    queryset = EntradasAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entradas = EntradasAlmacen.objects.filter(Q(id_tipo_entrada=2 ) | Q(id_tipo_entrada=3) | Q(id_tipo_entrada=4) & ~Q(fecha_anulacion=None))
        serializer = self.serializer_class(entradas, many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)


class GetItemsEntradasEntregasView(generics.ListAPIView):
    serializer_class = GetItemsEntradasEntregasSerializer
    queryset = ItemEntradaAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_entrada):
        items_entrada = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=id_entrada, id_bien__solicitable_vivero=True)
        serializer = self.serializer_class(items_entrada, many=True)
        return Response({'success': True, 'detail': 'Items encontrados exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)


        

