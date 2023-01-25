from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen, ItemEntradaAlmacen
from almacen.serializers.bienes_serializers import CatalogoBienesSerializer
from almacen.serializers.despachos_serializers import SerializersDespachoConsumo, SerializersItemDespachoConsumo, SerializersSolicitudesConsumibles, SerializersItemsSolicitudConsumible, SearchBienInventarioSerializer
from rest_framework import generics,status
from rest_framework.response import Response
from seguridad.models import Personas, User
from rest_framework.decorators import api_view
from seguridad.utils import Util
from almacen.utils import UtilAlmacen
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum,F
from datetime import datetime, date,timedelta
import copy
import json
from almacen.serializers.despachos_viveros_serializers import (
    SerializersDespachoViverosConsumo,
    SerializersDespachoConsumoViverosActualizar,
    SerializersItemDespachoViverosConsumo,
    SerializersDespachoEntrantes,
    SerializersItemsDespachoEntrantes
)
from almacen.models.solicitudes_models import (
    SolicitudesConsumibles, 
    DespachoConsumo, 
    ItemDespachoConsumo, 
    SolicitudesConsumibles, 
    ItemsSolicitudConsumible
)
from seguridad.models import (
    Personas,
    User,
    ClasesTerceroPersona
)
from almacen.models.organigrama_models import (
    UnidadesOrganizacionales,
    NivelesOrganigrama
)
from conservacion.models.despachos_models import (
    DespachoEntrantes,
    ItemsDespachoEntrante
)
from almacen.models.generics_models import (
    UnidadesMedida,
    Bodegas
)
from almacen.models.inventario_models import (
    Inventario
)
from almacen.serializers.solicitudes_serialiers import ( 
    CrearSolicitudesPostSerializer,
    CrearItemsSolicitudConsumiblePostSerializer
    )
from seguridad.serializers.personas_serializers import PersonasSerializer

class CreateDespachoMaestroVivero(generics.UpdateAPIView):
    serializer_class = SerializersDespachoViverosConsumo
    queryset = DespachoConsumo
    serializer_item_consumo = SerializersItemDespachoViverosConsumo
    serializer_despacho_entrante = SerializersDespachoEntrantes
    serializer_items_despacho_entrante = SerializersItemsDespachoEntrantes
    
    def put(self, request):
        datos_ingresados = request.data
        user_logeado = request.user
        info_despacho = json.loads(datos_ingresados['info_despacho'])
        items_despacho = json.loads(datos_ingresados['items_despacho'])
        info_despacho['ruta_archivo_doc_con_recibido'] = request.FILES.get('ruta_archivo_doc_con_recibido')
        #Validaciones primarias
        if str(user_logeado) == 'AnonymousUser':
            return Response({'success':False,'detail':'Esta solicitud solo la puede ejecutar un usuario logueado'},status=status.HTTP_404_NOT_FOUND)
        if info_despacho['es_despacho_conservacion'] != True:
            return Response({'success':False,'detail':'En este servicio no se pueden procesar despachos que no sean de vivero, además verfique el campo (es_despacho_conservacion), este debe ser True o False'},status=status.HTTP_404_NOT_FOUND)
        if len(info_despacho['motivo']) > 255:
            return Response({'success':False,'detail':'El motivo debe tener como máximo 255 caracteres'},status=status.HTTP_404_NOT_FOUND)
        #Validaciones de la solicitud
        instancia_solicitud = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=info_despacho['id_solicitud_consumo']).first()
        if not instancia_solicitud:
            return Response({'success':False,'detail':'Debe ingresar un id de solicitud válido'},status=status.HTTP_404_NOT_FOUND)
        if instancia_solicitud.solicitud_abierta == False or instancia_solicitud.estado_aprobacion_responsable != 'A':
            return Response({'success':False,'detail':'La solicitud a despachar debe de estar aprobada por el funcionario responsable y no debe de estar cerrada'},status=status.HTTP_404_NOT_FOUND)
        if instancia_solicitud.es_solicitud_de_conservacion != True:
            return Response({'success':False,'detail':'La solicitud que ingresó para despachar no es de viveros'},status=status.HTTP_404_NOT_FOUND)
        #Asignación de fecha de registro
        info_despacho['fecha_registro'] = datetime.now()
        #Se valida que la fecha de la solicitud no sea inferior a (fecha_actual - 8 días) ni superior a la actual
        fecha_despacho = datetime.strptime(info_despacho.get('fecha_despacho'), "%Y-%m-%d %H:%M:%S")
        aux_validacion_fechas = info_despacho['fecha_registro'] - fecha_despacho
        if int(aux_validacion_fechas.days) > 8 or int(aux_validacion_fechas.days) < 0:
            return Response({'success':False,'detail':'La fecha ingresada no es permita dentro de los parametros existentes'},status=status.HTTP_404_NOT_FOUND)
        #Se valida que la fecha de aprobación de la solicitud sea inferior a la fecha de despacho
        fecha_aprobacion_solicitud = instancia_solicitud.fecha_aprobacion_responsable
        if fecha_aprobacion_solicitud == None:
            return Response({'success':False,'detail':'La solicitud que desea despachar no tiene registrada fecha de aprobación del responsable'},status=status.HTTP_404_NOT_FOUND)
        if fecha_despacho <= fecha_aprobacion_solicitud:
            return Response({'success':False,'detail':'La fecha de despacho debe ser mayor o igual a la fecha de aprobación de la solicitud'},status=status.HTTP_404_NOT_FOUND)
        #Consulta y asignación de los campos que se repiten con solicitudes de bienes de consumos
        info_despacho['numero_solicitud_por_tipo'] = instancia_solicitud.nro_solicitud_por_tipo
        info_despacho['fecha_solicitud'] = instancia_solicitud.fecha_solicitud
        info_despacho['id_persona_solicita'] = instancia_solicitud.id_persona_solicita.id_persona
        info_despacho['id_unidad_para_la_que_solicita'] = instancia_solicitud.id_unidad_para_la_que_solicita.id_unidad_organizacional
        info_despacho['id_funcionario_responsable_unidad'] = instancia_solicitud.id_funcionario_responsable_unidad.id_persona
        #Asignación de persona que despacha
        info_despacho['id_persona_despacha'] = user_logeado.persona.id_persona
        #Asignacion de número de despacho
        despachos_existentes = DespachoConsumo.objects.all()
        if despachos_existentes:
            numero_despachos = [i.numero_despacho_consumo for i in despachos_existentes]
            info_despacho['numero_despacho_consumo'] = max(numero_despachos) + 1
        else:
            info_despacho['numero_despacho_consumo'] = 1
        # SE OBTIENEN TODOS LOS ITEMS DE LA SOLICITUD PARA LUEGO VALIDAR QUE LOS ITEMS DESPACHADOS ESTÉN DENTRO DE LA SOLICITUD
        items_solicitud = ItemsSolicitudConsumible.objects.filter(id_solicitud_consumibles=info_despacho['id_solicitud_consumo'])
        if not items_solicitud:
            return Response({'success':False,'detail':'La solicitud que quiere despachar no tiene items, por favor añada items a la solicitud para poderla despachar' },status=status.HTTP_404_NOT_FOUND)
        id_items_solicitud = [i.id_bien.id_bien for i in items_solicitud]
        # SE VALIDA QUE EL NUMERO DE POSICION SEA UNICO
        nro_posicion_items = [i['numero_posicion_despacho'] for i in items_despacho]
        if len(nro_posicion_items) != len(set(nro_posicion_items)):
            return Response({'success':False,'detail':'El número de posición debe ser único' },status=status.HTTP_404_NOT_FOUND)
        # VALIDACIONES EN ITEMS DEL DESPACHO
        aux_validacion_bienes_despachados_repetidos = []
        aux_validacion_bienes_despachados_contra_solicitados = []
        axu_validacion_cantidades_despachadas_total = []
        valores_creados_detalles = []
        aux_validacion_bienes_repetidos = {}
        aux_validacion_unidades_dic = {}
        for i in items_despacho:
            bien_solicitado = i.get('id_bien_solicitado')
            instancia_entrada = EntradasAlmacen.objects.filter(id_entrada_almacen=i.get('id_entrada_almacen_bien')).first()
            if not instancia_entrada:
                return Response({'success':False,'detail':'En el número de posición del despacho (' + str(i['numero_posicion_despacho']) + '), no existe el id_entrada_bien ingresado'},status=status.HTTP_404_NOT_FOUND)
            if (instancia_entrada.id_tipo_entrada.nombre != "Donación") and (instancia_entrada.id_tipo_entrada.nombre != "Resarcimiento") and (instancia_entrada.id_tipo_entrada.nombre != "Compensación"):
                return Response({'success':False,'detail':'En el número de posición del despacho (' + str(i['numero_posicion_despacho']) + '), el tipo entrada de la entrada ingresada no es correcto para un despacho de bienes de consumo de solicitables por vivero'},status=status.HTTP_404_NOT_FOUND)
            instancia_item_entrada_alamacen = ItemEntradaAlmacen.objects.filter(id_bien=i.get('id_bien_despachado'), id_entrada_almacen=i.get('id_entrada_almacen_bien')).first()
            if not instancia_item_entrada_alamacen:
                return Response({'success':False,'detail':'En el número de posición del despacho (' + str(i['numero_posicion_despacho']) + '), no existe el id_entrada_bien ingresado'},status=status.HTTP_404_NOT_FOUND)
            if (bien_solicitado not in id_items_solicitud):
                return Response({'success':False,'detail':'En el número de posición del despacho (' + str(i['numero_posicion_despacho']) + '), el bien ingresado no está dentro de la entrada seleccionada'},status=status.HTTP_404_NOT_FOUND)
            if bien_solicitado == None:
                return Response({'success':False,'detail':'Debe ingresar un id de un bien solicitado'},status=status.HTTP_404_NOT_FOUND)
            bien_solicitado_instancia = CatalogoBienes.objects.filter(id_bien = i['id_bien_solicitado']).first()
            if not bien_solicitado_instancia:
                return Response({'success':False,'detail':'El bien solicitado (' + i['id_bien_solicitado'] + ') no existe' },status=status.HTTP_404_NOT_FOUND)
            if bien_solicitado_instancia.nivel_jerarquico > 5 or bien_solicitado_instancia.nivel_jerarquico < 2:
                return Response({'success':False,'detail':'Error en el numero_posicion (' + str(i['numero_posicion_despacho']) + '). El bien solicitado (' + bien_solicitado_instancia.nombre + ') no es de nivel 2 al 5' },status=status.HTTP_404_NOT_FOUND)
            if bien_solicitado_instancia.cod_tipo_bien != 'C':
                return Response({'success':False,'detail':'El bien (' + bien_solicitado_instancia.nombre + ') no es de consumo' },status=status.HTTP_404_NOT_FOUND)
            item_solicitado_instancia = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=info_despacho['id_solicitud_consumo']) & Q(id_bien=i['id_bien_solicitado'])).first()
            if item_solicitado_instancia.cantidad != i['cantidad_solicitada'] or item_solicitado_instancia.id_unidad_medida.id_unidad_medida != i['id_unidad_medida_solicitada']:
                return Response({'success':False,'detail':'Error en el numero_posicion (' + str(i['numero_posicion_despacho']) + ') del despacho. La cantidad solicitada o la unidad de medida solicitada no corresponde a las registrada en la solicitud' },status=status.HTTP_404_NOT_FOUND)
            # VALIDACION 94:
            if i['cantidad_despachada'] == 0:
                if i['id_bien_despachado'] != 0:
                    return Response({'success':False,'detail':'Si la cantidad a despachar de un bien solicitado es 0, en el campo (id_bien_despachado) debe ingresar 0' },status=status.HTTP_404_NOT_FOUND)
                if i['id_bodega'] != 0:
                    return Response({'success':False,'detail':'Si la cantidad a despachar de un bien solicitado es 0, en el campo (id_bodega) debe ingresar 0' },status=status.HTTP_404_NOT_FOUND)
                if i['observacion'] != 0:
                    return Response({'success':False,'detail':'Si la cantidad a despachar de un bien solicitado es 0, en el campo (observacion) debe ingresar 0' },status=status.HTTP_404_NOT_FOUND)
                    
                if i['id_bien_despachado'] == 0:
                    i['id_bien_despachado'] = None
                if i['id_bodega'] == 0:
                    i['id_bodega'] = None
                if i['observacion'] == 0:
                    i['observacion'] = 0

            if i['cantidad_despachada'] > 0:
                bien_despachado = i.get('id_bien_despachado')
                if not bien_despachado:
                    return Response({'success':False,'detail':'Debe ingresar un bien despachado' },status=status.HTTP_404_NOT_FOUND)
                bien_despachado_instancia = CatalogoBienes.objects.filter(id_bien=bien_despachado).first()
                if not bien_despachado_instancia:
                    return Response({'success':False,'detail':'Debe ingresar un id_bien válido en el bien despachado' },status=status.HTTP_404_NOT_FOUND)
                nivel_bien_despachado = int(bien_despachado_instancia.nivel_jerarquico)
                # SE VALIDA QUE EL BIEN DESPACHADO PERTENESCA A LA LINEA DEL BIEN SOLICITADO
                cont = nivel_bien_despachado
                arreglo_id_bienes_ancestros = []
                while cont>0:
                    arreglo_id_bienes_ancestros.append(bien_despachado_instancia.id_bien)
                    if bien_despachado_instancia.nivel_jerarquico > 1:
                        bien_despachado_instancia = CatalogoBienes.objects.filter(id_bien=bien_despachado_instancia.id_bien_padre.id_bien).first()
                        if not bien_despachado_instancia:
                            return Response({'success':False,'detail':'Uno de los bienes no tiene padre' },status=status.HTTP_404_NOT_FOUND)
                        nivel_bien_despachado = int(bien_despachado_instancia.nivel_jerarquico)
                    cont -= 1
                # SE VALIDA QUE EL BIEN DESPACHADO SEA DESENDIENTE DEL BIEN SOLICITADO
                if (bien_solicitado_instancia.id_bien_padre.id_bien not in arreglo_id_bienes_ancestros):
                    return Response({'success':False,'detail':'En el número de posición (' + str(i['numero_posicion_despacho']) + ') el bien solicitado no es de la misma linea del bien despachado' },status=status.HTTP_404_NOT_FOUND)
                bodega_solicita = i.get('id_bodega')
                if bodega_solicita == None:
                    return Response({'success':False,'detail':'Debe ingresar un id de bodega válido'},status=status.HTTP_404_NOT_FOUND)
                instancia_bodega_solcitud = Bodegas.objects.filter(id_bodega = i['id_bodega']).first()
                if not instancia_bodega_solcitud:
                    return Response({'success':False,'detail':'El id de bodega no existe' },status=status.HTTP_404_NOT_FOUND)
                observaciones = i.get('observacion')
                if observaciones == None:
                    return Response({'success':False,'detail':'El JSON debe contener un campo (observaciones)' },status=status.HTTP_404_NOT_FOUND)
                if len(observaciones) > 30:
                    return Response({'success':False,'detail':'La observacion solo puede contener hasta 30 caracteres' },status=status.HTTP_404_NOT_FOUND)
                # ESTO SE USA EN LA "VALIDACION 93" SE CREAN LAS CONDICIONES PARA LA VALIDACIÓN DE LA CANTIDAD DESPACHADA NO SUPERE LA SOLICITADA SI LAS UNIDADES SON IGUALES
                aux_validacion_unidades_solicitado = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=info_despacho['id_solicitud_consumo']) & Q(id_bien=i['id_bien_solicitado'])).first()
                aux_validacion_unidades_despachado = CatalogoBienes.objects.filter(Q(id_bien=i['id_bien_despachado'])).first()
                if aux_validacion_unidades_solicitado.id_bien.id_unidad_medida.nombre == aux_validacion_unidades_despachado.id_unidad_medida.nombre:
                    if i['cantidad_despachada'] > aux_validacion_unidades_solicitado.cantidad:
                        return Response({'success':False,'detail':'Una de las cantidades despachadas supera la cantidad solicitada' },status=status.HTTP_404_NOT_FOUND)
                    if not aux_validacion_bienes_repetidos.get(str(i['id_bien_solicitado'])):
                        aux_validacion_bienes_repetidos[str(i['id_bien_solicitado'])] = [i['cantidad_despachada']]
                    else:
                        aux_validacion_bienes_repetidos[str(i['id_bien_solicitado'])].append(i['cantidad_despachada'])
                    aux_validacion_unidades_dic[str(i['id_bien_solicitado'])] = True
                else:
                    aux_validacion_unidades_dic[str(i['id_bien_solicitado'])] = False
                # VALIDACION 95: SE VALIDA LA EXISTENCIA DEL BIEN EN LA TABLA INVENTARIO (POR BODEGA)
                instancia_inventario_auxiliar = Inventario.objects.filter(Q(id_bien=i['id_bien_despachado'])&Q(id_bodega=i['id_bodega'])).first()
                if not instancia_inventario_auxiliar:
                    return Response({'success':False,'detail':'Por favor verifique la existencia del bien en la bodega, o la existencia del bien en la tabla inventario' },status=status.HTTP_404_NOT_FOUND)
                valores_creados_detalles.append({'nombre' : instancia_inventario_auxiliar.id_bien.nombre})
                #VALIDACION 96: SE VALIDA LAS CANTIDADES POSITIVAS DEL BIEN EN LA FECHA DEL DESPACHO
                cantidad_disponible = UtilAlmacen.get_cantidad_disponible(i['id_bien_despachado'], i['id_bodega'], fecha_despacho)
                if i['cantidad_despachada'] > cantidad_disponible:
                    return Response({'success':False,'detail':'La cantidad disponible del bien (' + bien_despachado_instancia.nombre + ') es inferior a la cantidad a despachar' },status=status.HTTP_404_NOT_FOUND)
                cantidad_por_distribuir = UtilAlmacen.get_cantidad_por_distribuir(i['id_bien_despachado'], i['id_entrada_almacen_bien'], fecha_despacho)
                if i['cantidad_despachada'] > cantidad_por_distribuir:
                    return Response({'success':False,'detail':'La cantidad por distribuir de la entrada que intenta despachar es insuficiente en el nro posición (' + str(i['numero_posicion_despacho']) + ')' },status=status.HTTP_404_NOT_FOUND)
                items_despachados_aux_val_97 = ItemDespachoConsumo.objects.filter(id_bien_despachado=i['id_bien_despachado'], id_despacho_consumo__fecha_despacho__gte=info_despacho['fecha_despacho'])
                if items_despachados_aux_val_97:
                    return Response({'success':False, 'detail':'El bien tiene despachos o entregas posteriores a la fecha de despacho elegida', 'data': []}, status=status.HTTP_403_FORBIDDEN)
                
            # VALIDACION 90: SE VALIDA QUE UN BIEN DESPACHADO NO SE REPITA DENTRO DEL MISMO DESPACHO
            if [i['id_bien_solicitado'], i['id_bien_despachado'], i['id_bodega']] in aux_validacion_bienes_despachados_repetidos:
                return Response({'success':False,'detail':'Error en los bienes despachados, no se puede despachar el mismo bien varias veces dentro de un despacho, elimine los bienes despachados repetidos' },status=status.HTTP_404_NOT_FOUND)
            # ESTO SE USA PARA LA "VALIDACION 90"
            aux_validacion_bienes_despachados_repetidos.append([i['id_bien_solicitado'], i['id_bien_despachado'], i['id_bodega']])
            # ESTO SE USA PARA LA "VALIDACION 91"
            aux_validacion_bienes_despachados_contra_solicitados.append(i['id_bien_solicitado'])
            # ESTO SE USA PARA LA "VALIDACION 92"
            axu_validacion_cantidades_despachadas_total.append(i['cantidad_despachada'])
            
        # VALIDACION 91: SE VALIDA QUE TODOS LOS BIENES SOLICITUADOS SE ENCUENTREN DENTRO DE LA SOLICITUD
        if len(items_solicitud) != len(set(aux_validacion_bienes_despachados_contra_solicitados)):
            return Response({'success':False,'detail':'Error en los bienes despachados, se deben despachar cada uno de los bienes solicitados, si no desea despachar alguno de los bienes solicitados ingrese cantidad despachada en 0' },status=status.HTTP_404_NOT_FOUND)
        # VALIDACION 92: SE VALIDA QUE DENTRO DE LA SOLICITUD SE DESPACHE AL MENOS 1 BIEN, NO ES POSIBLE DESPACHAR TODO EN 0 
        axu_validacion_cantidades_despachadas_total = sum(axu_validacion_cantidades_despachadas_total)
        if axu_validacion_cantidades_despachadas_total < 1:
            return Response({'success':False,'detail':'Debe despachar como mínimo una unidad de los bienes en la solicitud, si quiere cerrar la solicitud porque no hay stock disponible de ningún item por favor diríjase al módulo de cierre de solicitud por inexistencia' },status=status.HTTP_404_NOT_FOUND)
        # VALIDACION 93: SE VALIDAN LAS CANTIDADES SI TIENEN LA MISMA UNIDAD
        for key, value in aux_validacion_bienes_repetidos.items():
            aux_validacion_bienes_repetidos[key] = sum(value)
            aux_local_uno = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=info_despacho['id_solicitud_consumo']) & Q(id_bien=int(key))).first()
            if int(aux_validacion_bienes_repetidos[key]) > aux_local_uno.cantidad:
                return Response({'success':False,'detail':'Una de las cantidades despachadas supera la cantidad solicitada' },status=status.HTTP_404_NOT_FOUND)
 
        serializer = self.serializer_class(data=info_despacho)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        despacho_creado = DespachoConsumo.objects.filter(Q(id_solicitud_consumo=info_despacho['id_solicitud_consumo']) & Q(numero_despacho_consumo=info_despacho['numero_despacho_consumo'])).first()
        
        # SE ASIGNA EL ID DEL DESPACHO A LOS ITEMS DEL DESPACHO
        for i in items_despacho:
            i['id_despacho_consumo'] = despacho_creado.id_despacho_consumo
        
        serializer_items = self.serializer_item_consumo(data=items_despacho, many=True)
        serializer_items.is_valid(raise_exception=True)
        serializer_items.save()
        # INSERT EN LA TABLA INVENTARIO
        for i in items_despacho:
            inventario_instancia = Inventario.objects.filter(Q(id_bien=i['id_bien_despachado'])&Q(id_bodega=i['id_bodega'])).first()
            aux_suma = inventario_instancia.cantidad_saliente_consumo
            if aux_suma == None:
                aux_suma = 0
            inventario_instancia.cantidad_saliente_consumo = int(aux_suma) + int(i['cantidad_despachada'])
            inventario_instancia.save()
        
        # INSERT EN LA TABLA SOLICITUDES DE CONSUMIBLES
        despacho_creado = DespachoConsumo.objects.filter(Q(id_solicitud_consumo=info_despacho['id_solicitud_consumo']) & Q(numero_despacho_consumo=info_despacho['numero_despacho_consumo'])).first()
        instancia_solicitud.id_despacho_consumo = despacho_creado.id_despacho_consumo
        instancia_solicitud.fecha_cierre_solicitud = despacho_creado.fecha_despacho
        instancia_solicitud.gestionada_almacen = True
        instancia_solicitud.solicitud_abierta = False
        instancia_solicitud.save()
        
        # INSERT EN LAS TABLAS DespachoEntrantes, ItemsDespachoEntrante
        despacho_entrantes = {}
        despacho_entrantes['id_despacho_consumo_alm'] = despacho_creado.id_despacho_consumo
        despacho_entrantes['fecha_ingreso'] = despacho_creado.fecha_despacho
        despacho_entrantes['distribucion_confirmada'] = False
        despacho_entrantes['fecha_confirmacion_distribucion'] = None
        despacho_entrantes['observacion_distribucion'] = None
        despacho_entrantes['id_persona_distribuye'] = None

        SerializersDespachoEntrantes = self.serializer_despacho_entrante(data=despacho_entrantes, many=False)
        SerializersDespachoEntrantes.is_valid(raise_exception=True)
        SerializersDespachoEntrantes.save()
        
        instancia_despacho_entrante = DespachoEntrantes.objects.filter(id_despacho_consumo_alm=despacho_creado.id_despacho_consumo).first()
        items_despacho_entrante_lista = []
        aux_validacion = []
        repetidos_items_despacho_entrante_lista = []
        carry_items_despacho_entrante_lista = []
        cont = 0
        for i in items_despacho:
            items_despacho_entrante = {}
            aux_validacion = [i['id_bien_despachado'], i['id_entrada_almacen_bien']]

            if aux_validacion in repetidos_items_despacho_entrante_lista:
                carry_items_despacho_entrante_lista.append([i['id_bien_despachado'], i['id_entrada_almacen_bien'], i['cantidad_despachada'], cont])
                cont = cont + 1
            else:
                items_despacho_entrante['id_despacho_entrante'] = instancia_despacho_entrante.id_despacho_entrante
                items_despacho_entrante['id_bien'] = i['id_bien_despachado']
                items_despacho_entrante['id_entrada_alm_del_bien'] = i['id_entrada_almacen_bien']
                items_despacho_entrante['fecha_ingreso'] = despacho_creado.fecha_despacho
                items_despacho_entrante['cantidad_entrante'] = i['cantidad_despachada']
                items_despacho_entrante['cantidad_distribuida'] = 0
                items_despacho_entrante['observacion'] = i['observacion']
                items_despacho_entrante_lista.append(items_despacho_entrante)
                repetidos_items_despacho_entrante_lista.append([i['id_bien_despachado'], i['id_entrada_almacen_bien']])
                
        SerializersItemsDespachoEntrantes = self.serializer_items_despacho_entrante(data=items_despacho_entrante_lista, many=True)
        SerializersItemsDespachoEntrantes.is_valid(raise_exception=True)
        SerializersItemsDespachoEntrantes.save()
        
        for i in carry_items_despacho_entrante_lista:
            instancia_items_despacho_entrante = ItemsDespachoEntrante.objects.filter(id_bien=i[0], id_entrada_alm_del_bien=i[1],id_despacho_entrante=instancia_despacho_entrante.id_despacho_entrante).first()
            instancia_items_despacho_entrante.cantidad_entrante = instancia_items_despacho_entrante.cantidad_entrante + i[2]
            instancia_items_despacho_entrante.save()
            
        # AUDITORIA MAESTRO DETALLE DE DESPACHO
        descripcion = {"numero_despacho_consumo": str(info_despacho['numero_despacho_consumo']), "es_despacho_conservacion": "true", "fecha_despacho": str(info_despacho['fecha_despacho'])}
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
        return Response({'success':True,'detail':'Despacho creado con éxito', 'Numero despacho' : info_despacho["numero_despacho_consumo"]},status=status.HTTP_200_OK)

class ActualizarDespachoConsumo(generics.UpdateAPIView):
    serializer_class = SerializersDespachoConsumoViverosActualizar
    queryset=DespachoConsumo.objects.all()
    serializer_item_consumo = SerializersItemDespachoViverosConsumo
    serializer_items_despacho_entrante = SerializersItemsDespachoEntrantes
    
    def put(self, request):
        datos_ingresados = request.data
        user_logeado = request.user
        info_despacho = json.loads(datos_ingresados['info_despacho'])
        items_despacho = json.loads(datos_ingresados['items_despacho'])
        info_despacho['ruta_archivo_doc_con_recibido'] = request.FILES.get('ruta_archivo_doc_con_recibido')

        # VALIDACION 0: SE VALIDA EL QUE EL USUARIO ESTÉ LOGUEADO
        if str(user_logeado) == 'AnonymousUser':
            return Response({'success':False,'detail':'Esta solicitud solo la puede ejecutar un usuario logueado'},status=status.HTTP_404_NOT_FOUND)
        # VALIDACION 1: SE VALIDA LA LONGITUD DE LA CADENA 'MOTIVO'
        if len(info_despacho['motivo']) > 255:
            return Response({'success':False,'detail':'El motivo debe tener como máximo 255 caracteres'},status=status.HTTP_404_NOT_FOUND)
        
        # SE INSTANCIAN ALGUNAS TABLAS QUE SE VAN A TOCAR
        despacho_maestro_instancia = DespachoConsumo.objects.filter(id_despacho_consumo=info_despacho['id_despacho_consumo']).first()
        if not despacho_maestro_instancia:
            return Response({'success':False,'detail':'Ingrese un id de despacho de bienes de consumo válido' },status=status.HTTP_404_NOT_FOUND)
        items_despacho_instancia = ItemDespachoConsumo.objects.filter(id_despacho_consumo=despacho_maestro_instancia.id_despacho_consumo)
        if not items_despacho_instancia:
            return Response({'success':False,'detail':'No es posible actualizar el despacho debido a que este no tiene items asociados' },status=status.HTTP_404_NOT_FOUND)
        solicitud_del_despacho_instancia = SolicitudesConsumibles.objects.filter(id_despacho_consumo=despacho_maestro_instancia.id_despacho_consumo).first()
        if not solicitud_del_despacho_instancia:
            return Response({'success':False,'detail':'Por favor verifique que la solicitud se haya despachado anteriormente' },status=status.HTTP_404_NOT_FOUND)
        items_solcitud_instancia = ItemsSolicitudConsumible.objects.filter(id_solicitud_consumibles=solicitud_del_despacho_instancia.id_solicitud_consumibles)
        if not items_solcitud_instancia:
            return Response({'success':False,'detail':'La solicitud que quiere despachar no tiene items, por favor añada items a la solicitud para poderla despachar' },status=status.HTTP_404_NOT_FOUND)
        despacho_entrante_instancia = DespachoEntrantes.objects.filter(id_despacho_consumo_alm=despacho_maestro_instancia.id_despacho_consumo).first()
        if despacho_entrante_instancia.id_persona_distribuye != None:
            return Response({'success':False,'detail':'Este despacho no se puede actualizar debido a que ya tiene distribuciones de vivero' },status=status.HTTP_404_NOT_FOUND)
        # VALIDACION 2: SE VALIDA QUE LA ACTUALIZACIÓN NO SE REALIZA EN UNA FECHA POSTERIOR A 45 DÍAS DESPUES DEL DESPACHO
        fecha_despacho = despacho_maestro_instancia.fecha_despacho
        aux_validacion_fechas = datetime.now() - fecha_despacho
        if int(aux_validacion_fechas.days) > 45:
            return Response({'success':False,'detail':'No puede actualizar un despacho con fecha anterior a 45 días respecto a la actual'},status=status.HTTP_404_NOT_FOUND)
        
         # SE OBTIENEN TODOS LOS ITEMS DE LA SOLICITUD PARA LUEGO VALIDAR QUE LOS ITEMS DESPACHADOS ESTÉN DENTRO DE LA SOLICITUD
        id_items_solicitud = [i.id_bien.id_bien for i in items_solcitud_instancia]
        # SE OBTIENEN TODOS LOS ITEMS DEL DESPACHO PARA LA VALIDACION 4
        id_items_despacho = [i.id_item_despacho_consumo for i in items_despacho_instancia]
        
        # SE VALIDA QUE EL NUMERO DE POSICION SEA UNICO
        nro_posicion_items_entrantes = [i['numero_posicion_despacho'] for i in items_despacho if i.get('numero_posicion_despacho')]
        nro_posicion_items_existentes = [i.numero_posicion_despacho for i in items_despacho_instancia]
        nro_posicion_total_items = nro_posicion_items_entrantes + nro_posicion_items_existentes
        if len(nro_posicion_total_items) != len(set(nro_posicion_total_items)):
            return Response({'success':False,'detail':'El número de posición debe ser único' },status=status.HTTP_404_NOT_FOUND)
        aux_validacion_bienes_despachados_repetidos = []
        valores_creados_detalles = []
        aux_validacion_bienes_repetidos = {}
        aux_validacion_unidades_dic = {}
        valores_actualizados__solicitud = []
        aux_dic_mod_inventario = []
        items_a_actualizar = []
        items_a_crear = []
        valores_actualizados_detalles = []
        # VALIDACIONES DE LOS ITEMS
        for i in items_despacho:
            id_item_a_despachar = i.get('id_item_despacho_consumo')
#----------># VALIDACIONES DE ITEMS ACTUALIZADOS
            if id_item_a_despachar:
                # VALIDACION 4: SE VALIDA LA EXISTENCIA DEL ITEM A ACTUIALIZAR EN LOS ITEMS PREVIAMENTE REGISTRADOS
                if id_item_a_despachar not in id_items_despacho:
                    return Response({'success':False,'detail':'Uno de los ids que ingresó de los items a despachar que desea actualizar no pertenece al despacho que está actualizando'},status=status.HTTP_404_NOT_FOUND)
                # VALIDACION 5:
                instancia_item_a_actualizar_aux_5 = ItemDespachoConsumo.objects.filter(id_item_despacho_consumo=id_item_a_despachar).first()
                valores_actualizados__solicitud.append(instancia_item_a_actualizar_aux_5.id_bien_solicitado.id_bien)
                ajuste_cantidad_despachada = i.get('cantidad_despachada') - instancia_item_a_actualizar_aux_5.cantidad_despachada    
                # SE GUARDAN LOS DATOS NECESARIOS PARA ACTUALIZAR EL INVENTARIO          
                aux_dic_mod_inventario.append([instancia_item_a_actualizar_aux_5.id_bien_despachado.id_bien, instancia_item_a_actualizar_aux_5.id_bodega.id_bodega, ajuste_cantidad_despachada])
                # VALIDACION 94:
                if i['cantidad_despachada'] == 0:
                    if i['id_bien_despachado'] != 0:
                        return Response({'success':False,'detail':'Si la cantidad a despachar de un bien solicitado es 0, en el campo (id_bien_despachado) debe ingresar 0' },status=status.HTTP_404_NOT_FOUND)
                    if i['id_bodega'] != 0:
                        return Response({'success':False,'detail':'Si la cantidad a despachar de un bien solicitado es 0, en el campo (id_bodega) debe ingresar 0' },status=status.HTTP_404_NOT_FOUND)
                    if i['observacion'] != 0:
                        return Response({'success':False,'detail':'Si la cantidad a despachar de un bien solicitado es 0, en el campo (observacion) debe ingresar 0' },status=status.HTTP_404_NOT_FOUND)
                        
                    if i['id_bien_despachado'] == 0:
                        i['id_bien_despachado'] = None
                    if i['id_bodega'] == 0:
                        i['id_bodega'] = None
                    if i['observacion'] == 0:
                        i['observacion'] = 0
                    i['id_despacho_consumo'] = instancia_item_a_actualizar_aux_5.id_despacho_consumo.id_despacho_consumo
                    i['id_bien_solicitado'] = instancia_item_a_actualizar_aux_5.id_bien_solicitado
                    i['id_unidad_medida_solicitada'] = instancia_item_a_actualizar_aux_5.id_unidad_medida_solicitada
                    i['numero_posicion_despacho'] = instancia_item_a_actualizar_aux_5.numero_posicion_despacho
                else:
                    i['id_despacho_consumo'] = instancia_item_a_actualizar_aux_5.id_despacho_consumo.id_despacho_consumo
                    i['id_bien_despachado'] = instancia_item_a_actualizar_aux_5.id_bien_despachado.id_bien
                    i['id_bien_solicitado'] = instancia_item_a_actualizar_aux_5.id_bien_solicitado.id_bien
                    i['id_bodega'] = instancia_item_a_actualizar_aux_5.id_bodega.id_bodega
                    i['cantidad_solicitada'] = instancia_item_a_actualizar_aux_5.cantidad_solicitada
                    i['id_unidad_medida_solicitada'] = instancia_item_a_actualizar_aux_5.id_unidad_medida_solicitada.id_unidad_medida
                    i['numero_posicion_despacho'] = instancia_item_a_actualizar_aux_5.numero_posicion_despacho
                items_a_actualizar.append(i)
                # VALIDACION 6: SE VALIDA QUE LA CANTIDAD DESPACHADA SEA CORRECTA (EN LOS ITEMS ACTUALIZADOS)
                aux_validacion_cantidades_fecha_despacho = UtilAlmacen.get_valor_maximo_despacho(i['id_bien_despachado'], i['id_bodega'], despacho_maestro_instancia.id_despacho_consumo)
                if i['cantidad_despachada'] > aux_validacion_cantidades_fecha_despacho:
                    return Response({'success':False,'detail':'La cantidad disponible del bien (' + instancia_item_a_actualizar_aux_5.id_bien_despachado.nombre + ') es inferior a la cantidad a despachar' },status=status.HTTP_404_NOT_FOUND)
                aux_validacion_bienes_despachados_repetidos.append([i['id_bien_solicitado'], i['id_bien_despachado'], i['id_bodega']])
                # VALIDAR QUE LA CANTIDAD DESPACHADA NO SUPERE LA CANTIDAD SOLICITADA
                if i['cantidad_despachada'] > instancia_item_a_actualizar_aux_5.cantidad_solicitada:
                    return Response({'success':False,'detail':'La cantidad a despachar del bien (' + instancia_item_a_actualizar_aux_5.id_bien_despachado.nombre + ') es mayor a la cantidad solicituda' },status=status.HTTP_404_NOT_FOUND)
 #---------># VALIDACIONES DE DE ITEMS CREADOS
            if not id_item_a_despachar:
                bien_solicitado = i.get('id_bien_solicitado')
                if (bien_solicitado not in id_items_solicitud):
                    return Response({'success':False,'detail':'Uno de los bienes que intenta despachar no se encuentra dentro de la solicitud, verifique que cada id_bien_solicitado se encuentre dentro de la solicitud'},status=status.HTTP_404_NOT_FOUND)
                if bien_solicitado == None:
                    return Response({'success':False,'detail':'Debe ingresar un id de un bien solicitado'},status=status.HTTP_404_NOT_FOUND)
                bien_solicitado_instancia = CatalogoBienes.objects.filter(id_bien = i['id_bien_solicitado']).first()
                if not bien_solicitado_instancia:
                    return Response({'success':False,'detail':'El bien solicitado (' + i['id_bien_solicitado'] + ') no existe' },status=status.HTTP_404_NOT_FOUND)
                if bien_solicitado_instancia.nivel_jerarquico > 5 or bien_solicitado_instancia.nivel_jerarquico < 2:
                    return Response({'success':False,'detail':'Error en el numero_posicion (' + str(i['numero_posicion_despacho']) + '). El bien solicitado (' + bien_solicitado_instancia.nombre + ') no es de nivel 2 al 5' },status=status.HTTP_404_NOT_FOUND)
                if bien_solicitado_instancia.cod_tipo_bien != 'C':
                    return Response({'success':False,'detail':'El bien (' + bien_solicitado_instancia.nombre + ') no es de consumo' },status=status.HTTP_404_NOT_FOUND)
                item_solicitado_instancia = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=solicitud_del_despacho_instancia.id_solicitud_consumibles) & Q(id_bien=i['id_bien_solicitado'])).first()
                if item_solicitado_instancia.cantidad != i['cantidad_solicitada'] or item_solicitado_instancia.id_unidad_medida.id_unidad_medida != i['id_unidad_medida_solicitada']:
                    return Response({'success':False,'detail':'Error en el numero_posicion (' + str(i['numero_posicion_despacho']) + ') del despacho. La cantidad solicitada o la unidad de medida solicitada no corresponde a las registrada en la solicitud' },status=status.HTTP_404_NOT_FOUND)
                # VALIDACION 94:
                if i['cantidad_despachada'] == 0:
                    if i['id_bien_despachado'] != 0:
                        return Response({'success':False,'detail':'Si la cantidad a despachar de un bien solicitado es 0, en el campo (id_bien_despachado) debe ingresar 0' },status=status.HTTP_404_NOT_FOUND)
                    if i['id_bodega'] != 0:
                        return Response({'success':False,'detail':'Si la cantidad a despachar de un bien solicitado es 0, en el campo (id_bodega) debe ingresar 0' },status=status.HTTP_404_NOT_FOUND)
                    if i['observacion'] != 0:
                        return Response({'success':False,'detail':'Si la cantidad a despachar de un bien solicitado es 0, en el campo (observacion) debe ingresar 0' },status=status.HTTP_404_NOT_FOUND)
                        
                    if i['id_bien_despachado'] == 0:
                        i['id_bien_despachado'] = None
                    if i['id_bodega'] == 0:
                        i['id_bodega'] = None
                    if i['observacion'] == 0:
                        i['observacion'] = 0

                if i['cantidad_despachada'] > 0:
                    bien_despachado = i.get('id_bien_despachado')
                    if not bien_despachado:
                        return Response({'success':False,'detail':'Debe ingresar un bien despachado' },status=status.HTTP_404_NOT_FOUND)
                    bien_despachado_instancia = CatalogoBienes.objects.filter(id_bien=bien_despachado).first()
                    if not bien_despachado_instancia:
                        return Response({'success':False,'detail':'Debe ingresar un id_bien válido en el bien despachado' },status=status.HTTP_404_NOT_FOUND)
                    nivel_bien_despachado = int(bien_despachado_instancia.nivel_jerarquico)
                    # SE VALIDA QUE EL BIEN DESPACHADO PERTENESCA A LA LINEA DEL BIEN SOLICITADO
                    cont = nivel_bien_despachado
                    arreglo_id_bienes_ancestros = []
                    while cont>0:
                        arreglo_id_bienes_ancestros.append(bien_despachado_instancia.id_bien)
                        if bien_despachado_instancia.nivel_jerarquico > 1:
                            bien_despachado_instancia = CatalogoBienes.objects.filter(id_bien=bien_despachado_instancia.id_bien_padre.id_bien).first()
                            if not bien_despachado_instancia:
                                return Response({'success':False,'detail':'Uno de los bienes no tiene padre' },status=status.HTTP_404_NOT_FOUND)
                            nivel_bien_despachado = int(bien_despachado_instancia.nivel_jerarquico)
                        cont -= 1
                    # SE VALIDA QUE EL BIEN DESPACHADO SEA DESENDIENTE DEL BIEN SOLICITADO
                    if (bien_solicitado_instancia.id_bien_padre.id_bien not in arreglo_id_bienes_ancestros):
                        return Response({'success':False,'detail':'En el número de posición (' + str(i['numero_posicion_despacho']) + ') el bien solicitado no es de la misma linea del bien despachado' },status=status.HTTP_404_NOT_FOUND)
                    bodega_solicita = i.get('id_bodega')
                    if bodega_solicita == None:
                        return Response({'success':False,'detail':'Debe ingresar un id de bodega válido'},status=status.HTTP_404_NOT_FOUND)
                    instancia_bodega_solcitud = Bodegas.objects.filter(id_bodega = i['id_bodega']).first()
                    if not instancia_bodega_solcitud:
                        return Response({'success':False,'detail':'El id de bodega no existe' },status=status.HTTP_404_NOT_FOUND)
                    observaciones = i.get('observacion')
                    if observaciones == None:
                        return Response({'success':False,'detail':'El JSON debe contener un campo (observaciones)' },status=status.HTTP_404_NOT_FOUND)
                    if len(observaciones) > 30:
                        return Response({'success':False,'detail':'La observacion solo puede contener hasta 30 caracteres' },status=status.HTTP_404_NOT_FOUND)
                    # ESTO SE USA EN LA "VALIDACION 93" SE CREAN LAS CONDICIONES PARA LA VALIDACIÓN DE LA CANTIDAD DESPACHADA NO SUPERE LA SOLICITADA SI LAS UNIDADES SON IGUALES
                    aux_validacion_unidades_solicitado = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=solicitud_del_despacho_instancia.id_solicitud_consumibles) & Q(id_bien=i['id_bien_solicitado'])).first()
                    aux_validacion_unidades_despachado = CatalogoBienes.objects.filter(Q(id_bien=i['id_bien_despachado'])).first()
                    if aux_validacion_unidades_solicitado.id_bien.id_unidad_medida.nombre == aux_validacion_unidades_despachado.id_unidad_medida.nombre:
                        if i['cantidad_despachada'] > aux_validacion_unidades_solicitado.cantidad:
                            return Response({'success':False,'detail':'Una de las cantidades despachadas supera la cantidad solicitada' },status=status.HTTP_404_NOT_FOUND)
                        if not aux_validacion_bienes_repetidos.get(str(i['id_bien_solicitado'])):
                            aux_validacion_bienes_repetidos[str(i['id_bien_solicitado'])] = [i['cantidad_despachada']]
                        else:
                            aux_validacion_bienes_repetidos[str(i['id_bien_solicitado'])].append(i['cantidad_despachada'])
                        aux_validacion_unidades_dic[str(i['id_bien_solicitado'])] = True
                    else:
                        aux_validacion_unidades_dic[str(i['id_bien_solicitado'])] = False
                    # VALIDACION 95: SE VALIDA LA EXISTENCIA DEL BIEN EN LA TABLA INVENTARIO (POR BODEGA)
                    instancia_inventario_auxiliar = Inventario.objects.filter(Q(id_bien=i['id_bien_despachado'])&Q(id_bodega=i['id_bodega'])).first()
                    if not instancia_inventario_auxiliar:
                        return Response({'success':False,'detail':'Por favor verifique la existencia del bien en la bodega, o la existencia del bien en la tabla inventario' },status=status.HTTP_404_NOT_FOUND)
                    valores_creados_detalles.append({'nombre' : instancia_inventario_auxiliar.id_bien.nombre})
                    #VALIDACION 96: SE VALIDA LAS CANTIDADES POSITIVAS DEL BIEN EN LA FECHA DEL DESPACHO
                    aux_validacion_cantidades_fecha_despacho = UtilAlmacen.get_valor_maximo_despacho(i['id_bien_despachado'], i['id_bodega'], despacho_maestro_instancia.id_despacho_consumo)
                    if i['cantidad_despachada'] > aux_validacion_cantidades_fecha_despacho:
                        return Response({'success':False,'detail':'La cantidad disponible del bien (' + instancia_item_a_actualizar_aux_5.id_bien_despachado.nombre + ') es inferior a la cantidad a despachar' },status=status.HTTP_404_NOT_FOUND)
                i['id_despacho_consumo'] = despacho_maestro_instancia.id_despacho_consumo
                # VALIDACION 90: SE VALIDA QUE UN BIEN DESPACHADO NO SE REPITA DENTRO DEL MISMO DESPACHO
                if [i['id_bien_solicitado'], i['id_bien_despachado'], i['id_bodega']] in aux_validacion_bienes_despachados_repetidos:
                    return Response({'success':False,'detail':'Error en los bienes despachados, no se puede despachar el mismo bien varias veces dentro de un despacho, elimine los bienes despachados repetidos' },status=status.HTTP_404_NOT_FOUND)
                # ESTO SE USA PARA LA "VALIDACION 90"
                aux_validacion_bienes_despachados_repetidos.append([i['id_bien_solicitado'], i['id_bien_despachado'], i['id_bodega']])
                items_a_crear.append(i)

        # VALIDACION 93: SE VALIDAN LAS CANTIDADES SI TIENEN LA MISMA UNIDAD
        for key, value in aux_validacion_bienes_repetidos.items():
            aux_validacion_bienes_repetidos[key] = sum(value)
            aux_local_uno = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=solicitud_del_despacho_instancia.id_solicitud_consumibles) & Q(id_bien=int(key))).first()
            if int(aux_validacion_bienes_repetidos[key]) > aux_local_uno.cantidad:
                return Response({'success':False,'detail':'Una de las cantidades despachadas supera la cantidad solicitada' },status=status.HTTP_404_NOT_FOUND)

        # SE ACTUALIZA EL MAESTRO (DESPACHO)
        serializer = self.serializer_class(despacho_maestro_instancia, data=info_despacho)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # ACTUALIZACIÓN DE ITEMS
        for i in items_a_actualizar:
            items_despacho_instancia = ItemDespachoConsumo.objects.filter(id_item_despacho_consumo=i['id_item_despacho_consumo']).first()
            i['id_entrada_almacen_bien'] = items_despacho_instancia.id_entrada_almacen_bien.id_entrada_almacen
            print(items_despacho_instancia.id_entrada_almacen_bien)
            previous_instancia_item = copy.copy(items_despacho_instancia)
            serializer_items = self.serializer_item_consumo(items_despacho_instancia, data=i)
            serializer_items.is_valid(raise_exception=True)
            serializer_items.save()
            valores_actualizados_detalles.append({'descripcion': {'nombre':items_despacho_instancia.id_bien_despachado.nombre}, 'previous':previous_instancia_item,'current':items_despacho_instancia})
        
        # CREACIÓN DE ITEMS
        serializer_items = self.serializer_item_consumo(data=items_a_crear, many=True)
        serializer_items.is_valid(raise_exception=True)
        serializer_items.save()
        
        # INSERT EN LA TABLA INVENTARIO
        for i in items_a_crear:
            inventario_instancia = Inventario.objects.filter(Q(id_bien=i['id_bien_despachado'])&Q(id_bodega=i['id_bodega'])).first()
            aux_suma = inventario_instancia.cantidad_saliente_consumo
            if aux_suma == None:
                aux_suma = 0
            inventario_instancia.cantidad_saliente_consumo = int(aux_suma) + int(i['cantidad_despachada'])
            inventario_instancia.save()            
        for i in aux_dic_mod_inventario:
            inventario_instancia = Inventario.objects.filter(Q(id_bien=i[0])&Q(id_bodega=i[1])).first()
            inventario_instancia.cantidad_saliente_consumo = int(inventario_instancia.cantidad_saliente_consumo) + i[2]
            inventario_instancia.save()   
        
        # INSERT EN LAS TABLAS DespachoEntrantes, ItemsDespachoEntrante
        instancia_despacho_entrante = DespachoEntrantes.objects.filter(id_despacho_consumo_alm=despacho_maestro_instancia.id_despacho_consumo).first()
  
        items_despacho_entrante_lista = []
        aux_validacion = []
        repetidos_items_despacho_entrante_lista = []
        carry_items_despacho_entrante_lista = []
        cont = 0
        print(items_a_crear)
        
        for i in items_a_actualizar:
            items_despacho_instancia = ItemDespachoConsumo.objects.filter(id_item_despacho_consumo=i['id_item_despacho_consumo']).first()
            instancia_items_despacho_entrante = ItemsDespachoEntrante.objects.filter(id_bien=items_despacho_instancia.id_bien_despachado.id_bien, 
                                                                                        id_entrada_alm_del_bien=items_despacho_instancia.id_entrada_almacen_bien.id_entrada_almacen,
                                                                                        id_despacho_entrante=instancia_despacho_entrante.id_despacho_entrante).first()
            instancia_items_despacho_entrante.cantidad_entrante = items_despacho_instancia.cantidad_despachada
            instancia_items_despacho_entrante.save()
            
        for i in items_a_crear:
            items_despacho_entrante = {}
            aux_validacion = [i['id_bien_despachado'], i['id_entrada_almacen_bien']]
            instancia_validacion_existencia_item = ItemsDespachoEntrante.objects.filter(id_despacho_entrante=instancia_despacho_entrante.id_despacho_entrante, id_bien=i['id_bien_despachado']).first()
            if aux_validacion in repetidos_items_despacho_entrante_lista or instancia_validacion_existencia_item:
                carry_items_despacho_entrante_lista.append([i['id_bien_despachado'], i['id_entrada_almacen_bien'], i['cantidad_despachada'], cont])
                cont = cont + 1
            else:
                items_despacho_entrante['id_despacho_entrante'] = instancia_despacho_entrante.id_despacho_entrante
                items_despacho_entrante['id_bien'] = i['id_bien_despachado']
                items_despacho_entrante['id_entrada_alm_del_bien'] = i['id_entrada_almacen_bien']
                items_despacho_entrante['fecha_ingreso'] = despacho_maestro_instancia.fecha_despacho
                items_despacho_entrante['cantidad_entrante'] = i['cantidad_despachada']
                items_despacho_entrante['cantidad_distribuida'] = 0
                items_despacho_entrante['observacion'] = i['observacion']
                items_despacho_entrante_lista.append(items_despacho_entrante)
                repetidos_items_despacho_entrante_lista.append([i['id_bien_despachado'], i['id_entrada_almacen_bien']])
                
        SerializersItemsDespachoEntrantes = self.serializer_items_despacho_entrante(data=items_despacho_entrante_lista, many=True)
        SerializersItemsDespachoEntrantes.is_valid(raise_exception=True)
        SerializersItemsDespachoEntrantes.save()
        
        for i in carry_items_despacho_entrante_lista:
            instancia_items_despacho_entrante = ItemsDespachoEntrante.objects.filter(id_bien=i[0], id_entrada_alm_del_bien=i[1],id_despacho_entrante=instancia_despacho_entrante.id_despacho_entrante).first()
            instancia_items_despacho_entrante.cantidad_entrante = instancia_items_despacho_entrante.cantidad_entrante + i[2]
            instancia_items_despacho_entrante.save()
            
        descripcion = {"numero_despacho_almacen": str(despacho_maestro_instancia.numero_despacho_consumo), "fecha_despacho": str(despacho_maestro_instancia.fecha_despacho)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 35,
            "cod_permiso": "AC",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles,
            "valores_actualizados_detalles": valores_actualizados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
            
        return Response({'success':True,'detail':'Despacho actualizado con éxito'},status=status.HTTP_200_OK)

class EliminarItemsDespachoVivero(generics.DestroyAPIView):
    serializer_class = SerializersItemDespachoViverosConsumo
    queryset=ItemDespachoConsumo.objects.all()

    def destroy(self, request, id_despacho_consumo):
        datos_ingresados = request.data
        user_logeado = request.user
        # VALIDACION 0: SE VALIDA EL QUE EL USUARIO ESTÉ LOGUEADO
        if str(user_logeado) == 'AnonymousUser':
            return Response({'success':False,'detail':'Esta solicitud solo la puede ejecutar un usuario logueado'},status=status.HTTP_404_NOT_FOUND)
        ids_items_a_eliminar = [i['id_item_despacho_consumo'] for i in datos_ingresados]
        instancia_despacho = DespachoConsumo.objects.filter(id_despacho_consumo=id_despacho_consumo).first()
        instancia_despacho_entrante = DespachoEntrantes.objects.filter(id_despacho_consumo_alm=instancia_despacho.id_despacho_consumo).first()
        aux_instancia_items = ItemDespachoConsumo.objects.filter(id_despacho_consumo=instancia_despacho.id_despacho_consumo)
        # SE VALDIA QUE EL DESPACHO SEA DE VIVERO
        if instancia_despacho.es_despacho_conservacion != True:
            return Response({'success':False,'detail':'En este módulo solo se pueden elimanar items de despachos de viveros' },status=status.HTTP_404_NOT_FOUND)
        if len(ids_items_a_eliminar) != len(set(ids_items_a_eliminar)):
            return Response({'success':False,'detail':'Verifique que no existan items repetidos dentro de la petición' },status=status.HTTP_404_NOT_FOUND)
        if len(aux_instancia_items) <= len(datos_ingresados):
            return Response({'success':False,'detail':'La cantidad de items que desea borrar es superior o igual a los que el despacho posee' },status=status.HTTP_404_NOT_FOUND)
        # SE VALIDA QUE EL DESPACHO NO TENGA DISTRIBUCIONES EN DESPACHO_ENTRANTES
        if instancia_despacho_entrante.id_persona_distribuye != None:
            return Response({'success':False,'detail':'No se pueden eliminar items de este despahco debido a que los items ya se fueron distribuidos en el vivero' },status=status.HTTP_404_NOT_FOUND)
        # VALIDACION 2: SE VALIDA QUE LA ACTUALIZACIÓN NO SE REALIZA EN UNA FECHA POSTERIOR A 45 DÍAS DESPUES DEL DESPACHO
        fecha_despacho = instancia_despacho.fecha_despacho
        aux_validacion_fechas = datetime.now() - fecha_despacho
        if int(aux_validacion_fechas.days) > 45:
            return Response({'success':False,'detail':'No pueden eliminar los items de un despacho con fecha anterior a 45 días respecto a la actual'},status=status.HTTP_404_NOT_FOUND)
        # SE VALIDA QUE CADA UNO DE LOS ITEMS INGRESADOS PERTENEZCA A AL DESPACHO QUE SE INGRESÓ EN LA URL
        for  i in datos_ingresados:
            instance = ItemDespachoConsumo.objects.filter(Q(id_item_despacho_consumo=i['id_item_despacho_consumo']) & Q(id_despacho_consumo=instancia_despacho.id_despacho_consumo)).first()
            if not instance:
                return Response({'success':False,'detail':'Uno de los items que desea borrar no pertenece a la solicitud que ingresó' },status=status.HTTP_404_NOT_FOUND)
        # SE BORRAN LOS ITEMS DE LA TABLA DESPACHO_ENTRANTE
        for i in datos_ingresados:
            instancia_item_despacho = ItemDespachoConsumo.objects.filter(Q(id_item_despacho_consumo=i['id_item_despacho_consumo']) & Q(id_despacho_consumo=instancia_despacho.id_despacho_consumo)).first()
            instancia_item_despacho_entrante = ItemsDespachoEntrante.objects.filter(Q(id_despacho_entrante=instancia_despacho_entrante.id_despacho_entrante) 
                                                                                    & Q(id_bien=instancia_item_despacho.id_bien_despachado.id_bien)
                                                                                    & Q(id_entrada_alm_del_bien=instancia_item_despacho.id_entrada_almacen_bien.id_entrada_almacen)).first()
            if instancia_item_despacho.cantidad_despachada == instancia_item_despacho_entrante.cantidad_entrante:
                instancia_item_despacho_entrante.delete()
            else:
                instancia_item_despacho_entrante.cantidad_entrante = instancia_item_despacho_entrante.cantidad_entrante - instancia_item_despacho.cantidad_despachada
                instancia_item_despacho_entrante.save()
                
        # INSERT EN LA TABLA INVENTARIO, SE RESTRAN CANTIDADES A LA CANTIDAD DEDSPACHADA
        for i in datos_ingresados:
            instance = ItemDespachoConsumo.objects.filter(Q(id_item_despacho_consumo=i['id_item_despacho_consumo']) & Q(id_despacho_consumo=instancia_despacho.id_despacho_consumo)).first()
            inventario_instancia = Inventario.objects.filter(Q(id_bien=instance.id_bien_despachado)&Q(id_bodega=instance.id_bodega)).first()
            inventario_instancia.cantidad_saliente_consumo = int(inventario_instancia.cantidad_saliente_consumo) - int(instance.cantidad_despachada)
            inventario_instancia.save()
        # SE BORRAN LOS ITEMS DEL DESPACHO
        valores_eliminados_detalles = []
        for  i in datos_ingresados:
            instance = ItemDespachoConsumo.objects.filter(Q(id_item_despacho_consumo=i['id_item_despacho_consumo']) & Q(id_despacho_consumo=instancia_despacho.id_despacho_consumo)).first()
            valores_eliminados_detalles.append({'nombre' : instance.id_bien_despachado.nombre})
            instance.delete()
        descripcion = {"numero_despacho_almacen": str(instancia_despacho.numero_despacho_consumo), "es_despacho_conservacion": "true", "fecha_despacho": str(instancia_despacho.fecha_despacho)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 35,
            "cod_permiso": "AC",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        return Response({'success':True,'detail':'Se eliminaron los items del despacho de manera correcta'},status=status.HTTP_200_OK)

class AnularDespachoConsumoVivero(generics.UpdateAPIView):
    serializer_class = SerializersDespachoViverosConsumo
    queryset=DespachoConsumo.objects.all()
    
    def put(self, request, despacho_a_anular):
        # SE CAPTURAN LOS DATOS Y SE ADQUIERE EL DATO DE LA FECHA DE ANULACIÓN
        datos_ingresados = request.data
        datos_ingresados['fecha_anualacion'] = datetime.now()
        
        # VALIDACION DE USUARIO LOGUEADO
        user_logeado = request.user
        if str(user_logeado) == 'AnonymousUser':
            return Response({'success':False,'detail':'Esta solicitud solo la puede ejecutar un usuario logueado'},status=status.HTTP_404_NOT_FOUND)
        instancia_despacho_anular = DespachoConsumo.objects.filter(id_despacho_consumo=despacho_a_anular).first()
        instancia_despacho_entrante = DespachoEntrantes.objects.filter(id_despacho_consumo_alm=instancia_despacho_anular.id_despacho_consumo).first()
        items_despacho = ItemDespachoConsumo.objects.filter(id_despacho_consumo=despacho_a_anular)
        items_despacho_entrante_instancia = ItemsDespachoEntrante.objects.filter(Q(id_despacho_entrante=instancia_despacho_entrante.id_despacho_entrante))
        # SE VALDIA QUE EL DESPACHO SEA DE VIVERO
        if instancia_despacho_anular.es_despacho_conservacion != True:
            return Response({'success':False,'detail':'En este módulo solo se pueden anular despachos de viveros' },status=status.HTTP_404_NOT_FOUND)
        # SE VALDIA QUE EL DESPACHO NO TENGA DISTRIBUCIONES
        if instancia_despacho_entrante.id_persona_distribuye != None:
            return Response({'success':False,'detail':'No se puede aanular este despahco debido a que los items ya se fueron distribuidos en el vivero' },status=status.HTTP_404_NOT_FOUND)
        # SE BORRAN LOS ITEMS DE LA TABLA DESPACHO_ENTRANTE
        items_despacho_entrante_instancia.delete()
        # SE BORRAR EL REGISTRO DEL DESPACHO ENTRNATE
        print(instancia_despacho_entrante)
        instancia_despacho_entrante.delete()
        # SE RESTA DEL INVENTARIO LAS CANTIDADES DESPACHAS DEL DESPACHO QUE SE ESTÁ ANULANDO
        for i in items_despacho:
            inventario_instancia = Inventario.objects.filter(Q(id_bien=i.id_bien_despachado)&Q(id_bodega=i.id_bodega)).first()
            inventario_instancia.cantidad_saliente_consumo = int(inventario_instancia.cantidad_saliente_consumo) - int(i.cantidad_despachada)
            inventario_instancia.save()
            # SE BORRAN LOS ITEMS DEL DESPACHO
            items_despacho.delete()
        # INSERT EN LA TABLA SOLICITUDES DE CONSUMIBLES
        instancia_despacho_anular = DespachoConsumo.objects.filter(id_despacho_consumo=despacho_a_anular).first()
        instancia_solicitud = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=instancia_despacho_anular.id_solicitud_consumo.id_solicitud_consumibles).first()
        instancia_solicitud.id_despacho_consumo = None
        instancia_solicitud.fecha_cierre_solicitud = None
        instancia_solicitud.gestionada_almacen = False
        instancia_solicitud.solicitud_abierta = True
        instancia_solicitud.save()
        # INSERT EN LA TABLA DE DESPACHO DE CONSUMIBLES
        persona_anula = Personas.objects.filter(id_persona=request.user.persona.id_persona).first()
        instancia_despacho_anular.despacho_anulado = True
        instancia_despacho_anular.justificacion_anulacion = datos_ingresados['justificacion_anulacion']
        instancia_despacho_anular.fecha_anulacion = datos_ingresados['fecha_anualacion']
        instancia_despacho_anular.id_persona_anula = persona_anula
        instancia_despacho_anular.save()
        return Response({'success':True,'detail':'Despacho anulado con éxito'},status=status.HTTP_200_OK)
