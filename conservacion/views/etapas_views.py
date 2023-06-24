from rest_framework.response import Response
from rest_framework import generics,status
from django.db.models import Q
from conservacion.serializers.etapas_serializers import (
    InventarioViverosSerializer,
    GuardarCambioEtapaSerializer,
    ActualizarCambioEtapaSerializer,
    GetCambioEtapasSerializer,
    AnularCambioEtapaSerializer
)
from conservacion.models.cuarentena_models import(
    CuarentenaMatVegetal
)
from conservacion.models.incidencias_models import(
    IncidenciasMatVegetal
)
from conservacion.models.inventario_models import InventarioViveros
from conservacion.models.siembras_models import CambiosDeEtapa
from conservacion.models.viveros_models import Vivero
from datetime import datetime, timedelta,date
from conservacion.utils import UtilConservacion
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

class FiltroMaterialVegetal(generics.ListAPIView):
    serializer_class=InventarioViverosSerializer
    queryset=InventarioViveros.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get(self,request,id_vivero):
        filter={}
        
        for key,value in request.query_params.items():
            if key in ['codigo_bien','nombre','cod_etapa_lote','agno_lote']:
                if key != "cod_etapa_lote" and key != 'agno_lote':
                    filter['id_bien__'+key+'__icontains'] = value
                else:
                    if value != '':
                        filter[key]=value
                        
        vivero=Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            raise NotFound('El Vivero seleccionado no existe')
        
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
    permission_classes=[IsAuthenticated]
    
    def post(self,request):
        data = request.data
        data._mutable = True
        
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
        fecha_cambio = datetime.strptime(data['fecha_cambio'], '%Y-%m-%d %H:%M:%S')
        fecha_cambio = fecha_cambio.replace(minute=0, second=0, microsecond=0)
        if fecha_cambio < datetime.now()-timedelta(days=30):
            raise ValidationError('La fecha de cambio no puede superar 30 días de antiguedad')
        
        # VALIDAR EXISTENCIA DE CAMBIO DE ETAPA DE MV GERMINACION
        cambio_etapa = CambiosDeEtapa.objects.filter(id_bien=inventario_vivero.id_bien.id_bien,id_vivero=inventario_vivero.id_vivero.id_vivero,agno_lote=inventario_vivero.agno_lote,nro_lote=inventario_vivero.nro_lote)
        cambio_etapa_all = cambio_etapa
        cambio_etapa = cambio_etapa.filter(~Q(cambio_anulado=True))
        if data['cod_etapa_lote_origen'] == 'G':
            data['cantidad_disponible_al_crear'] = 0
            
            cambio_etapa_g=cambio_etapa_all.filter(cod_etapa_lote_origen='G').last()
            consec_por_lote_etapa_g = 1
            if cambio_etapa_g:
                consec_por_lote_etapa_g = cambio_etapa_g.consec_por_lote_etapa + 1
            
            data['consec_por_lote_etapa'] = consec_por_lote_etapa_g
            
            cambio_etapa_germinacion = cambio_etapa.filter(cod_etapa_lote_origen='G').last()
            if cambio_etapa_germinacion:
                raise PermissionDenied('Ya se realizó un cambio de etapa de germinación a producción del material vegetal elegido')
        
        
        if fecha_cambio != datetime.now().replace(minute=0, second=0, microsecond=0):
            
            # VALIDACIONES FECHA CAMBIO SI ETAPA LOTE ES GERMINACIÓN
            if data['cod_etapa_lote_origen'] == 'G':
                if fecha_cambio < inventario_vivero.fecha_ingreso_lote_etapa or fecha_cambio < inventario_vivero.fecha_ult_altura_lote:
                    raise ValidationError('La fecha de cambio debe ser posterior a la fecha de ingreso al lote y posterior a la fecha de la última altura del material elegido')
                
                if fecha_cambio < inventario_vivero.fecha_ingreso_lote_etapa or fecha_cambio < inventario_vivero.fecha_ult_altura_lote:
                    raise ValidationError('La fecha de cambio debe ser posterior a la fecha de ingreso')
                
                # VALIDAR QUE LA FECHA DE CAMBIO NO SEA INFERIOR A NINGÚN REGISTRO DE CUARENTENA
                cuarentenas = CuarentenaMatVegetal.objects.filter(
                    id_vivero=data['id_vivero'],
                    id_bien=data['id_bien'],
                    agno_lote=data['agno_lote'],
                    nro_lote=data['nro_lote'],
                    cod_etapa_lote=data['cod_etapa_lote_origen'],
                    cuarentena_anulada=False,
                    fecha_registro__lt=fecha_cambio
                ).last()
                
                if cuarentenas:
                    raise PermissionDenied('La fecha de cambio debe ser superior a la cuarentena con fecha ' + str(cuarentenas.fecha_registro))

                # VALIDAR QUE LA FECHA DE CAMBIO NO SEA INFERIOR A NINGÚN REGISTRO DE INCIDENCIAS
                incidencias = IncidenciasMatVegetal.objects.filter(
                    id_vivero=data['id_vivero'],
                    id_bien=data['id_bien'],
                    agno_lote=data['agno_lote'],
                    nro_lote=data['nro_lote'],
                    cod_etapa_lote=data['cod_etapa_lote_origen'],
                    fecha_registro__lte=fecha_cambio
                ).last()
                
                if incidencias:
                    raise PermissionDenied('La fecha de cambio debe ser superior a la incidencia con fecha ' +  str(incidencias.fecha_registro))
            
            #VALIDACION DE FECHA CAMBIO PARA LA ETAPA LOTE DE PRODUCCIÓN
            cambio_etapa=cambio_etapa.filter(cod_etapa_lote_origen='P').last()
            if data['cod_etapa_lote_origen'] == 'P':
                if inventario_vivero.cantidad_traslados_lote_produccion_distribucion > 0:
                    if cambio_etapa:
                        if  fecha_cambio < cambio_etapa.fecha_cambio:
                            raise PermissionDenied('La fecha elegida para el cambio debe ser posterior a la fecha del último cambio de etapa')
                else:
                    if fecha_cambio < inventario_vivero.fecha_ingreso_lote_etapa:
                        raise PermissionDenied('La fecha elegida para el Cambio debe ser posterior a la fecha de ingreso del lote')
                # VALIDAR QUE LA FECHA DE CAMBIO NO SEA INFERIOR A NINGÚN REGISTRO DE CUARENTENA
                cuarentenas = CuarentenaMatVegetal.objects.filter(
                    id_vivero=data['id_vivero'],
                    id_bien=data['id_bien'],
                    agno_lote=data['agno_lote'],
                    nro_lote=data['nro_lote'],
                    cod_etapa_lote=data['cod_etapa_lote_origen'],
                    cuarentena_anulada=False,
                    cuarentena_abierta=False,
                    fecha_registro__lt=fecha_cambio
                ).last()
                
                if cuarentenas:
                    raise PermissionDenied('La fecha de cambio debe ser superior a la cuarentena con fecha ' + str(cuarentenas.fecha_registro))
                
                #VALIDACIÓN DE FECHA DE ACTUALIZACIÓN CUANDO SE MUEVE TODA LA CANTIDAD
                if int(data['cantidad_movida']) ==  int(data['cantidad_disponible_al_crear']) and (inventario_vivero.cantidad_lote_cuarentena == 0 or inventario_vivero.cantidad_lote_cuarentena == None):
                    if inventario_vivero.fecha_ult_altura_lote > fecha_cambio:
                        raise PermissionDenied('La fecha de cambio debe ser mayor a la ultima fecha de actualización que fue: ' + str(inventario_vivero.fecha_ult_altura_lote))
                
        #VALIDACIÓN DE CANTIDAD DISPONIBLE
        cantidad_disponible=UtilConservacion.get_cantidad_disponible_etapa(inventario_vivero)
        if data['cod_etapa_lote_origen'] == 'P':
            if cantidad_disponible != int(data['cantidad_disponible_al_crear']):
                if int(data['cantidad_movida']) > cantidad_disponible:
                    raise ValidationError('La cantidad disponible cambió, por favor cambiar la cantidad movida')
            else:
                if int(data['cantidad_movida']) > cantidad_disponible:
                    raise ValidationError('La cantidad movida no puede superar la cantidad disponible actual')
            
            cambio_etapa_p=cambio_etapa_all.filter(cod_etapa_lote_origen='P').last()
            consec_por_lote_etapa_p = 1
            if cambio_etapa_p:
                consec_por_lote_etapa_p = cambio_etapa_p.consec_por_lote_etapa + 1
            
            data['consec_por_lote_etapa'] = consec_por_lote_etapa_p
            
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
    permission_classes=[IsAuthenticated]
    
    def put(self,request,pk):
        data = request.data
        cambio_etapa = self.queryset.all().filter(id_cambio_de_etapa=pk).first()
        if cambio_etapa:
            # VALIDAR ANTIGUEDAD POSIBLE DE FECHA CAMBIO
            if cambio_etapa.fecha_cambio < datetime.now() - timedelta(days=30):
                raise ValidationError('No puede actualizar porque la fecha de cambio supera los 30 días de antiguedad')
            
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
                raise ValidationError('La altura del lote debe ser mayor a cero')
            
            if inventario_vivero_etapa_nueva.fecha_ult_altura_lote.replace(minute=0, second=0, microsecond=0) != cambio_etapa.fecha_cambio.replace(minute=0, second=0, microsecond=0):
                raise PermissionDenied('No se puede actualizar la altura del lote debido a que la fecha de la última altura ('+str(inventario_vivero_etapa_nueva.fecha_ult_altura_lote.replace(minute=0, second=0, microsecond=0))+') es distinta a la fecha del cambio de etapa ('+str(cambio_etapa.fecha_cambio.replace(minute=0, second=0, microsecond=0))+')')
            
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
                        raise ValidationError ('No puede realizar la actualización de la cantidad movida, aumente el valor de la cantidad movida')

                    inventario_vivero_etapa_nueva.cantidad_entrante = cantidad_entrante_disminuida
                    inventario_vivero_etapa_nueva.save()
            else:
                if int(data['cantidad_movida']) > cambio_etapa.cantidad_movida:
                    saldo_disponible = UtilConservacion.get_cantidad_disponible_etapa(inventario_vivero_etapa_origen)
                    
                    if (int(data['cantidad_movida']) - cambio_etapa.cantidad_movida) > saldo_disponible:
                        raise ValidationError ('No puede realizar la actualización de la cantidad movida ya que supera la cantidad disponible')
                    
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
                        raise ValidationError ('No puede realizar la actualización de la cantidad movida, aumente el valor de la cantidad movida')
                    
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
            raise NotFound('No existe el cambio de etapa que desea actualizar')
        
        
class FiltroCambioEtapa(generics.ListAPIView):
    serializer_class=GetCambioEtapasSerializer
    queryset=CambiosDeEtapa.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get(self,request,id_vivero):
        filter={}
        for key,value in request.query_params.items():
            if key in ['codigo_bien','nombre','cod_etapa_lote_origen','agno_lote']:
                if key != "cod_etapa_lote_origen" and key != 'agno_lote':
                    filter['id_bien__'+key+'__icontains'] = value
                else:
                    if value != '':
                        filter[key]=value
                    
        vivero=Vivero.objects.filter(id_vivero=id_vivero).first()
        
        if not vivero:
            raise NotFound('El Vivero seleccionado no existe')
        
        cambio_etapa=CambiosDeEtapa.objects.filter(**filter).filter(id_vivero=id_vivero)
        serializador=self.serializer_class(cambio_etapa,many=True)    
        return Response ({'success':True,'detail':'Se encontraron las siguientes coincidencias','data':serializador.data},status=status.HTTP_200_OK)
    
class AnularCambioEtapa(generics.UpdateAPIView):
    serializer_class = AnularCambioEtapaSerializer
    queryset = CambiosDeEtapa.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
        data = request.data
        persona = request.user.persona.id_persona
        cambio_etapa = self.queryset.all().filter(id_cambio_de_etapa=pk).first()
        if cambio_etapa:
            # VALIDAR ANTIGUEDAD POSIBLE DE FECHA CAMBIO
            if cambio_etapa.fecha_cambio.replace(minute=0, second=0, microsecond=0) < datetime.now()-timedelta(days=30):
                raise ValidationError('No puede actualizar porque la fecha de cambio supera los 30 días de antiguedad')
            
            cod_nueva_etapa = 'P' if cambio_etapa.cod_etapa_lote_origen == 'G' else 'D'
            
            inventario_vivero = InventarioViveros.objects.filter(
                id_vivero=cambio_etapa.id_vivero.id_vivero,
                id_bien=cambio_etapa.id_bien.id_bien,
                agno_lote=cambio_etapa.agno_lote,
                nro_lote=cambio_etapa.nro_lote
            )
            inventario_vivero_etapa_nueva = inventario_vivero.filter(cod_etapa_lote=cod_nueva_etapa).first()
            inventario_vivero_etapa_origen = inventario_vivero.filter(cod_etapa_lote=cambio_etapa.cod_etapa_lote_origen).first()
            
            if cambio_etapa.cod_etapa_lote_origen == 'G':
                if inventario_vivero_etapa_nueva.fecha_ult_altura_lote < inventario_vivero_etapa_nueva.fecha_ingreso_lote_etapa:
                    raise PermissionDenied('No se puede anular el cambio de etapa porque hubo una actualización a la altura del lote en Producción')
                
                if inventario_vivero_etapa_nueva.cantidad_bajas and inventario_vivero_etapa_nueva.cantidad_bajas > 0:
                    raise PermissionDenied('No se puede anular el cambio de etapa porque tiene registros de bajas')
                
                if inventario_vivero_etapa_nueva.cantidad_traslados_lote_produccion_distribucion and inventario_vivero_etapa_nueva.cantidad_traslados_lote_produccion_distribucion > 0:
                    raise PermissionDenied('No se puede anular el cambio de etapa porque tiene traslados a la etapa de Distribución')
                
                if inventario_vivero_etapa_nueva.cantidad_salidas and inventario_vivero_etapa_nueva.cantidad_salidas > 0:
                    raise PermissionDenied('No se puede anular el cambio de etapa porque tiene salidas a otros viveros')

                if inventario_vivero_etapa_nueva.cantidad_lote_cuarentena and inventario_vivero_etapa_nueva.cantidad_lote_cuarentena > 0:
                    raise PermissionDenied('No se puede anular el cambio de etapa porque tiene unidades del lote en cuarentena')
                
                # VALIDAR QUE NO HAYAN REGISTROS DE CUARENTENA EN MISMO LOTE-ETAPA
                cuarentenas = CuarentenaMatVegetal.objects.filter(
                    id_vivero=data['id_vivero'],
                    id_bien=data['id_bien'],
                    agno_lote=data['agno_lote'],
                    nro_lote=data['nro_lote'],
                    cod_etapa_lote=data['cod_etapa_lote_origen']
                )
                
                if cuarentenas:
                    raise PermissionDenied('No se puede anular el cambio de etapa porque existen registros de cuarentena para el mismo lote-etapa')
                
                # VALIDAR QUE NO HAYAN REGISTROS DE INCIDENCIAS EN MISMO LOTE-ETAPA
                incidencias = IncidenciasMatVegetal.objects.filter(
                    id_vivero=data['id_vivero'],
                    id_bien=data['id_bien'],
                    agno_lote=data['agno_lote'],
                    nro_lote=data['nro_lote'],
                    cod_etapa_lote=data['cod_etapa_lote_origen']
                )
                
                if incidencias:
                    raise PermissionDenied('No se puede anular el cambio de etapa porque existen registros de incidencias para el mismo lote-etapa')
            
                # SE ELIMINA EL REGISTRO DEL CAMBIO DE ETAPA EN INVENTARIO VIVERO
                inventario_vivero_etapa_nueva.delete()
                
                # SE REABRE LA SIEMBRA
                inventario_vivero_etapa_origen.siembra_lote_cerrada = False
                inventario_vivero_etapa_origen.save()
                
                # SE ANULA CAMBIO DE ETAPA
                data['id_persona_anula'] = persona
                data['cambio_anulado'] = True
                data['fecha_anulacion'] = datetime.now()
                
                serializer = self.serializer_class(cambio_etapa, data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
                return Response({'success':True, 'detail':'Se anuló correctamente el cambio de etapa', 'data':serializer.data}, status=status.HTTP_201_CREATED)
            else:
                cantidad_entrante = inventario_vivero_etapa_nueva.cantidad_entrante if inventario_vivero_etapa_nueva.cantidad_entrante else 0
                cantidad_bajas = inventario_vivero_etapa_nueva.cantidad_bajas if inventario_vivero_etapa_nueva.cantidad_bajas else 0
                cantidad_salidas = inventario_vivero_etapa_nueva.cantidad_salidas if inventario_vivero_etapa_nueva.cantidad_salidas else 0
                cantidad_lote_cuarentena = inventario_vivero_etapa_nueva.cantidad_lote_cuarentena if inventario_vivero_etapa_nueva.cantidad_lote_cuarentena else 0
                    
                saldo_disponible = cantidad_entrante - cantidad_bajas - cantidad_salidas - cantidad_lote_cuarentena
                
                if cambio_etapa.cantidad_movida == inventario_vivero_etapa_nueva.cantidad_entrante:
                    if inventario_vivero_etapa_nueva.fecha_ult_altura_lote < inventario_vivero_etapa_nueva.fecha_ingreso_lote_etapa:
                        raise PermissionDenied('No se puede anular el cambio de etapa porque hubo una actualización a la altura del lote en Producción')
                    
                    if cambio_etapa.cantidad_movida != saldo_disponible:
                        raise PermissionDenied('No se puede anular el cambio de etapa porque la cantidad movida (' + str(cambio_etapa.cantidad_movida) + ') no es igual al saldo disponible (' + str(saldo_disponible) + ')')

                    # VALIDAR QUE NO HAYAN REGISTROS DE CUARENTENA EN MISMO LOTE-ETAPA
                    cuarentenas = CuarentenaMatVegetal.objects.filter(
                        id_vivero=data['id_vivero'],
                        id_bien=data['id_bien'],
                        agno_lote=data['agno_lote'],
                        nro_lote=data['nro_lote'],
                        cod_etapa_lote=data['cod_etapa_lote_origen'],
                        cuarentena_anulada=False
                    )
                    
                    if cuarentenas:
                        raise PermissionDenied('No se puede anular el cambio de etapa porque existen registros de cuarentena para el mismo lote-etapa')
                    
                    # VALIDAR QUE NO HAYAN REGISTROS DE INCIDENCIAS EN MISMO LOTE-ETAPA
                    incidencias = IncidenciasMatVegetal.objects.filter(
                        id_vivero=data['id_vivero'],
                        id_bien=data['id_bien'],
                        agno_lote=data['agno_lote'],
                        nro_lote=data['nro_lote'],
                        cod_etapa_lote=data['cod_etapa_lote_origen']
                    )
                    
                    if incidencias:
                        raise PermissionDenied('No se puede anular el cambio de etapa porque existen registros de incidencias para el mismo lote-etapa')
            
                    # SE ELIMINA EL REGISTRO DEL CAMBIO DE ETAPA EN INVENTARIO VIVERO
                    inventario_vivero_etapa_nueva.delete()
                    
                    # SE ACTUALIZA EL REGISTRO ETAPA ORIGEN
                    inventario_vivero_etapa_origen.cantidad_traslados_lote_produccion_distribucion = inventario_vivero_etapa_origen.cantidad_traslados_lote_produccion_distribucion - cambio_etapa.cantidad_movida if inventario_vivero_etapa_origen.cantidad_traslados_lote_produccion_distribucion else 0
                    inventario_vivero_etapa_origen.save()
                    
                    # SE ANULA CAMBIO DE ETAPA  
                    data['id_persona_anula'] = persona
                    data['cambio_anulado'] = True
                    data['fecha_anulacion'] = datetime.now()
                    
                    serializer = self.serializer_class(cambio_etapa, data=data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    
                    return Response({'success':True, 'detail':'Se anuló correctamente el cambio de etapa', 'data':serializer.data}, status=status.HTTP_201_CREATED)
                
                else:
                    if saldo_disponible < cambio_etapa.cantidad_movida:
                        raise PermissionDenied('No se puede anular el cambio de etapa porque el saldo disponible (' + str(saldo_disponible) + ') es menor a la cantidad movida (' + str(cambio_etapa.cantidad_movida) + ')')
                    
                    ultimo_cambio_etapa = self.queryset.all().filter(id_bien=cambio_etapa.id_bien, id_vivero=cambio_etapa.id_vivero, agno_lote=cambio_etapa.agno_lote, nro_lote=cambio_etapa.nro_lote, cod_etapa_lote_origen=cambio_etapa.cod_etapa_lote_origen, cambio_anulado=None).last()
                    
                    if cambio_etapa.consec_por_lote_etapa != ultimo_cambio_etapa.consec_por_lote_etapa:
                        raise PermissionDenied('No se puede anular el cambio de etapa debido a que no es el último cambio de etapa para dicho lote-etapa de Producción')
                    
                    # VALIDAR QUE NO HAYAN REGISTROS DE CUARENTENA EN MISMO LOTE-ETAPA
                    cantidad_entrante_resta = inventario_vivero_etapa_nueva.cantidad_entrante - cambio_etapa.cantidad_movida if inventario_vivero_etapa_nueva.cantidad_entrante else 0
                    
                    cuarentenas = CuarentenaMatVegetal.objects.filter(
                        id_vivero=data['id_vivero'],
                        id_bien=data['id_bien'],
                        agno_lote=data['agno_lote'],
                        nro_lote=data['nro_lote'],
                        cod_etapa_lote=data['cod_etapa_lote_origen'],
                        cuarentena_anulada=False,
                        cantidad_cuarentena__gt=cantidad_entrante_resta
                    )
                    
                    if cuarentenas:
                        raise PermissionDenied('No se puede anular el cambio de etapa porque hay registros de cuarentena que contaron con unidades pertenecientes a este cambio de etapa')
                    
                    if cambio_etapa.consec_por_lote_etapa == 1:
                        # SE ELIMINA EL REGISTRO DEL CAMBIO DE ETAPA EN INVENTARIO VIVERO
                        inventario_vivero_etapa_nueva.delete()
                        
                        # SE ACTUALIZA EL REGISTRO ETAPA ORIGEN
                        inventario_vivero_etapa_origen.cantidad_traslados_lote_produccion_distribucion = inventario_vivero_etapa_origen.cantidad_traslados_lote_produccion_distribucion - cambio_etapa.cantidad_movida if inventario_vivero_etapa_origen.cantidad_traslados_lote_produccion_distribucion else 0
                        inventario_vivero_etapa_origen.save()
                        
                        # SE ANULA CAMBIO DE ETAPA  
                        data['id_persona_anula'] = persona
                        data['cambio_anulado'] = True
                        data['fecha_anulacion'] = datetime.now()
                        
                        serializer = self.serializer_class(cambio_etapa, data=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        
                        return Response({'success':True, 'detail':'Se anuló correctamente el cambio de etapa', 'data':serializer.data}, status=status.HTTP_201_CREATED)
                    else:
                        # SE ACTUALIZA EL REGISTRO ETAPA DESTINO
                        inventario_vivero_etapa_nueva.cantidad_entrante = inventario_vivero_etapa_nueva.cantidad_entrante - cambio_etapa.cantidad_movida if inventario_vivero_etapa_nueva.cantidad_entrante else 0
                        inventario_vivero_etapa_nueva.save()
                        
                        # SE ACTUALIZA EL REGISTRO ETAPA ORIGEN
                        inventario_vivero_etapa_origen.cantidad_traslados_lote_produccion_distribucion = inventario_vivero_etapa_origen.cantidad_traslados_lote_produccion_distribucion - cambio_etapa.cantidad_movida if inventario_vivero_etapa_origen.cantidad_traslados_lote_produccion_distribucion else 0
                        inventario_vivero_etapa_origen.save()
                        
                        # SE ANULA CAMBIO DE ETAPA  
                        data['id_persona_anula'] = persona
                        data['cambio_anulado'] = True
                        data['fecha_anulacion'] = datetime.now()
                        
                        serializer = self.serializer_class(cambio_etapa, data=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        
                        # VALIDACIÓN SI FECHA ULTIMA ALTURA Y FECHA CAMBIO SON IGUALES - PENDIENTE
                        if inventario_vivero_etapa_nueva.fecha_ult_altura_lote.replace(minute=0, second=0, microsecond=0) == cambio_etapa.fecha_cambio.replace(minute=0, second=0, microsecond=0):
                            return Response({'success':True, 'detail':'Se realizó la anulación, pero la altura con la que quedó el lote-destino fue registrada por el cambio de etapa que se está anulando, se le recomienda ir a verificar que sea correcta y actualizar de ser necesario'}, status=status.HTTP_201_CREATED)
                        
                        return Response({'success':True, 'detail':'Se anuló correctamente el cambio de etapa', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        else:
            raise NotFound('No existe el cambio de etapa que desea actualizar')
