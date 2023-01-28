from rest_framework.response import Response
from rest_framework import generics,status
from django.db.models import Q
from conservacion.serializers.etapas_serializers import InventarioViverosSerializer, GuardarCambioEtapaSerializer
from conservacion.models.inventario_models import InventarioViveros
from conservacion.models.siembras_models import CambiosDeEtapa
from conservacion.models.viveros_models import Vivero
from datetime import datetime, timedelta
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
    
class GuardarCambioEtapa(generics.UpdateAPIView):
    serializer_class=GuardarCambioEtapaSerializer
    queryset=CambiosDeEtapa.objects.all()
    
    def put(self,request):
        data = request.data
        
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
        if fecha_cambio < datetime.today()-timedelta(days=30):
            return Response({'success':False, 'detail':'La fecha de cambio no puede superar 30 días de antiguedad'}, status=status.HTTP_400_BAD_REQUEST)
        
        # VALIDACIONES FECHA CAMBIO SI ETAPA LOTE ES GERMINACIÓN
        if data['cod_etapa_lote_origen'] == 'G':
            if fecha_cambio < inventario_vivero.fecha_ingreso_lote_etapa or fecha_cambio < inventario_vivero.fecha_ult_altura_lote:
                return Response({'success':False, 'detail':'La fecha de cambio debe ser posterior a la fecha de ingreso al lote y posterior a la fecha de la última altura del material elegido'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACION DE FECHA CAMBIO PARA LA ETAPA LOTE DE PRODUCCIÓN 
        if data['cod_etapa_lote_origen'] == 'P':
            if inventario_vivero.cantidad_traslados_lote_produccion_distribucion > 0:
                cambio_etapa=CambiosDeEtapa.objects.filter(id_bien=inventario_vivero.id_bien.id_bien,id_vivero=inventario_vivero.id_vivero.id_vivero,agno_lote=inventario_vivero.agno_lote,nro_lote=inventario_vivero.nro_lote,cambio_anulado=False).last()
                if cambio_etapa:
                    if  fecha_cambio < cambio_etapa.fecha_cambio:
                        return Response({'success':False,'detail':'La fecha elegida para el cambio debe ser posterior a la fecha del último cambio de etapa'},status=status.HTTP_403_FORBIDDEN)
            else:
                if fecha_cambio < inventario_vivero.fecha_ingreso_lote_etapa:
                    return Response({'success':False,'detail':'la fecha elegida para el Cambio debe ser posterior a la fecha de ingreso del lote'},status=status.HTTP_403_FORBIDDEN)
        
        #VALIDACIÓN DE CANTIDAD DISPONIBLE
        cantidad_disponible=UtilConservacion.get_cantidad_disponible_etapa(inventario_vivero)
        if data['cod_etapa_lote_origen'] == 'P':
            if cantidad_disponible != int(data['cantidad_disponible_al_crear']):
                if int(data['cantidad_movida']) > cantidad_disponible:
                    return Response ({'success':False,'detail':'La cantidad disponible cambió, por favor cambiar la cantidad movida'},status=status.HTTP_400_BAD_REQUEST)
            else:
                if int(data['cantidad_movida']) > cantidad_disponible:
                        return Response ({'success':False,'detail':'La cantidad movida no puede superar la cantidad disponible actual'},status=status.HTTP_400_BAD_REQUEST)
            
        # serializador.save()
        
        return Response ({'success':True,'detail':'Se realizó el cambio de etapa correctamente','data':[]},status=status.HTTP_200_OK)
