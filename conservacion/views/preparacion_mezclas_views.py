from rest_framework.response import Response
from rest_framework import generics,status
from django.db.models import Q
from conservacion.serializers.mezclas_serializers import (
    MezclasSerializer,
    PreparacionMezclasSerializer,
    ItemsPreparacionMezclasSerializer,
    CatalogoBienesInsumoSerializer,
    CreateMezclaInventarioViveroSerializer,
    ItemsPreparacionMezclaActualizarSerializer
    )
from conservacion.models.mezclas_models import Mezclas, PreparacionMezclas, ItemsPreparacionMezcla
from conservacion.models.inventario_models import InventarioViveros
from conservacion.models.viveros_models import Vivero
from conservacion.models.traslados_models import TrasladosViveros, ItemsTrasladoViveros
from almacen.models.bienes_models import CatalogoBienes
from seguridad.models import Personas, User
from conservacion.models.siembras_models import CambiosDeEtapa
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
import json
from seguridad.utils import Util
import copy
from conservacion.utils import UtilConservacion
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

class GetMezclasByNombre(generics.ListAPIView):
    serializer_class = MezclasSerializer
    queryset = Mezclas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,nombre_mezcla):
        queryset = self.queryset.all()
        mezcla = queryset.filter(nombre__icontains=nombre_mezcla, item_activo=True)
        if not mezcla:
            raise ValidationError('No se encontró ninguna mezcla con ese nombre.')
        
        serializer = self.serializer_class(mezcla, many=True)
        
        return Response ({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data':serializer.data}, status=status.HTTP_200_OK)

class CreatePreparacionMezclas(generics.UpdateAPIView):
    serializer_class = PreparacionMezclasSerializer
    queryset = PreparacionMezclas.objects.all()
    permission_classes = [IsAuthenticated]
    serializador_items_preparacion_mezclas = ItemsPreparacionMezclasSerializer
    
    def put(self, request):
        queryset = self.queryset.all()
        datos_ingresados = request.data
        info_preparacion = datos_ingresados['info_preparacion']
        items_preparacion = datos_ingresados['items_preparacion']
        user_logeado = request.user
        
        instancia_mezcla = Mezclas.objects.filter(id_mezcla=info_preparacion['id_mezcla']).first()
        if not instancia_mezcla:
            raise ValidationError('No se encontró ninguna mezcla con ese nombre.')
        if instancia_mezcla.item_activo == False:
            raise ValidationError('Debe elegir una mezcla que esté activa.')
        
        # SE VALIDA LA FECHA
        fecha_preparacion = datetime.strptime(info_preparacion['fecha_preparacion'], '%Y-%m-%d %H:%M:%S')
        aux_validacion_fecha = queryset.filter(fecha_preparacion__range=[fecha_preparacion,datetime.now()], preparacion_anulada=False)
        if aux_validacion_fecha:
            raise ValidationError('No es posible registrar una mezcla con fecha anterior o igual a la ultima mezcla registrada.')
        fecha_posible = datetime.now() - timedelta(days=1)
        if fecha_preparacion < fecha_posible:
            raise ValidationError('No es posible registrar una preparación de mezclas con más de un día de anterioridad.')
        
        instancia_vivero = Vivero.objects.filter(id_vivero=info_preparacion['id_vivero']).first()
        if not instancia_vivero:
            raise ValidationError('No existe el vivero ingresado.')
        
        if info_preparacion['cantidad_creada'] == None or info_preparacion['cantidad_creada'] <= 0:
            raise ValidationError ('La cantidad de mezcla debe ser mayor a cero.')
        
        info_preparacion['fecha_registro'] = datetime.now()
        info_preparacion['id_persona_prepara'] = user_logeado.persona.id_persona
        
        # SE OBTIENE EL ÚLTIMO NÚMERO DE TRASLADO DISPONIBLE
        cosecutivo_preparacion = PreparacionMezclas.objects.filter(id_vivero=info_preparacion['id_vivero'], id_mezcla=info_preparacion['id_mezcla'])
        if cosecutivo_preparacion:
            consecutivos_preparacion_existentes = [i.consec_vivero_mezclas for i in cosecutivo_preparacion]
            info_preparacion['consec_vivero_mezclas'] = max(consecutivos_preparacion_existentes) + 1
        else:
            info_preparacion['consec_vivero_mezclas'] = 1
        
        # VALIDACIONES DE LOS ITEMS USADOS EN LA PREPARACIÓN
        aux_nro_posicion = []
        aux_valores_repetidos = []
        valores_creados_detalles = [] 
        for i in items_preparacion:
            instancia_bien = CatalogoBienes.objects.filter(id_bien=i['id_bien_usado']).first()
            instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=i['id_bien_usado'],id_vivero=info_preparacion['id_vivero']).first()
                        
            # SE VALIDA LA EXISTENCIA DEL BIEN
            if not instancia_bien:
                raise ValidationError('El bien con número de posición ' + str(i['nro_posicion']) +  'no existe.')

            # SE VALIDA LA EXISTENCIA DEL BIEN EN EL INVENTARIO VIVERO
            if not instancia_bien_vivero:
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) +  'no tiene registros en el inventario del vivero.')
            
            # SE VALIDA QUE EL BIEN TENGA ENTRADAS
            if instancia_bien_vivero.cantidad_entrante == None or instancia_bien_vivero.cantidad_entrante == 0:
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) +  'no tiene entradas, por lo tanto su saldo es cero.')
            
            # SE VALIDA QUE EL BIEN SEA DEL TIPO INSUMO
            if instancia_bien.cod_tipo_elemento_vivero != "IN":
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) +  ' no es un insumo.')
            # SE VALIDA QUE EL NÚMERO DE POSICIÓN SEA ÚNICO
            if int(i['id_bien_usado']) in aux_valores_repetidos:
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' No se puede ingresar dos veces un mismo bien dentro de una preparación de mezclas.')
            
            # SE VALIDA QUE EL NÚMERO DE POSICIÓN SEA ÚNICO
            if int(i['nro_posicion']) in aux_nro_posicion:
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' tiene un número de posición que ya existe.')
            
            # SE VALIDA QUE LA CANTIDAD USADA SEA MAYOR QUE CERO
            if int(i['cantidad_usada']) <= 0:
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' tiene como cantidad de usada cero, la cantidad debe ser mayor que cero.')
            
            # SE VALIDA QUE HAYA SALDO DISPONIBLE
            saldo_disponible = UtilConservacion.get_cantidad_disponible_F(instancia_bien, instancia_bien_vivero)
            if int(i['cantidad_usada']) > saldo_disponible:
                raise ValidationError ('En el bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' no tiene saldo disponible para suplir la cantidad usada.')
            
            # SE GUARDAN EL NÚMERO DE POSICIÓN Y EL ID DE BIEN EN LISTAS PARA VALIDAR SI SE REPITEN
            aux_nro_posicion.append(i['nro_posicion'])
            aux_valores_repetidos.append(i['id_bien_usado'])
            valores_creados_detalles.append({'nombre' : instancia_bien.nombre})
        
        # SE CREA EL REGISTRO EN LA TABLA PREPARACION_MEZCLAS
        serializer_crear = self.serializer_class(data=info_preparacion, many=False)
        serializer_crear.is_valid(raise_exception=True)
        aux_ultimo = serializer_crear.save()
        
        # SE ASIGNA EL ID TRASLADO A LOS ITEMS USADOS EN LA PREPARACIÓN
        for i in items_preparacion:
            i['id_preparacion_mezcla'] = aux_ultimo.pk
        
        # SE CREA EL REGISTRO EN LA TABLA ITEM_PREPARACION
        serializer_crear_items = self.serializador_items_preparacion_mezclas(data=items_preparacion, many=True)
        serializer_crear_items.is_valid(raise_exception=True)
        serializer_crear_items.save()
        
        # AUDITORIA MAESTRO DETALLE DE LA MEZCLA
        descripcion = {"id_vivero": str(info_preparacion['id_vivero']), "consecutivo_preparacion": str(info_preparacion['consec_vivero_mezclas']), "Id_mezcla": str(info_preparacion['id_mezcla'])}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 58,
            "cod_permiso": "CR",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        # SE CREA O ACTUALIZA LA CANTIDAD ENTRANTE DE LA MEZCLA EN EL INVENTARIO VIVERO
        instancia_mezcla_vivero = InventarioViveros.objects.filter(id_mezcla=info_preparacion['id_mezcla'],id_vivero=info_preparacion['id_vivero']).first()
        
        if not instancia_mezcla_vivero:
            inventario_vivero_dict = {
                "id_vivero": info_preparacion['id_vivero'],
                "id_bien": None,
                "agno_lote" : None,
                "nro_lote" : None,
                "cod_etapa_lote" : None,
                "es_produccion_propia_lote" : None,
                "cod_tipo_entrada_alm_lote" : None,
                "nro_entrada_alm_lote" : None,
                "fecha_ingreso_lote_etapa" : info_preparacion['fecha_preparacion'],
                "ult_altura_lote" : None,
                "fecha_ult_altura_lote" : None,
                "cantidad_entrante" : info_preparacion['cantidad_creada'],
                "id_mezcla" : info_preparacion['id_mezcla']
                }
            serializer_inventario = CreateMezclaInventarioViveroSerializer(data=inventario_vivero_dict, many=False)
            serializer_inventario.is_valid(raise_exception=True)
            serializer_inventario.save()
        
        else:
            instancia_mezcla_vivero.cantidad_entrante = instancia_mezcla_vivero.cantidad_entrante if instancia_mezcla_vivero.cantidad_entrante else 0
            instancia_mezcla_vivero.cantidad_entrante = instancia_mezcla_vivero.cantidad_entrante + info_preparacion['cantidad_creada']
            instancia_mezcla_vivero.save()
        
        # SE PONE EN TRUE EL CAMPO ITEM_YA_USADO DE LA TABLA MEZCLAS
        instancia_mezcla.item_ya_usado = True
        instancia_mezcla.save()
            
        # SE GUARDAN LOS DATOS EN EL INVENTARIO VIVERO
        for i in items_preparacion:
            instancia_bien = CatalogoBienes.objects.filter(id_bien=i['id_bien_usado']).first()
            instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=i['id_bien_usado'],id_vivero=info_preparacion['id_vivero']).first()
            instancia_bien_vivero.cantidad_consumos_internos = instancia_bien_vivero.cantidad_consumos_internos if instancia_bien_vivero.cantidad_consumos_internos else 0
            instancia_bien_vivero.cantidad_consumos_internos = instancia_bien_vivero.cantidad_consumos_internos + i['cantidad_usada']
            instancia_bien_vivero.save()       
        
        return Response ({'success':True, 'detail':'Preparación de mezcla creada correctamente', 'data':serializer_crear.data}, status=status.HTTP_200_OK)
    
class GetBienInsumosByCodigo(generics.ListAPIView):
    serializer_class = CatalogoBienesInsumoSerializer
    queryset = CatalogoBienes.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,codigo_bien,id_vivero):
        queryset = self.queryset.all()
        instancia_bien = queryset.filter(codigo_bien=codigo_bien, cod_tipo_elemento_vivero="IN").first()
        
        if not instancia_bien:
            raise ValidationError('No se encontró ningún insumo con el código ingresado.')
        
        instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=instancia_bien.id_bien,id_vivero=id_vivero).first()
        if not instancia_bien_vivero:
            raise ValidationError('El bien ingresado no tiene registros en el inventario del vivero.')
        
        # SE LE AGRAGA EL SALDO DISPONIBLE AL RESULTADO DE BUSQUEDA
        instancia_bien.saldo_disponible = UtilConservacion.get_cantidad_disponible_F(instancia_bien, instancia_bien_vivero) 
        serializer = self.serializer_class(instancia_bien, many=False)
        
        return Response ({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data':serializer.data}, status=status.HTTP_200_OK)

class GetBienInsumosByCodigoAndName(generics.ListAPIView):
    serializer_class = CatalogoBienesInsumoSerializer
    queryset = CatalogoBienes.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        queryset = self.queryset.all()
        filter = {}
        id_vivero = None
        
        for key, value in request.query_params.items():
            if key in ['id_vivero']:
                if value == '' and value == None:
                    raise ValidationError('Es obligatorio elegir un vivero')
                else:
                    id_vivero = value
            elif key in ['nombre_bien']:
                if value != '' and value != None:
                    filter['nombre__icontains'] = value
            elif key in ['codigo_bien']:
                if value != '' and value != None:
                    filter['codigo_bien__icontains'] = value
                    
        filter['cod_tipo_elemento_vivero'] = "IN"
        
        if id_vivero == None:
            raise ValidationError('Es obligatorio elegir un vivero')
                 
        resultados_busqueda = queryset.filter(**filter)
        
        if not resultados_busqueda:
            raise ValidationError('No se encontró ningún insumo con el código ingresado.')
        
        # SE LE AGRAGA EL SALDO DISPONIBLE AL RESULTADO DE BUSQUEDA
        for i in resultados_busqueda:
            instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=i.id_bien,id_vivero=id_vivero).first()
            if not instancia_bien_vivero:
                raise ValidationError('El bien que intenta seleccionar no tiene registros en el inventario del vivero.')
            i.saldo_disponible = UtilConservacion.get_cantidad_disponible_F(i, instancia_bien_vivero) 
                
        serializer = self.serializer_class(resultados_busqueda, many=True)
        
        return Response ({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data':serializer.data}, status=status.HTTP_200_OK)

class UpdatePreparacionMezclas(generics.UpdateAPIView):
    serializer_class = PreparacionMezclasSerializer
    queryset = PreparacionMezclas.objects.all()
    permission_classes = [IsAuthenticated]
    serializador_items_preparacion_mezclas = ItemsPreparacionMezclasSerializer
    serializador_actualizar_items = ItemsPreparacionMezclaActualizarSerializer
    
    def put(self, request):
        queryset = self.queryset.all()
        datos_ingresados = request.data
        info_preparacion = datos_ingresados['info_preparacion']
        items_preparacion = datos_ingresados['items_preparacion']
        user_logeado = request.user
        items_nuevos = []
        items_actualizar = []
        items_eliminar = []
        valores_eliminados_detalles = []
        valores_actualizados_detalles = []
        aux_valores_repetidos = []
        aux_nro_posicion = []
                
        instancia_preparacion = PreparacionMezclas.objects.filter(id_preparacion_mezcla=info_preparacion['id_preparacion_mezcla']).first()

        if not instancia_preparacion:
            raise ValidationError('No se encontró la preparación de mezclas que desea actualizar.')
        
        ultima_preparacion = queryset.filter(id_mezcla=instancia_preparacion.id_mezcla.id_mezcla, id_vivero=instancia_preparacion.id_vivero).order_by("consec_vivero_mezclas").last()
        
        if not ultima_preparacion:
            raise ValidationError('No se encontró ninguna preparación de mezclas.')

        # SE VALIDA QUE SOLO SE PUEDA ACTUALIZAR EL ULTIMO REGISTRO DE LA COMBINACIÓN ID_VIVERO-ID_MEZCLA
        if instancia_preparacion.consec_vivero_mezclas != ultima_preparacion.consec_vivero_mezclas or instancia_preparacion.preparacion_anulada == True:
            raise ValidationError ('Solo es posible actualizar la última preparación de mezclas registrada que no está anulada.')
        
        # SE VALIDA LA FECHA
        fecha_preparacion = instancia_preparacion.fecha_preparacion
        fecha_posible = datetime.now() - timedelta(days=30)
        if fecha_preparacion < fecha_posible:
            raise ValidationError('No es posible actualiazar una preparación de mezclas con más de 30 días de anterioridad.')
        
        if info_preparacion['cantidad_creada'] != instancia_preparacion.cantidad_creada:
            # SE VALIDA LA FECHA
            fecha_posible = datetime.now() - timedelta(days=2)
            if fecha_preparacion < fecha_posible:
                raise ValidationError('No es posible actualiazar la cantidad creada de una preparación de mezclas con más de 2 días de anterioridad.')
            if info_preparacion['cantidad_creada'] == None or info_preparacion['cantidad_creada'] <= 0:
                raise ValidationError('No es posible actualiazar la cantidad creada a 0.')
        
        # SE VALIDA LA EXISTENCIA DE LA MEZCLA EN EL INVENTARIO VIVERO
        instancia_mezcla_vivero = InventarioViveros.objects.filter(id_mezcla=instancia_preparacion.id_mezcla.id_mezcla,id_vivero=instancia_preparacion.id_vivero).first()
        if not instancia_mezcla_vivero:
            raise ValidationError('No existe el registro de la mezcla en el inventario del vivero.')
        
        # SE VALIDA QUE EN CASO DE QUE SE DISMINUYA LA CANTIDAD CREADA DE LA MEZCLA, EL SALDO DISPONIBLE SUPLA LA CANTIDAD POR LA QUE SE ESTÁ ACTUALIZANDO
        if instancia_preparacion.cantidad_creada > info_preparacion['cantidad_creada']:
            instancia_mezcla_vivero.cantidad_entrante = instancia_mezcla_vivero.cantidad_entrante if instancia_mezcla_vivero.cantidad_entrante else 0
            instancia_mezcla_vivero.cantidad_consumos_internos = instancia_mezcla_vivero.cantidad_consumos_internos if instancia_mezcla_vivero.cantidad_consumos_internos else 0
            aux_cantidad = info_preparacion['cantidad_creada'] - instancia_preparacion.cantidad_creada
            instancia_mezcla_vivero.cantidad_entrante = instancia_mezcla_vivero.cantidad_entrante + aux_cantidad
            saldo_disponible_mezcla = instancia_mezcla_vivero.cantidad_entrante -  instancia_mezcla_vivero.cantidad_consumos_internos
            if saldo_disponible_mezcla <= 0:
                raise ValidationError('La cantidad a disminuir de la mezcla es mayor al saldo disponible.')
        
        # SE OBTIENEN LOS ITEMS ITEMS QUE SE VAN A AÑADIR
        items_nuevos = [i for i in items_preparacion if i['id_item_preparacion_mezcla'] == None]
        
        if items_nuevos:
            # SE VALIDA LA FECHA
            fecha_posible = datetime.now() - timedelta(days=2)
            if fecha_preparacion < fecha_posible:
                raise ValidationError('No es posible añadir items a una preparación de mezcla que tenga más de 2 días de anterioridad.')
        
        # SE OBTIENEN LOS ITEMS QUE SE VAN A ACTUALZIAR
        items_actualizar = [i for i in items_preparacion if i['id_item_preparacion_mezcla'] != None]
        
        # SE OBTIENEN LOS ITEMS QUE SE VAN A ELIMINAR
        items_existentes = ItemsPreparacionMezcla.objects.filter(id_preparacion_mezcla=info_preparacion['id_preparacion_mezcla'])
        id_items_existentes = [i.id_item_preparacion_mezcla for i in items_existentes]
        id_items_entrantes = [i['id_item_preparacion_mezcla'] for i in items_preparacion if i['id_item_preparacion_mezcla']!=None]
        id_items_eliminar = [i for i in id_items_existentes if i not in id_items_entrantes]
        items_eliminar = ItemsPreparacionMezcla.objects.filter(id_item_preparacion_mezcla__in=id_items_eliminar)
        
        valores_eliminados_detalles = [{'nombre' : i.id_bien_usado.nombre} for i in items_eliminar]

#----------------------------------------------------> VALIDACIONES DE LOS ITEMS INSERTADOS USADOS EN LA PREPARACION <----------------------------#
        aux_nro_posicion = []
        aux_valores_repetidos = []
        valores_creados_detalles = [] 
        aux_valores_repetidos = [i.id_bien_usado.id_bien for i in items_existentes]
        aux_nro_posicion = [i.nro_posicion for i in items_existentes]   
        for i in items_nuevos:
            instancia_bien = CatalogoBienes.objects.filter(id_bien=i['id_bien_usado']).first()
            instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=i['id_bien_usado'],id_vivero=instancia_preparacion.id_vivero).first()
                        
            # SE VALIDA LA EXISTENCIA DEL BIEN
            if not instancia_bien:
                raise ValidationError('El bien con número de posición ' + str(i['nro_posicion']) +  'no existe.')

            # SE VALIDA LA EXISTENCIA DEL BIEN EN EL INVENTARIO VIVERO
            if not instancia_bien_vivero:
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) +  'no tiene registros en el inventario del vivero.')
            
            # SE VALIDA QUE EL BIEN TENGA ENTRADAS
            if instancia_bien_vivero.cantidad_entrante == None or instancia_bien_vivero.cantidad_entrante == 0:
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) +  'no tiene entradas, por lo tanto su saldo es cero.')
            
            # SE VALIDA QUE EL BIEN SEA DEL TIPO INSUMO
            if instancia_bien.cod_tipo_elemento_vivero != "IN":
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) +  ' no es un insumo.')
            
            # SE VALIDA QUE EL BIEN USADO SEA UNICO DENTRO LA PREPARACION DE MEZCLA
            if int(i['id_bien_usado']) in aux_valores_repetidos:
                raise ValidationError('Error en el bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + '. No se puede ingresar dos veces un mismo bien dentro de una preparación de mezclas.')
            
            # SE VALIDA QUE EL NÚMERO DE POSICIÓN SEA ÚNICO
            if int(i['nro_posicion']) in aux_nro_posicion:
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' tiene un número de posición que ya existe.')
            
            # SE VALIDA QUE LA CANTIDAD DEL BIEN USADO SEA MAYOR QUE CERO
            if int(i['cantidad_usada']) <= 0:
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' tiene como cantidad de usada cero, la cantidad debe ser mayor que cero.')
            
            # SE VALIDA QUE HAYA SALDO DISPONIBLE
            saldo_disponible = UtilConservacion.get_cantidad_disponible_F(instancia_bien, instancia_bien_vivero)
            if int(i['cantidad_usada']) > saldo_disponible:
                raise ValidationError('En el bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' no tiene saldo disponible para suplir la cantidad usada.')
            
            # SE GUARDAN EL NÚMERO DE POSICIÓN Y EL ID DE BIEN EN LISTAS PARA VALIDAR SI SE REPITEN
            aux_nro_posicion.append(i['nro_posicion'])
            aux_valores_repetidos.append(i['id_bien_usado'])
            valores_creados_detalles.append({'nombre' : instancia_bien.nombre})
            
#----------------------------------------------------> VALIDACIONES DE LOS ITEMS A ACTUALIZAR USADOS EN LA PREPARACION <----------------------------#
        for i in items_actualizar:
            # SE VALIDA LA EXISTENCIA DE LA ITEM USADO EN LA PREPARACIÓN
            instancia_item_preparacion = ItemsPreparacionMezcla.objects.filter(id_item_preparacion_mezcla=i['id_item_preparacion_mezcla']).first()
            if not instancia_item_preparacion:
                raise ValidationError('El bien con número de posición ' + str(i['nro_posicion']) + ' no existe el registro de la preparación de la mezcla.')
            
            # SE VALIDA LA EXISTENCIA DEL BIEN USADO EN CATALOGO DE BIENES
            instancia_bien = CatalogoBienes.objects.filter(id_bien=instancia_item_preparacion.id_bien_usado.id_bien).first()
            if not instancia_bien:
                raise ValidationError('El bien con número de posición ' + str(i['nro_posicion']) + ' no existe registrado en el sistema como bien.')
            
            # SE VALIDA LA EXISTENCIA DEL BIEN USADO EN EL INVENTARIO DEL VIVERO
            instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=instancia_bien.id_bien,id_vivero=instancia_preparacion.id_vivero).first()
            if not instancia_bien_vivero:
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' no existe en el inventario del vivero.')
            
            # SE VALIDA QUE LA FECHA DE ACTUALIZACIÓN DE LA CANTIDAD USADA NO SEA SUPERIOR A DOS DÍAS DE ANTERIORIDAD
            if int(i['cantidad_usada']) != instancia_item_preparacion.cantidad_usada:
                fecha_posible = datetime.now() - timedelta(days=2)
                if instancia_preparacion.fecha_preparacion < fecha_posible:
                    raise ValidationError('No es posible actualizar una cantidad usada de una prepracación con más de dos días de anterioridad.')
                
                # SE VALIDA QUE EL SALDO DISPONIBLE SEA SUFICIENTE PARA SATISFACER LA CANTIDAD USADA POR LA QUE SE VA A REEMPLAZAR
                aux_cantidad = i['cantidad_usada'] - instancia_item_preparacion.cantidad_usada
                saldo_disponible = UtilConservacion.get_cantidad_disponible_F(instancia_bien, instancia_bien_vivero)
                saldo_disponible = saldo_disponible - aux_cantidad
                if saldo_disponible <= 0:
                    raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ', no tiene saldo disponible para cubrir la cantidad usada ingresada.')
                
            # SE VALIDA QUE LA CANTIDAD ACTUALIZADA NO SE VALIDE POR CERO
            if int(i['cantidad_usada']) <= 0:
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' tiene cantidad igual a cero, la cantidad debe ser mayor que cero.')
                       
#----------------------------------------------------> ACTUALIZACION DE LOS VALORES DEL INVENTARIO VIVEROS <----------------------------#
        # SE ACTUALIZA LA CANTIDAD ENTRANTE DE LA MEZCLA EN EL INVENTARIO DEL VIVERO
        instancia_mezcla_vivero.cantidad_entrante = instancia_mezcla_vivero.cantidad_entrante if instancia_mezcla_vivero.cantidad_entrante else 0
        aux_cantidad = info_preparacion['cantidad_creada'] - instancia_preparacion.cantidad_creada
        instancia_mezcla_vivero.cantidad_entrante = instancia_mezcla_vivero.cantidad_entrante + aux_cantidad
        instancia_mezcla_vivero.save()
        
        # SE RESTAN LAS CANTIDADES AL INVENTARIO VIVERO DE LOS ITEMS ELIMINADOS
        for i in items_eliminar:
            instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=i.id_bien_usado,id_vivero=instancia_preparacion.id_vivero).first()
            instancia_bien_vivero.cantidad_consumos_internos = instancia_bien_vivero.cantidad_consumos_internos if instancia_bien_vivero.cantidad_consumos_internos else 0
            instancia_bien_vivero.cantidad_consumos_internos = instancia_bien_vivero.cantidad_consumos_internos - i.cantidad_usada
            instancia_bien_vivero.save()    
            
        # SE ACTUALIZAN LAS CANTIDADES DE LOS ITEMS USADOS EN EL INVENTARIO VIVERO
        for i in items_preparacion:
            if i['id_item_preparacion_mezcla'] == None:
                instancia_bien = CatalogoBienes.objects.filter(id_bien=i['id_bien_usado']).first()
                instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=i['id_bien_usado'],id_vivero=instancia_preparacion.id_vivero).first()
                instancia_bien_vivero.cantidad_consumos_internos = instancia_bien_vivero.cantidad_consumos_internos if instancia_bien_vivero.cantidad_consumos_internos else 0
                instancia_bien_vivero.cantidad_consumos_internos = instancia_bien_vivero.cantidad_consumos_internos + i['cantidad_usada']
                instancia_bien_vivero.save()   
            elif i['id_item_preparacion_mezcla'] != None:
                instancia_item_preparacion = ItemsPreparacionMezcla.objects.filter(id_item_preparacion_mezcla=i['id_item_preparacion_mezcla']).first()
                instancia_bien = CatalogoBienes.objects.filter(id_bien=instancia_item_preparacion.id_bien_usado.id_bien).first()
                instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=instancia_item_preparacion.id_bien_usado,id_vivero=instancia_preparacion.id_vivero).first()
                instancia_bien_vivero.cantidad_consumos_internos = instancia_bien_vivero.cantidad_consumos_internos if instancia_bien_vivero.cantidad_consumos_internos else 0
                aux_cantidad = i['cantidad_usada'] - instancia_item_preparacion.cantidad_usada
                instancia_bien_vivero.cantidad_consumos_internos = instancia_bien_vivero.cantidad_consumos_internos + aux_cantidad
                instancia_bien_vivero.save()

#----------------------------------------------------> SE GUARDAN LOS VALORES DEL MAESTRO Y SE INSERTAN Y/O ACTUALIZAN Y/O ELIMININAN LOS ITEMS <----------------------------#

        # SE GUARDAN LOS DATOS ACTUALIZADOS DEL MAESTRO DE LA PREPARACIÓN
        instancia_preparacion.observaciones = info_preparacion['observaciones']
        instancia_preparacion.cantidad_creada = info_preparacion['cantidad_creada']
        instancia_preparacion.save()
        
        # SE BORRAN LOS ITEMS A ELIMINAR
        items_eliminar.delete()
        
        # SE ACTUALIZAN LOS ITEMS A ACTUALIZAR
        for i in items_actualizar:
            instancia_item_preparacion = ItemsPreparacionMezcla.objects.filter(id_item_preparacion_mezcla=i['id_item_preparacion_mezcla']).first()
            previous_instancia_item = copy.copy(instancia_item_preparacion)
            serializer_crear_items = self.serializador_actualizar_items(instancia_item_preparacion, data=i, many=False)
            serializer_crear_items.is_valid(raise_exception=True)
            serializer_crear_items.save()
            valores_actualizados_detalles.append({'descripcion': {'nombre' : instancia_item_preparacion.id_bien_usado.nombre},'previous':previous_instancia_item,'current':instancia_item_preparacion})
        
        # SE ASIGNA EL ID TRASLADO A LOS ITEMS A TRASLADAR
        for i in items_nuevos:
            i['id_preparacion_mezcla'] = instancia_preparacion.id_preparacion_mezcla
        
        # SE CREA EL REGISTRO EN LA TABLA ITEM_TRASLADOS
        serializer_crear_items = self.serializador_items_preparacion_mezclas(data=items_nuevos, many=True)
        serializer_crear_items.is_valid(raise_exception=True)
        serializer_crear_items.save()

#----------------------------------------------------> AUDITORIA MAESTRO DETALLE <----------------------------#
        
        # AUDITORIA MAESTRO DETALLE DE LA MEZCLA
        descripcion = {"id_vivero": str(instancia_preparacion.id_vivero), "consecutivo_preparacion": str(instancia_preparacion.consec_vivero_mezclas), "Id_mezcla": str(instancia_preparacion.id_mezcla.id_mezcla)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 58,
            "cod_permiso": "AC",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles,
            "valores_actualizados_detalles": valores_actualizados_detalles,
            "valores_eliminados_detalles": valores_eliminados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        return Response ({'success':True, 'detail':'Preparación de mezcla actualizada correctamente', 'data':"datos"}, status=status.HTTP_200_OK)
    
class AnularPreparacionMezclas(generics.UpdateAPIView):
    serializer_class = PreparacionMezclasSerializer
    queryset = PreparacionMezclas.objects.all()
    permission_classes = [IsAuthenticated]
    serializador_items_preparacion_mezclas = ItemsPreparacionMezclasSerializer
    
    def put(self, request, id_preparacion_anular):
        queryset = self.queryset
        datos_ingresados = request.data
        valores_eliminados_detalles = []
        
        preparacion_a_anular = queryset.filter(id_preparacion_mezcla=id_preparacion_anular).first()
        if not preparacion_a_anular:
            raise ValidationError('No se encontró ninguna preparación de mezcla con el id que ingresó')
        
        ultima_mezcla = queryset.filter(id_vivero=preparacion_a_anular.id_vivero,id_mezcla=preparacion_a_anular.id_mezcla).order_by('consec_vivero_mezclas').last()
        ultimo_consecutivo = 0 if not ultima_mezcla else ultima_mezcla.consec_vivero_mezclas
                
        if not preparacion_a_anular:
            raise ValidationError('No se encontró ninguna preparación de mezcla con el id que ingresó')
        
        if preparacion_a_anular.preparacion_anulada == True:
            raise ValidationError('Esta preparación ya fue anulada.')
        
        items_preparacion_a_anular = ItemsPreparacionMezcla.objects.filter(id_preparacion_mezcla=preparacion_a_anular.id_preparacion_mezcla)
        if not items_preparacion_a_anular:
            raise ValidationError('Esta preparación no registra items.')
        
        # SE OBTIENE LA ÚLTIMA BAJA REGISTRADA Y SE CONTRASTA CON EL NRO DE BAJA INGRESADO
        if preparacion_a_anular.consec_vivero_mezclas != ultimo_consecutivo:
            raise ValidationError('Solo es posible actualizar la última preparación de la mezcla.')
        
        # SE VALIDA LA FECHA
        fecha_posible = datetime.now() - timedelta(days=2)
        if preparacion_a_anular.fecha_preparacion < fecha_posible:
            raise ValidationError('No es posible anular una preparación de mezcla que tenga más de 2 días de anterioridad.')
        
        # SE VALIDA LA EXISTENCIA DE LA MEZCLA EN EL INVENTARIO VIVERO
        instancia_mezcla_vivero = InventarioViveros.objects.filter(id_mezcla=preparacion_a_anular.id_mezcla.id_mezcla,id_vivero=preparacion_a_anular.id_vivero).first()
        if not instancia_mezcla_vivero:
            raise ValidationError('No existe el registro de la mezcla en el inventario del vivero.')
        
        # SE VALIDA QUE EN CASO DE QUE SE DISMINUYA LA CANTIDAD CREADA DE LA MEZCLA, EL SALDO DISPONIBLE SUPLA LA CANTIDAD POR LA QUE SE ESTÁ ACTUALIZANDO
        instancia_mezcla_vivero.cantidad_entrante = instancia_mezcla_vivero.cantidad_entrante if instancia_mezcla_vivero.cantidad_entrante else 0
        instancia_mezcla_vivero.cantidad_consumos_internos = instancia_mezcla_vivero.cantidad_consumos_internos if instancia_mezcla_vivero.cantidad_consumos_internos else 0
        instancia_mezcla_vivero.cantidad_bajas = instancia_mezcla_vivero.cantidad_bajas if instancia_mezcla_vivero.cantidad_bajas else 0
        instancia_mezcla_vivero.cantidad_entrante = instancia_mezcla_vivero.cantidad_entrante - preparacion_a_anular.cantidad_creada
        saldo_disponible_mezcla = instancia_mezcla_vivero.cantidad_entrante -  instancia_mezcla_vivero.cantidad_consumos_internos - instancia_mezcla_vivero.cantidad_bajas
        if saldo_disponible_mezcla < 0:
            raise ValidationError('La cantidad a disminuir de la mezcla es mayor al saldo disponible.')
        elif saldo_disponible_mezcla == 0:
            instancia_mezcla_vivero.delete()
        elif saldo_disponible_mezcla > 0:
            instancia_mezcla_vivero.save()
             
        # SE RESTA LA CANTIDAD DE LOS ITEMS DE LA PREPARACIÓN AL INVENTARIO DE VIVERO
        for i in items_preparacion_a_anular:
            instancia_inventario_vivero = InventarioViveros.objects.filter(id_bien=i.id_bien_usado.id_bien, id_vivero=preparacion_a_anular.id_vivero).first()
            if not instancia_inventario_vivero:
                raise ValidationError('El bien con número de posición ' + str(i.nro_posicion) +  'no tiene registro en el inventario del vivero.')
            instancia_inventario_vivero.cantidad_consumos_internos = instancia_inventario_vivero.cantidad_consumos_internos if instancia_inventario_vivero.cantidad_consumos_internos else 0
            instancia_inventario_vivero.cantidad_consumos_internos = instancia_inventario_vivero.cantidad_consumos_internos - i.cantidad_usada
            instancia_inventario_vivero.save()   
        
        # SE BORRAN LOS REGISTROS DE LA TABLA ITEMS_PREPARACIÓN
        valores_eliminados_detalles = [{'nombre' : i.id_bien_usado.nombre} for i in items_preparacion_a_anular]
        items_preparacion_a_anular.delete()
        preparacion_a_anular.preparacion_anulada = True
        preparacion_a_anular.fecha_anulacion = datetime.now()
        preparacion_a_anular.id_persona_anula = Personas.objects.filter(id_persona=request.user.persona.id_persona).first()
        preparacion_a_anular.justificacion_anulacion = datos_ingresados['justificacion_anulacion']
        preparacion_a_anular.save()
        
        # AUDITORIA MAESTRO DETALLE DE DESPACHO
        descripcion = {"id_vivero": str(preparacion_a_anular.id_vivero), "consecutivo_preparacion": str(preparacion_a_anular.consec_vivero_mezclas), "Id_mezcla": str(preparacion_a_anular.id_mezcla.id_mezcla)}
        direccion = Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 58,
            "cod_permiso": "AN",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_eliminados_detalles": valores_eliminados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        return Response({'succes' : True, 'detail' : 'Preparación anualada con éxito'}, status=status.HTTP_200_OK)
    
class BusquedaAvanzadaPreparacionesMezclas(generics.ListAPIView):
    serializer_class = PreparacionMezclasSerializer
    queryset = PreparacionMezclas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        filter = {}
        
        for key, value in request.query_params.items():
            if key in ['id_vivero', 'id_mezcla']:
                if value != '' and value != None:
                    filter[key] = value
            elif key in ['nombre_mezcla']:
                if value != '' and value != None:
                    filter['id_mezcla__nombre__icontains'] = value

        if not filter:
            raise ValidationError('No ingresó ningún parámetro de búsqueda.')
        else:
            resultados_busqueda = PreparacionMezclas.objects.filter(**filter)
            serializer = self.serializer_class(resultados_busqueda, many=True)
        
        return Response({'succes':True, 'detail':'Ok', 'data':serializer.data}, status=status.HTTP_200_OK)

class GetPreparacionById(generics.ListAPIView):
    serializer_class = PreparacionMezclasSerializer
    queryset = PreparacionMezclas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id_preparacion):
        queryset = self.queryset.all()
        instancia_preparacion = queryset.filter(id_preparacion_mezcla=id_preparacion).first()
        
        if not instancia_preparacion:
            raise ValidationError('No se encontró ninguna preparación con el id ingresado.')
        
        # SE LE AGRAGA EL SALDO DISPONIBLE AL RESULTADO DE BUSQUEDA
        serializer = self.serializer_class(instancia_preparacion, many=False)
        
        return Response ({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data':serializer.data}, status=status.HTTP_200_OK)
    
