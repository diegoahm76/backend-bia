from rest_framework import status
from seguridad.utils import Util
from conservacion.models.viveros_models import (
    Vivero
)
from conservacion.models.despachos_models import (
    DespachoEntrantes,
    ItemsDespachoEntrante,
    DistribucionesItemDespachoEntrante
)
from conservacion.serializers.despachos_serializers import (
    DistribucionesItemDespachoEntranteSerializer
)
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
import copy

class UtilConservacion:
    
    @staticmethod
    def guardar_distribuciones(id_despacho_entrante, request, distribuciones_items, confirmacion=False):
        response_dict = {'success':True, 'detail':'', 'status':status.HTTP_201_CREATED}
        despacho_entrante=DespachoEntrantes.objects.filter(id_despacho_entrante=id_despacho_entrante).first()
        if despacho_entrante:
            data = request.data
            user = request.user.persona
            observacion_distribucion = request.query_params.get('observaciones_distribucion')
            
            # VALIDAR SI DESPACHO YA HA SIDO CONFIRMADO
            if  despacho_entrante.distribucion_confirmada == True:
                response_dict['success'] = False
                response_dict['detail'] = 'El despacho ya ha sido confirmado'
                response_dict['status'] = status.HTTP_403_FORBIDDEN
                return response_dict
                
            # VALIDAR EXISTENCIA DE ITEMS
            items_id_list = [item['id_item_despacho_entrante'] for item in data]
            items_despacho_entrante = ItemsDespachoEntrante.objects.filter(id_item_despacho_entrante__in=items_id_list)
            if len(set(items_id_list)) != len(items_despacho_entrante):
                response_dict['success'] = False
                response_dict['detail'] = 'Debe elegir items de despacho entrante existentes'
                response_dict['status'] = status.HTTP_400_BAD_REQUEST
                return response_dict
            
            # VALIDAR EXISTENCIA DE ITEMS PARA DESPACHO ELEGIDO
            items_despachos_distintos = items_despacho_entrante.exclude(id_despacho_entrante=id_despacho_entrante)
            if items_despachos_distintos:
                response_dict['success'] = False
                response_dict['detail'] = 'No puede enviar items de otro despacho distinto al seleccionado'
                response_dict['status'] = status.HTTP_400_BAD_REQUEST
                return response_dict
                
            # VALIDAR EXISTENCIA DE VIVEROS
            viveros_id_list = [item['id_vivero'] for item in data]
            viveros = Vivero.objects.filter(id_vivero__in=viveros_id_list)
            if len(set(viveros_id_list)) != len(viveros):
                response_dict['success'] = False
                response_dict['detail'] = 'Debe elegir viveros existentes'
                response_dict['status'] = status.HTTP_400_BAD_REQUEST
                return response_dict
            
            # VALIDAR CANTIDADES MAYOR A CERO
            cantidades = [item['cantidad_asignada'] for item in data]
            if cantidades.count(0) > 0:
                response_dict['success'] = False
                response_dict['detail'] = 'Debe distribuir cantidades mayores a cero'
                response_dict['status'] = status.HTTP_400_BAD_REQUEST
                return response_dict
            
            # VALIDAR CODIGOS ETAPA LOTE
            dict_cod_etapa_lote = [x for x,y in cod_etapa_lote_CHOICES]
            cod_etapa_lote_list = [item['cod_etapa_lote_al_ingresar'] for item in data]
            if not set(cod_etapa_lote_list).issubset(dict_cod_etapa_lote):
                response_dict['success'] = False
                response_dict['detail'] = 'Debe seleccionar códigos de etapa lote existentes'
                response_dict['status'] = status.HTTP_400_BAD_REQUEST
                return response_dict

            # VALIDAR UNICIDAD ITEM DESPACHO Y VIVERO
            items_viveros = [{'id_item_despacho_entrante': item['id_item_despacho_entrante'], 'id_vivero': item['id_vivero']} for item in data]
            items_viveros = [dict(t) for t in {tuple(d.items()) for d in items_viveros}]
            for item_vivero in items_viveros:
                duplicados = [item for item in data if item['id_item_despacho_entrante'] == item_vivero['id_item_despacho_entrante'] and item['id_vivero'] == item_vivero['id_vivero']]
                if len(duplicados) > 1:
                    response_dict['success'] = False
                    response_dict['detail'] = 'El item despacho entrante y el vivero deben ser una pareja única'
                    response_dict['status'] = status.HTTP_400_BAD_REQUEST
                    return response_dict
            
            # ACTUALIZAR EN DESPACHO ENTRANTE
            despacho_entrante.observacion_distribucion = observacion_distribucion
            despacho_entrante.id_persona_distribuye = user
            despacho_entrante.save()
            
            items_create = []
            
            valores_actualizados_detalles = []
            valores_eliminados_detalles = []
            
            for item in items_despacho_entrante:
                # ELIMINAR ITEMS DESPACHO ENTRANTE
                distribuciones_item_despacho = distribuciones_items.filter(id_item_despacho_entrante = item.id_item_despacho_entrante)
                viveros_id = [obj['id_vivero'] for obj in items_viveros if obj['id_item_despacho_entrante']==item.id_item_despacho_entrante]
            
                distribuciones_items_eliminar = distribuciones_item_despacho.exclude(id_vivero__in=viveros_id)
                valores_eliminados_detalles = [{'nombre_bien': item_eliminar.id_item_despacho_entrante.id_bien.nombre} for item_eliminar in distribuciones_items_eliminar]
                distribuciones_items_eliminar.delete()

                # ACTUALIZAR ITEMS DESPACHO ENTRANTE
                cantidades_item = [obj['cantidad_asignada'] for obj in data if obj['id_item_despacho_entrante']==item.id_item_despacho_entrante]
                cantidad_total_item = sum(cantidades_item)
                
                if cantidad_total_item > item.cantidad_entrante:
                    response_dict['success'] = False
                    response_dict['detail'] = 'La cantidad distribuida del bien ' + item.id_bien.nombre + ' no puede superar la cantidad entrante de ' + str(item.cantidad_entrante)
                    response_dict['status'] = status.HTTP_400_BAD_REQUEST
                    return response_dict
                
                # VALIDACION PARA CONFIRMACION CUANDO NO TIENE TODAS LAS UNIDADES DISTRIBUIDAS
                if confirmacion and (cantidad_total_item != item.cantidad_entrante):
                    response_dict['success'] = False
                    response_dict['detail'] = 'El bien ' + item.id_bien.nombre + ' no tiene todas las unidades pre-distribuidas'
                    response_dict['status'] = status.HTTP_400_BAD_REQUEST
                    return response_dict
                
                # VALIDACION PARA CONFIRMACION CUANDO NO EL ITEM NO ESTÁ CORRECTAMENTE TIPIFICADO
                if confirmacion and (item.id_bien.es_semilla_vivero == None or item.id_bien.cod_tipo_elemento_vivero == None):
                    response_dict['success'] = False
                    response_dict['detail'] = 'El bien ' + item.id_bien.nombre + ' no está correctamente tipificado'
                    response_dict['status'] = status.HTTP_400_BAD_REQUEST
                    return response_dict
                
                item_despacho_entrante = items_despacho_entrante.filter(id_item_despacho_entrante=item.id_item_despacho_entrante).first()
                item_despacho_entrante.cantidad_distribuida = cantidad_total_item
                item_despacho_entrante.save()
            
            for item in data:
                distribucion_item = DistribucionesItemDespachoEntrante.objects.filter(id_item_despacho_entrante=item['id_item_despacho_entrante'], id_vivero=item['id_vivero']).first()
                distribucion_item_previous = copy.copy(distribucion_item)
                
                if distribucion_item:
                    valores_actualizados_detalles.append({'descripcion': {'nombre_bien':distribucion_item.id_item_despacho_entrante.id_bien.nombre}, 'previous':distribucion_item_previous,'current':distribucion_item})
                    serializer_update = DistribucionesItemDespachoEntranteSerializer(distribucion_item, data=item)
                    serializer_update.is_valid(raise_exception=True)
                    serializer_update.save()
                else:
                    items_create.append(item)
            
            # VALIDACION PARA CONFIRMACION CUANDO NO SE HA DISTRIBUIDO TODAS LAS UNIDADES DE UN ITEM
            items_no_distribuidos = ItemsDespachoEntrante.objects.filter(id_despacho_entrante=id_despacho_entrante).exclude(id_item_despacho_entrante__in=items_id_list)
            items_no_distribuidos_id = [item_no_distribuido.id_item_despacho_entrante for item_no_distribuido in items_no_distribuidos]
            if confirmacion:
                for item_no_distribuido in set(items_no_distribuidos_id):
                    bien = items_no_distribuidos.filter(id_item_despacho_entrante=item_no_distribuido).first()
                    response_dict['success'] = False
                    response_dict['detail'] = 'Le falta distribuir todas las unidades del ' + bien.id_bien.nombre
                    response_dict['status'] = status.HTTP_400_BAD_REQUEST
                    return response_dict
            
            # ELIMINAR ITEMS DESPACHO ENTRANTE
            distribuciones_items_eliminar = distribuciones_items.filter(id_item_despacho_entrante__in=items_no_distribuidos)
            distribuciones_items_eliminar_id = [distribucion_item.id_item_despacho_entrante.id_item_despacho_entrante for distribucion_item in distribuciones_items_eliminar]
            if distribuciones_items_eliminar_id:
                for distribucion_item in set(distribuciones_items_eliminar_id):
                    item_despacho_entrante = ItemsDespachoEntrante.objects.filter(id_item_despacho_entrante=distribucion_item).first()
                    item_despacho_entrante.cantidad_distribuida = 0
                    item_despacho_entrante.save()
                valores_eliminados_detalles.extend([{'nombre_bien': item_eliminar.id_item_despacho_entrante.id_bien.nombre} for item_eliminar in distribuciones_items_eliminar])
                distribuciones_items_eliminar.delete()
            
            valores_creados_detalles = []
            
            # CREAR ITEMS DESPACHO ENTRANTE
            if items_create:
                items_create_id = [item_create['id_item_despacho_entrante'] for item_create in items_create]
                items_despacho_entrante_create = items_despacho_entrante.filter(id_item_despacho_entrante__in=items_create_id)
                for item_create in items_create:
                    item_despacho_entrante_create = items_despacho_entrante_create.filter(id_item_despacho_entrante=item_create['id_item_despacho_entrante']).first()
                    item_create['nombre_bien'] = item_despacho_entrante_create.id_bien.nombre
                valores_creados_detalles = [{'nombre_bien': item_create['nombre_bien']} for item_create in items_create]
                
                serializer_create = DistribucionesItemDespachoEntranteSerializer(data=items_create, many=True)
                serializer_create.is_valid(raise_exception=True)
                serializer_create.save()
            
            response_dict['detail'] = 'Se realizó el guardado de las distribuciones correctamente'
            
            # AUDITORIA MAESTRO DETALLE
            descripcion_maestro = {
                "numero_despacho_consumo": str(despacho_entrante.id_despacho_consumo_alm.numero_despacho_consumo),
                "fecha_ingreso": str(despacho_entrante.fecha_ingreso),
                "distribucion_confirmada": str(despacho_entrante.distribucion_confirmada),
                "fecha_confirmacion_distribucion": str(despacho_entrante.fecha_confirmacion_distribucion),
                "observacion_distribucion": str(despacho_entrante.observacion_distribucion),
                "persona_distribuye": str(despacho_entrante.id_persona_distribuye.primer_nombre + ' ' + despacho_entrante.id_persona_distribuye.primer_apellido if despacho_entrante.id_persona_distribuye.tipo_persona=='N' else despacho_entrante.id_persona_distribuye.razon_social)
            }
            direccion=Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario": request.user.id_usuario,
                "id_modulo": 48,
                "cod_permiso": 'AC',
                "subsistema": 'CONS',
                "dirip": direccion,
                "descripcion": descripcion_maestro,
                "valores_creados_detalles": valores_creados_detalles,
                "valores_actualizados_detalles": valores_actualizados_detalles,
                "valores_eliminados_detalles": valores_eliminados_detalles
            }
            Util.save_auditoria_maestro_detalle(auditoria_data)
            
            return response_dict
        else:
            response_dict['success'] = False
            response_dict['detail'] = 'El despacho entrante elegido no existe'
            response_dict['status'] = status.HTTP_404_NOT_FOUND
            return response_dict