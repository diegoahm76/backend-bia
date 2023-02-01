from rest_framework.response import Response
from rest_framework import generics,status
from django.db.models import Q
from conservacion.serializers.etapas_serializers import InventarioViverosSerializer, GuardarCambioEtapaSerializer, ActualizarCambioEtapaSerializer
from conservacion.models.inventario_models import InventarioViveros
from conservacion.models.siembras_models import CambiosDeEtapa
from conservacion.models.viveros_models import Vivero
from datetime import datetime, timedelta,date
from conservacion.utils import UtilConservacion

class FiltroMaterialVegetal(generics.ListAPIView):
    serializer_class=InventarioViverosSerializer
    queryset=InventarioViveros
    
    def get(self,request,id_vivero):
        filter={}
        
        for key,value in request.query_params.items():
            if key in ['codigo_bien','nombre','cod_etapa_lote','agno_lote']:
                if key != "cod_etapa_lote" and key != 'agno_lote':
                    filter['id_bien__'+key+'__icontains'] = value
                else:
                    filter[key] = value
        vivero=Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            return Response({'success':False,'detail':'El Vivero seleccionado no existe'},status=status.HTTP_404_NOT_FOUND)
        
        inventario_vivero=InventarioViveros.objects.filter(**filter).filter(id_vivero=id_vivero,id_bien__cod_tipo_elemento_vivero="MV",id_bien__es_semilla_vivero=False,cod_etapa_lote__in=['G','P']).filter(~Q(siembra_lote_cerrada=True))
        list_items=[]
        for item in inventario_vivero:
            if item.cod_etapa_lote == "P":
                item.cantidad_disponible = UtilConservacion.get_cantidad_disponible_etapa(item)
                if item.cantidad_disponible > 0:
                    list_items.append(item)
            else:
                list_items.append(item)
                    
        serializador=self.serializer_class(list_items,many=True)    
        return Response ({'success':True,'detail':'Se encontraron las siguientes coincidencias','data':serializador.data},status=status.HTTP_200_OK)
    
class GuardarCambioEtapa(generics.CreateAPIView):
    serializer_class=GuardarCambioEtapaSerializer
    queryset=CambiosDeEtapa.objects.all()
    
    def post(self,request):
        data = request.data
        
        data['consec_por_lote_etapa'] = 0
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        
        inventario_vivero = InventarioViveros.objects.filter(
            id_vivero=data['id_vivero'],
            id_bien=data['id_bien'],
            agno_lote=data['agno_lote'],
            nro_lote=data['nro_lote'],
            cod_etapa_lote=data['cod_etapa_lote_origen']
        ).first()
        
        # VALIDAR ANTIGUEDAD POSIBLE DE FECHA CAMBIO
        fecha_cambio = datetime.strptime(data['fecha_cambio'], '%Y-%m-%d')
        if fecha_cambio < datetime.today()-timedelta(days=30):
            return Response({'success':False, 'detail':'La fecha de cambio no puede superar 30 días de antiguedad'}, status=status.HTTP_400_BAD_REQUEST)
        
        # VALIDAR EXISTENCIA DE CAMBIO DE ETAPA DE MV GERMINACION
        cambio_etapa=CambiosDeEtapa.objects.filter(id_bien=inventario_vivero.id_bien.id_bien,id_vivero=inventario_vivero.id_vivero.id_vivero,agno_lote=inventario_vivero.agno_lote,nro_lote=inventario_vivero.nro_lote).filter(~Q(cambio_anulado=True))
        if data['cod_etapa_lote_origen'] == 'G':
            data['cantidad_disponible_al_crear'] = 0
            data['consec_por_lote_etapa'] = 1
            cambio_etapa_germinacion = cambio_etapa.filter(cod_etapa_lote_origen='G').last()
            if cambio_etapa_germinacion:
                return Response({'success':False, 'detail':'Ya se realizó un cambio de etapa de germinación a producción del material vegetal elegido'}, status=status.HTTP_403_FORBIDDEN)
        
        
        if fecha_cambio.date() != datetime.now().date():
            
            # VALIDACIONES FECHA CAMBIO SI ETAPA LOTE ES GERMINACIÓN
            if data['cod_etapa_lote_origen'] == 'G':
                if fecha_cambio < inventario_vivero.fecha_ingreso_lote_etapa or fecha_cambio < inventario_vivero.fecha_ult_altura_lote:
                    return Response({'success':False, 'detail':'La fecha de cambio debe ser posterior a la fecha de ingreso al lote y posterior a la fecha de la última altura del material elegido'}, status=status.HTTP_400_BAD_REQUEST)
            
            #VALIDACION DE FECHA CAMBIO PARA LA ETAPA LOTE DE PRODUCCIÓN
            cambio_etapa=cambio_etapa.filter(cod_etapa_lote_origen='P').last()
            if data['cod_etapa_lote_origen'] == 'P':
                if inventario_vivero.cantidad_traslados_lote_produccion_distribucion > 0:
                    if cambio_etapa:
                        if  fecha_cambio < cambio_etapa.fecha_cambio:
                            return Response({'success':False,'detail':'La fecha elegida para el cambio debe ser posterior a la fecha del último cambio de etapa'},status=status.HTTP_403_FORBIDDEN)
                else:
                    if fecha_cambio < inventario_vivero.fecha_ingreso_lote_etapa:
                        return Response({'success':False,'detail':'la fecha elegida para el Cambio debe ser posterior a la fecha de ingreso del lote'},status=status.HTTP_403_FORBIDDEN)
            
                #VALIDACIÓN DE FECHA DE ACTUALIZACIÓN CUANDO SE MUEVE TODA LA CANTIDAD
                if int(data['cantidad_movida']) ==  int(data['cantidad_disponible_al_crear']) and (inventario_vivero.cantidad_lote_cuarentena == 0 or inventario_vivero.cantidad_lote_cuarentena == None):
                    print('fecha_altura',inventario_vivero.fecha_ult_altura_lote)
                    print('fecha_cambio',fecha_cambio)
                    if inventario_vivero.fecha_ult_altura_lote > fecha_cambio:
                        print('Entró')
                        return Response({'succes':False,'detail':'La fecha de cambio debe ser mayor a la ultima fecha de actualización que fue: ' + str(inventario_vivero.fecha_ult_altura_lote)},status=status.HTTP_403_FORBIDDEN)
                
        #VALIDACIÓN DE CANTIDAD DISPONIBLE
        cantidad_disponible=UtilConservacion.get_cantidad_disponible_etapa(inventario_vivero)
        if data['cod_etapa_lote_origen'] == 'P':
            if cantidad_disponible != int(data['cantidad_disponible_al_crear']):
                if int(data['cantidad_movida']) > cantidad_disponible:
                    return Response ({'success':False,'detail':'La cantidad disponible cambió, por favor cambiar la cantidad movida'},status=status.HTTP_400_BAD_REQUEST)
            else:
                if int(data['cantidad_movida']) > cantidad_disponible:
                    return Response ({'success':False,'detail':'La cantidad movida no puede superar la cantidad disponible actual'},status=status.HTTP_400_BAD_REQUEST)
            
            cambio_etapa=cambio_etapa.filter(cod_etapa_lote_origen='P').last()
            consec_por_lote_etapa = 1
            if cambio_etapa:
                consec_por_lote_etapa = cambio_etapa.consec_por_lote_etapa + 1
            
            data['consec_por_lote_etapa'] = consec_por_lote_etapa
            
            
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        
        # CERRAR LOTE Y NUEVO REGISTRO EN PRODUCCIÓN
        if data['cod_etapa_lote_origen'] == 'G':
            # CERRAR LOTE
            inventario_vivero.siembra_lote_cerrada = True
            inventario_vivero.save()
            
            # NUEVO REGISTRO
            InventarioViveros.objects.create(
                id_vivero = inventario_vivero.id_vivero,
                id_bien = inventario_vivero.id_bien,
                agno_lote = inventario_vivero.agno_lote,
                nro_lote = inventario_vivero.nro_lote,
                cod_etapa_lote = 'P',
                es_produccion_propia_lote = True,
                fecha_ingreso_lote_etapa = fecha_cambio,
                ult_altura_lote = data['altura_lote_en_cms'],
                fecha_ult_altura_lote = fecha_cambio,
                cantidad_entrante = data['cantidad_movida']
            )
        else:
            # ACTUALIZAR LOTE ACTUAL PRODUCCIÓN
            inventario_vivero.cantidad_traslados_lote_produccion_distribucion = inventario_vivero.cantidad_traslados_lote_produccion_distribucion + int(data['cantidad_movida']) if inventario_vivero.cantidad_traslados_lote_produccion_distribucion else data['cantidad_movida']
            inventario_vivero.save()
            
            # VALIDAR Y CREAR REGISTRO SI ES NECESARIO
            inventario_vivero_dist = InventarioViveros.objects.filter(
                id_vivero=data['id_vivero'],
                id_bien=data['id_bien'],
                agno_lote=data['agno_lote'],
                nro_lote=data['nro_lote'],
                cod_etapa_lote='D'
            ).first()
            
            if inventario_vivero_dist:
                inventario_vivero_dist.cantidad_entrante = inventario_vivero_dist.cantidad_entrante + int(data['cantidad_movida']) if inventario_vivero_dist.cantidad_entrante else data['cantidad_movida']
                inventario_vivero_dist.ult_altura_lote = data['altura_lote_en_cms']
                inventario_vivero_dist.fecha_ult_altura_lote = fecha_cambio
                inventario_vivero_dist.save()
            else:
                InventarioViveros.objects.create(
                    id_vivero = inventario_vivero.id_vivero,
                    id_bien = inventario_vivero.id_bien,
                    agno_lote = inventario_vivero.agno_lote,
                    nro_lote = inventario_vivero.nro_lote,
                    cod_etapa_lote = 'D',
                    es_produccion_propia_lote = inventario_vivero.es_produccion_propia_lote,
                    cod_tipo_entrada_alm_lote = inventario_vivero.cod_tipo_entrada_alm_lote,
                    nro_entrada_alm_lote = inventario_vivero.nro_entrada_alm_lote,
                    fecha_ingreso_lote_etapa = fecha_cambio,
                    ult_altura_lote = data['altura_lote_en_cms'],
                    fecha_ult_altura_lote = fecha_cambio,
                    cantidad_entrante = data['cantidad_movida']
                )
                
        return Response ({'success':True,'detail':'Se realizó el cambio de etapa correctamente','data':serializador.data},status=status.HTTP_200_OK)

class ActualizarCambioEtapa(generics.UpdateAPIView):
    serializer_class=ActualizarCambioEtapaSerializer
    queryset=CambiosDeEtapa.objects.all()
    
    def put(self,request,pk):
        data = request.data
        cambio_etapa = CambiosDeEtapa.objects.filter(id_cambio_de_etapa=pk).first()
        if cambio_etapa:
            # VALIDAR ANTIGUEDAD POSIBLE DE FECHA CAMBIO
            if cambio_etapa.fecha_cambio.date() < date.today()-timedelta(days=30):
                return Response({'success':False, 'detail':'No puede actualizar porque la fecha de cambio supera los 30 días de antiguedad'}, status=status.HTTP_400_BAD_REQUEST)
            
            cod_nueva_etapa = 'P' if cambio_etapa.cod_etapa_lote_origen == 'G' else 'D'
            
            # VALIDAR ALTURA LOTE
            inventario_vivero = InventarioViveros.objects.filter(
                id_vivero=cambio_etapa.id_vivero.id_vivero,
                id_bien=cambio_etapa.id_bien.id_bien,
                agno_lote=cambio_etapa.agno_lote,
                nro_lote=cambio_etapa.nro_lote
            )
            inventario_vivero_etapa_nueva = inventario_vivero.filter(cod_etapa_lote=cod_nueva_etapa).first()
            inventario_vivero_etapa_origen = inventario_vivero.filter(cod_etapa_lote=cambio_etapa.cod_etapa_lote_origen).first()
            
            if int(data['altura_lote_en_cms']) <= 0:
                return Response({'success':False, 'detail':'La altura del lote debe ser mayor a cero'}, status=status.HTTP_400_BAD_REQUEST)
            
            if inventario_vivero_etapa_nueva.fecha_ult_altura_lote.date() != cambio_etapa.fecha_cambio.date():
                return Response({'success':False, 'detail':'No se puede actualizar la altura del lote debido a que la fecha de la última altura ('+str(inventario_vivero_etapa_nueva.fecha_ult_altura_lote.date())+') es distinta a la fecha del cambio de etapa ('+str(cambio_etapa.fecha_cambio.date())+')'}, status=status.HTTP_403_FORBIDDEN)
            
            if cambio_etapa.cod_etapa_lote_origen == 'G':
                if int(data['cantidad_movida']) > cambio_etapa.cantidad_movida:
                    inventario_vivero_etapa_nueva.cantidad_entrante = inventario_vivero_etapa_nueva.cantidad_entrante + (int(data['cantidad_movida']) - cambio_etapa.cantidad_movida) if inventario_vivero_etapa_nueva.cantidad_entrante else int(data['cantidad_movida'])
                    inventario_vivero_etapa_nueva.save()
                elif int(data['cantidad_movida']) < cambio_etapa.cantidad_movida:
                    cantidad_entrante_disminuida = inventario_vivero_etapa_nueva.cantidad_entrante - (cambio_etapa.cantidad_movida - int(data['cantidad_movida']))
                    
                    cantidad_bajas = inventario_vivero_etapa_nueva.cantidad_bajas if inventario_vivero_etapa_nueva.cantidad_bajas else 0
                    cantidad_traslados = inventario_vivero_etapa_nueva.cantidad_traslados_lote_produccion_distribucion if inventario_vivero_etapa_nueva.cantidad_traslados_lote_produccion_distribucion else 0
                    cantidad_salidas = inventario_vivero_etapa_nueva.cantidad_salidas if inventario_vivero_etapa_nueva.cantidad_salidas else 0
                    cantidad_lote_cuarentena = inventario_vivero_etapa_nueva.cantidad_lote_cuarentena if inventario_vivero_etapa_nueva.cantidad_lote_cuarentena else 0
                    
                    suma_cantidades = cantidad_bajas + cantidad_traslados + cantidad_salidas + cantidad_lote_cuarentena
                    
                    if cantidad_entrante_disminuida < suma_cantidades:
                        return Response({'success':False, 'detail':'No puede realizar la actualización de la cantidad movida, aumente el valor de la cantidad movida'}, status=status.HTTP_400_BAD_REQUEST)

                    inventario_vivero_etapa_nueva.cantidad_entrante = cantidad_entrante_disminuida
                    inventario_vivero_etapa_nueva.save()
            else:
                if int(data['cantidad_movida']) > cambio_etapa.cantidad_movida:
                    saldo_disponible = UtilConservacion.get_cantidad_disponible_etapa(inventario_vivero_etapa_origen)
                    
                    if (int(data['cantidad_movida']) - cambio_etapa.cantidad_movida) > saldo_disponible:
                        return Response({'success':False, 'detail':'No puede realizar la actualización de la cantidad movida ya que supera la cantidad disponible'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    cantidad_aumentada = int(data['cantidad_movida']) - cambio_etapa.cantidad_movida
                    
                    inventario_vivero_etapa_origen.cantidad_traslados_lote_produccion_distribucion = inventario_vivero_etapa_origen.cantidad_traslados_lote_produccion_distribucion + cantidad_aumentada if inventario_vivero_etapa_origen.cantidad_traslados_lote_produccion_distribucion else cantidad_aumentada
                    inventario_vivero_etapa_origen.save()
                    
                    inventario_vivero_etapa_nueva.cantidad_entrante = inventario_vivero_etapa_nueva.cantidad_entrante + cantidad_aumentada if inventario_vivero_etapa_nueva.cantidad_entrante else cantidad_aumentada
                    inventario_vivero_etapa_nueva.save()
                elif int(data['cantidad_movida']) < cambio_etapa.cantidad_movida:
                    cantidad_entrante_disminuida = inventario_vivero_etapa_nueva.cantidad_entrante - (cambio_etapa.cantidad_movida - int(data['cantidad_movida']))
                    
                    cantidad_bajas = inventario_vivero_etapa_nueva.cantidad_bajas if inventario_vivero_etapa_nueva.cantidad_bajas else 0
                    cantidad_salidas = inventario_vivero_etapa_nueva.cantidad_salidas if inventario_vivero_etapa_nueva.cantidad_salidas else 0
                    cantidad_lote_cuarentena = inventario_vivero_etapa_nueva.cantidad_lote_cuarentena if inventario_vivero_etapa_nueva.cantidad_lote_cuarentena else 0
                    
                    suma_cantidades = cantidad_bajas + cantidad_salidas + cantidad_lote_cuarentena
                    
                    if cantidad_entrante_disminuida < suma_cantidades:
                        return Response({'success':False, 'detail':'No puede realizar la actualización de la cantidad movida, aumente el valor de la cantidad movida'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    cantidad_disminuida = cambio_etapa.cantidad_movida - int(data['cantidad_movida']) 
                    
                    inventario_vivero_etapa_origen.cantidad_traslados_lote_produccion_distribucion = inventario_vivero_etapa_origen.cantidad_traslados_lote_produccion_distribucion - cantidad_disminuida if inventario_vivero_etapa_origen.cantidad_traslados_lote_produccion_distribucion else 0
                    inventario_vivero_etapa_origen.save()
                    
                    inventario_vivero_etapa_nueva.cantidad_entrante = inventario_vivero_etapa_nueva.cantidad_entrante - cantidad_disminuida if inventario_vivero_etapa_nueva.cantidad_entrante else 0
                    inventario_vivero_etapa_nueva.save()
            
            serializador = self.serializer_class(cambio_etapa, data=data)
            serializador.is_valid(raise_exception=True)
            serializador.save()
            return Response({'success':True, 'detail':'Se realizó la actualización de manera exitosa', 'data':serializador.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success':False, 'detail':'No existe el cambio de etapa que desea actualizar'}, status=status.HTTP_404_NOT_FOUND)