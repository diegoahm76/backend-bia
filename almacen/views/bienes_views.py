from almacen.models.bienes_models import CatalogoBienes
from rest_framework import generics, status
from rest_framework.views import APIView
from almacen.serializers.bienes_serializers import (
    CatalogoBienesSerializer
    )
from almacen.models.inventario_models import (
    Inventario
)   
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

class CreateCatalogoDeBienes(generics.CreateAPIView):
    serializer_class = CatalogoBienesSerializer
    def post(self, request):
        print(request)

class GetCatalogoBienesList(generics.ListAPIView):
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()

    def get(self, request):
        codigo_bien = request.query_params.get('codigo-bien')
        nombre = request.query_params.get('nombre')
        
        # FILTROS
        # nodo_found = None
        # if codigo_bien and not nombre:
        #     nodo_found = CatalogoBienes.objects.filter(nro_elemento_bien=None, codigo_bien=codigo_bien).values().first()
        # elif not codigo_bien and nombre:
        #     nodo_found = CatalogoBienes.objects.filter(nro_elemento_bien=None, nombre=nombre).values().first()
        # elif codigo_bien and nombre:
        #     nodo_found = CatalogoBienes.objects.filter(nro_elemento_bien=None, codigo_bien=codigo_bien, nombre=nombre).values().first()
        
        # if nodo_found:
        #     nodo_padre = [nodo_found]
        #     id_bien_padre = nodo_found['id_bien_padre_id']
        #     for i in range(nodo_found['nivel_jerarquico']-1, 0, -1):
        #         nodo_padre_for = CatalogoBienes.objects.filter(id_bien=id_bien_padre).values().first()
        #         nodo_padre_for['nodos_hijos'] = nodo_padre
        #         id_bien_padre = nodo_padre_for['id_bien_padre_id']
        #         nodo_padre = [nodo_padre_for]
        #     return Response({'status':True, 'detail':'Se encontraron resultados', 'data':nodo_padre}, status=status.HTTP_200_OK)
        # else:
        #     return Response({'status':True, 'detail':'No se encontró el nodo por los parámetros indicados', 'data':nodo_found}, status=status.HTTP_200_OK)
        
        nodos_principales = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=1).values()
        if not nodos_principales:
            return Response({'success':True, 'detail':'No se encontró nada en almacén', 'data':nodos_principales}, status=status.HTTP_200_OK)
        
        for nodo in nodos_principales:
            nodos_nivel_dos = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=2, id_bien_padre=nodo['id_bien']).values()
            if nodos_nivel_dos:
                nodo['nodos_hijos'] = nodos_nivel_dos
                for nodo_dos in nodos_nivel_dos:
                    nodos_nivel_tres = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=3, id_bien_padre=nodo_dos['id_bien']).values()
                    if nodos_nivel_tres:
                        nodo_dos['nodos_hijos'] = nodos_nivel_tres
                        for nodo_tres in nodos_nivel_tres:
                            nodos_nivel_cuatro = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=4, id_bien_padre=nodo_tres['id_bien']).values()
                            if nodos_nivel_cuatro:
                                nodo_tres['nodos_hijos'] = nodos_nivel_cuatro
                                for nodo_cuatro in nodos_nivel_cuatro:
                                    nodos_nivel_cinco = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=5, id_bien_padre=nodo_cuatro['id_bien']).values()
                                    if nodos_nivel_cinco:
                                        nodo_cuatro['nodos_hijos'] = nodos_nivel_cinco
            
        return Response({'success':True, 'detail':'Se encontró lo siguiente en almacén', 'data':nodos_principales}, status=status.HTTP_200_OK)


class DeleteNodos(generics.RetrieveDestroyAPIView):
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()
    lookup_field = 'id_bien'

    def delete(self, request, id_bien):
        nodo = CatalogoBienes.objects.filter(id_bien=id_bien).first()
        if nodo:
            if nodo.nro_elemento_bien:
                registra_movimiento = Inventario.objects.filter(id_bien=nodo.id_bien)
                if registra_movimiento:
                    return Response({'success': False, 'detail': 'No se puede eliminar un elemento, solo nodos iniciales'}, status=status.HTTP_400_BAD_REQUEST)
                nodo.delete()
                return Response({'success': True, 'detail': 'Eliminado el elemento'}, status=status.HTTP_204_NO_CONTENT)
            
            hijos = CatalogoBienes.objects.filter(id_bien_padre=nodo.id_bien)
            if hijos:
                return Response({'success': False, 'detail': 'No se puede eliminar un bien si es padre de otros bienes'}, status=status.HTTP_403_FORBIDDEN)
            
            nodo.delete()
            return Response({'success': True,'detail': 'Se ha eliminado el bien correctamente'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'success': False, 'detail': 'No se encontró ningún nodo con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)