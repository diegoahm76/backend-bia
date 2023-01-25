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

class UtilConservacion:
    
    @staticmethod
    def guardar_distribuciones(id_despacho_entrante, request, distribuciones_items):
        response_dict = {'success':True, 'detail':'', 'status':status.HTTP_201_CREATED}
        despacho_entrante=DespachoEntrantes.objects.filter(id_despacho_entrante=id_despacho_entrante).first()
        if despacho_entrante:
            data = request.data
            user = request.user.persona
            observacion_distribucion = request.query_params.get('observaciones_distribucion')
            
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
            print("ITEMS_VIVEROS: ", items_viveros)
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
            
            for item in items_despacho_entrante:
                # ELIMINAR ITEMS DESPACHO ENTRANTE
                distribuciones_item_despacho = distribuciones_items.filter(id_item_despacho_entrante = item.id_item_despacho_entrante)
                viveros_id = [obj['id_vivero'] for obj in items_viveros if obj['id_item_despacho_entrante']==item.id_item_despacho_entrante]
            
                distribuciones_items_eliminar = distribuciones_item_despacho.exclude(id_vivero__in=viveros_id)
                distribuciones_items_eliminar.delete()

                # ACTUALIZAR ITEMS DESPACHO ENTRANTE
                cantidades_item = [obj['cantidad_asignada'] for obj in data if obj['id_item_despacho_entrante']==item.id_item_despacho_entrante]
                cantidad_total_item = sum(cantidades_item)
                
                if cantidad_total_item > item.cantidad_entrante:
                    response_dict['success'] = False
                    response_dict['detail'] = 'La cantidad distribuida del bien ' + item.id_bien.nombre + ' no puede superar la cantidad entrante de ' + str(item.cantidad_entrante)
                    response_dict['status'] = status.HTTP_400_BAD_REQUEST
                    return response_dict
                
                item_despacho_entrante = items_despacho_entrante.filter(id_item_despacho_entrante=item.id_item_despacho_entrante).first()
                item_despacho_entrante.cantidad_distribuida = cantidad_total_item
                item_despacho_entrante.save()
            
            for item in data:
                distribucion_item = DistribucionesItemDespachoEntrante.objects.filter(id_item_despacho_entrante=item['id_item_despacho_entrante'], id_vivero=item['id_vivero']).first()
                if distribucion_item:
                    serializer_update = DistribucionesItemDespachoEntranteSerializer(distribucion_item, data=item)
                    serializer_update.is_valid(raise_exception=True)
                    serializer_update.save()
                else:
                    items_create.append(item)
            
            # ELIMINAR ITEMS DESPACHO ENTRANTE
            distribuciones_items_eliminar = distribuciones_items.exclude(id_item_despacho_entrante__in=items_id_list)
            distribuciones_items_eliminar_id = [distribucion_item.id_item_despacho_entrante.id_item_despacho_entrante for distribucion_item in distribuciones_items_eliminar]
            for distribucion_item in set(distribuciones_items_eliminar_id):
                item_despacho_entrante = ItemsDespachoEntrante.objects.filter(id_item_despacho_entrante=distribucion_item).first()
                item_despacho_entrante.cantidad_distribuida = 0
                item_despacho_entrante.save()
                
            distribuciones_items_eliminar.delete()
            
            # CREAR ITEMS DESPACHO ENTRANTE
            if items_create:
                serializer_create = DistribucionesItemDespachoEntranteSerializer(data=items_create, many=True)
                serializer_create.is_valid(raise_exception=True)
                serializer_create.save()
            
            response_dict['detail'] = 'Se realizó el guardado de las distribuciones correctamente'
            
            # AUDITORIA MAESTRO DETALLE
            # descripcion = {"numero_despacho_consumo": str(info_despacho['id_despacho_consumo_alm']), "es_despacho_conservacion": "false", "fecha_despacho": str(info_despacho['fecha_despacho'])}
            # direccion=Util.get_client_ip(request)
            # auditoria_data = {
            #     "id_usuario": request.user.id_usuario,
            #     "id_modulo": 48,
            #     "cod_permiso": 'AC',
            #     "subsistema": 'CONS',
            #     "dirip": direccion,
            #     "descripcion": descripcion,
            #     "valores_creados_detalles": valores_eliminados_detalles,
            #     "valores_actualizados_detalles": valores_eliminados_detalles,
            #     "valores_eliminados_detalles": valores_eliminados_detalles
            # }
            # Util.save_auditoria_maestro_detalle(auditoria_data)
            
            return response_dict
        else:
            response_dict['success'] = False
            response_dict['detail'] = 'El despacho entrante elegido no existe'
            response_dict['status'] = status.HTTP_404_NOT_FOUND
            return response_dict