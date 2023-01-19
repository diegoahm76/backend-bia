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
    AnularEntregaSerializer,
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

        #VALIDACIÓN DE QUE NO HAYAN ENTREGAS POSTERIORES DE LOS BIENES QUE SE QUIEREN ENTREGAR
        items_fecha_posterior_entrega_actual = []
        items_fecha_anterior_entrega_actual = []

        for item in data_items_entrega:
            items_despachos_fecha = ItemDespachoConsumo.objects.filter(id_bien_despachado=item['id_bien_despachado'], id_bodega=item['id_bodega'])
            for itemsito in items_despachos_fecha:
                if itemsito.id_despacho_consumo.fecha_despacho > fecha_entrega_strptime:
                    items_fecha_posterior_entrega_actual.append(item)
                else:
                    items_fecha_anterior_entrega_actual.append(item)
        
        if items_fecha_posterior_entrega_actual:
            return Response({'success': False, 'detail': 'No se puede realizar la entrega si a un bien ya se le generaron salidas posteriores en la misma bodega', 'items_fecha_posterior_entrega_actual': items_fecha_posterior_entrega_actual}, status=status.HTTP_400_BAD_REQUEST)
    
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

        #VALIDACIÓN QUE TODOS LOS ID_BIENES DEBEN ESTAR DENTRO DE LOS ITEMS DE LA ENTRADA SELECCIONADA
        id_bien_in_bienes_despachados = [bien.id_bien for bien in bien_despachados_instance]
        bien_in_items = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=entrada_almacen, id_bien__in=id_bien_in_bienes_despachados)
        id_bien_in_bienes_despachados = [bien.id_bien.id_bien for bien in bien_in_items]
        if not set(id_bien_in_bienes_despachados).issubset(id_bien_in_bienes_despachados):
            return Response({'success': False, 'detail': 'Todos los id_bienes_despachados deben pertenecer a la entrada seleccionada'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE LOS BIENES_DESPACHADOS TENGAN CANTIDAD DISPONIBLE POR DESPACHAR SEGÚN LAS ENTREGAS ANTERIORES DE LA ENTRADA SELECCIONADA
        items_pasan_validacion = []
        items_no_pasan_validacion = []

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
                    del item['cantidad_despachada']
                    del item['id_bodega']
                    del item['id_despacho_consumo']
                    items_no_pasan_validacion.append(item)
                else:
                    items_pasan_validacion.append(item)
            else:
                items_pasan_validacion.append(item)

        if items_no_pasan_validacion:
            return Response({'success': False, 'detail': 'No se puede realizar una entrega si alguno de sus items ya fue totalmente entregado', 'Items totalmente entregados': items_no_pasan_validacion}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE EL ID_ENTRADA_ALMACEN SEA LA MISMA DEL MAESTRO Y QUE EXISTA
        id_entrada_almacen = [item['id_entrada_almacen_bien'] for item  in data_items_entrega]
        if len(set(id_entrada_almacen)) > 1:
            return Response({'success': False, 'detail': 'Todos los items deben compartir la misma entrada de almacen'}, status=status.HTTP_400_BAD_REQUEST)
        if not EntradasAlmacen.objects.filter(id_entrada_almacen=id_entrada_almacen[0]).first():
            return Response({'success': False, 'detail': 'La entrada asociada a todos los items debe existir'}, status=status.HTTP_400_BAD_REQUEST)
        if id_entrada_almacen[0] != data_entrega['id_entrada_almacen_cv']:
            return Response({'success': False, 'detail': 'La entrada asociada a los items debe ser la misma que la de la tabla maestro'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE LOS ID_BODEGAS ENVIADOS EXISTAN
        bodegas = [item['id_bodega']for item in data_items_entrega]
        bodegas_instance = Bodegas.objects.filter(id_bodega__in=bodegas)
        if len(set(bodegas)) != len(set(bodegas_instance)):
            return Response({'success': False, 'detail': 'Todas las bodegas seleccionadas desde la cúal se entregan los items de entrega deben existir'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE EL NÚMERO DE POSICIÓN NO SEA REPETIDO
        numeros_posicion = [item['numero_posicion_despacho'] for item in data_items_entrega]
        if len(numeros_posicion) != len(set(numeros_posicion)):
            return Response({'success': False, 'detail': 'Los números de posición de los items deben ser únicos'}, status=status.HTTP_400_BAD_REQUEST)


        #VALIDACIÓN QUE EXISTA LA CANTIDAD A ENTREGAR EN LA BODEGA SELECCIONADA
        items_con_cantidades_disponible_en_bodega = []
        items_con_cantidad_no_disponible_en_bodega = []

        for item in data_items_entrega:
            cantidad = UtilAlmacen.get_cantidades_disponibles_entregas(item['id_bien_despachado'], item['id_bodega'], fecha_entrega_strptime)
            if int(item['cantidad_despachada']) > cantidad:
                item['cantidad_disponible_en_bodega'] = cantidad
                items_con_cantidad_no_disponible_en_bodega.append(item)
            else:
                items_con_cantidades_disponible_en_bodega.append(item)

        if items_con_cantidad_no_disponible_en_bodega:
            return Response({'success': False, 'detail': 'No se puede realizar una entrega si alguno de los bienes enviados a despachar no tiene cantidades disponibles en bodega', 'Items que no tienen cantidades disponibles en bodega': items_con_cantidad_no_disponible_en_bodega}, status=status.HTTP_400_BAD_REQUEST)

        #CREACIÓN DE ENTREGA MAESTRO
        serializer = self.serializer_class(data=data_entrega, many=False)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()

        #CREACIÓN DE ENTREGA DETALLE
        for item in data_items_entrega:
            item['observacion'] = data_entrega['motivo']
            item['id_despacho_consumo'] = serializador.pk

        items_serializer = CreateItemsEntregaSerializer(data=data_items_entrega, many=True)
        items_serializer.is_valid(raise_exception=True)
        items_serializador = items_serializer.save()

        #REAGRUPACIÓN PARA CONVERTIR DOS REGISTROS DE ITEMS DESPACHOS SALIENTES EN UNO SOLO PARA ITEMS DESPACHOS ENTRANTES

        id_bien_items_serializador = [item.id_bien_despachado.id_bien for item in items_serializador]
        id_bien_items_serializador_instance = ItemDespachoConsumo.objects.filter(id_bien_despachado__in=id_bien_items_serializador, id_despacho_consumo=serializador.pk).values('id_bien_despachado', 'id_entrada_almacen_bien', 'observacion').annotate(cantidad_despachada=Sum('cantidad_despachada'))

        #CREACIÓN DE DESPACHO ENTRANTE
        despacho_entrante = DespachoEntrantes.objects.create(
            id_despacho_consumo_alm = serializador,
            distribucion_confirmada = False,
            fecha_ingreso = serializador.fecha_despacho
        )

        #CREACIÓN DE ITEMS DESPACHO ENTRANTE
        for id_bien in id_bien_items_serializador_instance:
            item_despacho = ItemDespachoConsumo.objects.filter(id_bien_despachado=id_bien['id_bien_despachado'], id_despacho_consumo=serializador.pk).first()
            item_despacho_entrante = ItemsDespachoEntrante.objects.create(
                id_despacho_entrante = despacho_entrante,
                id_bien = item_despacho.id_bien_despachado,
                id_entrada_alm_del_bien = item_despacho.id_entrada_almacen_bien,
                cantidad_entrante = int(id_bien_items_serializador_instance[0]['cantidad_despachada']),
                cantidad_distribuida = 0,
                observacion = item_despacho.observacion,
                fecha_ingreso = serializador.fecha_despacho
                )
        
        #REGISTRO DEL AUMENTO DE LA CANTIDAD SALIENTE POR BIEN Y BODEGA EN INVENTARIO
        for item in data_items_entrega:
            inventario_bien_bodega = Inventario.objects.filter(id_bien=item['id_bien_despachado'], id_bodega=item['id_bodega']).first()
            cantidad_saliente_existente = 0
            if inventario_bien_bodega.cantidad_saliente_consumo != None:
                cantidad_saliente_existente = inventario_bien_bodega.cantidad_saliente_consumo
            inventario_bien_bodega.cantidad_saliente_consumo = cantidad_saliente_existente + int(item['cantidad_despachada'])
            inventario_bien_bodega.save()

        return Response({'success': True, 'detail': 'Entrega creada exitosamente', 'Entrega creada': serializer.data, 'Items entregados': items_serializer.data}, status=status.HTTP_200_OK)


class AnularEntregaView(generics.RetrieveUpdateAPIView):
    serializer_class = AnularEntregaSerializer
    queryset = DespachoConsumo.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, id_entrega):
        data = request.data
        entrega_instance = DespachoConsumo.objects.filter(id_despacho_consumo=id_entrega).first()
        if not entrega_instance:
            return Response({'success': False, 'detail': 'No existe ningún despacho con el parámetro ingresado'}, status=status.HTTP_400_BAD_REQUEST)
        
        despacho_entrante = DespachoEntrantes.objects.filter(id_despacho_consumo_alm=entrega_instance.id_despacho_consumo).first()
        if despacho_entrante.id_persona_distribuye or despacho_entrante.id_persona_distribuye == '':
            return Response({'success': False, 'detail': 'No se puede anular una entrega que ya fue distribuida en viveros'}, status=status.HTTP_400_BAD_REQUEST)
        
        items_entrega = ItemDespachoConsumo.objects.filter(id_despacho_consumo=id_entrega)
        for item in items_entrega:
            anulacion_bien = Inventario.objects.filter(id_bien=item.id_bien_despachado, id_bodega=item.id_bodega).first()
            anulacion_bien.cantidad_saliente_consumo = anulacion_bien.cantidad_saliente_consumo - item.cantidad_despachada
            if anulacion_bien.cantidad_saliente_consumo == 0:
                anulacion_bien.cantidad_saliente_consumo = None
            anulacion_bien.save()
        
        
        items_entrega.delete()
        entrega_instance.despacho_anulado = True
        entrega_instance.justificacion_anulacion = data['descripcion_anulacion']
        entrega_instance.fecha_anulacion = datetime.now()
        entrega_instance.id_persona_anula = request.user.persona
        entrega_instance.save()

        items_despacho_entrante = ItemsDespachoEntrante.objects.filter(id_despacho_entrante=despacho_entrante.id_despacho_entrante)
        items_despacho_entrante.delete()
        
        despacho_entrante.delete()

        return Response({'success': True, 'detail': 'Se ha anulado la entrega correctamente'}, status=status.HTTP_204_NO_CONTENT)

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




