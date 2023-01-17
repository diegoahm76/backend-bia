from rest_framework import generics,status
from rest_framework.response import Response
from seguridad.models import Personas, User
from seguridad.utils import Util
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum
from datetime import datetime, date, timedelta
import copy
import json
from almacen.utils import UtilAlmacen


from almacen.serializers.entregas_serializers import (
    GetNumeroEntregas,
    GetEntregasSerializer,
    CreateItemsEntregaSerializer,
    CreateEntregaSerializer,
    GetEntradasEntregasSerializer,
    GetItemsEntradasEntregasSerializer,
)
from almacen.models.solicitudes_models import (
    DespachoConsumo,
    ItemDespachoConsumo,
)
from almacen.models.bienes_models import (
    EntradasAlmacen,
    ItemEntradaAlmacen,
    CatalogoBienes
)
from almacen.models.generics_models import (
    Bodegas,
)
from conservacion.models.despachos_models import (
    DespachoEntrantes,
    ItemsDespachoEntrante
)
from almacen.models.inventario_models import (
    Inventario
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
        data_items_entrega = json.loads(request.data['data_items_entrega'])

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

        #VALIDACIÓN LOS ID_BIEN ENVIADOS DEBEN ESTAR EN ALGÚN ITEM DESPACHO DE LA ENTRADA
        id_bien_list = [item['id_bien_despachado'] for item in data_items_entrega]
        if not id_bien_list:
            return Response({'success': False, 'detail': 'Debe ser enviado por lo menos un item en una entrega'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN DE EXISTENCIA DE LA BODEGA ENVIADA
        bodega_entrega = data_entrega.get('id_bodega_general')
        bodega_entrega_instance = Bodegas.objects.filter(id_bodega=bodega_entrega).first()
        if not bodega_entrega_instance:
            return Response({'success': False, 'detail': 'No existe la bodega relacionada con la entrega'}, status=status.HTTP_404_NOT_FOUND)

        #VALIDACIÓN DEL NÚMERO DE ENTREGA EN ITEMS
        numero_entrada = [item['id_despacho_consumo'] for item in data_items_entrega if item['id_despacho_consumo'] != None]
        if numero_entrada:
            return Response({'success': False, 'detail': 'Para crear entregas el id_entrega de los items debe ser nulo'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACIÓN QUE LOS ID_BIEN_DESPACHADOS EXISTAN Y SEAN DE LA ENTRADA
        id_bien_despachados = [item['id_bien_despachado'] for item in data_items_entrega]
        bien_despachados_instance = CatalogoBienes.objects.filter(id_bien__in=id_bien_despachados)
        if len(set(id_bien_despachados)) != len(bien_despachados_instance):
            return Response({'success': False, 'detail': 'Todos los id_bien_despachados seleccionados deben existir'}, status=status.HTTP_400_BAD_REQUEST)
        
        id_bien_in_bienes_despachados = [bien.id_bien for bien in bien_despachados_instance]
        bien_in_items = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=entrada_almacen, id_bien__in=id_bien_in_bienes_despachados)
        id_bien_in_bienes_despachados = [bien.id_bien.id_bien for bien in bien_in_items]
        if not set(id_bien_in_bienes_despachados).issubset(id_bien_in_bienes_despachados):
            return Response({'success': False, 'detail': 'Todos los id_bienes_despachados deben pertenecer a la entrada seleccionada'}, status=status.HTTP_400_BAD_REQUEST)

        items_pasan_validacion = []
        items_no_pasan_validacion = []

        #VALIDACIÓN QUE LOS BIENES_DESPACHADOS TENGAN CANTIDAD DISPONIBLE POR DESPACHAR
        for item in data_items_entrega:
            item_entrada = ItemEntradaAlmacen.objects.filter(id_bien=item['id_bien_despachado'], id_entrada_almacen=item['id_entrada_almacen_bien'])
            cantidad_entrante_sin_sumar = [item.cantidad for item in item_entrada]
            cantidad_entrante_sumada = sum(cantidad_entrante_sin_sumar)
            item_despachado_por_entrada = ItemDespachoConsumo.objects.filter(id_entrada_almacen_bien=item['id_entrada_almacen_bien'], id_bien_despachado=item['id_bien_despachado'])
            cantidad_despachada = 0
            if item_despachado_por_entrada:
                for item_despachado in item_despachado_por_entrada:
                    cantidad_despachada += item_despachado.cantidad_despachada

                if cantidad_despachada >= cantidad_entrante_sumada:
                    items_no_pasan_validacion.append(item)
                else:
                    items_pasan_validacion.append(item)
            else:
                items_pasan_validacion.append(item)

        if not items_pasan_validacion:
            return Response({'success': False, 'detail': 'No se puede guardar una entrega si ninguno de sus items tiene cantidades por entregar'}, status=status.HTTP_400_BAD_REQUEST)    
        
        #VALIDACIÓN QUE EL ID_ENTRADA_ALMACEN SEA LA MISMA DEL MAESTRO Y QUE EXISTA
        id_entrada_almacen = [item['id_entrada_almacen_bien'] for item  in items_pasan_validacion]
        if len(set(id_entrada_almacen)) > 1:
            return Response({'success': False, 'detail': 'Todos los items deben compartir la misma entrada de almacen'}, status=status.HTTP_400_BAD_REQUEST)
        if not EntradasAlmacen.objects.filter(id_entrada_almacen=id_entrada_almacen[0]).first():
            return Response({'success': False, 'detail': 'La entrada asociada a todos los items debe existir'}, status=status.HTTP_400_BAD_REQUEST)
        if id_entrada_almacen[0] != data_entrega['id_entrada_almacen_cv']:
            return Response({'success': False, 'detail': 'La entrada asociada a los items debe ser la misma que la de la tabla maestro'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE LOS ID_BODEGAS ENVIADOS EXISTAN
        bodegas = [item['id_bodega']for item in items_pasan_validacion]
        bodegas_instance = Bodegas.objects.filter(id_bodega__in=bodegas)
        if len(set(bodegas)) != len(set(bodegas_instance)):
            return Response({'success': False, 'detail': 'Todas las bodegas seleccionadas desde la cúal se entregan los items de entrega deben existir'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE EL NÚMERO DE POSICIÓN NO SEA REPETIDO
        numeros_posicion = [item['numero_posicion_despacho'] for item in items_pasan_validacion]
        if len(numeros_posicion) != len(set(numeros_posicion)):
            return Response({'success': False, 'detail': 'Los números de posición de los items deben ser únicos'}, status=status.HTTP_400_BAD_REQUEST)

        for item in data_items_entrega:
            cantidad = UtilAlmacen.get_cantidades_disponibles_entregas(item['id_bien_despachado'], item['id_bodega'], fecha_entrega_strptime)
            print(cantidad)
            # if cantidad:
            return Response({'success': False, 'detail': 'No se encuentra disponible la cantidad solicitada', 'data':[], 'cantidad_disponible': cantidad}, status=status.HTTP_400_BAD_REQUEST)

        #CREACIÓN DE ENTREGA MAESTRO
        serializer = self.serializer_class(data=data_entrega, many=False)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()

        for item in items_pasan_validacion:
            item['observacion'] = data_entrega['motivo']
            item['id_despacho_consumo'] = serializador.pk

        #CREACIÓN DE ENTREGA DETALLE
        items_serializer = CreateItemsEntregaSerializer(data=items_pasan_validacion, many=True)
        items_serializer.is_valid(raise_exception=True)
        items_serializador = items_serializer.save()
        print(items_serializador)
        for item in items_serializador:
            print(item.id_bien_despachado)

        despacho_creado = DespachoEntrantes.objects.create(
            id_despacho_consumo_alm = serializador,
            distribucion_confirmada = False
        )

        for item in items_serializador:
            ItemsDespachoEntrante.objects.create(
                id_despacho_entrante = despacho_creado,
                id_bien = item.id_bien_despachado,
                id_entrada_alm_del_bien = item.id_entrada_almacen_bien,
                cantidad_entrante = item.cantidad_despachada,
                cantidad_distribuida = 0,
                observacion = item.observacion
            )
        
        return Response({'success': True, 'detail': 'Entrega creada exitosamente', 'data_entrega': serializer.data, 'data_items_entrega': items_serializer.data, 'items_no_pasaron_validaciones': items_no_pasan_validacion}, status=status.HTTP_200_OK)


class GetEntradasEntregasView(generics.ListAPIView):
    serializer_class = GetEntradasEntregasSerializer
    queryset = EntradasAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entradas = EntradasAlmacen.objects.filter(Q(id_tipo_entrada=2 ) | Q(id_tipo_entrada=3) | Q(id_tipo_entrada=4) & ~Q(fecha_anulacion=None))
        entrada_con_items_disponibles = []
        entrada_sin_items_disponibles = []
        for entrada in entradas:
            items_entrada = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=entrada.id_entrada_almacen, id_bien__solicitable_vivero=True).values('id_entrada_almacen', 'id_bien').annotate(cantidad_entrante=Sum('cantidad'))
            if not items_entrada:
                entrada_sin_items_disponibles.append(entrada)

            item_con_disponibilidad = []
            item_sin_disponibilidad = []
            for item in items_entrada:
                cantidad_entrante = item['cantidad_entrante']
                item_despachado_por_entrada = ItemDespachoConsumo.objects.filter(id_entrada_almacen_bien=entrada.id_entrada_almacen, id_bien_despachado=item['id_bien'])
                cantidad_despachada = 0
                for item_despachado in item_despachado_por_entrada:
                    cantidad_despachada += item_despachado.cantidad_despachada
                if cantidad_despachada >= cantidad_entrante:
                    item['tiene_cantidad_disponible'] = False
                    item['cantidad_disponible'] = 0
                    item_sin_disponibilidad.append(item)
                else:
                    item['tiene_cantidad_disponible'] = True
                    item['cantidad_disponible'] = cantidad_entrante - cantidad_despachada
                    item_con_disponibilidad.append(item)
                    entrada_con_items_disponibles.append(entrada)
                item_instanciado_entrada = ItemEntradaAlmacen.objects.filter(id_bien=item['id_bien']).first()
                item['codigo_bien'] = item_instanciado_entrada.id_bien.codigo_bien
                item['nombre_bien'] = item_instanciado_entrada.id_bien.nombre
                item['observaciones'] = item_instanciado_entrada.id_entrada_almacen.observacion

            if not item_con_disponibilidad:
                entrada_sin_items_disponibles.append(entrada)
            setsito = set(entrada_con_items_disponibles)
        serializer = self.serializer_class(set(entrada_con_items_disponibles), many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)


class GetItemsEntradasEntregasView(generics.ListAPIView):
    serializer_class = GetItemsEntradasEntregasSerializer
    queryset = ItemEntradaAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_entrada):
        items_entrada = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=id_entrada, id_bien__solicitable_vivero=True).values('id_entrada_almacen', 'id_bien').annotate(cantidad_entrante=Sum('cantidad'))
        if not items_entrada:
            return Response({'success': True, 'detail': 'No existe ningún item de esta entrada que pueda ser entregado a viveros'}, status=status.HTTP_200_OK)
        
        item_con_disponibilidad = []
        item_sin_disponibilidad = []
        for item in items_entrada:
            cantidad_entrante = item['cantidad_entrante']
            item_despachado_por_entrada = ItemDespachoConsumo.objects.filter(id_entrada_almacen_bien=id_entrada, id_bien_despachado=item['id_bien'])
            cantidad_despachada = 0
            for item_despachado in item_despachado_por_entrada:
                cantidad_despachada += item_despachado.cantidad_despachada
            if cantidad_despachada >= cantidad_entrante:
                item['tiene_cantidad_disponible'] = False
                item['cantidad_disponible'] = 0
                item_sin_disponibilidad.append(item)
            else:
                item['tiene_cantidad_disponible'] = True
                item['cantidad_disponible'] = cantidad_entrante - cantidad_despachada
                item_con_disponibilidad.append(item)
            item_instanciado_entrada = ItemEntradaAlmacen.objects.filter(id_bien=item['id_bien']).first()
            item['codigo_bien'] = item_instanciado_entrada.id_bien.codigo_bien
            item['nombre_bien'] = item_instanciado_entrada.id_bien.nombre
            item['observaciones'] = item_instanciado_entrada.id_entrada_almacen.observacion

        if not item_con_disponibilidad:
            return Response({'success': True, 'detail': 'Ninguno de los items de esta entrada tiene cantidades faltantes por entregar'})
        return Response({'success': True, 'detail': 'Items encontrados exitosamente', 'data': item_con_disponibilidad}, status=status.HTTP_200_OK)


        

