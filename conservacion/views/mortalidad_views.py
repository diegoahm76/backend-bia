from django.urls import path
from rest_framework.response import Response
from conservacion.views import mortalidad_views as views
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from almacen.models import (
    CatalogoBienes
)
from conservacion.models import (
    BajasVivero,
    ItemsBajasVivero,
    InventarioViveros,
    Vivero,
    CuarentenaMatVegetal
)
from conservacion.serializers.mortalidad_serializers import (
    RegistrarMortalidadSerializer,
    MortalidadMaterialVegetalSerializer,
    RegistrarItemsMortalidadSerializer,
    ActualizarMortalidadSerializer,
    ActualizarItemsMortalidadSerializer
)
from conservacion.utils import UtilConservacion
import json

class GetMaterialVegetalByCodigo(generics.ListAPIView):
    serializer_class=MortalidadMaterialVegetalSerializer
    queryset=InventarioViveros.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get(self,request,id_vivero):
        codigo_bien = request.query_params.get('codigo_bien')
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        
        # VALIDAR EXISTENCIA DEL VIVERO
        if not vivero:
            return Response({'success':False, 'detail':'Debe elegir un vivero que exista'}, status=status.HTTP_404_NOT_FOUND)
        
        catalogo_bien = CatalogoBienes.objects.filter(codigo_bien=codigo_bien).first()
        
        # VALIDACIONES DEL CÓDIGO BIEN
        if not catalogo_bien:
            return Response({'success':False, 'detail':'El código ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
        
        if catalogo_bien.cod_tipo_elemento_vivero:
            if catalogo_bien.cod_tipo_elemento_vivero != 'MV' or (catalogo_bien.cod_tipo_elemento_vivero == 'MV' and catalogo_bien.es_semilla_vivero):
                return Response({'success':False, 'detail':'El código ingresado no es el código de una planta o una plántula'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success':False, 'detail':'El código ingresado no es de consumo o no se encuentra tipificado'}, status=status.HTTP_400_BAD_REQUEST)
           
        inventarios_viveros = InventarioViveros.objects.filter(id_bien__codigo_bien=codigo_bien, id_bien__cod_tipo_elemento_vivero='MV', id_bien__es_semilla_vivero=False).exclude(cod_etapa_lote='G')
        serializador = self.serializer_class(inventarios_viveros, many=True)
        
        data_serializada = serializador.data
        saldos_disponibles = [data['saldo_disponible'] for data in data_serializada]
        
        if data_serializada:
            if len(set(saldos_disponibles)) == 1 and list(set(saldos_disponibles))[0] == 0:
                return Response({'success':False, 'detail':'El código ingresado es de una planta que no tiene saldo disponible en ningún lote-etapa'}, status=status.HTTP_403_FORBIDDEN)
        
        data_serializada = [data for data in data_serializada if data['saldo_disponible'] != 0]
        
        return Response ({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data':data_serializada}, status=status.HTTP_200_OK)

class GetMaterialVegetalByLupa(generics.ListAPIView):
    serializer_class=MortalidadMaterialVegetalSerializer
    queryset=InventarioViveros.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get(self,request,id_vivero):
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        
        # VALIDAR EXISTENCIA DEL VIVERO
        if not vivero:
            return Response({'success':False, 'detail':'Debe elegir un vivero que exista'}, status=status.HTTP_404_NOT_FOUND)
        
        filtro = {}
        for key,value in request.query_params.items():
            if key in ['codigo_bien','nombre','cod_etapa_lote']:
                if key == 'codigo_bien':
                    filtro['id_bien__' + key + '__startswith'] = value
                elif key == 'nombre':
                    filtro['id_bien__' + key + '__icontains'] = value
                else:
                    if value != '':
                        filtro[key]=value
        
        inventarios_viveros = InventarioViveros.objects.filter(**filtro).filter(id_vivero=id_vivero, id_bien__cod_tipo_elemento_vivero='MV', id_bien__es_semilla_vivero=False).exclude(cod_etapa_lote='G')
        serializador = self.serializer_class(inventarios_viveros, many=True)
        
        data_serializada = serializador.data
        data_serializada = [data for data in data_serializada if data['saldo_disponible'] >= 1]
        
        return Response ({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data':data_serializada}, status=status.HTTP_200_OK)
    
class RegistrarMortalidad(generics.CreateAPIView):
    serializer_class=RegistrarMortalidadSerializer
    queryset=InventarioViveros.objects.all()
    permission_classes=[IsAuthenticated]
    
    def post(self,request):
        data = request.data
        persona = request.user.persona.id_persona
        
        data_mortalidad = json.loads(data['data_mortalidad'])
        data_items_mortalidad = json.loads(data['data_items_mortalidad'])
        
        data_mortalidad['ruta_archivo_soporte'] = request.FILES.get('ruta_archivo_soporte')
        data_mortalidad['tipo_baja'] = 'M'
        data_mortalidad['id_persona_baja'] = persona
        
        ultima_mortalidad = BajasVivero.objects.filter(tipo_baja='M').last()
        nro_baja = ultima_mortalidad.nro_baja_por_tipo + 1 if ultima_mortalidad and ultima_mortalidad.nro_baja_por_tipo else 1
        data_mortalidad['nro_baja_por_tipo'] = nro_baja
        
        fecha_baja = datetime.strptime(data_mortalidad['fecha_baja'], "%Y-%m-%d %H:%M:%S")
        fecha_posible = datetime.now() - timedelta(days=1)
        
        # VALIDACIONES MAESTRO
        serializador_maestro = self.serializer_class(data=data_mortalidad)
        serializador_maestro.is_valid(raise_exception=True)
        
        if fecha_baja < fecha_posible:
            return Response({'success':False, 'detail':'La fecha de baja no puede superar las 24 horas'}, status=status.HTTP_400_BAD_REQUEST)
        
        if ultima_mortalidad:
            if fecha_baja < ultima_mortalidad.fecha_baja:
                return Response({'success':False, 'detail':'La fecha de baja no puede superar la fecha de mortalidad del último registro en el sistema (' + str(ultima_mortalidad.fecha_baja) + ')'}, status=status.HTTP_400_BAD_REQUEST)
        
        # VALIDACIONES DETALLE
        if not data_items_mortalidad:
            return Response({'success':False, 'detail':'No puede guardar un registro de mortalidad sin haber agregado por lo menos un ítem'}, status=status.HTTP_400_BAD_REQUEST)
            
        for item in data_items_mortalidad:
            if item['cantidad_baja'] <= 0:
                return Response({'success':False, 'detail':'Debe ingresar una cantidad de mortalidad mayor a cero en el item de la posición ' + str(item['nro_posicion'])})
                
            items_repetidos = [item_data for item_data in data_items_mortalidad if
                               item_data['id_bien']==item['id_bien'] and
                               item_data['agno_lote']==item['agno_lote'] and
                               item_data['nro_lote']==item['nro_lote'] and
                               item_data['cod_etapa_lote']==item['cod_etapa_lote'] and
                               item_data['consec_cuaren_por_lote_etapa']==item['consec_cuaren_por_lote_etapa']]
            
            if len(items_repetidos) > 1:
                return Response({'success':False, 'detail':'El item de la posición ' + str(item['nro_posicion']) + ' ha sido agregado más de una vez en los registros. Si desea actualizar la cantidad a registrar de mortalidad de dicho material vegetal, debe borrar el registro y agregarlo nuevamente'}, status=status.HTTP_400_BAD_REQUEST)
            
            saldo_disponible = 0
            
            if item['consec_cuaren_por_lote_etapa']:
                item_cuarentena = CuarentenaMatVegetal.objects.filter(
                    id_vivero = data_mortalidad['id_vivero'],
                    id_bien = item['id_bien'],
                    agno_lote = item['agno_lote'],
                    nro_lote = item['nro_lote'],
                    cod_etapa_lote = item['cod_etapa_lote'],
                    consec_cueren_por_lote_etapa = item['consec_cuaren_por_lote_etapa']
                ).first()
                
                saldo_disponible = UtilConservacion.get_saldo_por_levantar(item_cuarentena)
            else:
                inventario_vivero = self.queryset.all().filter(
                    id_vivero = data_mortalidad['id_vivero'],
                    id_bien = item['id_bien'],
                    agno_lote = item['agno_lote'],
                    nro_lote = item['nro_lote'],
                    cod_etapa_lote = item['cod_etapa_lote']
                ).first()
                
                if item['cod_etapa_lote'] == 'P':
                    saldo_disponible = UtilConservacion.get_cantidad_disponible_levantamiento_mortalidad(inventario_vivero)
                else:
                    saldo_disponible = UtilConservacion.get_cantidad_disponible_etapa(inventario_vivero)
                
            if item['cantidad_baja'] > saldo_disponible:
                return Response({'success':False, 'detail':'La cantidad a registrar de mortalidad del item en la posición ' + str(item['nro_posicion']) + ' no puede superar el saldo disponible (' + str(saldo_disponible) + ')'})
            
        # PENDIENTE VALIDACION DETALLES CON FECHA_INCIDENCIA EN T171
        
        # REGISTRO MAESTRO
        response_maestro = serializador_maestro.save()
        
        for item in data_items_mortalidad:
            item['id_baja'] = response_maestro.pk
        
        # REGISTRO DETALLES
        serializador_detalle = RegistrarItemsMortalidadSerializer(data=data_items_mortalidad, many=True)
        serializador_detalle.is_valid(raise_exception=True)
        serializador_detalle.save()
        
        # ACTUALIZACIÓN DE CANTIDADES EN DETALLES
        for item in data_items_mortalidad:
            inventario_vivero = self.queryset.all().filter(
                id_vivero = data_mortalidad['id_vivero'],
                id_bien = item['id_bien'],
                agno_lote = item['agno_lote'],
                nro_lote = item['nro_lote'],
                cod_etapa_lote = item['cod_etapa_lote']
            ).first()
            
            inventario_vivero.cantidad_bajas = inventario_vivero.cantidad_bajas + item['cantidad_baja'] if inventario_vivero.cantidad_bajas else item['cantidad_baja']
            
            if item['consec_cuaren_por_lote_etapa']:
                item_cuarentena = CuarentenaMatVegetal.objects.filter(
                    id_vivero = data_mortalidad['id_vivero'],
                    id_bien = item['id_bien'],
                    agno_lote = item['agno_lote'],
                    nro_lote = item['nro_lote'],
                    cod_etapa_lote = item['cod_etapa_lote'],
                    consec_cueren_por_lote_etapa = item['consec_cuaren_por_lote_etapa']
                ).first()
                
                inventario_vivero.cantidad_lote_cuarentena = inventario_vivero.cantidad_lote_cuarentena - item['cantidad_baja'] if inventario_vivero.cantidad_lote_cuarentena else 0
                
                item_cuarentena.cantidad_bajas = item_cuarentena.cantidad_bajas + item['cantidad_baja'] if item_cuarentena.cantidad_bajas else item['cantidad_baja']
                item_cuarentena.save()
                
            inventario_vivero.save()
        
        return Response({'success':True, 'detail':'Se realizó el registro de mortalidad correctamente'}, status=status.HTTP_201_CREATED)

class ActualizarMortalidad(generics.UpdateAPIView):
    serializer_class=ActualizarMortalidadSerializer
    queryset=BajasVivero.objects.all()
    permission_classes=[IsAuthenticated]
    
    def put(self,request,id_baja):
        data = request.data
        baja = self.queryset.all().filter(id_baja=id_baja).first()
        
        if baja:
            data_mortalidad = json.loads(data['data_mortalidad'])
            data_items_mortalidad = json.loads(data['data_items_mortalidad'])
            
            data_mortalidad['ruta_archivo_soporte'] = request.FILES.get('ruta_archivo_soporte')
            
            fecha_maxima_maestro = baja.fecha_baja + timedelta(days=30)
            fecha_maxima_detalle_cantidad = baja.fecha_baja + timedelta(days=2)
            fecha_maxima_detalle_observaciones = baja.fecha_baja + timedelta(days=30)
            fecha_actual = datetime.now()
            
            inventarios_viveros = InventarioViveros.objects.filter(id_vivero=baja.id_vivero)
            cuarentenas = CuarentenaMatVegetal.objects.filter(id_vivero=baja.id_vivero)
            
            if not data_items_mortalidad:
                return Response({'success':False, 'detail':'No puede eliminar todos los items, debe dejar por lo menos uno'}, status=status.HTTP_403_FORBIDDEN)
            
            if baja.motivo != data_mortalidad['motivo'] or baja.ruta_archivo_soporte != data_mortalidad['ruta_archivo_soporte']:
                if fecha_actual > fecha_maxima_maestro:
                    return Response({'success':False, 'detail':'No puede actualizar el motivo o el archivo porque ha superado los 30 días después de la fecha de mortalidad'}, status=status.HTTP_403_FORBIDDEN)
            
            # REALIZAR VALIDACIONES INICIALES DETALLES
            for item in data_items_mortalidad:
                if item['cantidad_baja'] <= 0:
                    return Response({'success':False, 'detail':'Debe ingresar una cantidad de mortalidad mayor a cero en el item de la posición ' + str(item['nro_posicion'])})
                    
                items_repetidos = [item_data for item_data in data_items_mortalidad if
                                item_data['id_bien']==item['id_bien'] and
                                item_data['agno_lote']==item['agno_lote'] and
                                item_data['nro_lote']==item['nro_lote'] and
                                item_data['cod_etapa_lote']==item['cod_etapa_lote'] and
                                item_data['consec_cuaren_por_lote_etapa']==item['consec_cuaren_por_lote_etapa']]
                
                if len(items_repetidos) > 1:
                    return Response({'success':False, 'detail':'El item de la posición ' + str(item['nro_posicion']) + ' ha sido agregado más de una vez en los registros. Si desea actualizar la cantidad a registrar de mortalidad de dicho material vegetal, debe borrar el registro y agregarlo nuevamente'}, status=status.HTTP_400_BAD_REQUEST)
                
                saldo_disponible = 0
                
                if item['consec_cuaren_por_lote_etapa']:
                    item_cuarentena = cuarentenas.filter(
                        id_bien = item['id_bien'],
                        agno_lote = item['agno_lote'],
                        nro_lote = item['nro_lote'],
                        cod_etapa_lote = item['cod_etapa_lote'],
                        consec_cueren_por_lote_etapa = item['consec_cuaren_por_lote_etapa']
                    ).first()
                    
                    saldo_disponible = UtilConservacion.get_saldo_por_levantar(item_cuarentena)
                else:
                    inventario_vivero = inventarios_viveros.filter(
                        id_bien = item['id_bien'],
                        agno_lote = item['agno_lote'],
                        nro_lote = item['nro_lote'],
                        cod_etapa_lote = item['cod_etapa_lote']
                    ).first()
                    
                    if item['cod_etapa_lote'] == 'P':
                        saldo_disponible = UtilConservacion.get_cantidad_disponible_levantamiento_mortalidad(inventario_vivero)
                    else:
                        saldo_disponible = UtilConservacion.get_cantidad_disponible_etapa(inventario_vivero)
                    
                if item['cantidad_baja'] > saldo_disponible:
                    return Response({'success':False, 'detail':'La cantidad a registrar de mortalidad del item en la posición ' + str(item['nro_posicion']) + ' no puede superar el saldo disponible (' + str(saldo_disponible) + ')'})
                
                item['id_baja'] = id_baja
            
            items_crear = [item for item in data_items_mortalidad if not item['id_item_baja_viveros']]
            items_actualizar = [item for item in data_items_mortalidad if item['id_item_baja_viveros']!=None]
            
            items_detalle_list = [item['id_item_baja_viveros'] for item in items_actualizar]
            
            items_mortalidad_actual = ItemsBajasVivero.objects.filter(id_baja=id_baja)
            
            # VALIDAR QUE LOS IDs DE LOS ITEMS PERTENEZCAN A LA BAJA INDICADA
            items_id_list = [item_actualizar['id_item_baja_viveros'] for item_actualizar in items_actualizar]
            items_existentes = items_mortalidad_actual.filter(id_item_baja_viveros__in=items_id_list)
            if len(items_id_list) != len(items_existentes):
                return Response({'success':False, 'detail':'Debe validar que todos los items pertenezcan al mismo registro de mortalidad'}, status=status.HTTP_400_BAD_REQUEST)
            
            items_cambios_actualizar = []
            
            for item in items_actualizar:
                item_actual = items_mortalidad_actual.filter(id_item_baja_viveros=item['id_item_baja_viveros']).first()
                inventario_vivero = inventarios_viveros.filter(
                    id_bien = item_actual.id_bien.id_bien,
                    agno_lote = item_actual.agno_lote,
                    nro_lote = item_actual.nro_lote,
                    cod_etapa_lote = item_actual.cod_etapa_lote
                ).first()
                
                # VALIDAR SI ACTUALIZARON CANTIDAD_BAJA U OBSERVACIONES
                if item_actual.cantidad_baja != item['cantidad_baja']:
                    if fecha_actual > fecha_maxima_detalle_cantidad:
                        return Response({'success':False, 'detail':'No puede actualizar la cantidad de los items porque ha superado las 48 horas'}, status=status.HTTP_403_FORBIDDEN)

                    # if item['cantidad_baja'] <= 0:
                    #     return Response({'success':False, 'detail':'La cantidad de la mortalidad debe ser mayor a cero'}, status=status.HTTP_403_FORBIDDEN)
                    # if item['cantidad_baja'] > item_actual.cantidad_baja:
                    #     if not item_actual.consec_cuaren_por_lote_etapa:
                    #         if item_actual.cod_etapa_lote == 'P':
                    #             saldo_disponible = UtilConservacion.get_cantidad_disponible_levantamiento_mortalidad(inventario_vivero)
                    #             if item['cantidad_baja'] > saldo_disponible:
                    #                 return Response({'success':False, 'detail':'La cantidad aumentada del item en la posición ' + str(item_actual.nro_posicion) + ' no puede ser mayor al saldo disponible (' + str(saldo_disponible) + ')'}, status=status.HTTP_400_BAD_REQUEST)
                    #         else:
                    #             saldo_disponible = UtilConservacion.get_cantidad_disponible_etapa(inventario_vivero)
                    #             if item['cantidad_baja'] > saldo_disponible:
                    #                 return Response({'success':False, 'detail':'La cantidad aumentada del item en la posición ' + str(item_actual.nro_posicion) + ' no puede ser mayor al saldo disponible (' + str(saldo_disponible) + ')'}, status=status.HTTP_400_BAD_REQUEST)
                    #     else:
                    #         item_cuarentena = cuarentenas.filter(
                    #             id_bien = item_actual.id_bien,
                    #             agno_lote = item_actual.agno_lote,
                    #             nro_lote = item_actual.nro_lote,
                    #             cod_etapa_lote = item_actual.cod_etapa_lote,
                    #             consec_cueren_por_lote_etapa = item_actual.consec_cuaren_por_lote_etapa
                    #         ).first()
                    #         saldo_disponible = UtilConservacion.get_saldo_por_levantar(item_cuarentena)
                    #         if item['cantidad_baja'] > saldo_disponible:
                    #             return Response({'success':False, 'detail':'La cantidad aumentada del item en la posición ' + str(item_actual.nro_posicion) + ' no puede ser mayor al saldo disponible (' + str(saldo_disponible) + ')'})
                
                if item_actual.observaciones != item['observaciones']:
                    if fecha_actual > fecha_maxima_detalle_observaciones:
                        return Response({'success':False, 'detail':'No puede actualizar la observación de los items porque ha superado los 30 días'}, status=status.HTTP_403_FORBIDDEN)
            
                if item_actual.cantidad_baja != item['cantidad_baja'] or item_actual.observaciones != item['observaciones']:
                    items_cambios_actualizar.append(item)
            
            # if items_cambios_actualizar_cantidad:
            #     if fecha_actual > fecha_maxima_detalle_cantidad:
            #         return Response({'success':False, 'detail':'No puede actualizar la cantidad de los items porque ha superado las 48 horas'}, status=status.HTTP_403_FORBIDDEN)
                
            # if items_cambios_actualizar_observaciones:
            #     if fecha_actual > fecha_maxima_detalle_observaciones:
            #         return Response({'success':False, 'detail':'No puede actualizar la observación de los items porque ha superado los 30 días'}, status=status.HTTP_403_FORBIDDEN)
            
            # ACTUALIZAR MAESTRO
            if baja.motivo != data_mortalidad['motivo'] or baja.ruta_archivo_soporte != data_mortalidad['ruta_archivo_soporte']:
                serializer_maestro = self.serializer_class(baja, data=data_mortalidad)
                serializer_maestro.is_valid(raise_exception=True)
                serializer_maestro.save()
            
            # CREAR DETALLES
            if items_crear:
                serializer_detalle_crear = RegistrarItemsMortalidadSerializer(data=items_crear, many=True)
                serializer_detalle_crear.is_valid(raise_exception=True)
                serializer_detalle_crear.save()
            
            # ACTUALIZAR DETALLES
            if items_cambios_actualizar:
                for item in items_cambios_actualizar:
                    item_actual = items_mortalidad_actual.filter(id_item_baja_viveros=item['id_item_baja_viveros']).first()
                    inventario_vivero = inventarios_viveros.filter(
                        id_bien = item_actual.id_bien.id_bien,
                        agno_lote = item_actual.agno_lote,
                        nro_lote = item_actual.nro_lote,
                        cod_etapa_lote = item_actual.cod_etapa_lote
                    ).first()
                    
                    if item['cantidad_baja'] < item_actual.cantidad_baja:
                        cantidad_disminuida = item_actual.cantidad_baja - item['cantidad_baja']
                        inventario_vivero.cantidad_bajas = inventario_vivero.cantidad_bajas - cantidad_disminuida if inventario_vivero.cantidad_bajas else 0
                        if item_actual.consec_cuaren_por_lote_etapa:
                            item_cuarentena = cuarentenas.filter(
                                id_bien = item_actual.id_bien,
                                agno_lote = item_actual.agno_lote,
                                nro_lote = item_actual.nro_lote,
                                cod_etapa_lote = item_actual.cod_etapa_lote,
                                consec_cueren_por_lote_etapa = item_actual.consec_cuaren_por_lote_etapa
                            ).first()
                            
                            inventario_vivero.cantidad_lote_cuarentena = inventario_vivero.cantidad_lote_cuarentena - cantidad_disminuida if inventario_vivero.cantidad_lote_cuarentena else 0
                            
                            item_cuarentena.cantidad_bajas = item_cuarentena.cantidad_bajas - cantidad_disminuida if item_cuarentena.cantidad_bajas else 0
                            item_cuarentena.save()
                        inventario_vivero.save()
                    elif item['cantidad_baja'] > item_actual.cantidad_baja:
                        cantidad_aumentada = item['cantidad_baja'] - item_actual.cantidad_baja
                        inventario_vivero.cantidad_bajas = inventario_vivero.cantidad_bajas + cantidad_aumentada if inventario_vivero.cantidad_bajas else cantidad_aumentada
                        if item_actual.consec_cuaren_por_lote_etapa:
                            item_cuarentena = cuarentenas.filter(
                                id_bien = item_actual.id_bien,
                                agno_lote = item_actual.agno_lote,
                                nro_lote = item_actual.nro_lote,
                                cod_etapa_lote = item_actual.cod_etapa_lote,
                                consec_cueren_por_lote_etapa = item_actual.consec_cuaren_por_lote_etapa
                            ).first()
                            
                            item_cuarentena.cantidad_bajas = item_cuarentena.cantidad_bajas + cantidad_aumentada if item_cuarentena.cantidad_bajas else cantidad_aumentada
                            item_cuarentena.save()
                        inventario_vivero.save()
                    
                    serializer_detalle = ActualizarItemsMortalidadSerializer(item_actual, data=item)
                    serializer_detalle.is_valid(raise_exception=True)
                    serializer_detalle.save()
            
            # ELIMINACIÓN DE ITEMS MORTALIDAD
            items_mortalidad_eliminar = items_mortalidad_actual.exclude(id_item_baja_viveros__in=items_detalle_list)
            
            if items_mortalidad_eliminar:
                for item in items_mortalidad_eliminar:
                    inventario_vivero = inventarios_viveros.filter(
                        id_bien = item.id_bien.id_bien,
                        agno_lote = item.agno_lote,
                        nro_lote = item.nro_lote,
                        cod_etapa_lote = item.cod_etapa_lote
                    ).first()
                    inventario_vivero.cantidad_bajas = inventario_vivero.cantidad_bajas - item.cantidad_baja if inventario_vivero.cantidad_bajas else 0
                    
                    if item.consec_cuaren_por_lote_etapa:
                        inventario_vivero.cantidad_lote_cuarentena = inventario_vivero.cantidad_lote_cuarentena + item.cantidad_baja if inventario_vivero.cantidad_lote_cuarentena else item.cantidad_baja
                        item_cuarentena = cuarentenas.filter(
                            id_bien = item.id_bien,
                            agno_lote = item.agno_lote,
                            nro_lote = item.nro_lote,
                            cod_etapa_lote = item.cod_etapa_lote,
                            consec_cueren_por_lote_etapa = item.consec_cuaren_por_lote_etapa
                        ).first()
                        item_cuarentena.cantidad_bajas = item_cuarentena.cantidad_bajas - item.cantidad_baja if item_cuarentena.cantidad_bajas else 0
                        item_cuarentena.save()
                    inventario_vivero.save()
                items_mortalidad_eliminar.delete()
            
            return Response({'success':True, 'detail':'Se realizó la actualizacón del registro de mortalidad correctamente'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success':False, 'detail':'No existe el registro de mortalidad elegido'}, status=status.HTTP_404_NOT_FOUND)