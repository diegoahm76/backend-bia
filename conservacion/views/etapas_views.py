from rest_framework.response import Response
from rest_framework import generics,status
from django.db.models import Q
from conservacion.serializers.etapas_serializers import InventarioViverosSerializer
from conservacion.models.inventario_models import InventarioViveros
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES

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
                    
        inventario_vivero=InventarioViveros.objects.filter(**filter).filter(id_vivero=id_vivero,id_bien__cod_tipo_elemento_vivero="MV",id_bien__es_semilla_vivero=False,cod_etapa_lote__in=['G','P']).filter(~Q(siembra_lote_cerrada=True))
        list_items=[]
        for item in inventario_vivero:
            if item.cod_etapa_lote == "P":
                cantidad_entrante = item.cantidad_entrante if item.cantidad_entrante else 0
                cantidad_bajas = item.cantidad_bajas if item.cantidad_bajas else 0
                cantidad_traslados = item.cantidad_traslados_lote_produccion_distribucion if item.cantidad_traslados_lote_produccion_distribucion else 0
                cantidad_salidas = item.cantidad_salidas if item.cantidad_salidas else 0
                cantidad_lote_cuarentena = item.cantidad_lote_cuarentena if item.cantidad_lote_cuarentena else 0
                item.cantidad_disponible = cantidad_entrante - cantidad_bajas - cantidad_traslados - cantidad_salidas - cantidad_lote_cuarentena
                if item.cantidad_disponible > 0:
                    list_items.append(item)
            else:
                list_items.append(item)
                    
        serializador=self.serializer_class(list_items,many=True)    
        return Response ({'success':True,'detail':'Se encontraron las siguientes coincidencias','data':serializador.data},status=status.HTTP_200_OK)