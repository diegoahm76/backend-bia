from almacen.models.bienes_models import CatalogoBienes
from almacen.serializers.bienes_serializers import CatalogoBienesSerializer
from rest_framework import generics,status
from rest_framework.response import Response

class SearchVisibleBySolicitud(generics.ListAPIView):
    serializer_class=CatalogoBienesSerializer
    queryset=CatalogoBienes.objects.all()
    def get(self,request):
        filter={}
        for key,value in request.query_params.items():
            if key in ['nombre','codigo_bien']:
                filter[key+'__icontains']=value
        nodos=[2,3,4,5]
        filter['nivel_jerarquico__in'] = nodos
        filter['visible_solicitudes']= True
        bien=CatalogoBienes.objects.filter(**filter)
        serializador=self.serializer_class(bien,many=True)
        if bien:
            return Response({'success':True,'detail':'se encontró elementos','data':serializador.data},status=status.HTTP_200_OK)
        return Response({'success':True,'detail':'no se econtrò elementos','data':bien},status=status.HTTP_404_NOT_FOUND)