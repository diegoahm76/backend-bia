from almacen.models.bienes_models import CatalogoBienes
from rest_framework import generics, status
from rest_framework.views import APIView
from almacen.serializers.bienes_serializers import (
    CatalogoBienesSerializer
    )   
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

class GetCatalogoBienesList(generics.ListAPIView):
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()

    def get(self, request):
        codigo = request.query_params.get('codigo')
        nombre = request.query_params.get('nombre')
        
        nodos_principales = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=1).values()
        if not nodos_principales:
            return Response({'success':True, 'detail':'No se encontró nada en almacén', 'data':nodos_principales}, status=status.HTTP_200_OK)
        
        for nodo in nodos_principales:
            nodos_nivel_dos = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=2, id_bien_padre=nodo['id_bien']).values()
            if nodos_nivel_dos:
                nodo['nivel_dos'] = nodos_nivel_dos
                for nodo_dos in nodos_nivel_dos:
                    nodos_nivel_tres = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=3, id_bien_padre=nodo_dos['id_bien']).values()
                    if nodos_nivel_tres:
                        nodo_dos['nivel_tres'] = nodos_nivel_tres
                        for nodo_tres in nodos_nivel_tres:
                            nodos_nivel_cuatro = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=4, id_bien_padre=nodo_tres['id_bien']).values()
                            if nodos_nivel_cuatro:
                                nodo_tres['nivel_cuatro'] = nodos_nivel_cuatro
                                for nodo_cuatro in nodos_nivel_cuatro:
                                    nodos_nivel_cinco = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=5, id_bien_padre=nodo_cuatro['id_bien']).values()
                                    if nodos_nivel_cinco:
                                        nodo_cuatro['nivel_cinco'] = nodos_nivel_cinco
            
        return Response({'success':True, 'detail':'Se encontró lo siguiente en almacén', 'data':nodos_principales}, status=status.HTTP_200_OK)