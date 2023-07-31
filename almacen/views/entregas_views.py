from rest_framework import generics,status
from rest_framework.response import Response
from seguridad.utils import Util
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
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
    ActualizarEntregaSerializer,
    GetItemsEntregaSerializer,
    DeleteItemsEntregaSerializer
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
            return Response({'success':True, 'detail':'Resultado exitoso', 'data': numero_despacho}, status=status.HTTP_200_OK)
        numero_despacho = 1
        return Response({'success':True, 'detail':'Resultado exitoso', 'data': numero_despacho}, status=status.HTTP_200_OK)


class GetEntregasView(generics.ListAPIView):
    serializer_class = GetEntregasSerializer
    queryset = DespachoConsumo.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entregas = DespachoConsumo.objects.filter(Q(id_solicitud_consumo=None) & ~Q(id_entrada_almacen_cv=None))
        serializer = self.serializer_class(entregas, many=True)
        return Response({'success':True, 'detail':'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)

class GetItemsEntregaView(generics.ListAPIView):
    serializer_class = GetItemsEntregaSerializer
    queryset = ItemDespachoConsumo.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_entrega):
        entrega = DespachoConsumo.objects.filter(id_despacho_consumo=id_entrega).first()
        if not entrega:
            raise NotFound('No se encontró ningún item con el parámetro enviado')
        if entrega.despacho_anulado == True:
            raise ValidationError('Una entrega anulada no tiene detalle')
        
        items_entregas = ItemDespachoConsumo.objects.filter(id_despacho_consumo=id_entrega)
        if not items_entregas:
            raise NotFound('No se encontró ningún item con el parámetro enviado')

        serializer = self.serializer_class(items_entregas, many=True)
        return Response({'success':True, 'detail':'Búsqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)
            


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
            raise ValidationError('La fecha de entrega seleccionada no debe ser superior a la actual')
        if fecha_entrega_strptime < (fecha_actual - timedelta(days=8)):
            raise ValidationError('Las entregas pueden tener una fecha anterior hasta 8 días calendario')

        #VALIDACIÓN DE EXISTENCIA DE LA ENTRADA SELECCIONADA
        entrada_almacen = data_entrega.get('id_entrada_almacen_cv')
        entrada_almacen_instance = EntradasAlmacen.objects.filter(id_entrada_almacen=entrada_almacen).first()
        if not entrada_almacen_instance:
            raise NotFound('No existe la entrada relacionada con esta entrega')         

        #VALIDACIÓN LOS ID_BIEN ENVIADOS DEBEN ESTAR EN ALGÚN ITEM DESPACHO DE LA ENTRADA
        id_bien_list = [item['id_bien_despachado'] for item in data_items_entrega]
        bien_in_item = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=entrada_almacen, id_bien__in=id_bien_list)
        id_bien_in_bienes_despachados = [bien.id_bien.id_bien for bien in bien_in_item]
        if not set(id_bien_list).issubset(id_bien_in_bienes_despachados):
            raise ValidationError('Todos los id_bienes_despachados deben pertenecer a la entrada seleccionada')

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
            try:
                raise ValidationError('No se puede realizar la entrega si a un bien ya se le generaron salidas posteriores en la misma bodega')
            except ValidationError as e:
                return Response({'success':False, 'detail':'No se puede realizar la entrega si a un bien ya se le generaron salidas posteriores en la misma bodega', 'items_fecha_posterior_entrega_actual': items_fecha_posterior_entrega_actual}, status=status.HTTP_400_BAD_REQUEST)
    
        #VALIDACIÓN DE EXISTENCIA DE LA BODEGA ENVIADA
        bodega_entrega = data_entrega.get('id_bodega_general')
        bodega_entrega_instance = Bodegas.objects.filter(id_bodega=bodega_entrega).first()
        if not bodega_entrega_instance:
            raise NotFound('No existe la bodega relacionada con la entrega')

        #VALIDACIÓN DEL NÚMERO DE ENTREGA EN ITEMS
        numero_entrada = [item['id_despacho_consumo'] for item in data_items_entrega if item['id_despacho_consumo'] != None]
        if numero_entrada:
            raise ValidationError('Para crear entregas el id_entrega de los items debe ser nulo')

        #VALIDACIÓN QUE LOS ID_BIEN_DESPACHADOS EXISTAN Y SEAN DE LA ENTRADA
        id_bien_despachados = [item['id_bien_despachado'] for item in data_items_entrega]
        bien_despachados_instance = CatalogoBienes.objects.filter(id_bien__in=id_bien_despachados)
        if len(set(id_bien_despachados)) != len(bien_despachados_instance):
            raise ValidationError('Todos los id_bien_despachados seleccionados deben existir')

        #VALIDACIÓN QUE TODOS LOS ID_BIENES DEBEN ESTAR DENTRO DE LOS ITEMS DE LA ENTRADA SELECCIONADA
        id_bien_in_bienes_despachados = [bien.id_bien for bien in bien_despachados_instance]
        bien_in_items = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=entrada_almacen, id_bien__in=id_bien_in_bienes_despachados)
        id_bien_in_bienes_despachados = [bien.id_bien.id_bien for bien in bien_in_items]
        if not set(id_bien_in_bienes_despachados).issubset(id_bien_in_bienes_despachados):
            raise ValidationError('Todos los id_bienes_despachados deben pertenecer a la entrada seleccionada')

        #VALIDACIÓN QUE LOS BIENES_DESPACHADOS TENGAN CANTIDAD DISPONIBLE POR DESPACHAR SEGÚN LAS ENTREGAS ANTERIORES DE LA ENTRADA SELECCIONADA
        items_pasan_validacion = []
        items_no_pasan_validacion = []

        for item in data_items_entrega:
            item_entrada = ItemEntradaAlmacen.objects.filter(id_bien=item['id_bien_despachado'], id_entrada_almacen=item['id_entrada_almacen_bien'], id_bodega=item['id_bodega'])
            cantidad_entrante_sin_sumar = [item.cantidad for item in item_entrada]
            cantidad_entrante_sumada = sum(cantidad_entrante_sin_sumar)
            item_despachado_por_entrada = ItemDespachoConsumo.objects.filter(id_entrada_almacen_bien=item['id_entrada_almacen_bien'], id_bien_despachado=item['id_bien_despachado'], id_bodega=item['id_bodega'])
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
                if int(item['cantidad_despachada']) > cantidad_entrante_sumada:
                    items_no_pasan_validacion.append(item)
                    try:
                        raise ValidationError('No se puede despachar una cantidad mayor a la que se recibió en la entrada')
                    except ValidationError as e:
                        return Response({'success':False, 'detail':'No se puede despachar una cantidad mayor a la que se recibió en la entrada', 'data': item}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    items_pasan_validacion.append(item)
        if items_no_pasan_validacion:
            try:
                raise ValidationError('No se puede realizar una entrega si alguno de sus items ya fue totalmente entregado')
            except ValidationError as e:
                return Response({'success':False, 'detail':'No se puede realizar una entrega si alguno de sus items ya fue totalmente entregado', 'Items totalmente entregados': items_no_pasan_validacion}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE EL ID_ENTRADA_ALMACEN SEA LA MISMA DEL MAESTRO Y QUE EXISTA
        id_entrada_almacen = [item['id_entrada_almacen_bien'] for item  in data_items_entrega]
        if len(set(id_entrada_almacen)) > 1:
            raise ValidationError('Todos los items deben compartir la misma entrada de almacen')
        if not EntradasAlmacen.objects.filter(id_entrada_almacen=id_entrada_almacen[0]).first():
            raise ValidationError('La entrada asociada a todos los items debe existir')
        if id_entrada_almacen[0] != data_entrega['id_entrada_almacen_cv']:
            raise ValidationError('La entrada asociada a los items debe ser la misma que la de la tabla maestro')

        #VALIDACIÓN QUE LOS ID_BODEGAS ENVIADOS EXISTAN
        bodegas = [item['id_bodega']for item in data_items_entrega]
        bodegas_instance = Bodegas.objects.filter(id_bodega__in=bodegas)
        if len(set(bodegas)) != len(set(bodegas_instance)):
            raise ValidationError('Todas las bodegas seleccionadas desde la cúal se entregan los items de entrega deben existir')

        #VALIDACIÓN QUE EL NÚMERO DE POSICIÓN NO SEA REPETIDO
        numeros_posicion = [item['numero_posicion_despacho'] for item in data_items_entrega]
        if len(numeros_posicion) != len(set(numeros_posicion)):
            raise ValidationError('Los números de posición de los items deben ser únicos')

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
            try:
                raise ValidationError('No se puede realizar una entrega si alguno de los bienes enviados a despachar no tiene cantidades disponibles en bodega')
            except ValidationError as e:
                return Response({'success':False, 'detail':'No se puede realizar una entrega si alguno de los bienes enviados a despachar no tiene cantidades disponibles en bodega', 'Items que no tienen cantidades disponibles en bodega': items_con_cantidad_no_disponible_en_bodega}, status=status.HTTP_400_BAD_REQUEST)

        #CREACIÓN DE ENTREGA MAESTRO
        serializer = self.serializer_class(data=data_entrega, many=False)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()

        #CREACIÓN DE ENTREGA DETALLE
        for item in data_items_entrega:
            item['id_despacho_consumo'] = serializador.pk

        items_serializer = CreateItemsEntregaSerializer(data=data_items_entrega, many=True)
        items_serializer.is_valid(raise_exception=True)
        items_serializador = items_serializer.save()

        #REAGRUPACIÓN PARA CONVERTIR DOS REGISTROS DE ITEMS DESPACHOS SALIENTES EN UNO SOLO PARA ITEMS DESPACHOS ENTRANTES
        id_bien_items_serializador = [item.id_bien_despachado.id_bien for item in items_serializador]
        id_bien_items_serializador_instance = ItemDespachoConsumo.objects.filter(id_bien_despachado__in=id_bien_items_serializador, id_despacho_consumo=serializador.pk).values('id_bien_despachado', 'id_entrada_almacen_bien').annotate(cantidad_despachada=Sum('cantidad_despachada'))

        #CREACIÓN DE DESPACHO ENTRANTE
        despacho_entrante = DespachoEntrantes.objects.create(
            id_despacho_consumo_alm = serializador,
            distribucion_confirmada = False,
            fecha_ingreso = serializador.fecha_despacho
        )

        #CREACIÓN DE ITEMS DESPACHO ENTRANTE
        valores_creados_detalles = []
        for id_bien in id_bien_items_serializador_instance:
            item_despacho = ItemDespachoConsumo.objects.filter(id_bien_despachado=id_bien['id_bien_despachado'], id_despacho_consumo=serializador.pk).first()
            item_despacho_entrante = ItemsDespachoEntrante.objects.create(
                id_despacho_entrante = despacho_entrante,
                id_bien = item_despacho.id_bien_despachado,
                id_entrada_alm_del_bien = item_despacho.id_entrada_almacen_bien,
                cantidad_entrante = int(item_despacho.cantidad_despachada),
                cantidad_distribuida = 0,
                fecha_ingreso = serializador.fecha_despacho
                )
            valores_creados_detalles.append(item_despacho_entrante)
        
        #REGISTRO DEL AUMENTO DE LA CANTIDAD SALIENTE POR BIEN Y BODEGA EN INVENTARIO
        for item in data_items_entrega:
            inventario_bien_bodega = Inventario.objects.filter(id_bien=item['id_bien_despachado'], id_bodega=item['id_bodega']).first()
            cantidad_saliente_existente = 0
            if inventario_bien_bodega.cantidad_saliente_consumo != None:
                cantidad_saliente_existente = inventario_bien_bodega.cantidad_saliente_consumo
            inventario_bien_bodega.cantidad_saliente_consumo = cantidad_saliente_existente + int(item['cantidad_despachada'])
            inventario_bien_bodega.save()

        # AUDITORIA MAESTRO DETALLE DE ENTREGA
        valores_creados_detalles = []
        for item in items_serializador:
            valores_creados_detalles.append({'nombre':item.id_bien_despachado.nombre})
            
        descripcion = {"numero_despacho_consumo": str(serializador.numero_despacho_consumo),"es_despacho_conservacion": str(serializador.es_despacho_conservacion),"fecha_despacho": str(serializador.fecha_despacho)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 46,
            "cod_permiso": "CR",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)

        return Response({'success':True, 'detail':'Entrega creada exitosamente', 'Entrega creada': serializer.data, 'Items entregados': items_serializer.data}, status=status.HTTP_200_OK)


class AnularEntregaView(generics.RetrieveUpdateAPIView):
    serializer_class = AnularEntregaSerializer
    queryset = DespachoConsumo.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, id_entrega):
        data = request.data
        entrega_instance = DespachoConsumo.objects.filter(id_despacho_consumo=id_entrega).first()
        if not entrega_instance:
            raise ValidationError('No existe ningún despacho con el parámetro ingresado')
        
        #VALIDACIÓN PARA PODER ACTUALIZAR UNA ENTREGA SOLO HASTA 45 DÍAS HACIA ATRÁS
        if (entrega_instance.fecha_despacho + timedelta(days=45))  < datetime.now():
            raise PermissionDenied('No se puede actualizar una entrega despues de 45 días')

        despacho_entrante = DespachoEntrantes.objects.filter(id_despacho_consumo_alm=entrega_instance.id_despacho_consumo).first()
        if despacho_entrante.id_persona_distribuye or despacho_entrante.id_persona_distribuye == '':
            raise ValidationError('No se puede anular una entrega que ya fue distribuida en viveros')
        
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

        # AUDITORIA MAESTRO DETALLE DE ENTREGA
        valores_creados_detalles = []
        for item in items_entrega:
            valores_creados_detalles.append({'nombre':item.id_bien_despachado.nombre})
            
        descripcion = {"numero_despacho_consumo": str(entrega_instance.numero_despacho_consumo),"es_despacho_conservacion": str(entrega_instance.es_despacho_conservacion),"fecha_despacho": str(entrega_instance.fecha_despacho)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 46,
            "cod_permiso": "AN",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)

        return Response({'success':True, 'detail':'Se ha anulado la entrega correctamente'}, status=status.HTTP_200_OK)

class GetEntradasEntregasView(generics.ListAPIView):
    serializer_class = GetEntradasEntregasSerializer
    queryset = EntradasAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Validar si enviaron parámetros
        filter={}
        for key,value in request.query_params.items():
            if key in ['id_tipo_entrada','numero_entrada_almacen']:
                if value != '':
                    filter[key]=value
        
        entradas = EntradasAlmacen.objects.filter(**filter).filter(Q(id_tipo_entrada=2 ) | Q(id_tipo_entrada=3) | Q(id_tipo_entrada=4) & ~Q(fecha_anulacion=None))
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
        return Response({'success':True, 'detail':'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)

class ActualizarEntregaView(generics.RetrieveUpdateAPIView):
    serializer_class = ActualizarEntregaSerializer
    queryset = DespachoConsumo.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete_items(self, items_entrega, id_entrega):
        #VALIDACIÓN QUE LA ENTREGA ENVIADA EN LA URL EXISTA
        entrega = DespachoConsumo.objects.filter(id_despacho_consumo=id_entrega).first()
        if not entrega:
            raise NotFound('No se encontró ninguna entrega con el parámetro enviado')
        despacho_entrante = DespachoEntrantes.objects.filter(id_despacho_consumo_alm=entrega.id_despacho_consumo).first()

        #VALIDACIÓN PARA PODER ACTUALIZAR UNA ENTREGA SOLO HASTA 45 DÍAS HACIA ATRÁS
        if (entrega.fecha_despacho + timedelta(days=45))  < datetime.now():
            raise PermissionDenied('No se puede actualizar una entrega despues de 45 días')

        #VALIDACIÓN QUE TODOS LOS ITEMS ENVIADOS PARA ELIMINAR EXISTAN
        items_entrega_list = [item['id_item_despacho_consumo'] for item in items_entrega if item['id_item_despacho_consumo']!=None]
        items_entrega = ItemDespachoConsumo.objects.filter(id_despacho_consumo=id_entrega).exclude(id_item_despacho_consumo__in=items_entrega_list) 

        #VALIDACIÓN QUE EL DESPACHO ENTRANTE NO HAYA SIDO DISTRIBUIDO
        despacho_entrante = DespachoEntrantes.objects.filter(id_despacho_consumo_alm=entrega.id_despacho_consumo).first()
        if despacho_entrante.distribucion_confirmada == True:
            raise PermissionDenied('No se puede eliminar un item de una entrega que ya fue distribuido')
        
        #VALIDACIÓN QUE NO INTENTE ELIMINAR TODOS LOS ITEMS DE LA ENTREGA
        if not items_entrega_list:
            raise PermissionDenied('No se pueden eliminar todos los items de una entrega, debe anularla')

        valores_eliminados_detalles = []
        for item_entrega in items_entrega:
            item_despacho_entrante = ItemsDespachoEntrante.objects.filter(id_bien=item_entrega.id_bien_despachado.id_bien, id_entrada_alm_del_bien=item_entrega.id_entrada_almacen_bien.id_entrada_almacen, id_despacho_entrante=despacho_entrante.id_despacho_entrante).first()
            
            #CASO 1. SI EN DESPACHOS ENTRANTES SE SUMARON DOS ITEMS DESPACHO CONSUMO
            if item_despacho_entrante.cantidad_entrante > item_entrega.cantidad_despachada:
                #ACTUALIZA EN CANTIDAD ENTRANTE, EN INVENTARIO Y ELIMINA EL ITEM EN ITEM DESPACHO CONSUMO
                item_despacho_entrante.cantidad_entrante = item_despacho_entrante.cantidad_entrante - item_entrega.cantidad_despachada
                item_despacho_entrante.save()

                item_in_inventario = Inventario.objects.filter(id_bien=item_entrega.id_bien_despachado.id_bien, id_bodega=item_entrega.id_bodega.id_bodega).first()
                item_in_inventario.cantidad_saliente_consumo = item_in_inventario.cantidad_saliente_consumo - item_entrega.cantidad_despachada
                item_in_inventario.save()
                valores_eliminados_detalles.append({'nombre' : item_entrega.id_bien_despachado.nombre})
                item_entrega.delete()


            #CASO 2. SI EN DESPACHOS ENTRANTES SOLO LLEGÓ ESE ITEM POR ELIMINAR
            else:
                #ACTUALIZA EN INVENTARIO, ELIMINA EL ITEM ENTRANTE Y EL ITEM CONSUMO
                item_in_inventario = Inventario.objects.filter(id_bien=item_entrega.id_bien_despachado.id_bien, id_bodega=item_entrega.id_bodega.id_bodega).first()
                item_in_inventario.cantidad_saliente_consumo = item_in_inventario.cantidad_saliente_consumo - item_entrega.cantidad_despachada
                item_in_inventario.save()
                item_despacho_entrante.delete()
                valores_eliminados_detalles.append({'nombre' : item_entrega.id_bien_despachado.nombre})
                item_entrega.delete()

        return valores_eliminados_detalles

    def patch(self, request, id_entrega):
        data_entrega = request.data['data_entrega']
        data_items_entrega = request.data['data_items_entrega']
        entrega = DespachoConsumo.objects.filter(id_despacho_consumo=id_entrega).first()
        if not entrega:
            raise NotFound('No se encontró ninguna entrega con el parámetro ingresado')
        if entrega.despacho_anulado == True:
            raise PermissionDenied('No se puede actualizar una entrega que fue anulada')
        
        #VALIDACIÓN PARA PODER ACTUALIZAR UNA ENTREGA SOLO HASTA 45 DÍAS HACIA ATRÁS
        if (entrega.fecha_despacho + timedelta(days=45))  < datetime.now():
            raise PermissionDenied('No se puede actualizar una entrega despues de 45 días')

        #SE OBTIENEN DOS LISTAS, UNA DE ITEMS POR ACTUALIZAR, Y OTRA DE ITEMS POR CREAR
        items_entrega_crear = [item for item in data_items_entrega if item['id_item_despacho_consumo'] == None]
        items_entrega_actualizar = [item for item in data_items_entrega if item['id_item_despacho_consumo'] != None]
      
        #VALIDACIÓN QUE LOS ITEMS ENVIADOS PARA ACTUALIZAR EXISTAN
        id_items_entrega = [item['id_item_despacho_consumo'] for item in items_entrega_actualizar if item['id_item_despacho_consumo'] != None or item['id_item_despacho_consumo'] == '']
        items_entrega_instance = ItemDespachoConsumo.objects.filter(id_item_despacho_consumo__in=id_items_entrega)
        if len(id_items_entrega) != len(items_entrega_instance):
            raise ValidationError('Todos los id bien enviados para actualizar deben existir')
        
        """
            Validaciones para la creación de nuevos items
        
        """

        #VALIDACIÓN LOS ID_BIEN ENVIADOS DEBEN ESTAR EN ALGÚN ITEM DESPACHO DE LA ENTRADA
        id_bien_list = [item['id_bien_despachado'] for item in items_entrega_crear]
        bien_in_item = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=entrega.id_entrada_almacen_cv.id_entrada_almacen, id_bien__in=id_bien_list)
        id_bien_in_bienes_despachados = [bien.id_bien.id_bien for bien in bien_in_item]
        if not set(id_bien_list).issubset(id_bien_in_bienes_despachados):
            raise ValidationError('Todos los id_bienes_despachados deben pertenecer a la entrada seleccionada')

        #VALIDACIÓN DE QUE NO HAYAN ENTREGAS POSTERIORES DE LOS BIENES QUE SE QUIEREN ENTREGAR
        items_fecha_posterior_entrega_actual = []
        items_fecha_anterior_entrega_actual = []

        for item in items_entrega_crear:
            items_despachos_fecha = ItemDespachoConsumo.objects.filter(id_bien_despachado=item['id_bien_despachado'], id_bodega=item['id_bodega'])
            for itemsito in items_despachos_fecha:
                if itemsito.id_despacho_consumo.fecha_despacho > entrega.fecha_despacho:
                    items_fecha_posterior_entrega_actual.append(item)
                else:
                    items_fecha_anterior_entrega_actual.append(item)
        
        if items_fecha_posterior_entrega_actual:
            try:
                raise ValidationError('No se puede realizar la entrega si a un bien ya se le generaron salidas posteriores en la misma bodega')
            except ValidationError as e:
                return Response({'success':False, 'detail':'No se puede realizar la entrega si a un bien ya se le generaron salidas posteriores en la misma bodega', 'items_fecha_posterior_entrega_actual': items_fecha_posterior_entrega_actual}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE LOS ID_BIEN_DESPACHADOS EXISTAN EN INVENTARIO
        id_bien_despachados = [item['id_bien_despachado'] for item in items_entrega_crear]
        bien_despachados_instance = CatalogoBienes.objects.filter(id_bien__in=id_bien_despachados)
        if len(set(id_bien_despachados)) != len(bien_despachados_instance):
            raise ValidationError('Todos los id_bien_despachados seleccionados deben existir')

        #VALIDACIÓN QUE LOS ID_BODEGAS ENVIADOS EXISTAN
        bodegas = [item['id_bodega']for item in items_entrega_crear]
        bodegas_instance = Bodegas.objects.filter(id_bodega__in=bodegas)
        if len(set(bodegas)) != len(set(bodegas_instance)):
            raise ValidationError('Todas las bodegas seleccionadas desde la cúal se entregan los items de entrega deben existir')

        #VALIDACIÓN QUE LOS BIENES_DESPACHADOS TENGAN CANTIDAD DISPONIBLE POR DESPACHAR SEGÚN LAS ENTREGAS ANTERIORES DE LA ENTRADA SELECCIONADA
        items_pasan_validacion = []
        items_no_pasan_validacion = []

        for item in items_entrega_crear:
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
            try:
                raise ValidationError('No se puede realizar una entrega si alguno de sus items ya fue totalmente entregado')
            except ValidationError as e:
                return Response({'success':False, 'detail':'No se puede realizar una entrega si alguno de sus items ya fue totalmente entregado', 'Items totalmente entregados': items_no_pasan_validacion}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE EXISTA LA CANTIDAD A ENTREGAR EN LA BODEGA SELECCIONADA
        items_con_cantidades_disponible_en_bodega = []
        items_con_cantidad_no_disponible_en_bodega = []
        data = []

        for item in items_entrega_crear:
            cantidad = UtilAlmacen.get_cantidades_disponibles_entregas(item['id_bien_despachado'], item['id_bodega'], entrega.fecha_despacho)
            if int(item['cantidad_despachada']) > cantidad:
                item['cantidad_disponible_en_bodega'] = cantidad
                items_con_cantidad_no_disponible_en_bodega.append(item)
            else:
                items_con_cantidades_disponible_en_bodega.append(item)

        if items_con_cantidad_no_disponible_en_bodega:
            try:
                raise ValidationError('No se puede realizar una entrega si alguno de los bienes enviados a despachar no tiene cantidades disponibles en bodega')
            except ValidationError as e:
                return Response({'success':False, 'detail':'No se puede realizar una entrega si alguno de los bienes enviados a despachar no tiene cantidades disponibles en bodega', 'Items que no tienen cantidades disponibles en bodega': items_con_cantidad_no_disponible_en_bodega}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE EL NÚMERO DE POSICIÓN NO SEA REPETIDO
        items_entrega_number = ItemDespachoConsumo.objects.filter(id_despacho_consumo=id_entrega)
        numeros_posicion = [item.numero_posicion_despacho for item in items_entrega_number]
        numeros_posicion_items = [item['numero_posicion_despacho'] for item in items_entrega_crear]
        if len(numeros_posicion) != len(set(numeros_posicion)):
            raise ValidationError('Los números de posición de los items deben ser únicos')
        for numero in numeros_posicion_items:
            if numero in numeros_posicion:
                raise ValidationError('Los números de posición de los items deben ser únicos')
            
        # ACTUALIZAR MAESTRO
        previous_maestro = copy.copy(entrega)
        
        serializer_maestro = self.serializer_class(entrega, data=data_entrega)
        serializer_maestro.is_valid(raise_exception=True)
        serializer_maestro.save()
        
        valores_actualizados_maestro = {'previous':previous_maestro, 'current':entrega}

        """
        
            Inicia proceso de Creación de Nuevos Items
        
        """
        #DELETE ITEMS ENTREGA
        valores_eliminados_detalles = self.delete_items(data_items_entrega, id_entrega)

        #CREACIÓN DE ENTREGA DETALLE
        for item in items_entrega_crear:
            item['id_despacho_consumo'] = entrega.id_despacho_consumo

        items_serializer = CreateItemsEntregaSerializer(data=items_entrega_crear, many=True)
        items_serializer.is_valid(raise_exception=True)
        items_serializador = items_serializer.save()
        items_serializer_data = items_serializer.data

        for item in items_serializer_data:
            data.append(item)
        
        #INICIA CREACIÓN O ACTUALIZACIÓN DE ITEMS DESPACHOS ENTRANTES
        despacho_entrante_instance = DespachoEntrantes.objects.filter(id_despacho_consumo_alm=entrega.id_despacho_consumo).first()

        #VALIDACIÓN SI ESE BIEN YA ESTABA DESPACHADO EN ITEMS ENTRANTES
        bienes_existen_in_items_entrantes = []
        bienes_no_existen_in_items_entrantes = []
        for item in items_serializador:
            item_in_despachos_entrantes = ItemsDespachoEntrante.objects.filter(id_bien=item.id_bien_despachado.id_bien).first()
            if item_in_despachos_entrantes:
                print('entró por acá')
                bienes_existen_in_items_entrantes.append(item)
            else:
                bienes_no_existen_in_items_entrantes.append(item)

        #REAGRUPACIÓN PARA CONVERTIR DOS REGISTROS DE ITEMS DESPACHOS SALIENTES EN UNO SOLO PARA ITEMS DESPACHOS ENTRANTE
        id_bien_items_serializador = [item.id_bien_despachado.id_bien for item in bienes_no_existen_in_items_entrantes]
        id_bien_items_serializador_instance = ItemDespachoConsumo.objects.filter(id_bien_despachado__in=id_bien_items_serializador, id_despacho_consumo=entrega.id_despacho_consumo).values('id_bien_despachado', 'id_entrada_almacen_bien').annotate(cantidad_despachada=Sum('cantidad_despachada'))
        
        #ACTUALIZACIÓN DE ITEM DESPACHO ENTRANTE SI EL BIEN NO ESTABA EN ITEMS
        for item in bienes_existen_in_items_entrantes:
            item_in_despachos_entrantes = ItemsDespachoEntrante.objects.filter(id_bien=item.id_bien_despachado.id_bien, id_despacho_entrante=despacho_entrante_instance, id_entrada_alm_del_bien=entrega.id_entrada_almacen_cv.id_entrada_almacen).first()
            item_in_despachos_entrantes.cantidad_entrante += item.cantidad_despachada
            item_in_despachos_entrantes.save()

        #CREACIÓN DE ITEMS DESPACHO ENTRANTE SI EL BIEN NO ESTABA EN ITEMS DESPACHO ENTRANTE ANTES
        for id_bien in id_bien_items_serializador_instance:
            item_despacho = ItemDespachoConsumo.objects.filter(id_bien_despachado=id_bien['id_bien_despachado'], id_despacho_consumo=entrega.id_despacho_consumo).first()
            item_despacho_entrante = ItemsDespachoEntrante.objects.create(
                id_despacho_entrante = despacho_entrante_instance,
                id_bien = item_despacho.id_bien_despachado,
                id_entrada_alm_del_bien = item_despacho.id_entrada_almacen_bien,
                cantidad_entrante = int(id_bien_items_serializador_instance[0]['cantidad_despachada']),
                cantidad_distribuida = 0,
                fecha_ingreso = entrega.fecha_despacho
                )
        
        #REGISTRO DEL AUMENTO DE LA CANTIDAD SALIENTE POR BIEN Y BODEGA EN INVENTARIO
        for item in items_entrega_crear:
            inventario_bien_bodega = Inventario.objects.filter(id_bien=item['id_bien_despachado'], id_bodega=item['id_bodega']).first()
            cantidad_saliente_existente = 0
            if inventario_bien_bodega.cantidad_saliente_consumo != None:
                cantidad_saliente_existente = inventario_bien_bodega.cantidad_saliente_consumo
            inventario_bien_bodega.cantidad_saliente_consumo = cantidad_saliente_existente + int(item['cantidad_despachada'])
            inventario_bien_bodega.save()

        """"
        
            Inicia proceso de actualización de Items de la Entrega
        
        """
          
        for item in items_entrega_actualizar:
            item_instance = ItemDespachoConsumo.objects.filter(id_item_despacho_consumo=item['id_item_despacho_consumo']).first()
            cantidad_maxima_despachar = UtilAlmacen.get_valor_maximo_despacho(item_instance.id_bien_despachado.id_bien, item_instance.id_bodega.id_bodega, item_instance.id_despacho_consumo.id_despacho_consumo)
            if int(item['cantidad_despachada']) > cantidad_maxima_despachar:
                raise PermissionDenied('No se puede despachar una cantidad superior a la disponible en esa fecha')
        
        items_actualizados = []

        for item in items_entrega_actualizar:
            item_instance = ItemDespachoConsumo.objects.filter(id_item_despacho_consumo=item['id_item_despacho_consumo']).first()
            item_previous = copy.copy(item_instance)
            if int(item['cantidad_despachada']) < item_instance.cantidad_despachada and int(item['cantidad_despachada']) > 0:
                cantidad_anterior = item_instance.cantidad_despachada
                item_instance.cantidad_despachada = item['cantidad_despachada']
                item_instance.observacion = item['observacion']
                item_instance.save()
                serializer = GetItemsEntregaSerializer(item_instance, many=False)
                data.append(serializer.data)
                items_actualizados.append({'descripcion': {'nombre':item_instance.id_bien_despachado.nombre}, 'previous':item_previous,'current':item_instance})

                item_in_inventario = Inventario.objects.filter(id_bien=item_instance.id_bien_despachado, id_bodega=item_instance.id_bodega).first()
                item_in_inventario.cantidad_saliente_consumo = item_in_inventario.cantidad_saliente_consumo - (cantidad_anterior - int(item['cantidad_despachada']))
                item_in_inventario.save()

                item_in_despachos_entrantes = ItemsDespachoEntrante.objects.filter(id_bien=item['id_bien_despachado'], id_despacho_entrante=despacho_entrante_instance.id_despacho_entrante, id_entrada_alm_del_bien=entrega.id_entrada_almacen_cv.id_entrada_almacen).first()
                item_in_despachos_entrantes.cantidad_entrante = item_in_despachos_entrantes.cantidad_entrante - (cantidad_anterior - int(item['cantidad_despachada']))
                item_in_despachos_entrantes.save()
                
            if int(item['cantidad_despachada']) > item_instance.cantidad_despachada:
                cantidad_anterior = item_instance.cantidad_despachada
                item_instance.cantidad_despachada = item['cantidad_despachada']
                item_instance.observacion = item['observacion']
                item_instance.save()
                serializer = GetItemsEntregaSerializer(item_instance, many=False)
                data.append(serializer.data)
                items_actualizados.append({'descripcion': {'nombre':item_instance.id_bien_despachado.nombre}, 'previous':item_previous,'current':item_instance})
                
                item_in_inventario = Inventario.objects.filter(id_bien=item_instance.id_bien_despachado, id_bodega=item_instance.id_bodega).first()
                item_in_inventario.cantidad_saliente_consumo = item_in_inventario.cantidad_saliente_consumo + (int(item['cantidad_despachada']) - cantidad_anterior)
                item_in_inventario.save()

                item_in_despachos_entrantes = ItemsDespachoEntrante.objects.filter(id_bien=item['id_bien_despachado'], id_despacho_entrante=despacho_entrante_instance.id_despacho_entrante, id_entrada_alm_del_bien=entrega.id_entrada_almacen_cv.id_entrada_almacen).first()
                item_in_despachos_entrantes.cantidad_entrante = item_in_despachos_entrantes.cantidad_entrante + (int(item['cantidad_despachada']) - cantidad_anterior)
                item_in_despachos_entrantes.save()
            
            elif int(item['cantidad_despachada']) == item_previous.cantidad_despachada:
                item_instance.observacion = item['observacion']
                item_instance.save()
                serializer = GetItemsEntregaSerializer(item_instance, many=False)
                data.append(serializer.data)
                items_actualizados.append({'descripcion': {'nombre':item_instance.id_bien_despachado.nombre}, 'previous':item_previous,'current':item_instance})
        
        # AUDITORIA MAESTRO DETALLE DE ENTREGA
        valores_creados_detalles = []
        for item in items_serializador:
            valores_creados_detalles.append({'nombre':item.id_bien_despachado.nombre})
            
        descripcion = {"numero_despacho_consumo": str(entrega.numero_despacho_consumo),"es_despacho_conservacion": str(entrega.es_despacho_conservacion),"fecha_despacho": str(entrega.fecha_despacho)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 46,
            "cod_permiso": "AC",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados_maestro": valores_actualizados_maestro,
            "valores_creados_detalles": valores_creados_detalles,
            "valores_actualizados_detalles": items_actualizados,
            "valores_eliminados_detalles": valores_eliminados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)

        return Response({'success':True, 'detail':'Entrega actualizada correctamente', 'data': data}, status=status.HTTP_201_CREATED)

class GetItemsEntradasEntregasView(generics.ListAPIView):
    serializer_class = GetItemsEntradasEntregasSerializer
    queryset = ItemEntradaAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_entrada):
        items_entrada = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=id_entrada, id_bien__solicitable_vivero=True).values('id_entrada_almacen', 'id_bien').annotate(cantidad_entrante=Sum('cantidad'))
        if not items_entrada:
            return Response({'success':True, 'detail':'No existe ningún item de esta entrada que pueda ser entregado a viveros'}, status=status.HTTP_200_OK)

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
            raise PermissionDenied('Ninguno de los items de esta entrada tiene cantidades faltantes por entregar')
        return Response({'success':True, 'detail':'Items encontrados exitosamente', 'data': item_con_disponibilidad}, status=status.HTTP_200_OK)

# class DeleteItemsEntregaView(generics.RetrieveDestroyAPIView):
#     serializer_class = DeleteItemsEntregaSerializer
#     queryset = ItemDespachoConsumo.objects.all()
#     permission_classes = [IsAuthenticated]

#     def delete(self, request, id_entrega):
#         items_eliminar = request.data

#         #VALIDACIÓN QUE LA ENTREGA ENVIADA EN LA URL EXISTA
#         entrega = DespachoConsumo.objects.filter(id_despacho_consumo=id_entrega).first()
#         if not entrega:
#             raise NotFound('No se encontró ninguna entrega con el parámetro enviado')
#         despacho_entrante = DespachoEntrantes.objects.filter(id_despacho_consumo_alm=entrega.id_despacho_consumo).first()

#         #VALIDACIÓN PARA PODER ACTUALIZAR UNA ENTREGA SOLO HASTA 45 DÍAS HACIA ATRÁS
#         if (entrega.fecha_despacho + timedelta(days=45))  < datetime.now():
#             raise PermissionDenied('No se puede actualizar una entrega despues de 45 días')

#         #VALIDACIÓN QUE TODOS LOS ITEMS ENVIADOS PARA ELIMINAR EXISTAN
#         items_entrega_list = [item['id_item_despacho_consumo'] for item in items_eliminar]
#         items_entrega = ItemDespachoConsumo.objects.filter(id_item_despacho_consumo__in=items_entrega_list)
#         items_entrega_id = [item.id_item_despacho_consumo for item in items_entrega]
#         for item in items_entrega_list:
#             if item not in items_entrega_id:
#                 raise ValidationError('Todos los items por eliminar deben existir')

#         #VALIDACIÓN QUE TODOS LOS ITEMS ENVIADOS PERTENEZCAN A LA ENTREGA ENVIADA EN LA URL
#         entrega_items_list = [item['id_despacho_consumo'] for item in items_eliminar]
#         if len(set(entrega_items_list)) > 1:
#             raise ValidationError('Todos los items enviados deben pertenecer a la entrega seleccionada') 
#         if int(entrega_items_list[0]) !=  entrega.id_despacho_consumo:
#             raise ValidationError('Todos los items a eliminar deben pertenecer a la entrega seleccionada') 

#         #VALIDACIÓN QUE EL DESPACHO ENTRANTE NO HAYA SIDO DISTRIBUIDO
#         despacho_entrante = DespachoEntrantes.objects.filter(id_despacho_consumo_alm=entrega.id_despacho_consumo).first()
#         if despacho_entrante.distribucion_confirmada == True:
#             raise PermissionDenied('No se puede eliminar un item de una entrega que ya fue distribuido')
        
#         #VALIDACIÓN QUE NO INTENTE ELIMINAR TODOS LOS ITEMS DE LA ENTREGA
#         items_entrega_todos = ItemDespachoConsumo.objects.filter(id_despacho_consumo=id_entrega)
#         if len(items_entrega_list) == len(items_entrega_todos):
#             raise PermissionDenied('No se pueden eliminar todos los items de una entrega, debe anularla')

#         valores_eliminados_detalles = []
#         for item in items_eliminar:
#             item_entrega = ItemDespachoConsumo.objects.filter(id_item_despacho_consumo=item['id_item_despacho_consumo']).first()
#             item_despacho_entrante = ItemsDespachoEntrante.objects.filter(id_bien=item_entrega.id_bien_despachado.id_bien, id_entrada_alm_del_bien=item_entrega.id_entrada_almacen_bien.id_entrada_almacen, id_despacho_entrante=despacho_entrante.id_despacho_entrante).first()
            
#             #CASO 1. SI EN DESPACHOS ENTRANTES SE SUMARON DOS ITEMS DESPACHO CONSUMO
#             if item_despacho_entrante.cantidad_entrante > item_entrega.cantidad_despachada:
#                 #ACTUALIZA EN CANTIDAD ENTRANTE, EN INVENTARIO Y ELIMINA EL ITEM EN ITEM DESPACHO CONSUMO
#                 item_despacho_entrante.cantidad_entrante = item_despacho_entrante.cantidad_entrante - item_entrega.cantidad_despachada
#                 item_despacho_entrante.save()

#                 item_in_inventario = Inventario.objects.filter(id_bien=item_entrega.id_bien_despachado.id_bien, id_bodega=item_entrega.id_bodega.id_bodega).first()
#                 item_in_inventario.cantidad_saliente_consumo = item_in_inventario.cantidad_saliente_consumo - item_entrega.cantidad_despachada
#                 item_in_inventario.save()
#                 valores_eliminados_detalles.append({'nombre' : item_entrega.id_bien_despachado.nombre})
#                 item_entrega.delete()


#             #CASO 2. SI EN DESPACHOS ENTRANTES SOLO LLEGÓ ESE ITEM POR ELIMINAR
#             else:
#                 #ACTUALIZA EN INVENTARIO, ELIMINA EL ITEM ENTRANTE Y EL ITEM CONSUMO
#                 item_in_inventario = Inventario.objects.filter(id_bien=item_entrega.id_bien_despachado.id_bien, id_bodega=item_entrega.id_bodega.id_bodega).first()
#                 item_in_inventario.cantidad_saliente_consumo = item_in_inventario.cantidad_saliente_consumo - item_entrega.cantidad_despachada
#                 item_in_inventario.save()
#                 item_despacho_entrante.delete()
#                 valores_eliminados_detalles.append({'nombre' : item_entrega.id_bien_despachado.nombre})
#                 item_entrega.delete()

#         # AUDITORIA ELIMINACIÓN DE ITEMS ENTREGA
#         descripcion = {"numero_despacho_almacen": str(entrega.numero_despacho_consumo), "es_despacho_conservacion": str(entrega.es_despacho_conservacion),"fecha_despacho": str(entrega.fecha_despacho)}
#         direccion=Util.get_client_ip(request)
#         auditoria_data = {
#             "id_usuario" : request.user.id_usuario,
#             "id_modulo" : 46,
#             "cod_permiso": "BO",
#             "subsistema": 'ALMA',
#             "dirip": direccion,
#             "descripcion": descripcion,
#             "valores_eliminados_detalles": valores_eliminados_detalles
#         }
#         Util.save_auditoria_maestro_detalle(auditoria_data)

#         return Response({'success':True, 'detail':'Items Eliminados Exitosamente'}, status=status.HTTP_200_OK)