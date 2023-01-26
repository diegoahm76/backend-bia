from rest_framework.response import Response
from rest_framework import generics,status
from conservacion.serializers.etapas_serializers import InventarioViverosSerializer
from conservacion.models.inventario_models import InventarioViveros
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES

class FiltroMaterialVegetal(generics.ListAPIView):
    serializer_class=InventarioViverosSerializer
    queryset=InventarioViveros
    
    def get(self,request):
        filter={}
        
        for key,value in request.query_params.items():
            if key in ['codigo_bien','nombre','cod_etapa_lote','agno_lote']:
                if key != "cod_etapa_lote" and key != 'agno_lote':
                    filter['id_bien__'+key+'__icontains'] = value
                else:
                    filter[key] = value
                    
        inventario_vivero=InventarioViveros.objects.filter(**filter).filter(id_bien__cod_tipo_elemento_vivero="MV",id_bien__es_semilla_vivero=False,cod_etapa_lote__in=['G','P'])
        
        serializador=self.serializer_class(inventario_vivero,many=True)    
        return Response ({'success':True,'detail':'Se encontraron las siguientes coincidencias','data':serializador.data},status=status.HTTP_200_OK)
        
                    
 