from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen, ItemEntradaAlmacen
from almacen.serializers.bienes_serializers import CatalogoBienesSerializer
from almacen.serializers.despachos_serializers import  SerializersDespachoConsumo, SerializersDespachoConsumoConItems, SerializersItemDespachoConsumo, SerializersSolicitudesConsumibles, SerializersItemsSolicitudConsumible, SearchBienInventarioSerializer
from rest_framework import generics,status
from rest_framework.response import Response
from seguridad.models import Personas, User
from rest_framework.decorators import api_view
from seguridad.utils import Util
from almacen.utils import UtilAlmacen
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum,F
from datetime import datetime, date,timedelta
import copy
import json
from almacen.serializers.despachos_serializers import (
    CerrarSolicitudDebidoInexistenciaSerializer,
    SerializersDespachoConsumo,
    SerializersDespachoConsumoActualizar,
    SerializersItemDespachoConsumo,
    SerializersSolicitudesConsumibles,
    SerializersItemsSolicitudConsumible,
    AgregarBienesConsumoConservacionSerializer,
    GetItemOtrosOrigenesSerializers
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
from transversal.models.organigrama_models import (
    UnidadesOrganizacionales,
    NivelesOrganigrama
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

class CreateDespachoMaestro(generics.UpdateAPIView):
    serializer_class = SerializersDespachoConsumo
    queryset = DespachoConsumo
    serializer_item_consumo = SerializersItemDespachoConsumo
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        datos_ingresados = request.data
        user_logeado = request.user
        info_despacho = json.loads(datos_ingresados['info_despacho'])
        items_despacho = json.loads(datos_ingresados['items_despacho'])
        info_despacho['ruta_archivo_doc_con_recibido'] = request.FILES.get('ruta_archivo_doc_con_recibido')
        
        #Validaciones primarias
        if info_despacho['es_despacho_conservacion'] != False:
            raise NotFound('En este servicio no se pueden procesar despachos de vivero, además verfique el campo (es_despacho_conservacion) debe ser True o False')
        
        #Validaciones de la solicitud
        instancia_solicitud = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=info_despacho['id_solicitud_consumo']).first()
        if not instancia_solicitud:
            raise ValidationError('Debe ingresar un id de solicitud válido')
        if instancia_solicitud.solicitud_abierta == False or instancia_solicitud.estado_aprobacion_responsable != 'A':
            raise PermissionDenied('La solicitud a despachar debe de estar aprobada por el funcionario responsable y no debe de estar cerrada')
        if instancia_solicitud.es_solicitud_de_conservacion != False:
            raise PermissionDenied('En este módulo no se pueden despachar solicitudes de vivero')
        #Asignación de fecha de registro
        info_despacho['fecha_registro'] = datetime.now()
        #Se valida que la fecha de la solicitud no sea inferior a (fecha_actual - 8 días) ni superior a la actual
        fecha_despacho = datetime.strptime(info_despacho.get('fecha_despacho'), "%Y-%m-%d %H:%M:%S")
        aux_validacion_fechas = info_despacho['fecha_registro'] - fecha_despacho
        if int(aux_validacion_fechas.days) > 8 or int(aux_validacion_fechas.days) < 0:
            raise ValidationError('La fecha ingresada no es permitida dentro de los parametros existentes')
        #Se valida que la fecha de aprobación de la solicitud sea inferior a la fecha de despacho
        fecha_aprobacion_solicitud = instancia_solicitud.fecha_aprobacion_responsable
        if fecha_aprobacion_solicitud == None:
            raise ValidationError('La solicitud que desea despachar no tiene registrada fecha de aprobación del responsable')
        if fecha_despacho <= fecha_aprobacion_solicitud:
            raise ValidationError('La fecha de despacho debe ser mayor o igual a la fecha de aprobación de la solicitud')
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
            raise ValidationError('La solicitud que quiere despachar no tiene items, por favor añada items a la solicitud para poderla despachar')
        id_items_solicitud = [i.id_bien.id_bien for i in items_solicitud]
        # SE VALIDA QUE EL NUMERO DE POSICION SEA UNICO
        nro_posicion_items = [i['numero_posicion_despacho'] for i in items_despacho]
        if len(nro_posicion_items) != len(set(nro_posicion_items)):
            raise ValidationError('El número de posición debe ser único')
        
        # VALIDACIONES EN ITEMS DEL DESPACHO
        aux_validacion_bienes_despachados_repetidos = []
        aux_validacion_bienes_despachados_contra_solicitados = []
        axu_validacion_cantidades_despachadas_total = []
        valores_creados_detalles = []
        aux_validacion_bienes_repetidos = {}
        aux_validacion_unidades_dic = {}
        for i in items_despacho:
            bien_solicitado = i.get('id_bien_solicitado')
            if (bien_solicitado not in id_items_solicitud):
                raise ValidationError('Uno de los bienes que intenta despachar no se encuentra dentro de la solicitud, verifique que cada id_bien_solicitado se encuentre dentro de la solicitud')
            if bien_solicitado == None:
                raise ValidationError('Debe ingresar un id de un bien solicitado')
            bien_solicitado_instancia = CatalogoBienes.objects.filter(id_bien = i['id_bien_solicitado']).first()
            if not bien_solicitado_instancia:
                raise NotFound('El bien solicitado (' + i['id_bien_solicitado'] + ') no existe')
            if bien_solicitado_instancia.nivel_jerarquico > 5 or bien_solicitado_instancia.nivel_jerarquico < 2:
                raise ValidationError('Error en el numero_posicion (' + str(i['numero_posicion_despacho']) + '). El bien solicitado (' + bien_solicitado_instancia.nombre + ') no es de nivel 2 al 5')
            if bien_solicitado_instancia.cod_tipo_bien != 'C':
                raise ValidationError('El bien (' + bien_solicitado_instancia.nombre + ') no es de consumo')
            item_solicitado_instancia = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=info_despacho['id_solicitud_consumo']) & Q(id_bien=i['id_bien_solicitado'])).first()
            if item_solicitado_instancia.cantidad != i['cantidad_solicitada']: # or item_solicitado_instancia.id_unidad_medida.id_unidad_medida != i['id_unidad_medida_solicitada']:
                raise ValidationError('Error en el numero_posicion (' + str(i['numero_posicion_despacho']) + ') del despacho. La cantidad solicitada o la unidad de medida solicitada no corresponde a las registrada en la solicitud')
            # VALIDACION 94:
            if i['cantidad_despachada'] == 0:
                if i['id_bien_despachado'] != 0:
                    raise ValidationError('Si la cantidad a despachar de un bien solicitado es 0, en el campo (id_bien_despachado) debe ingresar 0')
                if i['id_bodega'] != 0:
                    raise ValidationError('Si la cantidad a despachar de un bien solicitado es 0, en el campo (id_bodega) debe ingresar 0')
                if i['observacion'] != 0:
                    raise ValidationError('Si la cantidad a despachar de un bien solicitado es 0, en el campo (observacion) debe ingresar 0')
                    
                if i['id_bien_despachado'] == 0:
                    i['id_bien_despachado'] = None
                if i['id_bodega'] == 0:
                    i['id_bodega'] = None
                if i['observacion'] == 0:
                    i['observacion'] = 0

            if i['cantidad_despachada'] > 0:
                bien_despachado = i.get('id_bien_despachado')
                if not bien_despachado:
                    raise ValidationError('Debe ingresar un bien despachado')
                bien_despachado_instancia = CatalogoBienes.objects.filter(id_bien=bien_despachado).first()
                if not bien_despachado_instancia:
                    raise ValidationError('Debe ingresar un id_bien válido en el bien despachado')
                nivel_bien_despachado = int(bien_despachado_instancia.nivel_jerarquico)
                # SE VALIDA QUE EL BIEN DESPACHADO PERTENESCA A LA LINEA DEL BIEN SOLICITADO
                cont = nivel_bien_despachado
                arreglo_id_bienes_ancestros = []
                while cont>0:
                    arreglo_id_bienes_ancestros.append(bien_despachado_instancia.id_bien)
                    if bien_despachado_instancia.nivel_jerarquico > 1:
                        bien_despachado_instancia = CatalogoBienes.objects.filter(id_bien=bien_despachado_instancia.id_bien_padre.id_bien).first()
                        if not bien_despachado_instancia:
                            raise ValidationError('Uno de los bienes no tiene padre')
                        nivel_bien_despachado = int(bien_despachado_instancia.nivel_jerarquico)
                    cont -= 1
                # SE VALIDA QUE EL BIEN DESPACHADO SEA DESENDIENTE DEL BIEN SOLICITADO
                if (bien_solicitado_instancia.id_bien_padre.id_bien not in arreglo_id_bienes_ancestros):
                   raise ValidationError('En el número de posición (' + str(i['numero_posicion_despacho']) + ') el bien solicitado no es de la misma linea del bien despachado')
                bodega_solicita = i.get('id_bodega')
                if bodega_solicita == None:
                    raise ValidationError('Debe ingresar un id de bodega válido')
                instancia_bodega_solcitud = Bodegas.objects.filter(id_bodega = i['id_bodega']).first()
                if not instancia_bodega_solcitud:
                    raise NotFound('El id de bodega no existe')
                observaciones = i.get('observacion')
                if observaciones == None:
                    raise ValidationError('El JSON debe contener un campo (observaciones)')
                if len(observaciones) > 30:
                    raise ValidationError('La observacion solo puede contener hasta 30 caracteres')
                # ESTO SE USA EN LA "VALIDACION 93" SE CREAN LAS CONDICIONES PARA LA VALIDACIÓN DE LA CANTIDAD DESPACHADA NO SUPERE LA SOLICITADA SI LAS UNIDADES SON IGUALES
                aux_validacion_unidades_solicitado = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=info_despacho['id_solicitud_consumo']) & Q(id_bien=i['id_bien_solicitado'])).first()
                aux_validacion_unidades_despachado = CatalogoBienes.objects.filter(Q(id_bien=i['id_bien_despachado'])).first()
                if aux_validacion_unidades_solicitado.id_bien.id_unidad_medida.nombre == aux_validacion_unidades_despachado.id_unidad_medida.nombre:
                    if i['cantidad_despachada'] > aux_validacion_unidades_solicitado.cantidad:
                        raise ValidationError('Una de las cantidades despachadas supera la cantidad solicitada')
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
                    raise ValidationError('Por favor verifique la existencia del bien en la bodega, o la existencia del bien en la tabla inventario')
                valores_creados_detalles.append({'nombre' : instancia_inventario_auxiliar.id_bien.nombre})
                #VALIDACION 96: SE VALIDA LAS CANTIDADES POSITIVAS DEL BIEN EN LA FECHA DEL DESPACHO
                aux_validacion_cantidades_fecha_despacho = UtilAlmacen.get_cantidad_disponible(i['id_bien_despachado'], i['id_bodega'], fecha_despacho)
                if i['cantidad_despachada'] > aux_validacion_cantidades_fecha_despacho:
                    raise ValidationError('Verifique que las cantidades del bien a despachar en la bodega ingresada en la fecha de despacho sean correctas')
                #VALIDACION 97: SE VALIDA QUE EL BIEN DESPACHADO NO TENGA DESPACHOS POSTERIORES A LA FECHA DE DESPACHO
                items_despachados_aux_val_97 = ItemDespachoConsumo.objects.filter(id_bien_despachado=i['id_bien_despachado'], id_despacho_consumo__fecha_despacho__gte=info_despacho['fecha_despacho'])
                if items_despachados_aux_val_97:
                    try:
                        raise PermissionDenied('El bien tiene despachos o entregas posteriores a la fecha de despacho elegida')
                    except PermissionDenied as e:
                        return Response({'success':False, 'detail':'El bien tiene despachos o entregas posteriores a la fecha de despacho elegida', 'data': []}, status=status.HTTP_403_FORBIDDEN)
                
            # VALIDACION 90: SE VALIDA QUE UN BIEN DESPACHADO NO SE REPITA DENTRO DEL MISMO DESPACHO
            if [i['id_bien_solicitado'], i['id_bien_despachado'], i['id_bodega']] in aux_validacion_bienes_despachados_repetidos:
                raise ValidationError('Error en los bienes despachados, no se puede despachar el mismo bien varias veces dentro de un despacho, elimine los bienes despachados repetidos')
            # ESTO SE USA PARA LA "VALIDACION 90"
            aux_validacion_bienes_despachados_repetidos.append([i['id_bien_solicitado'], i['id_bien_despachado'], i['id_bodega']])
            # ESTO SE USA PARA LA "VALIDACION 91"
            aux_validacion_bienes_despachados_contra_solicitados.append(i['id_bien_solicitado'])
            # ESTO SE USA PARA LA "VALIDACION 92"
            axu_validacion_cantidades_despachadas_total.append(i['cantidad_despachada'])
            
        # VALIDACION 91: SE VALIDA QUE TODOS LOS BIENES SOLICITUADOS SE ENCUENTREN DENTRO DE LA SOLICITUD
        if len(items_solicitud) != len(set(aux_validacion_bienes_despachados_contra_solicitados)):
            raise ValidationError('Error en los bienes despachados, se deben despachar cada uno de los bienes solicitados, si no desea despachar alguno de los bienes solicitados ingrese cantidad despachada en 0')
        # VALIDACION 92: SE VALIDA QUE DENTRO DE LA SOLICITUD SE DESPACHE AL MENOS 1 BIEN, NO ES POSIBLE DESPACHAR TODO EN 0 
        axu_validacion_cantidades_despachadas_total = sum(axu_validacion_cantidades_despachadas_total)
        if axu_validacion_cantidades_despachadas_total < 1:
            raise ValidationError('Debe despachar como mínimo una unidad de los bienes en la solicitud, si quiere cerrar la solicitud porque no hay stock disponible de ningún item por favor diríjase al módulo de cierre de solicitud por inexistencia')
        # VALIDACION 93: SE VALIDAN LAS CANTIDADES SI TIENEN LA MISMA UNIDAD
        for key, value in aux_validacion_bienes_repetidos.items():
            aux_validacion_bienes_repetidos[key] = sum(value)
            aux_local_uno = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=info_despacho['id_solicitud_consumo']) & Q(id_bien=int(key))).first()
            if int(aux_validacion_bienes_repetidos[key]) > aux_local_uno.cantidad:
                raise ValidationError('Una de las cantidades despachadas supera la cantidad solicitada')
 
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
        
        # AUDITORIA MAESTRO DETALLE DE DESPACHO
        descripcion = {"numero_despacho_consumo": str(info_despacho['numero_despacho_consumo']), "es_despacho_conservacion": "false", "fecha_despacho": str(info_despacho['fecha_despacho'])}
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
        return Response({'success':True, 'detail':'Despacho creado con éxito', 'Numero despacho' : info_despacho["numero_despacho_consumo"]},status=status.HTTP_200_OK)

class ActualizarDespachoConsumo(generics.UpdateAPIView):
    serializer_class = SerializersDespachoConsumoActualizar
    queryset=DespachoConsumo.objects.all()
    serializer_item_consumo = SerializersItemDespachoConsumo
    permission_classes = [IsAuthenticated]
    
    def delete_items(self, items_despacho_data, items_despacho_instancia):
        ids_items_despacho_data = [item['id_item_despacho_consumo'] for item in items_despacho_data if item['id_item_despacho_consumo']!=None]
        instancia_items_delete = items_despacho_instancia.exclude(id_item_despacho_consumo__in=ids_items_despacho_data)
        
        # INSERT EN LA TABLA INVENTARIO
        valores_eliminados_detalles = []
        
        for instance in instancia_items_delete:
            inventario_instancia = Inventario.objects.filter(Q(id_bien=instance.id_bien_despachado)&Q(id_bodega=instance.id_bodega)).first()
            aux_suma = inventario_instancia.cantidad_saliente_consumo
            if aux_suma == None:
                aux_suma = 0
            inventario_instancia.cantidad_saliente_consumo = int(aux_suma) - int(instance.cantidad_despachada)
            inventario_instancia.save()
            
            valores_eliminados_detalles.append({'nombre' : instance.id_bien_despachado.nombre})
            
        # SE BORRAN LOS ITEMS DEL DESPACHO
        instancia_items_delete.delete()
        
        return valores_eliminados_detalles
    
    def put(self, request):
        datos_ingresados = request.data
        user_logeado = request.user
        info_despacho = json.loads(datos_ingresados['info_despacho'])
        items_despacho = json.loads(datos_ingresados['items_despacho'])
        info_despacho['ruta_archivo_doc_con_recibido'] = request.FILES.get('ruta_archivo_doc_con_recibido')
    
        # SE INSTANCIAN ALGUNAS TABLAS QUE SE VAN A TOCAR
        despacho_maestro_instancia = DespachoConsumo.objects.filter(id_despacho_consumo=info_despacho['id_despacho_consumo']).first()
        if not despacho_maestro_instancia:
            raise ValidationError('Ingrese un id de despacho de bienes de consumo válido')
        items_despacho_instancia = ItemDespachoConsumo.objects.filter(id_despacho_consumo=despacho_maestro_instancia.id_despacho_consumo)
        if not items_despacho_instancia:
            raise ValidationError('No es posible actualizar el despacho debido a que este no tiene items asociados')
        solicitud_del_despacho_instancia = SolicitudesConsumibles.objects.filter(id_despacho_consumo=despacho_maestro_instancia.id_despacho_consumo).first()
        if not solicitud_del_despacho_instancia:
            raise ValidationError('Por favor verifique que la solicitud se haya despachado anteriormente')
        items_solcitud_instancia = ItemsSolicitudConsumible.objects.filter(id_solicitud_consumibles=solicitud_del_despacho_instancia.id_solicitud_consumibles)
        if not items_solcitud_instancia:
            raise ValidationError('La solicitud que quiere despachar no tiene items, por favor añada items a la solicitud para poderla despachar')
        
        # VALIDACION 2: SE VALIDA QUE LA ACTUALIZACIÓN NO SE REALIZA EN UNA FECHA POSTERIOR A 45 DÍAS DESPUES DEL DESPACHO
        #Se valida que la fecha de la solicitud no sea inferior a (fecha_actual - 8 días) ni superior a la actual
        fecha_despacho = despacho_maestro_instancia.fecha_despacho
        aux_validacion_fechas = datetime.now() - fecha_despacho
        if int(aux_validacion_fechas.days) > 45:
            raise PermissionDenied('No puede actualizar un despacho con fecha anterior a 45 días respecto a la actual')
        
        # SE OBTIENEN TODOS LOS ITEMS DE LA SOLICITUD PARA LUEGO VALIDAR QUE LOS ITEMS DESPACHADOS ESTÉN DENTRO DE LA SOLICITUD
        id_items_solicitud = [i.id_bien.id_bien for i in items_solcitud_instancia]
        # SE OBTIENEN TODOS LOS ITEMS DEL DESPACHO PARA LA VALIDACION 4
        id_items_despacho = [i.id_item_despacho_consumo for i in items_despacho_instancia]
        
        # SE VALIDA QUE EL NUMERO DE POSICION SEA UNICO
        nro_posicion_items_entrantes = [i['numero_posicion_despacho'] for i in items_despacho if i.get('numero_posicion_despacho')]
        nro_posicion_items_existentes = [i.numero_posicion_despacho for i in items_despacho_instancia]
        nro_posicion_total_items = nro_posicion_items_entrantes + nro_posicion_items_existentes
        if len(nro_posicion_total_items) != len(set(nro_posicion_total_items)):
            raise ValidationError('El número de posición debe ser único')
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
                    raise ValidationError('Uno de los ids que ingresó de los items a despachar que desea actualizar no pertenece al despacho que está actualizando')
                # VALIDACION 5:
                instancia_item_a_actualizar_aux_5 = ItemDespachoConsumo.objects.filter(id_item_despacho_consumo=id_item_a_despachar).first()
                valores_actualizados__solicitud.append(instancia_item_a_actualizar_aux_5.id_bien_solicitado.id_bien)
                ajuste_cantidad_despachada = i.get('cantidad_despachada') - instancia_item_a_actualizar_aux_5.cantidad_despachada    
                # SE GUARDAN LOS DATOS NECESARIOS PARA ACTUALIZAR EL INVENTARIO          
                aux_dic_mod_inventario.append([instancia_item_a_actualizar_aux_5.id_bien_despachado.id_bien, instancia_item_a_actualizar_aux_5.id_bodega.id_bodega, ajuste_cantidad_despachada])
                # VALIDACION 94:
                if i['cantidad_despachada'] == 0:
                    if i['id_bien_despachado'] != 0:
                        raise ValidationError('Si la cantidad a despachar de un bien solicitado es 0, en el campo (id_bien_despachado) debe ingresar 0')
                    if i['id_bodega'] != 0:
                        raise ValidationError('Si la cantidad a despachar de un bien solicitado es 0, en el campo (id_bodega) debe ingresar 0')
                    if i['observacion'] != 0:
                        raise ValidationError('Si la cantidad a despachar de un bien solicitado es 0, en el campo (observacion) debe ingresar 0')
                        
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
                    raise ValidationError('Verifique que las cantidades del bien a actualizar en el despacho, en la bodega ingresada en la fecha de despacho sean correctas')
                aux_validacion_bienes_despachados_repetidos.append([i['id_bien_solicitado'], i['id_bien_despachado'], i['id_bodega']])
                # VALIDAR QUE LA CANTIDAD DESPACHADA NO SUPERE LA CANTIDAD SOLICITADA
                if i['cantidad_despachada'] > instancia_item_a_actualizar_aux_5.cantidad_solicitada:
                    raise ValidationError('La cantidad a despachar es mayor a la cantidad solicituda')
 #---------># VALIDACIONES DE DE ITEMS CREADOS
            if not id_item_a_despachar:
                bien_solicitado = i.get('id_bien_solicitado')
                if (bien_solicitado not in id_items_solicitud):
                    raise ValidationError('Uno de los bienes que intenta despachar no se encuentra dentro de la solicitud, verifique que cada id_bien_solicitado se encuentre dentro de la solicitud')
                if bien_solicitado == None:
                    raise ValidationError('Debe ingresar un id de un bien solicitado')
                bien_solicitado_instancia = CatalogoBienes.objects.filter(id_bien = i['id_bien_solicitado']).first()
                if not bien_solicitado_instancia:
                    raise NotFound('El bien solicitado (' + str(i['id_bien_solicitado']) + ') no existe')
                if bien_solicitado_instancia.nivel_jerarquico > 5 or bien_solicitado_instancia.nivel_jerarquico < 2:
                    raise ValidationError('Error en el numero_posicion (' + str(i['numero_posicion_despacho']) + '). El bien solicitado (' + bien_solicitado_instancia.nombre + ') no es de nivel 2 al 5')
                if bien_solicitado_instancia.cod_tipo_bien != 'C':
                    raise ValidationError('El bien (' + bien_solicitado_instancia.nombre + ') no es de consumo')
                item_solicitado_instancia = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=solicitud_del_despacho_instancia.id_solicitud_consumibles) & Q(id_bien=i['id_bien_solicitado'])).first()
                if item_solicitado_instancia.cantidad != i['cantidad_solicitada']:# or item_solicitado_instancia.id_unidad_medida.id_unidad_medida != i['id_unidad_medida_solicitada']:
                    raise ValidationError('Error en el numero_posicion (' + str(i['numero_posicion_despacho']) + ') del despacho. La cantidad solicitada o la unidad de medida solicitada no corresponde a las registrada en la solicitud')
                # VALIDACION 94:
                if i['cantidad_despachada'] == 0:
                    if i['id_bien_despachado'] != 0:
                       raise ValidationError('Si la cantidad a despachar de un bien solicitado es 0, en el campo (id_bien_despachado) debe ingresar 0')
                    if i['id_bodega'] != 0:
                        raise ValidationError('Si la cantidad a despachar de un bien solicitado es 0, en el campo (id_bodega) debe ingresar 0')
                    if i['observacion'] != 0:
                        raise ValidationError('Si la cantidad a despachar de un bien solicitado es 0, en el campo (observacion) debe ingresar 0')
                        
                    if i['id_bien_despachado'] == 0:
                        i['id_bien_despachado'] = None
                    if i['id_bodega'] == 0:
                        i['id_bodega'] = None
                    if i['observacion'] == 0:
                        i['observacion'] = 0

                if i['cantidad_despachada'] > 0:
                    bien_despachado = i.get('id_bien_despachado')
                    if not bien_despachado:
                        raise ValidationError('Debe ingresar un bien despachado')
                    bien_despachado_instancia = CatalogoBienes.objects.filter(id_bien=bien_despachado).first()
                    if not bien_despachado_instancia:
                        raise ValidationError('Debe ingresar un id_bien válido en el bien despachado')
                    nivel_bien_despachado = int(bien_despachado_instancia.nivel_jerarquico)
                    # SE VALIDA QUE EL BIEN DESPACHADO PERTENESCA A LA LINEA DEL BIEN SOLICITADO
                    cont = nivel_bien_despachado
                    arreglo_id_bienes_ancestros = []
                    while cont>0:
                        arreglo_id_bienes_ancestros.append(bien_despachado_instancia.id_bien)
                        if bien_despachado_instancia.nivel_jerarquico > 1:
                            bien_despachado_instancia = CatalogoBienes.objects.filter(id_bien=bien_despachado_instancia.id_bien_padre.id_bien).first()
                            if not bien_despachado_instancia:
                                raise ValidationError('Uno de los bienes no tiene padre')
                            nivel_bien_despachado = int(bien_despachado_instancia.nivel_jerarquico)
                        cont -= 1
                    # SE VALIDA QUE EL BIEN DESPACHADO SEA DESENDIENTE DEL BIEN SOLICITADO
                    if (bien_solicitado_instancia.id_bien_padre.id_bien not in arreglo_id_bienes_ancestros):
                        raise ValidationError('En el número de posición (' + str(i['numero_posicion_despacho']) + ') el bien solicitado no es de la misma linea del bien despachado')
                    bodega_solicita = i.get('id_bodega')
                    if bodega_solicita == None:
                        raise ValidationError('Debe ingresar un id de bodega válido')
                    instancia_bodega_solcitud = Bodegas.objects.filter(id_bodega = i['id_bodega']).first()
                    if not instancia_bodega_solcitud:
                        raise NotFound('El id de bodega no existe')
                    observaciones = i.get('observacion')
                    if observaciones == None:
                        raise ValidationError('El JSON debe contener un campo (observaciones)')
                    if len(observaciones) > 30:
                        raise ValidationError('La observacion solo puede contener hasta 30 caracteres')
                    # ESTO SE USA EN LA "VALIDACION 93" SE CREAN LAS CONDICIONES PARA LA VALIDACIÓN DE LA CANTIDAD DESPACHADA NO SUPERE LA SOLICITADA SI LAS UNIDADES SON IGUALES
                    aux_validacion_unidades_solicitado = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=solicitud_del_despacho_instancia.id_solicitud_consumibles) & Q(id_bien=i['id_bien_solicitado'])).first()
                    aux_validacion_unidades_despachado = CatalogoBienes.objects.filter(Q(id_bien=i['id_bien_despachado'])).first()
                    if aux_validacion_unidades_solicitado.id_bien.id_unidad_medida.nombre == aux_validacion_unidades_despachado.id_unidad_medida.nombre:
                        if i['cantidad_despachada'] > aux_validacion_unidades_solicitado.cantidad:
                            raise ValidationError('Una de las cantidades despachadas supera la cantidad solicitada')
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
                        raise ValidationError('Por favor verifique la existencia del bien en la bodega, o la existencia del bien en la tabla inventario')
                    valores_creados_detalles.append({'nombre' : instancia_inventario_auxiliar.id_bien.nombre})
                    #VALIDACION 96: SE VALIDA LAS CANTIDADES POSITIVAS DEL BIEN EN LA FECHA DEL DESPACHO
                    aux_validacion_cantidades_fecha_despacho = UtilAlmacen.get_valor_maximo_despacho(i['id_bien_despachado'], i['id_bodega'], despacho_maestro_instancia.id_despacho_consumo)
                    if i['cantidad_despachada'] > aux_validacion_cantidades_fecha_despacho:
                        raise ValidationError('Verifique que las cantidades del bien a despachar en la bodega ingresada en la fecha de despacho sean correctas')
                i['id_despacho_consumo'] = despacho_maestro_instancia.id_despacho_consumo
                # VALIDACION 90: SE VALIDA QUE UN BIEN DESPACHADO NO SE REPITA DENTRO DEL MISMO DESPACHO
                if [i['id_bien_solicitado'], i['id_bien_despachado'], i['id_bodega']] in aux_validacion_bienes_despachados_repetidos:
                    raise ValidationError('Error en los bienes despachados, no se puede despachar el mismo bien varias veces dentro de un despacho, elimine los bienes despachados repetidos')
                # ESTO SE USA PARA LA "VALIDACION 90"
                aux_validacion_bienes_despachados_repetidos.append([i['id_bien_solicitado'], i['id_bien_despachado'], i['id_bodega']])
                items_a_crear.append(i)

        # VALIDACION 93: SE VALIDAN LAS CANTIDADES SI TIENEN LA MISMA UNIDAD
        for key, value in aux_validacion_bienes_repetidos.items():
            aux_validacion_bienes_repetidos[key] = sum(value)
            aux_local_uno = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=solicitud_del_despacho_instancia.id_solicitud_consumibles) & Q(id_bien=int(key))).first()
            if int(aux_validacion_bienes_repetidos[key]) > aux_local_uno.cantidad:
                raise ValidationError('Una de las cantidades despachadas supera la cantidad solicitada')

        previous_maestro = copy.copy(despacho_maestro_instancia)
        
        serializer = self.serializer_class(despacho_maestro_instancia, data=info_despacho)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        valores_actualizados_maestro = {'previous':previous_maestro, 'current':despacho_maestro_instancia}
        
        # ELIMINAR ITEMS
        valores_eliminados_detalles = self.delete_items(items_despacho, items_despacho_instancia)
        
        # ACTUALIZAR ITEMS
        for i in items_a_actualizar:
            items_despacho_instancia = ItemDespachoConsumo.objects.filter(id_item_despacho_consumo=i['id_item_despacho_consumo']).first()
            previous_instancia_item = copy.copy(items_despacho_instancia)
            serializer_items = self.serializer_item_consumo(items_despacho_instancia, data=i)
            serializer_items.is_valid(raise_exception=True)
            serializer_items.save()
            valores_actualizados_detalles.append({'descripcion': {'nombre':items_despacho_instancia.id_bien_despachado.nombre}, 'previous':previous_instancia_item,'current':items_despacho_instancia})
        
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
            aux_suma = inventario_instancia.cantidad_saliente_consumo
            if aux_suma == None:
                aux_suma = 0
            inventario_instancia.cantidad_saliente_consumo = int(aux_suma) + i[2]
            inventario_instancia.save()   
            
        descripcion = {"numero_despacho_almacen": str(despacho_maestro_instancia.numero_despacho_consumo), "es_despacho_conservacion": "false", "fecha_despacho": str(despacho_maestro_instancia.fecha_despacho)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 35,
            "cod_permiso": "AC",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados_maestro": valores_actualizados_maestro,
            "valores_creados_detalles": valores_creados_detalles,
            "valores_actualizados_detalles": valores_actualizados_detalles,
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
            
        return Response({'success':True, 'detail':'Despacho actualizado con éxito'},status=status.HTTP_200_OK)

# class EliminarItemsDespacho(generics.DestroyAPIView):
#     serializer_class = SerializersItemDespachoConsumo
#     queryset=ItemDespachoConsumo.objects.all()

#     def destroy(self, request, id_despacho_consumo):
#         datos_ingresados = request.data
#         user_logeado = request.user
#         # VALIDACION 0: SE VALIDA EL QUE EL USUARIO ESTÉ LOGUEADO
#         if str(user_logeado) == 'AnonymousUser':
#             raise NotFound('Esta solicitud solo la puede ejecutar un usuario logueado')
#         ids_items_a_eliminar = [i['id_item_despacho_consumo'] for i in datos_ingresados]
#         instancia_despacho = DespachoConsumo.objects.filter(id_despacho_consumo=id_despacho_consumo).first()
#         aux_instancia_items = ItemDespachoConsumo.objects.filter(id_despacho_consumo=instancia_despacho.id_despacho_consumo)
#         if len(ids_items_a_eliminar) != len(set(ids_items_a_eliminar)):
#             raise NotFound('Verifique que no existan items repetidos dentro de la petición')
#         if len(aux_instancia_items) <= len(datos_ingresados):
#             raise NotFound('La cantidad de items que desea borrar es superior o igual a los que el despacho posee')
#         # SE VALDIA QUE EL DESPACHO NO SEA DE VIVERO
#         if instancia_despacho.es_despacho_conservacion != False:
#             raise NotFound('En este módulo solo se pueden elimanar items de despachos de consumo que no sean de viveros')
#         # VALIDACION 2: SE VALIDA QUE LA ACTUALIZACIÓN NO SE REALIZA EN UNA FECHA POSTERIOR A 45 DÍAS DESPUES DEL DESPACHO
#         fecha_despacho = instancia_despacho.fecha_despacho
#         aux_validacion_fechas = datetime.now() - fecha_despacho
#         if int(aux_validacion_fechas.days) > 45:
#             raise NotFound('No pueden eliminar los items de un despacho con fecha anterior a 45 días respecto a la actual')
#         # SE VALIDA QUE CADA UNO DE LOS ITEMS INGRESADOS PERTENEZCA A AL DESPACHO QUE SE INGRESÓ EN LA URL
#         for  i in datos_ingresados:
#             instance = ItemDespachoConsumo.objects.filter(Q(id_item_despacho_consumo=i['id_item_despacho_consumo']) & Q(id_despacho_consumo=instancia_despacho.id_despacho_consumo)).first()
#             if not instance:
#                 raise NotFound('Uno de los items que desea borrar no pertenece a la solicitud que ingresó')
#         # INSERT EN LA TABLA INVENTARIO
#         for i in datos_ingresados:
#             instance = ItemDespachoConsumo.objects.filter(Q(id_item_despacho_consumo=i['id_item_despacho_consumo']) & Q(id_despacho_consumo=instancia_despacho.id_despacho_consumo)).first()
#             inventario_instancia = Inventario.objects.filter(Q(id_bien=instance.id_bien_despachado)&Q(id_bodega=instance.id_bodega)).first()
#             aux_suma = inventario_instancia.cantidad_saliente_consumo
#             if aux_suma == None:
#                 aux_suma = 0
#             inventario_instancia.cantidad_saliente_consumo = int(aux_suma) - int(instance.cantidad_despachada)
#             inventario_instancia.save()
#         # SE BORRAN LOS ITEMS DEL DESPACHO
#         valores_eliminados_detalles = []
#         for  i in datos_ingresados:
#             instance = ItemDespachoConsumo.objects.filter(Q(id_item_despacho_consumo=i['id_item_despacho_consumo']) & Q(id_despacho_consumo=instancia_despacho.id_despacho_consumo)).first()
#             valores_eliminados_detalles.append({'nombre' : instance.id_bien_despachado.nombre})
#             instance.delete()
#         descripcion = {"numero_despacho_almacen": str(instancia_despacho.numero_despacho_consumo), "fecha_despacho": str(instancia_despacho.fecha_despacho)}
#         direccion=Util.get_client_ip(request)
#         auditoria_data = {
#             "id_usuario" : request.user.id_usuario,
#             "id_modulo" : 35,
#             "cod_permiso": "AC",
#             "subsistema": 'ALMA',
#             "dirip": direccion,
#             "descripcion": descripcion,
#             "valores_eliminados_detalles": valores_eliminados_detalles
#         }
#         Util.save_auditoria_maestro_detalle(auditoria_data)
#         return Response({'success':True, 'detail':'Se eliminaron los items del despacho de manera correcta'},status=status.HTTP_200_OK)

class AnularDespachoConsumo(generics.UpdateAPIView):
    serializer_class = SerializersDespachoConsumo
    queryset=DespachoConsumo.objects.all()
    
    def put(self, request, despacho_a_anular):
        # SE CAPTURAN LOS DATOS Y SE ADQUIERE EL DATO DE LA FECHA DE ANULACIÓN
        datos_ingresados = request.data
        datos_ingresados['fecha_anualacion'] = datetime.now()
        # VALIDACION DE USUARIO LOGUEADO
        user_logeado = request.user
        instancia_despacho_anular = DespachoConsumo.objects.filter(id_despacho_consumo=despacho_a_anular).first()
        if not instancia_despacho_anular:
            raise NotFound('No se encontró el despacho que quiere anular')
        if str(user_logeado) == 'AnonymousUser':
            raise NotFound('Esta solicitud solo la puede ejecutar un usuario logueado')
        # SE VALDIA QUE EL DESPACHO NO SEA DE VIVERO
        if instancia_despacho_anular.es_despacho_conservacion != False:
            raise NotFound('En este módulo solo se pueden anular despachos de bienes de consumo que no sean de viveros')
        # SE RESTA DEL INVENTARIO LAS CANTIDADES DESPACHAS DEL DESPACHO QUE SE ESTÁ ANULANDO
        items_despacho = ItemDespachoConsumo.objects.filter(id_despacho_consumo=despacho_a_anular)
        for i in items_despacho:
            inventario_instancia = Inventario.objects.filter(Q(id_bien=i.id_bien_despachado)&Q(id_bodega=i.id_bodega)).first()
            aux_suma = inventario_instancia.cantidad_saliente_consumo
            if aux_suma == None:
                aux_suma = 0
            inventario_instancia.cantidad_saliente_consumo = int(aux_suma) - int(i.cantidad_despachada)
            inventario_instancia.save()
            # SE BORRAN LOS ITEMS DEL DESPACHO
            items_despacho.delete()
        # INSERT EN LA TABLA SOLICITUDES DE CONSUMIBLES
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
        return Response({'success':True, 'detail':'Despacho anulado con éxito'},status=status.HTTP_200_OK)

class GetNroDocumentoDespachoBienesConsumo(generics.ListAPIView):
    # ESTA FUNCIONALIDAD PERMITE CONSULTAR EL ÚLTIMO NÚMERO DE DOCUMENTO DE LA CREACIÓN DE DESPACHO
    serializer_class = SerializersDespachoConsumo
    queryset=DespachoConsumo.objects.all()
    
    def get(self, request):
        nro_solicitud = DespachoConsumo.objects.all().order_by('numero_despacho_consumo').last()     
        salida = 0 if nro_solicitud == None else nro_solicitud.numero_despacho_consumo
        return Response({'success':True,'detail':salida + 1, },status=status.HTTP_200_OK)

class CerrarSolicitudDebidoInexistenciaView(generics.RetrieveUpdateAPIView):
    serializer_class = CerrarSolicitudDebidoInexistenciaSerializer
    queryset = SolicitudesConsumibles.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, id_solicitud):
        data = request.data
        
        #VALIDACIÓN SI EXISTE LA SOLICITUD ENVIADA
        solicitud = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=id_solicitud).first()
        if not solicitud:
            raise NotFound('No se encontró ninguna solicitud con los parámetros enviados')
        
        if solicitud.fecha_cierre_no_dispo_alm:
            raise PermissionDenied('No se puede cerrar una solicitud que ya está cerrada')
        
        #SUSTITUIR INFORMACIÓN A LA DATA
        data['fecha_cierre_no_dispo_alm'] = datetime.now()
        data['id_persona_cierre_no_dispo_alm'] = request.user.persona.id_persona
        data['solicitud_abierta'] = False
        data['fecha_cierre_solicitud'] = datetime.now()
        data['gestionada_almacen'] = True

        serializer = self.serializer_class(solicitud, data=data)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()
        
        #Auditoria Cerrar Solicitud
        usuario = request.user.id_usuario
        descripcion = {"Es solicitud conservación": str(serializador.es_solicitud_de_conservacion), "Numero solicitud por tipo": str(serializador.nro_solicitud_por_tipo)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 47,
            "cod_permiso": "AC",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion, 
        }
        Util.save_auditoria(auditoria_data)

        return Response({'success':True, 'detail':'Se cerró la solicitud correctamente'}, status=status.HTTP_201_CREATED)
        
    
class SearchSolicitudesAprobadasYAbiertos(generics.ListAPIView):
    serializer_class=SerializersSolicitudesConsumibles
    queryset=SolicitudesConsumibles.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        filter = {}
        fecha_despacho=request.query_params.get('fecha_despacho')
       
        if not fecha_despacho:
            raise ValidationError('Ingresa el parametro de fecha de despacho')
        
        filter['estado_aprobacion_responsable'] = "A"
        filter['solicitud_abierta'] = True
        fecha_despacho_strptime = datetime.strptime(
                fecha_despacho, '%Y-%m-%d %H:%M:%S')
        solicitudes=SolicitudesConsumibles.objects.filter(**filter).filter(fecha_aprobacion_responsable__lte=fecha_despacho_strptime)
        if solicitudes:
            serializador=self.serializer_class(solicitudes,many = True)
            return Response({'success':True, 'detail':'Se encontraron solicitudes aprobadas y abiertas','data':serializador.data},status = status.HTTP_200_OK)
        else:
            raise NotFound('No se encontraron solicitudes') 
        
class GetDespachoConsumoByNumeroDespacho(generics.ListAPIView):
    serializer_class= SerializersDespachoConsumoConItems
    queryset=DespachoConsumo.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        numero_despacho_consumo=request.query_params.get('numero_despacho_consumo')
        if not numero_despacho_consumo:
            raise ValidationError('Ingresa el parametro de fecha de despacho')
        despacho=DespachoConsumo.objects.filter(numero_despacho_consumo=numero_despacho_consumo).first()
        if despacho:
            serializador=self.serializer_class(despacho,many=False)
            return Response ({'success':True, 'detail':'Despacho encontrado','data':serializador.data},status=status.HTTP_200_OK)
        else:
            raise NotFound('No se encontraron despachos')

class FiltroDespachoConsumo(generics.ListAPIView):
    serializer_class= SerializersDespachoConsumo
    queryset=DespachoConsumo.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        if (request.query_params.get('numero_solicitud_por_tipo') != None and request.query_params.get('numero_solicitud_por_tipo') != "") and (request.query_params.get('es_despacho_conservacion') == None or request.query_params.get('es_despacho_conservacion')== ""):
            raise PermissionDenied('No puede filtrar por un número de solicitud sin haber definido si es despacho de conservación o no.')
        if (request.query_params.get('es_despacho_conservacion') != None and request.query_params.get('es_despacho_conservacion') != "") and (request.query_params.get('numero_solicitud_por_tipo') == None or request.query_params.get('numero_solicitud_por_tipo')== ""):
            raise PermissionDenied('Debe enviar el número de solicitud')

        filter={}
        
        for key,value in request.query_params.items():
            if key in ['numero_solicitud_por_tipo', 'fecha_despacho','id_unidad_para_la_que_solicita','es_despacho_conservacion']:
                if key != 'id_unidad_para_la_que_solicita' and key != 'es_despacho_conservacion':
                    filter[key+"__icontains"]=value
                else:
                    if value != '':
                        filter[key]=value
        
        if filter.get('es_despacho_conservacion') == 'true':
            filter['es_despacho_conservacion']=True
        elif filter.get('es_despacho_conservacion') == 'false':
            filter['es_despacho_conservacion']=False
        
        despachos=DespachoConsumo.objects.filter(**filter)
        if despachos:
            serializador=self.serializer_class(despachos,many=True)
            return Response ({'success':True, 'detail':'Despacho encontrado','data':serializador.data},status=status.HTTP_200_OK)
        return Response ({'success':True, 'detail':'No se encontraron despachos','data':[]},status=status.HTTP_200_OK)

class SearchBienInventario(generics.ListAPIView):
    serializer_class=SearchBienInventarioSerializer
    queryset=Inventario.objects.all()
    
    def get(self,request):
        codigo_bien = request.query_params.get('codigo_bien')
        id_bodega = request.query_params.get('id_bodega')
        fecha_despacho = request.query_params.get('fecha_despacho')
        
        if (not codigo_bien or codigo_bien == '') or (not id_bodega or id_bodega == '') or (not fecha_despacho or fecha_despacho == ''):
            raise ValidationError('Debe ingresar los parámetros de búsqueda')

        bien = CatalogoBienes.objects.filter(codigo_bien=codigo_bien, cod_tipo_bien='C', nivel_jerarquico=5).first()
        fecha_despacho_strptime = datetime.strptime(fecha_despacho, '%Y-%m-%d %H:%M:%S')
        
        if bien:
            items_despachados = ItemDespachoConsumo.objects.filter(id_bien_despachado=bien.id_bien, id_bodega=id_bodega,id_despacho_consumo__fecha_despacho__gte=fecha_despacho_strptime)
            if items_despachados:
                try:
                    raise PermissionDenied('El bien tiene despachos o entregas posteriores a la fecha de despacho elegida')
                except PermissionDenied as e:
                    return Response({'success':False, 'detail':'El bien tiene despachos o entregas posteriores a la fecha de despacho elegida', 'data': []}, status=status.HTTP_403_FORBIDDEN)
            
            inventario = Inventario.objects.filter(id_bien=bien.id_bien, id_bodega=id_bodega).first()
            
            cantidad_disponible = UtilAlmacen.get_cantidad_disponible(bien.id_bien, id_bodega, fecha_despacho_strptime)
            
            if cantidad_disponible <= 0:
                raise ValidationError('El bien seleccionado no tiene cantidad disponible')
                   
            inventario.cantidad_disponible=cantidad_disponible
            serializador_inventario = self.serializer_class(inventario)
            
            
            return Response({'success':True, 'detail':'Se encontró el siguiente resultado', 'data': serializador_inventario.data}, status=status.HTTP_200_OK)
        else:
            try:
                raise NotFound('El bien no existe')
            except NotFound as e:
                return Response({'success':False, 'detail':'El bien no existe', 'data': []}, status=status.HTTP_404_NOT_FOUND)
        
class SearchBienesInventario(generics.ListAPIView):
    serializer_class=SearchBienInventarioSerializer
    queryset=Inventario.objects.all()
    
    def get(self,request):
        codigo_bien = request.query_params.get('codigo_bien_solicitado')
        fecha_despacho = request.query_params.get('fecha_despacho')
        
        if (not codigo_bien or codigo_bien == '')  or (not fecha_despacho or fecha_despacho == ''):
            raise ValidationError('Debe ingresar los parámetros de búsqueda')
        
        bienes = CatalogoBienes.objects.filter(codigo_bien__startswith=codigo_bien, cod_tipo_bien='C', nivel_jerarquico=5)

        fecha_despacho_strptime = datetime.strptime(fecha_despacho, '%Y-%m-%d %H:%M:%S')
        
        if bienes:
            bien_id_bien = [bien.id_bien for bien in bienes]
            bien_inventario = Inventario.objects.filter(id_bien__in=bien_id_bien)
            
            cantidades_disponibles = UtilAlmacen.get_cantidades_disponibles(bien_id_bien, fecha_despacho_strptime)

            inventarios_disponibles = []
            for inventario in bien_inventario:
                cantidad_disponible = [cantidad_disponible['cantidad_disponible'] for cantidad_disponible in cantidades_disponibles if cantidad_disponible['id_bien'] == inventario.id_bien.id_bien and cantidad_disponible['id_bodega'] == inventario.id_bodega.id_bodega][0]
                inventario.cantidad_disponible = cantidad_disponible
                inventario.disponible=True
                        
                items_despachados = ItemDespachoConsumo.objects.filter(id_bien_despachado=inventario.id_bien.id_bien,id_bodega=inventario.id_bodega.id_bodega,id_despacho_consumo__fecha_despacho__gte=fecha_despacho_strptime)

                if items_despachados:
                    inventario.disponible=False
                    inventario.cantidad_disponible=None
                    
                if cantidad_disponible > 0 and (inventario.disponible==True or inventario.disponible ==  False):
                    inventarios_disponibles.append(inventario)
                if cantidad_disponible <= 0 and inventario.disponible==False:
                    inventarios_disponibles.append(inventario)
                        
            serializador = self.serializer_class(inventarios_disponibles, many=True)
        
            return Response({'success':True, 'detail':'Se encontró el siguiente resultado','data':serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':True, 'detail':'El bien no existe', 'data': []}, status=status.HTTP_200_OK)

class AgregarBienesConsumoConservacionByCodigoBien(generics.ListAPIView):
    serializer_class=AgregarBienesConsumoConservacionSerializer
    queryset=CatalogoBienes.objects.all()
    
    def get(self,request):
        codigo_bien = request.query_params.get('codigo_bien')
        id_bodega = request.query_params.get('id_bodega')
        fecha_despacho = request.query_params.get('fecha_despacho')
        
        if (not codigo_bien or codigo_bien == '') or (not id_bodega or id_bodega == '') or (not fecha_despacho or fecha_despacho == ''):
            raise ValidationError('Debe ingresar los parámetros de búsqueda')

        bien = CatalogoBienes.objects.filter(codigo_bien=codigo_bien, solicitable_vivero=True, cod_tipo_bien='C', nivel_jerarquico=5).first()
        fecha_despacho_strptime = datetime.strptime(fecha_despacho, '%Y-%m-%d %H:%M:%S')
        if bien:
            items_despachados = ItemDespachoConsumo.objects.filter(id_bien_despachado=bien.id_bien,  id_bodega=id_bodega,id_despacho_consumo__fecha_despacho__gte=fecha_despacho_strptime)
            if items_despachados:
                try:
                    raise PermissionDenied('El bien tiene despachos o entregas posteriores a la fecha de despacho elegida')
                except PermissionDenied as e:
                    return Response({'success':False, 'detail':'El bien tiene despachos o entregas posteriores a la fecha de despacho elegida', 'data': []}, status=status.HTTP_403_FORBIDDEN)
                
            bien_inventario = Inventario.objects.filter(id_bien=bien.id_bien, id_bodega=id_bodega).first()
            
            cantidad_actual = UtilAlmacen.get_cantidad_disponible(bien.id_bien, id_bodega, fecha_despacho_strptime)
            bien_inventario.cantidad_disponible=cantidad_actual
            if cantidad_actual <= 0:
                raise ValidationError('El bien seleccionado no tiene cantidad disponible')
                    
            serializador=self.serializer_class(bien_inventario,many=False)
            
            return Response({'success':True, 'detail':'Se encontró el siguiente resultado','data':serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':True, 'detail':'El bien no existe', 'data': []}, status=status.HTTP_200_OK)
        

class AgregarBienesConsumoConservacionByLupa(generics.ListAPIView):
    serializer_class=AgregarBienesConsumoConservacionSerializer
    queryset=CatalogoBienes.objects.all()
    
    def get(self,request):
        codigo_bien = request.query_params.get('codigo_bien_solicitado')
        fecha_despacho = request.query_params.get('fecha_despacho')
        
        if (not codigo_bien or codigo_bien == '')  or (not fecha_despacho or fecha_despacho == ''):
            raise ValidationError('Debe ingresar los parámetros de búsqueda')

        bienes = CatalogoBienes.objects.filter(codigo_bien__startswith=codigo_bien, solicitable_vivero=True, cod_tipo_bien='C', nivel_jerarquico=5)

        fecha_despacho_strptime = datetime.strptime(fecha_despacho, '%Y-%m-%d %H:%M:%S')
        
        if bienes:
            bien_id_bien = [bien.id_bien for bien in bienes]
            
            bien_inventario = Inventario.objects.filter(id_bien__in=bien_id_bien)
            
            cantidades_disponibles = UtilAlmacen.get_cantidades_disponibles(bien_id_bien, fecha_despacho_strptime)
            inventarios_disponibles = []

            for inventario in bien_inventario:
                cantidad_disponible = [cantidad_disponible['cantidad_disponible'] for cantidad_disponible in cantidades_disponibles if cantidad_disponible['id_bien'] == inventario.id_bien.id_bien and cantidad_disponible['id_bodega'] == inventario.id_bodega.id_bodega][0]
                inventario.cantidad_disponible = cantidad_disponible
                inventario.disponible=True

                items_despachados = ItemDespachoConsumo.objects.filter(id_bien_despachado=inventario.id_bien.id_bien,id_bodega=inventario.id_bodega.id_bodega,id_despacho_consumo__fecha_despacho__gte=fecha_despacho_strptime)

                if items_despachados:
                    inventario.disponible=False
                    inventario.cantidad_disponible=None
                    
                if cantidad_disponible > 0 and (inventario.disponible==True or inventario.disponible ==  False):
                    inventarios_disponibles.append(inventario)
                if cantidad_disponible <= 0 and inventario.disponible==False:
                    inventarios_disponibles.append(inventario)
    
            serializador = self.serializer_class(inventarios_disponibles, many=True)

            return Response({'success':True, 'detail':'Se encontraron los siguientes resultados','data':serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':True, 'detail':'El bien no existe', 'data': []}, status=status.HTTP_200_OK)

class GetItemOtrosOrigenes(generics.ListAPIView):
    serializer_class=GetItemOtrosOrigenesSerializers
    queryset=EntradasAlmacen.objects.all()
    
    def get(self,request,id_bien):
        fecha_hace_un_año=datetime.today()-timedelta(days=365)
        fecha_despacho=request.query_params.get('fecha_despacho')
        if not fecha_despacho:
            raise PermissionDenied('Envía el parámetro de fecha de despacho del despacho')
        
        items=ItemEntradaAlmacen.objects.filter(
            id_bien=id_bien,id_entrada_almacen__fecha_entrada__gte=fecha_hace_un_año,
            id_entrada_almacen__fecha_entrada__lte=fecha_despacho).filter(
                Q(id_entrada_almacen__id_tipo_entrada=2) | 
                Q(id_entrada_almacen__id_tipo_entrada=3) | 
                Q(id_entrada_almacen__id_tipo_entrada=4)).values(
                    'id_bien',"id_entrada_almacen",
                    codigo_bien=F('id_bien__codigo_bien'),
                    nombre=F('id_bien__nombre'),
                    numero_documento=F('id_entrada_almacen__numero_entrada_almacen'),
                    tipo_documento=F('id_entrada_almacen__id_tipo_entrada__nombre')).annotate(cantidad_total_entrada=Sum('cantidad'))
                
        items_list=[item['id_entrada_almacen'] for item in items]
        items_despachados=ItemDespachoConsumo.objects.filter(id_bien_despachado=id_bien,id_entrada_almacen_bien__in=items_list).values('id_bien_despachado','id_entrada_almacen_bien').annotate(cantidad_total_despachada=Sum('cantidad_despachada'))
        items_por_distribuir=[]
        for item in items:
            item_despachado= [despacho for despacho in items_despachados if despacho['id_bien_despachado'] == item['id_bien'] and despacho['id_entrada_almacen_bien']==item['id_entrada_almacen']]
            item['cantidad_por_distribuir']=item['cantidad_total_entrada']-item_despachado[0]['cantidad_total_despachada'] if item_despachado else item['cantidad_total_entrada']
            if item['cantidad_por_distribuir'] > 0:
                items_por_distribuir.append(item)
        return Response({'success':True, 'detail':'Se encontraron los siguientes resultados','data':items_por_distribuir}, status=status.HTTP_200_OK)
        
        
        