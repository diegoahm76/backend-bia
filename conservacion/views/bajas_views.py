from rest_framework import generics, status
from rest_framework.views import APIView
from seguridad.utils import Util  
from django.db.models import Q, F, Sum
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, time, timedelta
from datetime import timezone
import copy
import json
from backend.settings.base import EMAIL_HOST_USER, AUTHENTICATION_360_NRS
from seguridad.models import Personas
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from conservacion.models.cuarentena_models import (
    BajasVivero,
    ItemsBajasVivero
)
from conservacion.models.viveros_models import (
    Vivero
)
from conservacion.serializers.bajas_serializers import (
    BajasViveroPostSerializer,
    ItemsBajasViveroGetSerializer,
    ItemsBajasViveroPostSerializer,
    ViveroBajasSerializer,
    CatalogoBienesBajasSerializer,
    CatalogoBienesSerializerBusquedaAvanzada,
    ItemsBajasActualizarViveroPostSerializer,
    GetBajaByNumeroSerializer
)
from almacen.models.bienes_models import (
    CatalogoBienes
)
from conservacion.models.inventario_models import (
    InventarioViveros
)
from conservacion.utils import UtilConservacion
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

class CreateBajasVivero(generics.UpdateAPIView):
    serializer_class = BajasViveroPostSerializer
    queryset = BajasVivero.objects.all()
    permission_classes = [IsAuthenticated]
    serializador_items_bajas = ItemsBajasViveroPostSerializer
    
    def put(self, request):
        datos_ingresados = request.data
        info_baja = json.loads(datos_ingresados['info_baja'])
        items_baja = json.loads(datos_ingresados['items_baja'])
        info_baja['ruta_archivo_soporte'] = request.FILES.get('ruta_archivo_soporte')
        user_logeado = request.user
        
        # SE OBTIENE EL ÚLTIMO NÚMERO DE TRASLADO DISPONIBLE
        bajas_existentes = BajasVivero.objects.filter(tipo_baja='B')
        if bajas_existentes:
            numero_baja = [i.nro_baja_por_tipo for i in bajas_existentes]
            info_baja['nro_baja_por_tipo'] = max(numero_baja) + 1
        else:
            info_baja['nro_baja_por_tipo'] = 1
        
        # SE ASIGNAN LOS CAMPOS POR DEFECTO
        info_baja['fecha_registro'] = datetime.now()
        info_baja['id_persona_baja'] = user_logeado.persona.id_persona
        info_baja['tipo_baja'] = 'B'
        
        # SE VALIDA LA EXISTENCIA DEL VIVERO, QUE EL VIVERO ESTE ABIERTO Y ACTIVO
        instancia_vivero = Vivero.objects.filter(id_vivero=info_baja['id_vivero']).first()
        
        if instancia_vivero.activo == False:
            raise ValidationError ('El vivero ingresado no se encuentra activo')
        
        if instancia_vivero.fecha_ultima_apertura == None and instancia_vivero.fecha_cierre_actual != None and instancia_vivero.id_persona_cierra != None and instancia_vivero.justificacion_cierre != None:
            raise ValidationError ('El vivero no está abierto')
        
        # SE VALIDA QUE LA QUE LA FECHA DE BAJA SEA DE MENOS DE UN DÍA DE ANTIGÜEDAD
        info_baja['fecha_baja'] = datetime.strptime(info_baja['fecha_baja'], '%Y-%m-%d %H:%M:%S')
                
        # SE VALIDA QUE NO HAYAN REGISTROS POSTERIORES A LA FECHA DE BAJA INGRESADA
        ultima_fecha_de_baja = bajas_existentes.order_by('fecha_baja').last()
        if ultima_fecha_de_baja:
            if info_baja['fecha_baja'] < ultima_fecha_de_baja.fecha_baja:
                raise ValidationError ('No es posible crear la baja porque hay un registro de bajas con fecha posterior al ingresado')
            
        # SE OBTIENEN LAS HORAS EXACTAS QUE HAN TRANSCURRIDO DESDE LA FECHA DE BAJA HASTA LA FECHA ACTUAL
        fecha_posible = datetime.now() - timedelta(days=1)
        if info_baja['fecha_baja'] < fecha_posible:
            raise ValidationError ('No es posible registrar una baja con más de un día de anterioridad.')
        
        # SE VALIDA QUE POR LO MENOS LLEGUE UN ITEM EN LA PETICIÓN
        if len(items_baja) <= 0:
            raise ValidationError ("'Debe ingresr al menos un bien para registrar una baja")
        
        # VALIDACIONES DE LOS ITEMS A DAR DE BAJA
        aux_nro_posicion = []
        aux_valores_repetidos = []
        valores_creados_detalles = [] 
        for i in items_baja:
            instancia_bien = CatalogoBienes.objects.filter(id_bien=i['id_bien']).first()
            instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=i['id_bien'],id_vivero=info_baja['id_vivero']).first()
            
            # SE VALIDA LA EXISTENCIA DEL BIEN
            if not instancia_bien:
                raise ValidationError ('El bien  con número de posición ' + str(i['nro_posicion']) +  'no existe')
            if not instancia_bien_vivero:
                raise ValidationError ('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) +  'no tiene registros en el inventario del vivero')
            
            # SE VALIDA QUE EL NÚMERO DE POSICIÓN SEA ÚNICO
            if int(i['id_bien']) in aux_valores_repetidos:
                raise ValidationError ('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' No se puede ingresar dos veces un mismo bien dentro de una solicitud')
            
            # SE VALIDA QUE EL NÚMERO DE POSICIÓN SEA ÚNICO
            if int(i['nro_posicion']) in aux_nro_posicion:
                raise ValidationError ('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' tiene un número de posición que ya existe')
            
            # SE VALIDA QUE LA CANTIDAD DEL BIEN A DAR DE BAJA SEA MAYOR QUE CERO
            if int(i['cantidad_baja']) <= 0:
                raise ValidationError ('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' tiene como cantidad de baja cero, la cantidad debe ser mayor que cero')
            
            # SE VALIDA QUE HAYA SALDO DISPONIBLE
            saldo_disponible = UtilConservacion.get_cantidad_disponible_F(instancia_bien, instancia_bien_vivero) 
            if int(i['cantidad_baja']) > saldo_disponible:
                raise ValidationError ('En el bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' no tiene saldo disponible para suplir la cantidad de bajas ingresada')
            
            # SE GUARDAN EL NÚMERO DE POSICIÓN Y EL ID DE BIEN EN LISTAS PARA VALIDAR SI SE REPITEN
            aux_nro_posicion.append(i['nro_posicion'])
            aux_valores_repetidos.append(i['id_bien'])
            valores_creados_detalles.append({'nombre' : instancia_bien.nombre})
        
        # SE CREA EL REGISTRO EN LA TABLA TRASLADOS
        serializer_crear = self.serializer_class(data=info_baja, many=False)
        serializer_crear.is_valid(raise_exception=True)
        aux_ultimo = serializer_crear.save()
        
        # SE ASIGNA EL ID TRASLADO A LOS ITEMS A TRASLADAR
        for i in items_baja:
            i['id_baja'] = aux_ultimo.pk
            
        # SE CREA EL REGISTRO EN LA TABLA ITEM_TRASLADOS
        serializer_crear_items = self.serializador_items_bajas(data=items_baja, many=True)
        serializer_crear_items.is_valid(raise_exception=True)
        serializer_crear_items.save()
        
        # AUDITORIA MAESTRO DETALLE DE DESPACHO
        descripcion = {"numero_baja": str(info_baja['nro_baja_por_tipo']), "tipo_baja": 'B', "fecha_baja": str(info_baja['fecha_baja'])}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 55,
            "cod_permiso": "CR",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        #SE GUARDAN LOS DATOS EN EL INVENTARIO VIVERO ORIGEN Y EN EL INVENTARIO DESTINO
        for i in items_baja:
            instancia_bien = CatalogoBienes.objects.filter(id_bien=i['id_bien']).first()
            instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=i['id_bien'],id_vivero=info_baja['id_vivero']).first()
            instancia_bien_vivero.cantidad_bajas = instancia_bien_vivero.cantidad_bajas if instancia_bien_vivero.cantidad_bajas else 0
            instancia_bien_vivero.cantidad_bajas = instancia_bien_vivero.cantidad_bajas + i['cantidad_baja']
            instancia_bien_vivero.save()
        
        return Response({'succes' : True, 'detail' : 'Baja creada con éxito'}, status=status.HTTP_200_OK)


class ActualizarBajasVivero(generics.UpdateAPIView):
    serializer_class = BajasViveroPostSerializer
    queryset = BajasVivero.objects.all()
    permission_classes = [IsAuthenticated]
    serializador_items_bajas = ItemsBajasViveroPostSerializer
    serializador_actualizar_items_bajas = ItemsBajasActualizarViveroPostSerializer
    
    def put(self, request):
        datos_ingresados = request.data
        info_baja = json.loads(datos_ingresados['info_baja'])
        items_baja = json.loads(datos_ingresados['items_baja'])
        info_baja['ruta_archivo_soporte'] = request.FILES.get('ruta_archivo_soporte')
        user_logeado = request.user
        items_nuevos = []
        items_actualizar = []
        items_eliminar = []
        valores_eliminados_detalles = []
        valores_actualizados_detalles = []
        aux_valores_repetidos = []
        aux_nro_posicion = []
        
        instancia_baja = BajasVivero.objects.filter(id_baja=info_baja['id_baja']).first()
        if not instancia_baja:
            raise ValidationError ('No existe una baja con ese id')
        
        # SE VALIDA QUE NO SE ACTUALICE UNA BAJA CON MÁS DE 30 DÍAS DE ANTIGÜEDAD
        fecha_posible = datetime.now() - timedelta(days=30)
        if (datetime.now()) < fecha_posible:
            raise ValidationError ('No es posible actualizar una baja con más 30 días de anterioridad')
        
        # SE VALIDA QUE POR LO MENOS LLEGUE UN ITEM EN LA PETICIÓN
        if len(items_baja) <= 0:
            raise ValidationError ('No es posible eliminar todos los items de una baja')
        
        # SE OBTIENEN LOS ITEMS ITEMS QUE SE VAN A AÑADIR
        items_nuevos = [i for i in items_baja if i['id_item_baja_viveros'] == None]
        
        # SE OBTIENEN LOS ITEMS QUE SE VAN A ACTUALZIAR
        items_actualizar = [i for i in items_baja if i['id_item_baja_viveros'] != None]
        
        # SE OBTIENEN LOS ITEMS QUE SE VAN A ELIMINAR
        items_existentes = ItemsBajasVivero.objects.filter(id_baja=info_baja['id_baja'])
        id_items_existentes = [i.id_item_baja_viveros for i in items_existentes]
        id_items_entrantes = [i['id_item_baja_viveros'] for i in items_baja if i['id_item_baja_viveros']!=None]
        id_items_eliminar = [i for i in id_items_existentes if i not in id_items_entrantes]
        items_eliminar = ItemsBajasVivero.objects.filter(id_item_baja_viveros__in=id_items_eliminar)
        
        valores_eliminados_detalles = [{'nombre' : i.id_bien.nombre} for i in items_eliminar]
        
        # SE HACEN LAS VALIDACIONES PARA LAS ACTUALIZACIONES
        for i in items_actualizar:
            instancia_item_baja = ItemsBajasVivero.objects.filter(id_item_baja_viveros=i['id_item_baja_viveros']).first()
            if not instancia_item_baja:
                raise ValidationError ('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' no existe el registro de la baja')
            instancia_bien = CatalogoBienes.objects.filter(id_bien=instancia_item_baja.id_bien.id_bien).first()
            if not instancia_bien:
                raise ValidationError ('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' no existe registrado en el sistema como bien')
            instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=instancia_bien.id_bien,id_vivero=instancia_baja.id_vivero).first()
            if not instancia_bien_vivero:
                raise ValidationError ('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' no existe en el inventario del vivero.')
            
            if i['cantidad_baja'] != instancia_bien_vivero.cantidad_bajas:
                fecha_posible = datetime.now() - timedelta(days=1)
                if instancia_baja.fecha_baja < fecha_posible:
                    raise ValidationError ('No es posible actualizar la cantidad de una baja con más de un día de anterioridad.')
                aux_cantidad = i['cantidad_baja'] - instancia_item_baja.cantidad_baja
                #instancia_bien_vivero.cantidad_bajas = instancia_bien_vivero.cantidad_bajas + aux_cantidad
                saldo_disponible = UtilConservacion.get_cantidad_disponible_F(instancia_bien, instancia_bien_vivero) - aux_cantidad
                if saldo_disponible <= 0:
                    raise ValidationError ('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ', not tiene saldo disponible para cubrir la cantidad de bajas ingresada')
                
            if i['cantidad_baja'] == 0:
                raise ValidationError ('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' tiene cantidad igual a cero, la cantidad debe ser mayor que cero')
        
        aux_valores_repetidos = [i.id_bien.id_bien for i in items_existentes]
        aux_nro_posicion = [i.nro_posicion for i in items_existentes]
        
        # VALIDACIONES DE LOS ITEMS CREADOS
        valores_creados_detalles = [] 
        for i in items_nuevos:
            instancia_bien = CatalogoBienes.objects.filter(id_bien=i['id_bien']).first()
            instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=i['id_bien'],id_vivero=instancia_baja.id_vivero).first()
            
            # SE VALIDA LA EXISTENCIA DEL BIEN
            if not instancia_bien:
                raise ValidationError ('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) +  'no existe.')
            if not instancia_bien_vivero:
                raise ValidationError ('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) +  'no tiene registros en el inventario del vivero.')
            
            # SE VALIDA QUE EL NÚMERO DE POSICIÓN SEA ÚNICO
            if i['id_bien'] in aux_valores_repetidos:
                raise ValidationError ('Error en el bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' No se puede ingresar dos veces un mismo bien dentro de una solicitud.')
            
            # SE VALIDA QUE EL NÚMERO DE POSICIÓN SEA ÚNICO
            if i['nro_posicion'] in aux_nro_posicion:
                raise ValidationError ('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' tiene un número de posición que ya existe.')            
            # SE VALIDA QUE LA CANTIDAD DEL BIEN A DAR DE BAJA SEA MAYOR QUE CERO
            if i['cantidad_baja'] <= 0:
                raise ValidationError ('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' tiene como cantidad de baja cero, la cantidad debe ser mayor que cero.')
            
            # SE VALIDA QUE HAYA SALDO DISPONIBLE
            saldo_disponible = UtilConservacion.get_cantidad_disponible_F(instancia_bien, instancia_bien_vivero) 
            if i['cantidad_baja'] > saldo_disponible:
                raise ValidationError ('En el bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' no tiene saldo disponible para suplir la cantidad de bajas ingresada.')
            
            # SE GUARDAN EL NÚMERO DE POSICIÓN Y EL ID DE BIEN EN LISTAS PARA VALIDAR SI SE REPITEN
            aux_nro_posicion.append(i['nro_posicion'])
            aux_valores_repetidos.append(i['id_bien'])
            valores_creados_detalles.append({'nombre' : instancia_bien.nombre})
        
        # SE RESTAN LAS CANTIDADES AL INVENTARIO VIVERO DE LOS ITEMS ELIMINADOS
        for i in items_eliminar:
            instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=i.id_bien,id_vivero=instancia_baja.id_vivero).first()
            instancia_bien_vivero.cantidad_bajas = instancia_bien_vivero.cantidad_bajas if instancia_bien_vivero.cantidad_bajas else 0
            instancia_bien_vivero.cantidad_bajas = instancia_bien_vivero.cantidad_bajas - i.cantidad_baja
            instancia_bien_vivero.save()
            
        # SE ACTUALIZAN LAS CANTIDADES DE BAJA EN EL INVENTARIO VIVERO
        for i in items_baja:
            if i['id_item_baja_viveros'] == None:
                instancia_bien = CatalogoBienes.objects.filter(id_bien=i['id_bien']).first()
                instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=i['id_bien'],id_vivero=instancia_baja.id_vivero).first()
                instancia_bien_vivero.cantidad_bajas = instancia_bien_vivero.cantidad_bajas if instancia_bien_vivero.cantidad_bajas else 0
                instancia_bien_vivero.cantidad_bajas = instancia_bien_vivero.cantidad_bajas + i['cantidad_baja']
                instancia_bien_vivero.save()
            elif i['id_item_baja_viveros'] != None:
                instancia_item_baja = ItemsBajasVivero.objects.filter(id_item_baja_viveros=i['id_item_baja_viveros']).first()
                instancia_bien = CatalogoBienes.objects.filter(id_bien=instancia_item_baja.id_bien.id_bien).first()
                instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=instancia_item_baja.id_bien,id_vivero=instancia_baja.id_vivero).first()
                instancia_bien_vivero.cantidad_bajas = instancia_bien_vivero.cantidad_bajas if instancia_bien_vivero.cantidad_bajas else 0
                aux_cantidad = i['cantidad_baja'] - instancia_item_baja.cantidad_baja
                instancia_bien_vivero.cantidad_bajas = instancia_bien_vivero.cantidad_bajas + aux_cantidad
                instancia_bien_vivero.save()
        
        # SE BOORRAN LOS ITEMS A ELIMINAR
        items_eliminar.delete()
        
        # SE ACTUALIZAN LOS ITEMS A ACTUALIZAR
        for i in items_actualizar:
            instancia_item_baja = ItemsBajasVivero.objects.filter(id_item_baja_viveros=i['id_item_baja_viveros']).first()
            previous_instancia_item = copy.copy(instancia_item_baja)
            serializer_crear_items = self.serializador_actualizar_items_bajas(instancia_item_baja, data=i, many=False)
            serializer_crear_items.is_valid(raise_exception=True)
            serializer_crear_items.save()
            valores_actualizados_detalles.append({'descripcion': {'nombre' : instancia_item_baja.id_bien.nombre},'previous':previous_instancia_item,'current':instancia_item_baja})

        # SE ACTUALIZA EL REGISTRO EN LA TABLA TRASLADOS
        instancia_baja.motivo = info_baja['motivo']
        instancia_baja.ruta_archivo_soporte = info_baja['ruta_archivo_soporte']
        instancia_baja.save()
        # SE ASIGNA EL ID TRASLADO A LOS ITEMS A TRASLADAR
        for i in items_nuevos:
            i['id_baja'] = instancia_baja.id_baja
        # SE CREA EL REGISTRO EN LA TABLA ITEM_TRASLADOS
        serializer_crear_items = self.serializador_items_bajas(data=items_nuevos, many=True)
        serializer_crear_items.is_valid(raise_exception=True)
        serializer_crear_items.save()
        
        # AUDITORIA MAESTRO DETALLE DE DESPACHO
        descripcion = {"numero_baja": str(instancia_baja.nro_baja_por_tipo), "tipo_baja": 'B', "fecha_baja": str(instancia_baja.fecha_baja)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 55,
            "cod_permiso": "CR",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles,
            "valores_actualizados_detalles": valores_actualizados_detalles,
            "valores_eliminados_detalles": valores_eliminados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)
                
        return Response({'succes' : True, 'detail' : 'Baja actualizada con éxito'}, status=status.HTTP_200_OK)
    
class AnularBajasVivero(generics.UpdateAPIView):
    serializer_class = BajasViveroPostSerializer
    queryset = BajasVivero.objects.all()
    permission_classes = [IsAuthenticated]
    serializador_items_bajas = ItemsBajasViveroPostSerializer
    
    def put(self, request, id_baja_anular):
        queryset = self.queryset
        datos_ingresados = request.data
        valores_eliminados_detalles = []
        
        baja_a_anular = queryset.filter(id_baja=id_baja_anular).first()
                
        if not baja_a_anular:
            raise ValidationError ('No se encontró ninguna baja de insumos, herramientas y semillas con el número que ingresó')
        if baja_a_anular.tipo_baja != 'B':
            raise ValidationError ('En este módulo solo se pueden anular bajas para insumos, herramientas y semillas.')
        if baja_a_anular.baja_anulado == True:
            raise ValidationError ('Esta baja ya fue anulada.')
        
        items_baja_a_anular = ItemsBajasVivero.objects.filter(id_baja=baja_a_anular.id_baja)
        if not items_baja_a_anular:
            raise ValidationError ('Esta baja no registra items.')
        
        # SE OBTIENE LA ÚLTIMA BAJA REGISTRADA Y SE CONTRASTA CON EL NRO DE BAJA INGRESADO
        ultimo_nro_baja = queryset.filter(tipo_baja='B', ).order_by('nro_baja_por_tipo').last()
        if ultimo_nro_baja.nro_baja_por_tipo != baja_a_anular.nro_baja_por_tipo:
            raise ValidationError ('Solo se puede anular la última baja registrada.')
             
        # SE RESTA LA CANTIDAD DE LOS ITEMS DE LAS BAJAS AL INVENTARIO DE VIVERO
        for i in items_baja_a_anular:
            instancia_inventario_vivero = InventarioViveros.objects.filter(id_bien=i.id_bien.id_bien, id_vivero=baja_a_anular.id_vivero).first()
            if not instancia_inventario_vivero:
                raise ValidationError ('El bien con número de posición ' + str(i.nro_posicion) +  'no tiene registro en el inventario del vivero.')
            instancia_inventario_vivero.cantidad_bajas = instancia_inventario_vivero.cantidad_bajas if instancia_inventario_vivero.cantidad_bajas else 0
            instancia_inventario_vivero.cantidad_bajas = instancia_inventario_vivero.cantidad_bajas - i.cantidad_baja
            instancia_inventario_vivero.save()
        
        # SE BORRAN LOS REGISTROS DE LA TABLA ITEMS_VIVERO
        valores_eliminados_detalles = [{'nombre' : i.id_bien.nombre} for i in items_baja_a_anular]
        items_baja_a_anular.delete()
        baja_a_anular.baja_anulado = True
        baja_a_anular.fecha_anulacion = datetime.now()
        baja_a_anular.id_persona_anula = Personas.objects.filter(id_persona=request.user.persona.id_persona).first()
        baja_a_anular.justificacion_anulacion = datos_ingresados['justificacion_anulacion']
        baja_a_anular.save()
        
        # AUDITORIA MAESTRO DETALLE DE DESPACHO
        descripcion = {"numero_baja": str(baja_a_anular.nro_baja_por_tipo), "tipo_baja": 'B', "fecha_baja": str(baja_a_anular.fecha_baja)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 55,
            "cod_permiso": "CR",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_eliminados_detalles": valores_eliminados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        return Response({'succes' : True, 'detail' : 'Baja anualada con éxito'}, status=status.HTTP_200_OK)
        
class GetVivero(generics.ListAPIView):
    serializer_class = ViveroBajasSerializer
    queryset = Vivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        viveros_habilitados = Vivero.objects.filter(activo=True, fecha_cierre_actual = None, id_persona_cierra = None, justificacion_cierre = None).exclude(fecha_ultima_apertura = None)
        serializer = self.serializer_class(viveros_habilitados, many=True)
        
        return Response({'succes':True, 'detail':'Ok', 'data':serializer.data}, status=status.HTTP_200_OK)

class GetBienesBajas(generics.ListAPIView):
    serializer_class = CatalogoBienesBajasSerializer
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, codigo_entrante, vivero_origen):
        # SE VALIDA LA EXISTENCIA DEL BIEN
        instancia_bien = CatalogoBienes.objects.filter(codigo_bien=codigo_entrante).first()
        if not instancia_bien:
            raise ValidationError ('No existe ningún bien asociado con el código ingresado.')
        
        # SE VALIDA QUE EL BIEN SEA INSUMO, HERRAMIENTA O SEMILLA
        if instancia_bien.es_semilla_vivero == False and instancia_bien.cod_tipo_elemento_vivero == 'MV':
            raise ValidationError ('El bien que intenta seleccionar no es del tipo herramienta, insumo o semilla.')
        
        # SE VALIDA LA EXISTENCIA DEL BIEN EN EL INVENTARIO
        instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=instancia_bien.id_bien,id_vivero=vivero_origen).first()
        if not instancia_bien_vivero:
            raise ValidationError ('El bien que intenta seleccionar no tiene registros en el inventario del vivero.')
        
        # SE VALIDA QUE HAYA SALDO DISPONIBLE PARA REALIZAR UNA BAJA
        saldo_disponible = UtilConservacion.get_cantidad_disponible_F(instancia_bien, instancia_bien_vivero)
        if saldo_disponible <= 0:
            raise ValidationError ('El bien ' + str(instancia_bien.nombre) + ', no cuenta con saldo disponible para realizar bajas.')
        
        serializer = self.serializer_class(instancia_bien, many=False)
        
        return Response({'succes':True, 'detail':'Ok', 'data':serializer.data}, status=status.HTTP_200_OK)
    
class BusquedaAvanzadaBienesBajas(generics.ListAPIView):
    serializer_class = CatalogoBienesSerializerBusquedaAvanzada
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, vivero_origen):
        filter = {}
        cod_tipo_elemento_vivero = request.query_params.get('cod_tipo_elemento_vivero')
        if not cod_tipo_elemento_vivero or cod_tipo_elemento_vivero == '':
            raise ValidationError ('Es obligatorio ingresar el tipo de bien.')
        
        for key, value in request.query_params.items():
            if key in ['cod_tipo_elemento_vivero', 'nombre', 'codigo_bien']:
                if key != 'cod_tipo_elemento_vivero':
                    if value != '':
                        filter[key + '__icontains'] = value
                else:
                    if value != '':
                        filter[key] = value
                    
        resultados_busqueda = CatalogoBienes.objects.filter(**filter)
        
        # SE LE AGRAGA EL SALDO DISPONIBLE AL RESULTADO DE BUSQUEDA
        for i in resultados_busqueda:
            instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=i.id_bien,id_vivero=int(vivero_origen)).first()
            if not instancia_bien_vivero:
                raise ValidationError ('El bien que intenta seleccionar no tiene registros en el inventario del vivero.')
            i.saldo_disponible = UtilConservacion.get_cantidad_disponible_F(i, instancia_bien_vivero) 
                
        serializer = self.serializer_class(resultados_busqueda, many=True)
        
        return Response({'succes':True, 'detail':'Ok', 'data':serializer.data}, status=status.HTTP_200_OK)

class GetBajasParaAnulacionPorNumeroBaja(generics.ListAPIView):
    serializer_class = GetBajaByNumeroSerializer
    queryset = BajasVivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, nro_baja):
        queryset = self.queryset.all()
        resultado_busqueda = queryset.filter(nro_baja_por_tipo=nro_baja).first()
        
        if not resultado_busqueda:
            raise ValidationError ('No se encontró ninguna baja de insumos, herramientas y semillas con el número que ingresó')
        if resultado_busqueda.tipo_baja != 'B':
            raise ValidationError ('En este módulo solo se pueden anular bajas para insumos, herramientas y semillas.')
        ultimo_nro_baja = queryset.filter(tipo_baja='B', ).order_by('nro_baja_por_tipo').last()
        # SE OBTIENE LA ÚLTIMA BAJA REGISTRADA Y SE CONTRASTA CON EL NRO DE BAJA INGRESADO
        if ultimo_nro_baja.nro_baja_por_tipo != resultado_busqueda.nro_baja_por_tipo:
            raise ValidationError ('Solo se puede anular la última baja registrada.')
        
        serializer = self.serializer_class(resultado_busqueda, many=False, context = {'request':request})
        
        return Response({'succes':True, 'detail':'Ok', 'data':serializer.data}, status=status.HTTP_200_OK)
    
class GetBajasPorFiltro(generics.ListAPIView):
    serializer_class = GetBajaByNumeroSerializer
    queryset = BajasVivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        nro_baja = request.query_params.get('nro_baja', '')
        print(nro_baja)
        resultado_busqueda = self.queryset.filter(nro_baja_por_tipo__icontains=nro_baja, tipo_baja='B').order_by('nro_baja_por_tipo')
        
        serializer = self.serializer_class(resultado_busqueda, many=True, context = {'request':request})
        
        return Response({'succes':True, 'detail':'Se encontraron las siguientes coincidencias', 'data':serializer.data}, status=status.HTTP_200_OK)
    
class GetItemsByBaja(generics.ListAPIView):
    serializer_class = ItemsBajasViveroGetSerializer
    queryset = ItemsBajasVivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_baja):
        resultado_busqueda = self.queryset.filter(id_baja=id_baja, id_baja__tipo_baja='B')
        
        serializer = self.serializer_class(resultado_busqueda, many=True)
        
        return Response({'succes':True, 'detail':'Se encontraron los siguientes items para la baja ingresada', 'data':serializer.data}, status=status.HTTP_200_OK)