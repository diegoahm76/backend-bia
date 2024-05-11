from rest_framework.response import Response
from rest_framework import generics,status
from django.db.models import Q
from conservacion.serializers.traslados_serializers import TrasladosGetViverosSerializers, TrasladosViverosSerializers, ItemsTrasladosViverosSerielizers, InventarioViverosSerielizers, CreateSiembraInventarioViveroSerializer
from conservacion.models.inventario_models import InventarioViveros
from conservacion.models.viveros_models import Vivero
from conservacion.models.traslados_models import TrasladosViveros, ItemsTrasladoViveros
from almacen.models.bienes_models import CatalogoBienes
from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.utils import UtilsGestor
from seguridad.permissions.permissions_conservacion import PermisoActualizarTrasladosEntreViveros, PermisoAnularTrasladosEntreViveros, PermisoBorrarTrasladosEntreViveros, PermisoCrearTrasladosEntreViveros
from transversal.models.personas_models import Personas
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
import json
from seguridad.utils import Util
import copy

class TrasladosCreate(generics.UpdateAPIView):
    serializer_class = TrasladosViverosSerializers
    queryset = TrasladosViveros.objects.all()
    permission_classes = [IsAuthenticated, PermisoCrearTrasladosEntreViveros]
    serializer_items_traslado = ItemsTrasladosViverosSerielizers
    
    def put(self, request):
        datos_ingresados = request.data
        user_logeado = request.user
        info_traslado = json.loads(datos_ingresados['info_traslado'])
        items_traslado = json.loads(datos_ingresados['items_traslado'])
        archivo_soporte = request.FILES.get('ruta_archivo_soporte')
        
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
            raise ValidationError('Unos de los dos viveros de la operación de traslado no existe')
        
        # SE VALIDA QUE LOS VIVEROS ESTEN ACTIVOS Y ESTÉN ABIERTOS
        if ((instancia_vivero_destino.activo != True) or (instancia_vivero_origen.activo != True) or 
            (instancia_vivero_destino.fecha_ultima_apertura == None) or (instancia_vivero_destino.fecha_cierre_actual != None) or 
            (instancia_vivero_origen.fecha_ultima_apertura == None) or (instancia_vivero_origen.fecha_cierre_actual != None)):
            raise ValidationError('Unos de los dos viveros está cerrado o no se encuentran activos')
        
        # SE VALIDA QUE AL MENOS INGRESEN UN BIEN PARA EJECUTAR EL TRASLADO
        if items_traslado == []:
            raise ValidationError('Debe ingresar al menos un bien para ejecutar un traslado')
        
        # SE VALIDA QUE EXISTE AL MENOS UNA CANTIDAD MAYOR A CERO
        aux_validacion_cantidades = [i['cantidad_a_trasladar'] for i in items_traslado if i['cantidad_a_trasladar']>0]
        if aux_validacion_cantidades == []:
            raise ValidationError('Las cantidades deben ser mayores a cero')
        if len(aux_validacion_cantidades) != len(items_traslado):
            raise ValidationError('Una de las cantidades es igual a cero, o ingresó un bien repetido')
        
        # VALIDACIONES DE LOS ITEMS DEL TRASLADO
        aux_nro_posicion = []
        aux_valores_repetidos = []
        valores_creados_detalles = []
        for i in items_traslado:
            aux_local = [i['id_bien_origen'], i['agno_lote_origen'], i['nro_lote_origen']]
            instancia_bien = CatalogoBienes.objects.filter(id_bien=i['id_bien_origen']).first()
            if not instancia_bien:
                raise ValidationError('En el número de posición: ' + str(i['nro_posicion']) + ', el bien seleccionado no existe')
            
            # SE VALIDA QUE EL BIEN A TRASLADAR NO ESTÉ EN ETAPA DE GERMINACIÓN
            if i['cod_etapa_lote_origen'] == 'G':
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ', no se pueden trasladar porque está en etapa de germinación.')
            
            if aux_local in aux_valores_repetidos:
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ', ya existe en este traslado.')
            instancia_item = InventarioViveros.objects.filter(id_vivero=info_traslado['id_vivero_origen'],id_bien=i['id_bien_origen'],agno_lote=i['agno_lote_origen'],nro_lote=i['nro_lote_origen'],cod_etapa_lote=i['cod_etapa_lote_origen']).first()
            if not instancia_item:
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ', no se encuentra registrado en el inventario del vivero.')
            
            # SE VALIDA LA CANTIDAD DISPONIBLE DEL BIEN A TRASLADAR
            instancia_item.cantidad_traslados_lote_produccion_distribucion = instancia_item.cantidad_traslados_lote_produccion_distribucion if instancia_item.cantidad_traslados_lote_produccion_distribucion else 0
            instancia_item.cantidad_salidas = instancia_item.cantidad_salidas if instancia_item.cantidad_salidas else 0
            instancia_item.cantidad_lote_cuarentena = instancia_item.cantidad_lote_cuarentena if instancia_item.cantidad_lote_cuarentena else 0
            instancia_item.cantidad_bajas = instancia_item.cantidad_bajas if instancia_item.cantidad_bajas else 0
            instancia_item.cantidad_consumos_internos = instancia_item.cantidad_consumos_internos if instancia_item.cantidad_consumos_internos else 0
            if instancia_bien.cod_tipo_elemento_vivero == 'MV'and instancia_bien.es_semilla_vivero == False:
                if instancia_item.cantidad_entrante == None:
                    raise NotFound('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ', no tiene catidad de entrada registrada en el inventario del vivero origen.')
                if instancia_item.cod_etapa_lote == 'P':
                    saldo_disponible = instancia_item.cantidad_entrante - instancia_item.cantidad_bajas - instancia_item.cantidad_traslados_lote_produccion_distribucion - instancia_item.cantidad_salidas - instancia_item.cantidad_lote_cuarentena
                if instancia_item.cod_etapa_lote == 'D':
                    saldo_disponible = instancia_item.cantidad_entrante - instancia_item.cantidad_bajas - instancia_item.cantidad_salidas - instancia_item.cantidad_lote_cuarentena
            elif (instancia_bien.cod_tipo_elemento_vivero == 'MV'and instancia_bien.es_semilla_vivero == True) or instancia_bien.cod_tipo_elemento_vivero == 'IN':
                saldo_disponible = instancia_item.cantidad_entrante - instancia_item.cantidad_bajas - instancia_item.cantidad_consumos_internos - instancia_item.cantidad_salidas
                if i['altura_lote_destion_en_cms'] != None:
                    raise NotFound('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' no es una planta, por ende la altura del lote debería ser nula')
            elif instancia_bien.cod_tipo_elemento_vivero == 'HE':
                if i['altura_lote_destion_en_cms'] != None:
                    raise NotFound('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' no es una planta, por ende la altura del lote debería ser nula')
                saldo_disponible = instancia_item.cantidad_entrante - instancia_item.cantidad_bajas - instancia_item.cantidad_salidas
            if i['cantidad_a_trasladar'] > saldo_disponible:
                raise ValidationError('En el bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ', la cantidad que desea trasladar es superior al saldo disponible.')
            
            # SE VALIDA QUE LA ETAPA DE DESTINO SEA DIFERENTE DE GERMINACIÓN
            if i['cod_etapa_lote_destino_MV'] == 'G':
                raise ValidationError('En el bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ', la etapa de destino no puede ser germinación')
            
            # SE ASIGNA EL AÑO DEL LOTE Y EL NÚMERO DEL LOTE
            i['agno_lote_destino_MV'] = info_traslado['fecha_traslado'].year
            aux_get_ultimo_nro_lote_by_agno = InventarioViveros.objects.filter(id_bien=i['id_bien_origen'],agno_lote=i['agno_lote_destino_MV']).order_by('nro_lote').last()
            if instancia_bien.cod_tipo_elemento_vivero == 'MV'and instancia_bien.es_semilla_vivero == False:
                if not aux_get_ultimo_nro_lote_by_agno:
                    i['nro_lote_destino_MV'] = 1
                else:
                    i['nro_lote_destino_MV'] = aux_get_ultimo_nro_lote_by_agno.nro_lote + 1 
            if i['nro_posicion'] in aux_nro_posicion:
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' tiene un número de posición que ya existe.')
            aux_nro_posicion.append(i['nro_posicion'])
            valores_creados_detalles.append({'nombre' : instancia_bien.nombre})
            aux_valores_repetidos.append([i['id_bien_origen'], i['agno_lote_origen'], i['nro_lote_origen']])
            
        # CREAR ARCHIVO EN T238
        if archivo_soporte:
            archivo_creado = UtilsGestor.create_archivo_digital(archivo_soporte, "TrasladosViveros")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            info_traslado['ruta_archivo_soporte'] = archivo_creado_instance.id_archivo_digital

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
            "id_modulo" : 52,
            "cod_permiso": "CR",
            "subsistema": 'CONS',
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
            raise NotFound('El vivero ingresado no existe')
        instancia_salida = InventarioViveros.objects.filter(Q(id_bien__codigo_bien=codigo_bien_entrante) & Q(id_vivero=id_vivero_entrante)).exclude(cod_etapa_lote='G')
        if not instancia_salida:
                raise NotFound('No se encontraron coincidencias')
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

class FilterInventarioVivero(generics.ListAPIView):
    serializer_class = InventarioViverosSerielizers
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_vivero_entrante):
        filter={}
        for key,value in request.query_params.items():
            if key in ['nombre','codigo_bien','cod_tipo_elemento_vivero','es_semilla_vivero']:
                if key != 'cod_tipo_elemento_vivero':
                    if value != '':
                        if key == 'es_semilla_vivero':
                            value = True if value == 'true' else False
                            filter['id_bien__'+key]=value
                        else:
                            filter['id_bien__'+key+'__icontains']=value
                else:
                    if value != '':
                        filter['id_bien__'+key]=value
                    
        instancia_vivero = Vivero.objects.filter(id_vivero=id_vivero_entrante).first()
        if not instancia_vivero:
            raise NotFound('El vivero ingresado no existe')
        instancia_salida = InventarioViveros.objects.filter(**filter).filter(id_vivero=id_vivero_entrante).exclude(cod_etapa_lote='G')
        if not instancia_salida:
            return Response({'success':True,'detail':'Se encontró lo siguiente', 'data':[]}, status=status.HTTP_200_OK)
        serializer = self.serializer_class(instancia_salida, many=True)
        
        return Response({'success':True,'detail':'Se encontró lo siguiente', 'data':serializer.data}, status=status.HTTP_200_OK)

class GetTrasladosByIdTraslados(generics.ListAPIView):
    serializer_class = TrasladosGetViverosSerializers
    queryset = TrasladosViveros
    serializer_item_class = ItemsTrasladosViverosSerielizers
    permission_classes = [IsAuthenticated]
    
    def get(self, request, nro_traslado_entrante):
        instancia_traslado = TrasladosViveros.objects.filter(nro_traslado=nro_traslado_entrante).first()
        instancia_items_traslado = ItemsTrasladoViveros.objects.filter(id_traslado=instancia_traslado)
        salida = {}
        if not instancia_traslado:
            raise ValidationError('La búsqueda no arrojó resultados')
        if not instancia_items_traslado:
            raise ValidationError('Este traslado no tiene items registrados')
        serializador = self.serializer_class(instancia_traslado, many=False)
        serializador_items = self.serializer_item_class(instancia_items_traslado, many=True,  context = {'request':request})
        salida['info_traslado'] = serializador.data
        salida['items_traslado'] = serializador_items.data
        return Response({'success':True, 'detail':'Ok', 'data':salida}, status=status.HTTP_200_OK)

class GetAvanzadoTraslados(generics.ListAPIView):
    serializer_class = TrasladosGetViverosSerializers
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
                raise ValidationError('Debe ingresar vivero origen o vivero destino, no puede hacer la busqueda sin enviar estos dos datos')
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
            raise ValidationError('El traslado no existe o no no tiene items registrados')
        serializer = self.serializer_class(instancia_items_traslado, many=True , context = {'request':request})
        return Response({'success':True, 'detail':'Ok', 'data':serializer.data}, status=status.HTTP_200_OK)

class TrasladosActualizar(generics.UpdateAPIView):
    serializer_class = TrasladosViverosSerializers
    queryset = TrasladosViveros.objects.all()
    permission_classes = [IsAuthenticated, (PermisoActualizarTrasladosEntreViveros|PermisoBorrarTrasladosEntreViveros)]
    serializer_items_traslado = ItemsTrasladosViverosSerielizers
    
    def put(self, request):
        datos_ingresados = request.data
        aux_valores_repetidos = []
        info_traslado = json.loads(datos_ingresados['info_traslado'])
        items_traslado = json.loads(datos_ingresados['items_traslado'])
        archivo_soporte = request.FILES.get('ruta_archivo_soporte')
        instancia_traslado = TrasladosViveros.objects.filter(id_traslado=info_traslado['id_traslado']).first()
        instancia_vivero_origen = Vivero.objects.filter(id_vivero=instancia_traslado.id_vivero_origen.id_vivero).first()
        instancia_vivero_destino = Vivero.objects.filter(id_vivero=instancia_traslado.id_vivero_destino.id_vivero).first()
        if (not instancia_vivero_origen) or (not instancia_vivero_destino):
            raise ValidationError('Unos de los dos viveros de la operación de traslado no existe')
        
        # SE VALIDA QUE LOS VIVEROS ESTEN ACTIVOS Y ESTÉN ABIERTOS
        if ((instancia_vivero_destino.activo != True) or (instancia_vivero_origen.activo != True) or 
            (instancia_vivero_destino.fecha_ultima_apertura == None) or (instancia_vivero_destino.fecha_cierre_actual != None) or 
            (instancia_vivero_origen.fecha_ultima_apertura == None) or (instancia_vivero_origen.fecha_cierre_actual != None)):
            raise ValidationError('Unos de los dos viveros está cerrado o no se encuentran activos')
        if not instancia_traslado:
            raise ValidationError('El traslado ingresado no existe.')
        
          # SE VALIDA QUE NO SE BORREN TODOS LOS ITEMS, AL MENOS DEBE QUEDAR UNO
        if len(items_traslado) < 1:
            raise ValidationError('No se pueden borrar todos los items de un traslado. Si lo desea hacer diríjase al módulo de anulación de traslados')
        
        # SE VALIDA QUE EXISTE AL MENOS UNA CANTIDAD MAYOR A CERO
        aux_validacion_cantidades = [i['cantidad_a_trasladar'] for i in items_traslado if i['cantidad_a_trasladar']>0]
        if aux_validacion_cantidades == []:
            raise ValidationError('Las cantidades deben ser mayores a cero')
        if len(aux_validacion_cantidades) != len(items_traslado):
            raise ValidationError('Una de las cantidades es igual a cero, o ingresó un bien repetido')
        
        # SE EVALUAN LOS ITEMS QUE SE VAN A ELIMINAR
        ids_items_entrantes = [i['id_item_traslado_viveros'] for i in items_traslado if i['id_item_traslado_viveros'] != None]
        aux_items_existentes = ItemsTrasladoViveros.objects.filter(id_traslado=info_traslado['id_traslado'])
        
        # SE TOMA EL UNIQUE TOGETHER DE LOS ITEMS EXISTENTES 
        aux_valores_repetidos = [[i.id_bien_origen.id_bien, i.agno_lote_origen, i.nro_lote_origen] for i in aux_items_existentes]
        for i in items_traslado:
            if i['id_item_traslado_viveros'] == None:
                aux_local = [i['id_bien_origen'], i['agno_lote_origen'], i['nro_lote_origen']]
                if aux_local in aux_valores_repetidos:
                    raise ValidationError('El bien con id ' + str(i['id_bien_origen']) + ' con número de posición ' + str(i['nro_posicion']) + ' ya existe en este traslado')
                aux_valores_repetidos.append([i['id_bien_origen'], i['agno_lote_origen'], i['nro_lote_origen']])
        
        # SE TOMAN LOS IDS DE LOS ITEMS A ELIMINAR
        ids_items_existentes = [i.id_item_traslado_viveros for i in aux_items_existentes]
        items_a_eliminar = [i for i in ids_items_existentes if i not in ids_items_entrantes]
        
#-----------> ELIMINACIÓN DE LOS ITEMS<--------------------------------------------------------------------------------------------#
        valores_eliminados_detalles = []
        for i in items_a_eliminar:
            aux_validaciones_items = ItemsTrasladoViveros.objects.filter(id_item_traslado_viveros=i).first()
            if not aux_validaciones_items:
                raise NotFound('No se encontró el item a eliminar')
            aux_bien = CatalogoBienes.objects.filter(id_bien=aux_validaciones_items.id_bien_origen.id_bien).first()
            if not aux_bien:
                raise NotFound('No se encontró el bien a eliminar')
            
            # SE INSTANCIAN LOS VIVEROS
            if (aux_bien.cod_tipo_elemento_vivero == 'IN' or aux_bien.cod_tipo_elemento_vivero == 'HE' or (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == True)):
                instancia_inventario_vivero_origen = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_origen.id_vivero,id_bien=aux_bien.id_bien).first()
                instancia_inventario_vivero_destino = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_destino.id_vivero,id_bien=aux_bien.id_bien).first()
            if (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == False):
                instancia_inventario_vivero_origen = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_origen.id_vivero,id_bien=aux_bien.id_bien,agno_lote=aux_validaciones_items.agno_lote_origen,nro_lote=aux_validaciones_items.nro_lote_origen,cod_etapa_lote=aux_validaciones_items.cod_etapa_lote_origen).first()
                instancia_inventario_vivero_destino = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_destino.id_vivero,id_bien=aux_bien.id_bien,agno_lote=aux_validaciones_items.agno_lote_destino_MV,nro_lote=aux_validaciones_items.nro_lote_destino_MV,cod_etapa_lote=aux_validaciones_items.cod_etapa_lote_destino_MV).first()
            if not instancia_inventario_vivero_origen or not instancia_inventario_vivero_destino:
                raise NotFound('No se encontró el registro en el inventario a eliminar')
            
            # SE VALIDA QUE LAS CANTIDADES SEAN MAYORES A CERO
            if ((instancia_inventario_vivero_destino.cantidad_bajas != 0 and instancia_inventario_vivero_destino.cantidad_bajas != None) or (instancia_inventario_vivero_destino.cantidad_consumos_internos != 0 and instancia_inventario_vivero_destino.cantidad_consumos_internos != None) or (instancia_inventario_vivero_destino.cantidad_salidas != 0 and instancia_inventario_vivero_destino.cantidad_salidas != None) 
                or (instancia_inventario_vivero_destino.cantidad_lote_cuarentena != 0 and instancia_inventario_vivero_destino.cantidad_lote_cuarentena != None) or (instancia_inventario_vivero_destino.cantidad_traslados_lote_produccion_distribucion != 0 and instancia_inventario_vivero_destino.cantidad_traslados_lote_produccion_distribucion != None)):
                instancia_inventario_vivero_destino.cantidad_entrante = instancia_inventario_vivero_destino.cantidad_entrante - aux_validaciones_items.cantidad_a_trasladar
                
                if (aux_bien.cod_tipo_elemento_vivero == 'IN' or aux_bien.cod_tipo_elemento_vivero == 'HE' or (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == True)):
                    if (aux_bien.cod_tipo_elemento_vivero == 'MV'and aux_bien.es_semilla_vivero == True) or aux_bien.cod_tipo_elemento_vivero == 'IN':
                        saldo_disponible = instancia_inventario_vivero_destino.cantidad_entrante - instancia_inventario_vivero_destino.cantidad_bajas - instancia_inventario_vivero_destino.cantidad_consumos_internos - instancia_inventario_vivero_destino.cantidad_salidas
                    elif aux_bien.cod_tipo_elemento_vivero == 'HE':
                        saldo_disponible = instancia_inventario_vivero_destino.cantidad_entrante - instancia_inventario_vivero_destino.cantidad_bajas - instancia_inventario_vivero_destino.cantidad_salidas
                elif (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == False):
                    if instancia_inventario_vivero_origen.cantidad_entrante == None:
                        raise NotFound('El bien' + str(aux_validaciones_items.id_bien_origen.nombre) + ' no tiene catidad de entrada.')
                    if instancia_inventario_vivero_destino.cod_etapa_lote == 'P':
                        raise NotFound('El bien' + str(aux_validaciones_items.id_bien_origen.nombre) + ' no puede borrarse del traslado porque ya tiene salidas, consumos, distribuciones o está en cuarentena')
                    if instancia_inventario_vivero_destino.cod_etapa_lote == 'D':
                        raise NotFound('El bien' + str(aux_validaciones_items.id_bien_origen.nombre) + ' no puede borrarse del traslado porque ya tiene salidas, consumos, distribuciones o está en cuarentena')
                    
                if saldo_disponible < 0:
                    raise ValidationError('En el bien' + str(aux_validaciones_items.id_bien_origen.nombre) + ' no se puede actualizar la cantidad debido a que si se ejectua la operación quedaría un saldo negativo en la actualidad.')
                else:
                    instancia_inventario_vivero_origen.cantidad_salidas = instancia_inventario_vivero_origen.cantidad_salidas - aux_validaciones_items.cantidad_a_trasladar
                aux_validaciones_items.delete()
                
            else:
                if (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == False):
                    if instancia_inventario_vivero_destino.cod_etapa_lote == 'P' or instancia_inventario_vivero_destino.cod_etapa_lote == 'D':
                        if instancia_inventario_vivero_destino.fecha_ingreso_lote_etapa != instancia_inventario_vivero_destino.fecha_ult_altura_lote:
                            raise NotFound('El bien' + str(aux_validaciones_items.id_bien_origen.nombre) + ' no puede borrarse debido a que tiene registros de altura posteriores a la fecha de creación del traslado.')
                        else:
                            instancia_inventario_vivero_origen.cantidad_salidas = instancia_inventario_vivero_origen.cantidad_salidas - aux_validaciones_items.cantidad_a_trasladar
                            instancia_inventario_vivero_destino.delete()
                            aux_validaciones_items.delete()
                if (aux_bien.cod_tipo_elemento_vivero == 'IN' or aux_bien.cod_tipo_elemento_vivero == 'HE' or (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == True)):
                    if (instancia_inventario_vivero_destino.cantidad_entrante - aux_validaciones_items.cantidad_a_trasladar) != 0:
                        instancia_inventario_vivero_origen.cantidad_salidas = instancia_inventario_vivero_origen.cantidad_salidas - aux_validaciones_items.cantidad_a_trasladar
                        instancia_inventario_vivero_destino.cantidad_entrante = instancia_inventario_vivero_destino.cantidad_entrante - aux_validaciones_items.cantidad_a_trasladar
                        aux_validaciones_items.delete()
                    else:
                        instancia_inventario_vivero_origen.cantidad_salidas = instancia_inventario_vivero_origen.cantidad_salidas - aux_validaciones_items.cantidad_a_trasladar
                        instancia_inventario_vivero_destino.delete()
                        aux_validaciones_items.delete()
            valores_eliminados_detalles.append({'nombre' : aux_bien.nombre})
        aux_nro_posicion = []
        
        # ACTUALIZAR ARCHIVO
        if archivo_soporte:
            if instancia_traslado.ruta_archivo_soporte:
                instancia_traslado.ruta_archivo_soporte.ruta_archivo.delete()
                instancia_traslado.ruta_archivo_soporte.delete()

            archivo_creado = UtilsGestor.create_archivo_digital(archivo_soporte, "TrasladosViveros")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            instancia_traslado.ruta_archivo_soporte = archivo_creado_instance.id_archivo_digital
        # elif not archivo_soporte and instancia_traslado.ruta_archivo_soporte:
        #     instancia_traslado.ruta_archivo_soporte.ruta_archivo.delete()
        #     instancia_traslado.ruta_archivo_soporte.delete()

        # SE GUARDAN LAS MODIFICACIONES EN LA TABLA TRASLADOS
        instancia_traslado.observaciones = info_traslado['observaciones']
        instancia_traslado.save()

        valores_creados_detalles = []
        valores_actualizados_detalles = []
        
        for i in items_traslado:
#-----------> CREACIÓN DE NUEVOS ITEMS<--------------------------------------------------------------------------------------------#
            if i['id_item_traslado_viveros'] == None:
                instancia_bien = CatalogoBienes.objects.filter(id_bien=i['id_bien_origen']).first()
                
                if not instancia_bien:
                    raise ValidationError('El bien seleccionado no existe')
               
                instancia_item = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_origen.id_vivero,id_bien=i['id_bien_origen'],agno_lote=i['agno_lote_origen'],nro_lote=i['nro_lote_origen'],cod_etapa_lote=i['cod_etapa_lote_origen']).first()
                if not instancia_item:
                    raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' no existe en el inventario del vivero origen.')
                
                # SE VALIDA QUE EL BIEN A TRASLADAR NO ESTÉ EN ETAPA DE GERMINACIÓN
                if i['cod_etapa_lote_origen'] == 'G':
                    raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) +' no se puede trasladar porque está en etapa de germinación')
                
                # SE VALIDA LA CANTIDAD DISPONIBLE DEL BIEN A TRASLADAR
                # SE SETEAN A CERO LAS CANTIDADES CUANDO SEAN NULAS
                instancia_item.cantidad_traslados_lote_produccion_distribucion = instancia_item.cantidad_traslados_lote_produccion_distribucion if instancia_item.cantidad_traslados_lote_produccion_distribucion else 0
                instancia_item.cantidad_salidas = instancia_item.cantidad_salidas if instancia_item.cantidad_salidas else 0
                instancia_item.cantidad_lote_cuarentena = instancia_item.cantidad_lote_cuarentena if instancia_item.cantidad_lote_cuarentena else 0
                instancia_item.cantidad_bajas = instancia_item.cantidad_bajas if instancia_item.cantidad_bajas else 0
                instancia_item.cantidad_consumos_internos = instancia_item.cantidad_consumos_internos if instancia_item.cantidad_consumos_internos else 0
                
                if instancia_bien.cod_tipo_elemento_vivero == 'MV'and instancia_bien.es_semilla_vivero == False:
                    if instancia_item.cantidad_entrante == None:
                        raise NotFound('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) +' no tiene cantidad disponible.')
                    if instancia_item.cod_etapa_lote == 'P':
                        saldo_disponible = instancia_item.cantidad_entrante - instancia_item.cantidad_bajas - instancia_item.cantidad_traslados_lote_produccion_distribucion - instancia_item.cantidad_salidas - instancia_item.cantidad_lote_cuarentena
                    if instancia_item.cod_etapa_lote == 'D':
                        saldo_disponible = instancia_item.cantidad_entrante - instancia_item.cantidad_bajas - instancia_item.cantidad_salidas - instancia_item.cantidad_lote_cuarentena
                elif (instancia_bien.cod_tipo_elemento_vivero == 'MV'and instancia_bien.es_semilla_vivero == True) or instancia_bien.cod_tipo_elemento_vivero == 'IN':
                    saldo_disponible = instancia_item.cantidad_entrante - instancia_item.cantidad_bajas - instancia_item.cantidad_consumos_internos - instancia_item.cantidad_salidas
                    if i['altura_lote_destion_en_cms'] != None:
                        raise NotFound('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) +' no es una planta, por ende la altura del lote se debería ingresar como nula')
                elif instancia_bien.cod_tipo_elemento_vivero == 'HE':
                    if i['altura_lote_destion_en_cms'] != None:
                        raise NotFound('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' no es una planta, por ende la altura del lote se debería ingresar como nula')
                    saldo_disponible = instancia_item.cantidad_entrante - instancia_item.cantidad_bajas - instancia_item.cantidad_salidas
                if i['cantidad_a_trasladar'] > saldo_disponible:
                    raise ValidationError('En el bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) +' la cantidad que desea trasladar es superior al saldo disponible')
                
                # SE VALIDA QUE LA ETAPA DE DESTINO SEA DIFERENTE DE GERMINACIÓN
                if i['cod_etapa_lote_destino_MV'] == 'G':
                    raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) +' la etapa de destino no puede ser germinación')
                
                # SE ASIGNA EL AÑO DEL LOTE Y EL NÚMERO DEL LOTE
                aux_get_ultimo_nro_lote_by_agno = InventarioViveros.objects.filter(id_bien=i['id_bien_origen'],agno_lote=i['agno_lote_destino_MV']).order_by('nro_lote').last()
                if instancia_bien.cod_tipo_elemento_vivero == 'MV'and instancia_bien.es_semilla_vivero == False:
                    i['agno_lote_destino_MV'] = instancia_traslado.fecha_traslado.year
                    if not aux_get_ultimo_nro_lote_by_agno:
                        i['nro_lote_destino_MV'] = 1
                    else:
                        i['nro_lote_destino_MV'] = aux_get_ultimo_nro_lote_by_agno.nro_lote + 1 
                if i['nro_posicion'] in aux_nro_posicion:
                    raise ValidationError('En el bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' el número de posición debe ser único')
                i['id_traslado'] = instancia_traslado.id_traslado
                aux_nro_posicion.append(i['nro_posicion'])
                del i['id_item_traslado_viveros']
                valores_creados_detalles.append({'nombre' : instancia_bien.nombre})
                serializer_items = self.serializer_items_traslado(data=i, many=False)
                serializer_items.is_valid(raise_exception=True)
                serializer_items.save()
                instancia_bien = CatalogoBienes.objects.filter(id_bien=i['id_bien_origen']).first()
                
                # SE GUARDAN LOS DATOS EN EL INVENTARIO VIVERO ORIGEN
                if instancia_bien.cod_tipo_elemento_vivero == 'MV'and instancia_bien.es_semilla_vivero == False:
                    instancia_item_origen = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_origen.id_vivero,id_bien=i['id_bien_origen'],agno_lote=i['agno_lote_origen'],nro_lote=i['nro_lote_origen'],cod_etapa_lote=i['cod_etapa_lote_origen']).first()
                else:
                    instancia_item_origen = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_origen.id_vivero,id_bien=i['id_bien_origen']).first()
                instancia_item_origen.cantidad_salidas = instancia_item_origen.cantidad_salidas if instancia_item_origen.cantidad_salidas else 0
                instancia_item_origen.cantidad_salidas = instancia_item_origen.cantidad_salidas + i['cantidad_a_trasladar']
                instancia_item_origen.save()
                
                # SE GUARDAN LOS DATOS EN EL INVENTARIO VIVERO DESTINO
                # SI ES UN MATERIAL VEGETAL QUE ES SEMILLA O UNA HERRAMIENTA O UN INSUMO
                if (instancia_bien.cod_tipo_elemento_vivero == 'MV'and instancia_bien.es_semilla_vivero == True) or instancia_bien.cod_tipo_elemento_vivero == 'HE' or instancia_bien.cod_tipo_elemento_vivero == 'IN':
                    instancia_item_despacho = InventarioViveros.objects.filter(id_vivero=info_traslado['id_vivero_destino'],id_bien=i['id_bien_origen']).first()
                    if instancia_item_despacho:
                        instancia_item_despacho.cantidad_entrante = instancia_item_despacho.cantidad_entrante if instancia_item_despacho.cantidad_entrante else 0
                        instancia_item_despacho.cantidad_entrante = instancia_item_despacho.cantidad_entrante + i['cantidad_a_trasladar']
                        instancia_item_despacho.save()
                    else:
                        inventario_vivero_dict = {
                                                "id_vivero": instancia_traslado.id_vivero_destino.id_vivero,
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
                        
                # SI ES UN MATERIAL VEGETAL QUE NO ES SEMILLA
                elif instancia_bien.cod_tipo_elemento_vivero == 'MV'and instancia_bien.es_semilla_vivero == False:
                    inventario_vivero_dict = {
                                            "id_vivero": instancia_traslado.id_vivero_destino.id_vivero,
                                            "id_bien": i['id_bien_origen'],
                                            "agno_lote" : i['agno_lote_destino_MV'],
                                            "nro_lote" : i['nro_lote_destino_MV'],
                                            "cod_etapa_lote" : i['cod_etapa_lote_destino_MV'],
                                            "es_produccion_propia_lote" : instancia_item_origen.es_produccion_propia_lote,
                                            "cod_tipo_entrada_alm_lote" : instancia_item_origen.cod_tipo_entrada_alm_lote,
                                            "nro_entrada_alm_lote" : instancia_item_origen.nro_entrada_alm_lote,
                                            "fecha_ingreso_lote_etapa" : instancia_traslado.fecha_traslado,
                                            "ult_altura_lote" : i['altura_lote_destion_en_cms'],
                                            "fecha_ult_altura_lote" : instancia_traslado.fecha_traslado,
                                            "cantidad_entrante" : i['cantidad_a_trasladar'],
                                            "id_mezcla" : None
                                            }
                    serializer_inventario = CreateSiembraInventarioViveroSerializer(data=inventario_vivero_dict, many=False)
                    serializer_inventario.is_valid(raise_exception=True)
                    serializer_inventario.save()
                    
                    # SE ACTUALIZA EL CAMPO ITEM YA USADO EN EL VIVERO DESTINO
                    instancia_vivero_destino.item_ya_usado = True if instancia_vivero_destino.item_ya_usado == False else instancia_vivero_destino.item_ya_usado
                    instancia_vivero_destino.save()
                    
                    
#-----------> ACTUALIZACIÓN DE LOS ITEMS<--------------------------------------------------------------------------------------------#
            elif i['id_item_traslado_viveros'] != None:
                aux_validaciones_items = ItemsTrasladoViveros.objects.filter(id_traslado=info_traslado['id_traslado'],id_item_traslado_viveros=i['id_item_traslado_viveros']).first()
                previous_instancia_item = copy.copy(aux_validaciones_items)
                if not aux_validaciones_items:
                    raise ValidationError('El bien con número de posición ' + str(i['nro_posicion']) + ' no se encuentra registrado en este traslado.')
                
                aux_bien = CatalogoBienes.objects.filter(id_bien=aux_validaciones_items.id_bien_origen.id_bien).first()
                if not aux_bien:
                    raise ValidationError('Error en el item nro: (' + str(i['nro_posicion']) + '). No existe el bien.')
                
                altura_ingresada_item = i.get('altura_lote_destion_en_cms')
                if altura_ingresada_item != None and ((aux_bien.cod_tipo_elemento_vivero != 'MV' and aux_bien.es_semilla_vivero != False) or (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero != False)):
                    raise ValidationError('El bien ' + str(aux_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' no es una planta, por ende no debería tener altura.')
                
                if i['nro_posicion'] in aux_nro_posicion:
                    raise ValidationError('El bien ' + str(aux_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' tiene un número de posición que ya existe.')
                aux_nro_posicion.append(i['nro_posicion'])
                
                # SE INSTANCIAN LOS VIVEROS
                if (aux_bien.cod_tipo_elemento_vivero == 'IN' or aux_bien.cod_tipo_elemento_vivero == 'HE' or (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == True)):
                    instancia_inventario_vivero_origen = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_origen.id_vivero,id_bien=aux_bien.id_bien).first()
                    instancia_inventario_vivero_destino = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_destino.id_vivero,id_bien=aux_bien.id_bien).first()
                if (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == False):
                    instancia_inventario_vivero_origen = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_origen.id_vivero,id_bien=aux_bien.id_bien,agno_lote=aux_validaciones_items.agno_lote_origen,nro_lote=aux_validaciones_items.nro_lote_origen,cod_etapa_lote=aux_validaciones_items.cod_etapa_lote_origen).first()
                    instancia_inventario_vivero_destino = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_destino.id_vivero,id_bien=aux_bien.id_bien,agno_lote=aux_validaciones_items.agno_lote_destino_MV,nro_lote=aux_validaciones_items.nro_lote_destino_MV,cod_etapa_lote=aux_validaciones_items.cod_etapa_lote_destino_MV).first()
                    
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
                if (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == False):
                    if aux_validaciones_items.altura_lote_destion_en_cms != i['altura_lote_destion_en_cms']:
                        fecha_actual = datetime.now()
                        if fecha_actual.day != instancia_traslado.fecha_traslado.day:
                            instancia_inventario_vivero_destino.ult_altura_lote = i['altura_lote_destion_en_cms']
                            instancia_inventario_vivero_destino.fecha_ult_altura_lote = fecha_actual
                            aux_validaciones_items.altura_lote_destion_en_cms = i['altura_lote_destion_en_cms']
                        else:
                            instancia_inventario_vivero_origen.ult_altura_lote = i['altura_lote_destion_en_cms']
                            instancia_inventario_vivero_destino.ult_altura_lote = i['altura_lote_destion_en_cms']
                            instancia_inventario_vivero_origen.fecha_ult_altura_lote = fecha_actual
                            instancia_inventario_vivero_destino.fecha_ult_altura_lote = fecha_actual
                            aux_validaciones_items.altura_lote_destion_en_cms = i['altura_lote_destion_en_cms']
                            
                # SE VALDIA QUE LA CANTIDAD NO SE ACTUALICE MÁS DE UN DÍA DESPUÉS DEL TRASLADO
                if aux_validaciones_items.cantidad_a_trasladar != i['cantidad_a_trasladar']:
                    fecha_actual = datetime.now()
                    aux_fecha = int((fecha_actual-instancia_traslado.fecha_traslado).days)
                    if aux_fecha > int(1):
                        raise ValidationError('No es posible actualizar las cantidades de un traslado mas de un día después de ejecutarlo.')
                    
                # EN CASO DE AUMENTAR LA CANTIDAD TRASLADADA
                if aux_validaciones_items.cantidad_a_trasladar < i['cantidad_a_trasladar']:
                    if (aux_bien.cod_tipo_elemento_vivero == 'IN' or aux_bien.cod_tipo_elemento_vivero == 'HE' or (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == True)):
                        if (aux_bien.cod_tipo_elemento_vivero == 'MV'and aux_bien.es_semilla_vivero == True) or aux_bien.cod_tipo_elemento_vivero == 'IN':
                            saldo_disponible = instancia_inventario_vivero_origen.cantidad_entrante - instancia_inventario_vivero_origen.cantidad_bajas - instancia_inventario_vivero_origen.cantidad_consumos_internos - instancia_inventario_vivero_origen.cantidad_salidas
                        elif aux_bien.cod_tipo_elemento_vivero == 'HE':
                            saldo_disponible = instancia_inventario_vivero_origen.cantidad_entrante - instancia_inventario_vivero_origen.cantidad_bajas - instancia_inventario_vivero_origen.cantidad_salidas
                    elif (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == False):
                        if instancia_inventario_vivero_origen.cantidad_entrante == None:
                            raise NotFound('El bien ' + str(aux_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) +  ' no tiene catidad de entrada registrada en el vivero origen.')
                        if instancia_inventario_vivero_origen.cod_etapa_lote == 'P':
                            saldo_disponible = instancia_inventario_vivero_origen.cantidad_entrante - instancia_inventario_vivero_origen.cantidad_bajas - instancia_inventario_vivero_origen.cantidad_traslados_lote_produccion_distribucion - instancia_inventario_vivero_origen.cantidad_salidas - instancia_inventario_vivero_origen.cantidad_lote_cuarentena
                        if instancia_inventario_vivero_origen.cod_etapa_lote == 'D':
                            saldo_disponible = instancia_inventario_vivero_origen.cantidad_entrante - instancia_inventario_vivero_origen.cantidad_bajas - instancia_inventario_vivero_origen.cantidad_salidas - instancia_inventario_vivero_origen.cantidad_lote_cuarentena
                    if i['cantidad_a_trasladar'] > saldo_disponible:
                        raise ValidationError('En el bien ' + str(aux_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' la cantidad que desea actualizar es superior al saldo disponible')
                    else:
                        instancia_inventario_vivero_origen.cantidad_salidas = instancia_inventario_vivero_origen.cantidad_salidas + (i['cantidad_a_trasladar'] - aux_validaciones_items.cantidad_a_trasladar)
                        instancia_inventario_vivero_destino.cantidad_entrante = instancia_inventario_vivero_destino.cantidad_entrante + (i['cantidad_a_trasladar'] - aux_validaciones_items.cantidad_a_trasladar)
                        aux_validaciones_items.cantidad_a_trasladar = i['cantidad_a_trasladar']
                        
                # EN CASO DE DISMINUIR LA CANTIDAD TRASLADADA          
                elif aux_validaciones_items.cantidad_a_trasladar > i['cantidad_a_trasladar']:
                    if i['cantidad_a_trasladar'] <= 0:
                        raise ValidationError('Error en el item nro: (' + str(i['nro_posicion']) + '). La cantidad debe ser mayor a cero')
                    instancia_inventario_vivero_destino.cantidad_entrante = instancia_inventario_vivero_destino.cantidad_entrante - (aux_validaciones_items.cantidad_a_trasladar - i['cantidad_a_trasladar'])
                    if (aux_bien.cod_tipo_elemento_vivero == 'IN' or aux_bien.cod_tipo_elemento_vivero == 'HE' or (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == True)):
                        if (aux_bien.cod_tipo_elemento_vivero == 'MV'and aux_bien.es_semilla_vivero == True) or aux_bien.cod_tipo_elemento_vivero == 'IN':
                            saldo_disponible = instancia_inventario_vivero_destino.cantidad_entrante - instancia_inventario_vivero_destino.cantidad_bajas - instancia_inventario_vivero_destino.cantidad_consumos_internos - instancia_inventario_vivero_destino.cantidad_salidas
                        elif aux_bien.cod_tipo_elemento_vivero == 'HE':
                            saldo_disponible = instancia_inventario_vivero_destino.cantidad_entrante - instancia_inventario_vivero_destino.cantidad_bajas - instancia_inventario_vivero_destino.cantidad_salidas
                    elif (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == False):
                        if instancia_inventario_vivero_origen.cantidad_entrante == None:
                            raise NotFound('El bien ' + str(aux_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' no tiene catidad de entrada registrada en el vivero.')
                        if instancia_inventario_vivero_destino.cod_etapa_lote == 'P':
                            saldo_disponible = instancia_inventario_vivero_destino.cantidad_entrante - instancia_inventario_vivero_destino.cantidad_bajas - instancia_inventario_vivero_destino.cantidad_traslados_lote_produccion_distribucion - instancia_inventario_vivero_destino.cantidad_salidas - instancia_inventario_vivero_destino.cantidad_lote_cuarentena
                        if instancia_inventario_vivero_destino.cod_etapa_lote == 'D':
                            saldo_disponible = instancia_inventario_vivero_destino.cantidad_entrante - instancia_inventario_vivero_destino.cantidad_bajas - instancia_inventario_vivero_destino.cantidad_salidas - instancia_inventario_vivero_destino.cantidad_lote_cuarentena
                    if saldo_disponible < 0:
                        raise ValidationError('En el bien ' + str(aux_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' no se puede actualizar la cantidad debido a que si se ejectua la operación quedaría un saldo negativo en la actualidad.')
                    else:
                        instancia_inventario_vivero_origen.cantidad_salidas = instancia_inventario_vivero_origen.cantidad_salidas - (aux_validaciones_items.cantidad_a_trasladar - (i['cantidad_a_trasladar']))
                        aux_validaciones_items.cantidad_a_trasladar = i['cantidad_a_trasladar']
                aux_validaciones_items.save()
                instancia_inventario_vivero_destino.save()
                instancia_inventario_vivero_origen.save()
                valores_actualizados_detalles.append({'descripcion': {'nombre' : aux_bien.nombre},'previous':previous_instancia_item,'current':aux_validaciones_items})
        
        # AUDITORIA DEL SERVICIO DE ACTUALIZACIÓN DE UN TRASLADO ENTRE VIVEROS
        descripcion = {"numero_traslado": str(instancia_traslado.nro_traslado), "fecha_traslado": str(instancia_traslado.fecha_traslado)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 52,
            "cod_permiso": "AC",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles,
            "valores_actualizados_detalles": valores_actualizados_detalles,
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        return Response({'success':True, 'detail':'Traslado actualizado con éxito'}, status=status.HTTP_200_OK)

class TrasladosAnular(generics.UpdateAPIView):
    serializer_class = TrasladosViverosSerializers
    queryset = TrasladosViveros.objects.all()
    permission_classes = [IsAuthenticated, PermisoAnularTrasladosEntreViveros]
    serializer_items_traslado = ItemsTrasladosViverosSerielizers
    
    def put(self, request, id_traslado_a_anular):
        datos_ingresados = request.data
        instancia_traslado = TrasladosViveros.objects.filter(id_traslado=id_traslado_a_anular).first()
        if not instancia_traslado:
            raise ValidationError('No existe el traslado que desea anular.')
        if instancia_traslado.traslado_anulado == True:
            raise ValidationError('Este traslado ya fue anulado.')
        items_del_traslado = ItemsTrasladoViveros.objects.filter(id_traslado=instancia_traslado.id_traslado)
        if not items_del_traslado:
            raise ValidationError('Este traslado no tiene items asociados o ya fue anulado.')
        fecha_traslado = instancia_traslado.fecha_traslado
        aux_validacion_fechas = datetime.now() - fecha_traslado
        if int(aux_validacion_fechas.days) > 30:
            raise NotFound('No puede anular un despacho con fecha anterior a 30 días respecto a la actual')
        
        valores_eliminados_detalles = []
        for i in items_del_traslado:
            aux_validaciones_items = ItemsTrasladoViveros.objects.filter(id_item_traslado_viveros=i.id_item_traslado_viveros).first()
            if not aux_validaciones_items:
                raise NotFound('No se encontró el item a eliminar')
            aux_bien = CatalogoBienes.objects.filter(id_bien=aux_validaciones_items.id_bien_origen.id_bien).first()
            if not aux_bien:
                raise NotFound('No se encontró el bien a eliminar')
            
            # SE INSTANCIAN LOS VIVEROS
            if (aux_bien.cod_tipo_elemento_vivero == 'IN' or aux_bien.cod_tipo_elemento_vivero == 'HE' or (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == True)):
                instancia_inventario_vivero_origen = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_origen.id_vivero,id_bien=aux_bien.id_bien).first()
                instancia_inventario_vivero_destino = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_destino.id_vivero,id_bien=aux_bien.id_bien).first()
            if (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == False):
                instancia_inventario_vivero_origen = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_origen.id_vivero,id_bien=aux_bien.id_bien,agno_lote=aux_validaciones_items.agno_lote_origen,nro_lote=aux_validaciones_items.nro_lote_origen,cod_etapa_lote=aux_validaciones_items.cod_etapa_lote_origen).first()
                instancia_inventario_vivero_destino = InventarioViveros.objects.filter(id_vivero=instancia_traslado.id_vivero_destino.id_vivero,id_bien=aux_bien.id_bien,agno_lote=aux_validaciones_items.agno_lote_destino_MV,nro_lote=aux_validaciones_items.nro_lote_destino_MV,cod_etapa_lote=aux_validaciones_items.cod_etapa_lote_destino_MV).first()
            if not instancia_inventario_vivero_origen or not instancia_inventario_vivero_destino:
                raise NotFound('No se encontró el registro en el inventario a eliminar')
            
            # SE VALIDA QUE LAS CANTIDADES SEAN MAYORES A CERO
            if ((instancia_inventario_vivero_destino.cantidad_bajas != 0 and instancia_inventario_vivero_destino.cantidad_bajas != None) or (instancia_inventario_vivero_destino.cantidad_consumos_internos != 0 and instancia_inventario_vivero_destino.cantidad_consumos_internos != None) or (instancia_inventario_vivero_destino.cantidad_salidas != 0 and instancia_inventario_vivero_destino.cantidad_salidas != None) 
                or (instancia_inventario_vivero_destino.cantidad_lote_cuarentena != 0 and instancia_inventario_vivero_destino.cantidad_lote_cuarentena != None) or (instancia_inventario_vivero_destino.cantidad_traslados_lote_produccion_distribucion != 0 and instancia_inventario_vivero_destino.cantidad_traslados_lote_produccion_distribucion != None)):
                instancia_inventario_vivero_destino.cantidad_entrante = instancia_inventario_vivero_destino.cantidad_entrante - aux_validaciones_items.cantidad_a_trasladar
                if (aux_bien.cod_tipo_elemento_vivero == 'IN' or aux_bien.cod_tipo_elemento_vivero == 'HE' or (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == True)):
                    if (aux_bien.cod_tipo_elemento_vivero == 'MV'and aux_bien.es_semilla_vivero == True) or aux_bien.cod_tipo_elemento_vivero == 'IN':
                        saldo_disponible = instancia_inventario_vivero_destino.cantidad_entrante - instancia_inventario_vivero_destino.cantidad_bajas - instancia_inventario_vivero_destino.cantidad_consumos_internos - instancia_inventario_vivero_destino.cantidad_salidas
                    elif aux_bien.cod_tipo_elemento_vivero == 'HE':
                        saldo_disponible = instancia_inventario_vivero_destino.cantidad_entrante - instancia_inventario_vivero_destino.cantidad_bajas - instancia_inventario_vivero_destino.cantidad_salidas
                elif (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == False):
                    if instancia_inventario_vivero_origen.cantidad_entrante == None:
                        raise NotFound('El bien' + str(aux_validaciones_items.id_bien_origen.nombre) + ' no tiene catidad de entrada en el vivero origen.')
                    if instancia_inventario_vivero_destino.cod_etapa_lote == 'P':
                        raise NotFound('El bien' + str(aux_validaciones_items.id_bien_origen.nombre) + ' no puede borrarse del traslado porque ya tiene salidas, consumos, distribuciones o está en cuarentena')
                    if instancia_inventario_vivero_destino.cod_etapa_lote == 'D':
                        raise NotFound('El bien' + str(aux_validaciones_items.id_bien_origen.nombre) + ' no puede borrarse del traslado porque ya tiene salidas, consumos, distribuciones o está en cuarentena')
                if saldo_disponible < 0:
                    raise ValidationError('En el bien' + str(aux_validaciones_items.id_bien_origen.nombre) + ' no se puede actualizar la cantidad debido a que si se ejectua la operación quedaría un saldo negativo en la actualidad.')
                else:
                    instancia_inventario_vivero_origen.cantidad_salidas = instancia_inventario_vivero_origen.cantidad_salidas - aux_validaciones_items.cantidad_a_trasladar
                aux_validaciones_items.delete()
            else:
                if (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == False):
                    if instancia_inventario_vivero_destino.cod_etapa_lote == 'P' or instancia_inventario_vivero_destino.cod_etapa_lote == 'D':
                        if instancia_inventario_vivero_destino.fecha_ingreso_lote_etapa != instancia_inventario_vivero_destino.fecha_ult_altura_lote:
                            raise NotFound('El bien' + str(aux_validaciones_items.id_bien_origen.nombre) + ' no puede borrarse debido a que tiene registros de altura posteriores a la fecha de creación del traslado.')
                        else:
                            instancia_inventario_vivero_origen.cantidad_salidas = instancia_inventario_vivero_origen.cantidad_salidas - aux_validaciones_items.cantidad_a_trasladar
                            instancia_inventario_vivero_destino.delete()
                            aux_validaciones_items.delete()
                if (aux_bien.cod_tipo_elemento_vivero == 'IN' or aux_bien.cod_tipo_elemento_vivero == 'HE' or (aux_bien.cod_tipo_elemento_vivero == 'MV' and aux_bien.es_semilla_vivero == True)):
                    if (instancia_inventario_vivero_destino.cantidad_entrante - aux_validaciones_items.cantidad_a_trasladar) != 0:
                        instancia_inventario_vivero_origen.cantidad_salidas = instancia_inventario_vivero_origen.cantidad_salidas - aux_validaciones_items.cantidad_a_trasladar
                        instancia_inventario_vivero_destino.cantidad_entrante = instancia_inventario_vivero_destino.cantidad_entrante - aux_validaciones_items.cantidad_a_trasladar
                        aux_validaciones_items.delete()
                    else:
                        instancia_inventario_vivero_origen.cantidad_salidas = instancia_inventario_vivero_origen.cantidad_salidas - aux_validaciones_items.cantidad_a_trasladar
                        instancia_inventario_vivero_destino.delete()
                        aux_validaciones_items.delete()
            valores_eliminados_detalles.append({'nombre' : aux_bien.nombre})
        persona_anula = Personas.objects.filter(id_persona=request.user.persona.id_persona).first()
        instancia_traslado.justificacion_anulacion = datos_ingresados['justificacion_anulacion']
        instancia_traslado.fecha_anulado = datetime.now()
        instancia_traslado.id_persona_anula = persona_anula
        instancia_traslado.traslado_anulado = True
        instancia_traslado.save()
        
        # AUDITORIA DEL SERVICIO DE ANULACIÓN
        descripcion = {"numero_traslado": str(instancia_traslado.nro_traslado), "fecha_traslado": str(instancia_traslado.fecha_traslado)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 52,
            "cod_permiso": "AC",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        return Response({'success':True, 'detail':'Traslado anulado con éxito'}, status=status.HTTP_200_OK)