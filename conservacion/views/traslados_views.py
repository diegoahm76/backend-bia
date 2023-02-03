from rest_framework.response import Response
from rest_framework import generics,status
from django.db.models import Q
from conservacion.serializers.traslados_serializers import TrasladosViverosSerializers, ItemsTrasladosViverosSerielizers, InventarioViverosSerielizers, CreateSiembraInventarioViveroSerializer
from conservacion.models.inventario_models import InventarioViveros
from conservacion.models.viveros_models import Vivero
from conservacion.models.traslados_models import TrasladosViveros, ItemsTrasladoViveros
from almacen.models.bienes_models import CatalogoBienes
from conservacion.models.siembras_models import CambiosDeEtapa
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
import json
from seguridad.utils import Util

class TrasladosCreate(generics.UpdateAPIView):
    serializer_class = TrasladosViverosSerializers
    queryset = TrasladosViveros.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_items_traslado = ItemsTrasladosViverosSerielizers
    
    def put(self, request):
        datos_ingresados = request.data
        user_logeado = request.user
        info_traslado = json.loads(datos_ingresados['info_traslado'])
        items_traslado = json.loads(datos_ingresados['items_traslado'])
        info_traslado['ruta_archivo_soporte'] = request.FILES.get('ruta_archivo_soporte')
        # SE OBTIENE EL ÚLTIMO NÚMERO DE TRASLADO DISPONIBLE
        traslados_existentes = TrasladosViveros.objects.all()
        if traslados_existentes:
            numero_traslados = [i.nro_traslado for i in traslados_existentes]
            info_traslado['nro_traslado'] = max(numero_traslados) + 1
        else:
            info_traslado['nro_traslado'] = 1
        # SE OBTIENE LA FECHA  DE TRASLADO
        info_traslado['fecha_traslado'] = datetime.now()
        # SE OBTIENE LA PERSONA QUIEN REGISTRADO
        info_traslado['id_persona_traslada'] = user_logeado.persona.id_persona
        # SE VALIDA QUE LOS VIVEROS INGRESADOS PARA EL TRASLADO EXISTAN
        instancia_vivero_origen = Vivero.objects.filter(id_vivero=info_traslado['id_vivero_origen']).first()
        instancia_vivero_destino = Vivero.objects.filter(id_vivero=info_traslado['id_vivero_destino']).first()
        if (not instancia_vivero_origen) or (not instancia_vivero_destino):
            return Response({'success':False,'detail':'Unos de los dos viveros de la operación de traslado no existe'}, status=status.HTTP_400_BAD_REQUEST)
        # SE VALIDA QUE LOS VIVEROS ESTEN ACTIVOS Y ESTÉN ABIERTOS
        if ((instancia_vivero_destino.activo != True) or (instancia_vivero_origen.activo != True) or 
            (instancia_vivero_destino.fecha_ultima_apertura == None) or (instancia_vivero_destino.fecha_cierre_actual != None) or 
            (instancia_vivero_origen.fecha_ultima_apertura == None) or (instancia_vivero_origen.fecha_cierre_actual != None)):
            return Response({'success':False,'detail':'Unos de los dos viveros está cerrado o no se encuentran activos'}, status=status.HTTP_400_BAD_REQUEST)
        # SE VALDIA QUE AL MENOS INGRESEN UN BIEN PARA EJECUTAR EL TRASLADO
        if items_traslado == []:
            return Response({'success':False,'detail':'Debe ingresar al menos un bien para ejecutar un traslado'}, status=status.HTTP_400_BAD_REQUEST)
        # SE VALIDA QUE EXISTE AL MENOS UNA CANTIDAD MAYOR A CERO
        aux_validacion_cantidades = [i['cantidad_a_trasladar'] for i in items_traslado if i['cantidad_a_trasladar']>0]
        if aux_validacion_cantidades == []:
            return Response({'success':False,'detail':'Las cantidades deben ser mayores a cero'}, status=status.HTTP_400_BAD_REQUEST)
        if len(set(aux_validacion_cantidades)) != len(items_traslado):
            return Response({'success':False,'detail':'Una de las cantidades es igual a cero, o ingresó un bien repetido'}, status=status.HTTP_400_BAD_REQUEST)
        # VALIDACIONES DE LOS ITEMS DEL TRASLADO
        aux_nro_posicion = []
        valores_creados_detalles = []
        for i in items_traslado:
            instancia_bien = CatalogoBienes.objects.filter(id_bien=i['id_bien_origen']).first()
            if not instancia_bien:
                return Response({'success':False,'detail':'El bien seleccionado no existe'}, status=status.HTTP_400_BAD_REQUEST)
            instancia_item = InventarioViveros.objects.filter(id_vivero=info_traslado['id_vivero_origen'],id_bien=i['id_bien_origen'],agno_lote=i['agno_lote_origen'],nro_lote=i['nro_lote_origen'],cod_etapa_lote=i['cod_etapa_lote_origen']).first()
            if not instancia_item:
                return Response({'success':False,'detail':'Error en el item nro: (' + str(i['nro_posicion']) + '). No se encuentra el item que desea trasladar'}, status=status.HTTP_400_BAD_REQUEST)
            # SE VALIDA QUE EL BIEN A TRASLADAR NO ESTÉ EN ETAPA DE GERMINACIÓN
            if i['cod_etapa_lote_origen'] == 'G':
                return Response({'success':False,'detail':'Error en el item nro: (' + str(i['nro_posicion']) + '). No se pueden trasladar bienes que estén en etapa de germinación'}, status=status.HTTP_400_BAD_REQUEST)
            # SE VALIDA LA CANTIDAD DISPONIBLE DEL BIEN A TRASLADAR
            instancia_item.cantidad_traslados_lote_produccion_distribucion = instancia_item.cantidad_traslados_lote_produccion_distribucion if instancia_item.cantidad_traslados_lote_produccion_distribucion else 0
            instancia_item.cantidad_salidas = instancia_item.cantidad_salidas if instancia_item.cantidad_salidas else 0
            instancia_item.cantidad_lote_cuarentena = instancia_item.cantidad_lote_cuarentena if instancia_item.cantidad_lote_cuarentena else 0
            instancia_item.cantidad_bajas = instancia_item.cantidad_bajas if instancia_item.cantidad_bajas else 0
            instancia_item.cantidad_consumos_internos = instancia_item.cantidad_consumos_internos if instancia_item.cantidad_consumos_internos else 0
            if instancia_bien.cod_tipo_elemento_vivero == 'MV'and instancia_bien.es_semilla_vivero == False:
                if instancia_item.cantidad_entrante == None:
                    return Response({'success':False,'detail':'En el item nro: (' + str(i['nro_posicion']) + '). El bien en el vivero no tiene catidad de entrada'}, status=status.HTTP_404_NOT_FOUND)
                if instancia_item.cod_etapa_lote == 'P':
                    saldo_disponible = instancia_item.cantidad_entrante - instancia_item.cantidad_bajas - instancia_item.cantidad_traslados_lote_produccion_distribucion - instancia_item.cantidad_salidas - instancia_item.cantidad_lote_cuarentena
                if instancia_item.cod_etapa_lote == 'D':
                    saldo_disponible = instancia_item.cantidad_entrante - instancia_item.cantidad_bajas - instancia_item.cantidad_salidas - instancia_item.cantidad_lote_cuarentena
            elif (instancia_bien.cod_tipo_elemento_vivero == 'MV'and instancia_bien.es_semilla_vivero == True) or instancia_bien.cod_tipo_elemento_vivero == 'IN':
                saldo_disponible = instancia_item.cantidad_entrante - instancia_item.cantidad_bajas - instancia_item.cantidad_consumos_internos - instancia_item.cantidad_salidas
                if i['altura_lote_destion_en_cms'] != None:
                    return Response({'success':False,'detail':'Error en el item nro: (' + str(i['nro_posicion']) + '). Si el bien no es una planta, altura del lote debería ingresar como nula'}, status=status.HTTP_404_NOT_FOUND)
            elif instancia_bien.cod_tipo_elemento_vivero == 'HE':
                if i['altura_lote_destion_en_cms'] != None:
                    return Response({'success':False,'detail':'Error en el item nro: (' + str(i['nro_posicion']) + '). Si el bien no es una planta, altura del lote debería ingresar como nula'}, status=status.HTTP_404_NOT_FOUND)
                saldo_disponible = instancia_item.cantidad_entrante - instancia_item.cantidad_bajas - instancia_item.cantidad_salidas
            if i['cantidad_a_trasladar'] > saldo_disponible:
                return Response({'success':False,'detail':'Error en el item nro: (' + str(i['nro_posicion']) + '). La cantidad que desea trasladar es superior al saldo disponible'}, status=status.HTTP_400_BAD_REQUEST)
            # SE VALIDA QUE LA ETAPA DE DESTINO SEA DIFERENTE DE GERMINACIÓN
            if i['cod_etapa_lote_destino_MV'] == 'G':
                return Response({'success':False,'detail':'Error en el item nro: (' + str(i['nro_posicion']) + '). La etapa de destino no puede ser germinación'}, status=status.HTTP_400_BAD_REQUEST)
            # SE ASIGNA EL AÑO DEL LOTE Y EL NÚMERO DEL LOTE
            i['agno_lote_destino_MV'] = info_traslado['fecha_traslado'].year
            aux_get_ultimo_nro_lote_by_agno = InventarioViveros.objects.filter(id_bien=i['id_bien_origen'],agno_lote=i['agno_lote_destino_MV']).order_by('nro_lote').last()
            if not aux_get_ultimo_nro_lote_by_agno:
                i['nro_lote_destino_MV'] = 1
            else:
                i['nro_lote_destino_MV'] = aux_get_ultimo_nro_lote_by_agno.nro_lote + 1 
            if i['nro_posicion'] in aux_nro_posicion:
                return Response({'success':False,'detail':'Error en el item nro: (' + str(i['nro_posicion']) + '). El número d eposición debe ser único'}, status=status.HTTP_400_BAD_REQUEST)
            aux_nro_posicion.append(i['nro_posicion'])
            valores_creados_detalles.append({'nombre' : instancia_bien.nombre})
        # SE CREA EL REGISTRO EN LA TABLA TRASLADOS
        serializer_crear = self.serializer_class(data=info_traslado, many=False)
        serializer_crear.is_valid(raise_exception=True)
        aux_ultimo = serializer_crear.save()
        # SE ASIGNA EL ID TRASLADO A LOS ITEMS A TRASLADAR
        for i in items_traslado:
            i['id_traslado'] = aux_ultimo.pk
        # SE CREA EL REGISTRO EN LA TABLA ITEM_TRASLADOS
        serializer_crear_items = self.serializer_items_traslado(data=items_traslado, many=True)
        serializer_crear_items.is_valid(raise_exception=True)
        serializer_crear_items.save()
        # AUDITORIA MAESTRO DETALLE DE DESPACHO
        descripcion = {"numero_traslado": str(info_traslado['nro_traslado']), "fecha_traslado": str(info_traslado['fecha_traslado'])}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 45,
            "cod_permiso": "CR",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        #SE GUARDAN LOS DATOS EN EL INVENTARIO VIVERO ORIGEN Y EN EL INVENTARIO DESTINO
        for i in items_traslado:
            instancia_bien = CatalogoBienes.objects.filter(id_bien=i['id_bien_origen']).first()
            # SE GUARDAN LOS DATOS EN EL INVENTARIO VIVERO ORIGEN
            if instancia_bien.cod_tipo_elemento_vivero == 'MV'and instancia_bien.es_semilla_vivero == False:
                instancia_item_origen = InventarioViveros.objects.filter(id_vivero=info_traslado['id_vivero_origen'],id_bien=i['id_bien_origen'],agno_lote=i['agno_lote_origen'],nro_lote=i['nro_lote_origen'],cod_etapa_lote=i['cod_etapa_lote_origen']).first()
            else:
                instancia_item_origen = InventarioViveros.objects.filter(id_vivero=info_traslado['id_vivero_origen'],id_bien=i['id_bien_origen']).first()
            instancia_item_origen.cantidad_salidas = instancia_item_origen.cantidad_salidas if instancia_item_origen.cantidad_salidas else 0
            instancia_item_origen.cantidad_salidas = instancia_item_origen.cantidad_salidas + i['cantidad_a_trasladar']
            instancia_item_origen.save()
            # SE GUARDAN LOS DATOS EN EL INVENTARIO VIVERO DESTINO
            if (instancia_bien.cod_tipo_elemento_vivero == 'MV'and instancia_bien.es_semilla_vivero == True) or instancia_bien.cod_tipo_elemento_vivero == 'HE' or instancia_bien.cod_tipo_elemento_vivero == 'IN':
                instancia_item_despacho = InventarioViveros.objects.filter(id_vivero=info_traslado['id_vivero_destino'],id_bien=i['id_bien_origen']).first()
                if instancia_item_despacho:
                    instancia_item_despacho.cantidad_entrante = instancia_item_despacho.cantidad_entrante if instancia_item_despacho.cantidad_entrante else 0
                    instancia_item_despacho.cantidad_entrante = instancia_item_despacho.cantidad_entrante + i['cantidad_a_trasladar']
                    instancia_item_despacho.save()
                else:
                    inventario_vivero_dict = {
                                            "id_vivero": info_traslado['id_vivero_destino'],
                                            "id_bien": i['id_bien_origen'],
                                            "agno_lote" : None,
                                            "nro_lote" : None,
                                            "cod_etapa_lote" : None,
                                            "es_produccion_propia_lote" : None,
                                            "cod_tipo_entrada_alm_lote" : None,
                                            "nro_entrada_alm_lote" : None,
                                            "fecha_ingreso_lote_etapa" : None,
                                            "ult_altura_lote" : None,
                                            "fecha_ult_altura_lote" : None,
                                            "cantidad_entrante" : i['cantidad_a_trasladar'],
                                            "id_mezcla" : None
                                            }
                    serializer_inventario = CreateSiembraInventarioViveroSerializer(data=inventario_vivero_dict, many=False)
                    serializer_inventario.is_valid(raise_exception=True)
                    serializer_inventario.save()
            elif instancia_bien.cod_tipo_elemento_vivero == 'MV'and instancia_bien.es_semilla_vivero == False:
                inventario_vivero_dict = {
                                        "id_vivero": info_traslado['id_vivero_destino'],
                                        "id_bien": i['id_bien_origen'],
                                        "agno_lote" : i['agno_lote_destino_MV'],
                                        "nro_lote" : i['nro_lote_destino_MV'],
                                        "cod_etapa_lote" : i['cod_etapa_lote_destino_MV'],
                                        "es_produccion_propia_lote" : instancia_item_origen.es_produccion_propia_lote,
                                        "cod_tipo_entrada_alm_lote" : instancia_item_origen.cod_tipo_entrada_alm_lote,
                                        "nro_entrada_alm_lote" : instancia_item_origen.nro_entrada_alm_lote,
                                        "fecha_ingreso_lote_etapa" : info_traslado['fecha_traslado'],
                                        "ult_altura_lote" : i['altura_lote_destion_en_cms'],
                                        "fecha_ult_altura_lote" : info_traslado['fecha_traslado'],
                                        "cantidad_entrante" : i['cantidad_a_trasladar'],
                                        "id_mezcla" : None
                                        }
                serializer_inventario = CreateSiembraInventarioViveroSerializer(data=inventario_vivero_dict, many=False)
                serializer_inventario.is_valid(raise_exception=True)
                serializer_inventario.save()
                # SE ACTUALIZA EL CAMPO ITEM YA USADO EN EL VIVERO DESTINO
                instancia_vivero_destino.item_ya_usado = True if instancia_vivero_destino.item_ya_usado == False else instancia_vivero_destino.item_ya_usado
                instancia_vivero_destino.save()
            instancia_item_origen.cantidad_salidas = instancia_item_origen.cantidad_salidas if instancia_item_origen.cantidad_salidas else 0
            instancia_item_origen.cantidad_salidas = instancia_item_origen.cantidad_salidas + i['cantidad_a_trasladar']
            
        return Response({'success':True,'detail':'Traslado creado con éxito','data':serializer_crear_items.data}, status=status.HTTP_200_OK)

class GetItemsInventarioVivero(generics.ListAPIView):
    serializer_class = InventarioViverosSerielizers
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, codigo_bien_entrante, id_vivero_entrante):
        instancia_vivero = Vivero.objects.filter(id_vivero=id_vivero_entrante).first()
        if not instancia_vivero:
            return Response({'success':False,'detail':'El vivero ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        instancia_salida = InventarioViveros.objects.filter(Q(id_bien__codigo_bien=codigo_bien_entrante) & Q(id_vivero=id_vivero_entrante)).exclude(cod_etapa_lote='G')
        if not instancia_salida:
                return Response({'success':False,'detail':'No se encontraron coincidencias'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(instancia_salida, many=True)
        if len(serializer.data) > 1:
            modal = True
        else:
            if serializer.data != []:
                if serializer.data[0]['cod_tipo_elemento_vivero'] == 'MV' and serializer.data[0]['es_semilla_vivero'] == False:
                    modal = True
                else:
                    modal = False
        return Response({'success':True,'detail':'OK', 'modal':modal, 'data':serializer.data}, status=status.HTTP_200_OK)

class GetTrasladosByIdTraslados(generics.ListAPIView):
    serializer_class = TrasladosViverosSerializers
    queryset = TrasladosViveros
    serializer_item_class = ItemsTrasladosViverosSerielizers
    permission_classes = [IsAuthenticated]
    
    def get(self, request, nro_traslado_entrante):
        instancia_traslado = TrasladosViveros.objects.filter(nro_traslado=nro_traslado_entrante).first()
        instancia_items_traslado = ItemsTrasladoViveros.objects.filter(id_traslado=instancia_traslado)
        salida = {}
        if not instancia_traslado:
            return Response({'success':False, 'detail':'La búsqueda no arrojó resultados'}, status=status.HTTP_400_BAD_REQUEST)
        if not instancia_items_traslado:
            return Response({'success':False, 'detail':'Este traslado no tiene items registrados'}, status=status.HTTP_400_BAD_REQUEST)
        serializador = self.serializer_class(instancia_traslado, many=False)
        serializador_items = self.serializer_item_class(instancia_items_traslado, many=True)
        salida['info_traslado'] = serializador.data
        salida['items_traslado'] = serializador_items.data
        return Response({'success':True, 'detail':'Ok', 'data':salida}, status=status.HTTP_200_OK)

class GetAvanzadoTraslados(generics.ListAPIView):
    serializer_class = TrasladosViverosSerializers
    queryset = TrasladosViveros
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        filter = {}
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        vivero_origen = request.query_params.get('id_vivero_origen')
        vivero_destino = request.query_params.get('id_vivero_destino')
        if fecha_desde != '':
            fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d')
        if fecha_hasta != '':    
            fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d')
        
        if not fecha_desde or fecha_desde == '':
            fecha_desde = datetime.today() - timedelta(30)
        if not fecha_hasta or fecha_hasta == '':
            fecha_hasta = datetime.today() + timedelta(1)
        else:
            fecha_hasta = fecha_hasta + timedelta(1)
        primer_filtro = TrasladosViveros.objects.filter(fecha_traslado__range=[fecha_desde,fecha_hasta])
        if not vivero_origen:
            if not vivero_destino:
                return Response({'success':False, 'detail':'Debe ingresar vivero origen o vivero destino, no puede hacer la busqueda sin enviar estos dos datos'}, status=status.HTTP_400_BAD_REQUEST)
        for key, value in request.query_params.items():
            if key in ['id_vivero_origen', 'id_vivero_destino']:
                if value != '':
                    filter[key]=value
        segundo_filtro = primer_filtro.filter(**filter)
        serializer = self.serializer_class(segundo_filtro, many=True)
        return Response({'success':True, 'detail':'Ok', 'data':serializer.data}, status=status.HTTP_200_OK)

class GetItemsTrasladoByIdTraslado(generics.ListAPIView):
    serializer_class = ItemsTrasladosViverosSerielizers
    queryset = ItemsTrasladoViveros
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_traslado_entrante):
        instancia_items_traslado = ItemsTrasladoViveros.objects.filter(id_traslado=id_traslado_entrante)
        if not instancia_items_traslado:
            return Response({'success':False, 'detail':'El traslado no existe o no no tiene items registrados'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(instancia_items_traslado, many=True)
        return Response({'success':True, 'detail':'Ok', 'data':serializer.data}, status=status.HTTP_200_OK)

class TrasladosActualizar(generics.UpdateAPIView):
    serializer_class = TrasladosViverosSerializers
    queryset = TrasladosViveros.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_items_traslado = ItemsTrasladosViverosSerielizers
    
    def put(self, request):
        datos_ingresados = request.data
        user_logeado = request.user
        info_traslado = json.loads(datos_ingresados['info_traslado'])
        items_traslado = json.loads(datos_ingresados['items_traslado'])
        
        instancia_traslado = TrasladosViveros.objects.filter(id_traslado=info_traslado['id_traslado']).first()
        if not instancia_traslado:
            return Response({'success':False, 'detail':'El traslado ingresado no existe.'}, status=status.HTTP_400_BAD_REQUEST)
        aux_nro_posicion = []
        # VALIDACIONES DE LOS ITEMS
        for i in items_traslado:
            aux_validaciones_items = ItemsTrasladoViveros.objects.filter(id_traslado=info_traslado['id_traslado'],id_item_traslado_viveros=i['id_item_traslado_viveros']).first()
            if not aux_validaciones_items:
                return Response({'success':False,'detail':'Error en el item nro: (' + str(i['nro_posicion']) + '). No se encuentra el item que desea actualizar.'}, status=status.HTTP_400_BAD_REQUEST)
            aux_bien = CatalogoBienes.objects.filter(id_bien=aux_validaciones_items.id_bien_origen.id_bien).first()
            if not aux_bien:
                return Response({'success':False,'detail':'Error en el item nro: (' + str(i['nro_posicion']) + '). No existe el bien.'}, status=status.HTTP_400_BAD_REQUEST)
            altura_ingresada_item = i.get('altura_lote_destion_en_cms')
            if altura_ingresada_item != None and ((aux_bien.cod_tipo_elemento_vivero != 'MV' and aux_bien.es_semilla_vivero != False) or (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero != False)):
                return Response({'success':False,'detail':'Error en el item nro: (' + str(i['nro_posicion']) + '). Una bien diferente a una planta no debería tener altura.'}, status=status.HTTP_400_BAD_REQUEST)
            if i['nro_posicion'] in aux_nro_posicion:
                return Response({'success':False,'detail':'Error en el item nro: (' + str(i['nro_posicion']) + '). El número d eposición debe ser único'}, status=status.HTTP_400_BAD_REQUEST)
            aux_nro_posicion.append(i['nro_posicion'])
        # SE GUARDAN LAS MODIFICACIONES EN LA TABLA TRASLADOS
        instancia_traslado.observaciones = info_traslado['observaciones']
        for i in items_traslado:
            aux_validaciones_items = ItemsTrasladoViveros.objects.filter(id_item_traslado_viveros=i['id_item_traslado_viveros']).first()
            aux_bien = CatalogoBienes.objects.filter(id_bien=aux_validaciones_items.id_bien_origen.id_bien).first()            
            # SE INSTANCIAN LOS VIVEROS
            if (aux_bien.cod_tipo_elemento_vivero == 'IN' or aux_bien.cod_tipo_elemento_vivero == 'HE' or (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == True)):
                instancia_inventario_vivero_origen = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_origen,id_bien=aux_bien.id_bien).first()
                instancia_inventario_vivero_destino = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_destino,id_bien=aux_bien.id_bien).first()
            if (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == False):
                instancia_inventario_vivero_origen = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_origen,id_bien=aux_bien.id_bien,agno_lote=aux_validaciones_items.agno_lote_origen,nro_lote=aux_validaciones_items.nro_lote_origen,cod_etapa_lote=aux_validaciones_items.cod_etapa_lote_origen).first()
                instancia_inventario_vivero_destino = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_destino,id_bien=aux_bien.id_bien,agno_lote=aux_validaciones_items.agno_lote_destino_MV,nro_lote=aux_validaciones_items.nro_lote_destino_MV,cod_etapa_lote=aux_validaciones_items.cod_etapa_lote_destino_MV).first()
            print(instancia_traslado.id_vivero_destino)
            print(aux_bien.id_bien)
            print(instancia_inventario_vivero_origen)
            print(instancia_inventario_vivero_destino)
            # SE PONE EL CERO EN LAS VARIABLES QUE GUARDAN CANTIDAD SI SON NONE DEL VIVERO ORIGEN
            instancia_inventario_vivero_origen.cantidad_traslados_lote_produccion_distribucion = instancia_inventario_vivero_origen.cantidad_traslados_lote_produccion_distribucion if instancia_inventario_vivero_origen.cantidad_traslados_lote_produccion_distribucion else 0
            instancia_inventario_vivero_origen.cantidad_salidas = instancia_inventario_vivero_origen.cantidad_salidas if instancia_inventario_vivero_origen.cantidad_salidas else 0
            instancia_inventario_vivero_origen.cantidad_lote_cuarentena = instancia_inventario_vivero_origen.cantidad_lote_cuarentena if instancia_inventario_vivero_origen.cantidad_lote_cuarentena else 0
            instancia_inventario_vivero_origen.cantidad_bajas = instancia_inventario_vivero_origen.cantidad_bajas if instancia_inventario_vivero_origen.cantidad_bajas else 0
            instancia_inventario_vivero_origen.cantidad_consumos_internos = instancia_inventario_vivero_origen.cantidad_consumos_internos if instancia_inventario_vivero_origen.cantidad_consumos_internos else 0
            # SE PONE EL CERO EN LAS VARIABLES QUE GUARDAN CANTIDAD SI SON NONE DEL VIVERO DESPACHO
            instancia_inventario_vivero_destino.cantidad_traslados_lote_produccion_distribucion = instancia_inventario_vivero_destino.cantidad_traslados_lote_produccion_distribucion if instancia_inventario_vivero_destino.cantidad_traslados_lote_produccion_distribucion else 0
            instancia_inventario_vivero_destino.cantidad_salidas = instancia_inventario_vivero_destino.cantidad_salidas if instancia_inventario_vivero_destino.cantidad_salidas else 0
            instancia_inventario_vivero_destino.cantidad_lote_cuarentena = instancia_inventario_vivero_destino.cantidad_lote_cuarentena if instancia_inventario_vivero_destino.cantidad_lote_cuarentena else 0
            instancia_inventario_vivero_destino.cantidad_bajas = instancia_inventario_vivero_destino.cantidad_bajas if instancia_inventario_vivero_destino.cantidad_bajas else 0
            instancia_inventario_vivero_destino.cantidad_consumos_internos = instancia_inventario_vivero_destino.cantidad_consumos_internos if instancia_inventario_vivero_destino.cantidad_consumos_internos else 0
            # SE ACTUALIZA LA ALTURA DE LAS PLANTAS
            aux_validaciones_items.altura_lote_destion_en_cms = i['altura_lote_destion_en_cms']
            if (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == False):
                fecha_actual = datetime.now()
                if fecha_actual.day != instancia_traslado.fecha_traslado.day:
                    instancia_inventario_vivero_destino.ult_altura_lote = i['altura_lote_destion_en_cms']
                    instancia_inventario_vivero_destino.fecha_ult_altura_lote = fecha_actual
                else:
                    instancia_inventario_vivero_origen.ult_altura_lote = i['altura_lote_destion_en_cms']
                    instancia_inventario_vivero_destino.ult_altura_lote = i['altura_lote_destion_en_cms']
                    instancia_inventario_vivero_origen.fecha_ult_altura_lote = fecha_actual
                    instancia_inventario_vivero_destino.fecha_ult_altura_lote = fecha_actual
            # SE VALDIA QUE LA CANTIDAD NO SE ACTUALICE MÁS DE UN DÍA DESPUÉS DEL TRASLADO
            if aux_validaciones_items.cantidad_a_trasladar != i['cantidad_a_trasladar']:
                fecha_actual = datetime.now()
                aux_fecha = int((fecha_actual-instancia_traslado.fecha_traslado).days)
                print((fecha_actual-instancia_traslado.fecha_traslado).days)
                if aux_fecha > int(1):
                    return Response({'success':False,'detail':'No es posible actualizar las cantidades de un traslado mas de un día después de ejecutarlo.'}, status=status.HTTP_400_BAD_REQUEST)
            # EN CASO DE AUMENTAR LA CANTIDAD TRASLADADA
            if aux_validaciones_items.cantidad_a_trasladar < i['cantidad_a_trasladar']:
                print("++++++++++++++++++++ENTROOOOOOOOOOOOOOO")
                if (aux_bien.cod_tipo_elemento_vivero == 'IN' or aux_bien.cod_tipo_elemento_vivero == 'HE' or (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == True)):
                    if (aux_bien.cod_tipo_elemento_vivero == 'MV'and aux_bien.es_semilla_vivero == True) or aux_bien.cod_tipo_elemento_vivero == 'IN':
                        saldo_disponible = instancia_inventario_vivero_origen.cantidad_entrante - instancia_inventario_vivero_origen.cantidad_bajas - instancia_inventario_vivero_origen.cantidad_consumos_internos - instancia_inventario_vivero_origen.cantidad_salidas
                    elif aux_bien.cod_tipo_elemento_vivero == 'HE':
                        saldo_disponible = instancia_inventario_vivero_origen.cantidad_entrante - instancia_inventario_vivero_origen.cantidad_bajas - instancia_inventario_vivero_origen.cantidad_salidas
                elif (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == False):
                    if instancia_inventario_vivero_origen.cantidad_entrante == None:
                        return Response({'success':False,'detail':'En el item nro: (' + str(i['nro_posicion']) + '). El bien en el vivero no tiene catidad de entrada'}, status=status.HTTP_404_NOT_FOUND)
                    if instancia_inventario_vivero_origen.cod_etapa_lote == 'P':
                        saldo_disponible = instancia_inventario_vivero_origen.cantidad_entrante - instancia_inventario_vivero_origen.cantidad_bajas - instancia_inventario_vivero_origen.cantidad_traslados_lote_produccion_distribucion - instancia_inventario_vivero_origen.cantidad_salidas - instancia_inventario_vivero_origen.cantidad_lote_cuarentena
                    if instancia_inventario_vivero_origen.cod_etapa_lote == 'D':
                        saldo_disponible = instancia_inventario_vivero_origen.cantidad_entrante - instancia_inventario_vivero_origen.cantidad_bajas - instancia_inventario_vivero_origen.cantidad_salidas - instancia_inventario_vivero_origen.cantidad_lote_cuarentena
                if i['cantidad_a_trasladar'] > saldo_disponible:
                    return Response({'success':False,'detail':'Error en el item nro: (' + str(i['nro_posicion']) + '). La cantidad que desea actualizar es superior al saldo disponible'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    instancia_inventario_vivero_origen.cantidad_salidas = instancia_inventario_vivero_origen.cantidad_salidas + (i['cantidad_a_trasladar'] - aux_validaciones_items.cantidad_a_trasladar)
                    instancia_inventario_vivero_destino.cantidad_entrante = instancia_inventario_vivero_destino.cantidad_entrante + (i['cantidad_a_trasladar'] - aux_validaciones_items.cantidad_a_trasladar)
                    aux_validaciones_items.cantidad_a_trasladar = i['cantidad_a_trasladar']
            # EN CASO DE DISMINUIR LA CANTIDAD TRASLADADA          
            elif aux_validaciones_items.cantidad_a_trasladar > i['cantidad_a_trasladar']:
                print("---------------------ENTROOOOOOOOOOOOOOO")
                if i['cantidad_a_trasladar'] <= 0:
                    return Response({'success':False,'detail':'Error en el item nro: (' + str(i['nro_posicion']) + '). La cantidad debe ser mayor a cero'}, status=status.HTTP_400_BAD_REQUEST)
                instancia_inventario_vivero_destino.cantidad_entrante = instancia_inventario_vivero_destino.cantidad_entrante - (aux_validaciones_items.cantidad_a_trasladar - i['cantidad_a_trasladar'])
                if (aux_bien.cod_tipo_elemento_vivero == 'IN' or aux_bien.cod_tipo_elemento_vivero == 'HE' or (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == True)):
                    if (aux_bien.cod_tipo_elemento_vivero == 'MV'and aux_bien.es_semilla_vivero == True) or aux_bien.cod_tipo_elemento_vivero == 'IN':
                        saldo_disponible = instancia_inventario_vivero_destino.cantidad_entrante - instancia_inventario_vivero_destino.cantidad_bajas - instancia_inventario_vivero_destino.cantidad_consumos_internos - instancia_inventario_vivero_destino.cantidad_salidas
                    elif aux_bien.cod_tipo_elemento_vivero == 'HE':
                        saldo_disponible = instancia_inventario_vivero_destino.cantidad_entrante - instancia_inventario_vivero_destino.cantidad_bajas - instancia_inventario_vivero_destino.cantidad_salidas
                elif (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == False):
                    if instancia_inventario_vivero_origen.cantidad_entrante == None:
                        return Response({'success':False,'detail':'En el item nro: (' + str(i['nro_posicion']) + '). El bien en el vivero no tiene catidad de entrada'}, status=status.HTTP_404_NOT_FOUND)
                    if instancia_inventario_vivero_destino.cod_etapa_lote == 'P':
                        saldo_disponible = instancia_inventario_vivero_destino.cantidad_entrante - instancia_inventario_vivero_destino.cantidad_bajas - instancia_inventario_vivero_destino.cantidad_traslados_lote_produccion_distribucion - instancia_inventario_vivero_destino.cantidad_salidas - instancia_inventario_vivero_destino.cantidad_lote_cuarentena
                    if instancia_inventario_vivero_destino.cod_etapa_lote == 'D':
                        saldo_disponible = instancia_inventario_vivero_destino.cantidad_entrante - instancia_inventario_vivero_destino.cantidad_bajas - instancia_inventario_vivero_destino.cantidad_salidas - instancia_inventario_vivero_destino.cantidad_lote_cuarentena
                if saldo_disponible <= 0:
                    return Response({'success':False,'detail':'Error en el item nro: (' + str(i['nro_posicion']) + '). No es posible actualizar la cantidad debido a que si se ejectua la operación quedaría un saldo negativo en la actualidad.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    instancia_inventario_vivero_origen.cantidad_salidas = instancia_inventario_vivero_origen.cantidad_salidas - (aux_validaciones_items.cantidad_a_trasladar - (i['cantidad_a_trasladar']))
                    instancia_inventario_vivero_destino.cantidad_entrante = instancia_inventario_vivero_destino.cantidad_entrante - (aux_validaciones_items.cantidad_a_trasladar - (i['cantidad_a_trasladar']))
                    aux_validaciones_items.cantidad_a_trasladar = i['cantidad_a_trasladar']
            
        return Response({'success':True, 'detail':'Ok', 'data':'daticos'}, status=status.HTTP_200_OK)