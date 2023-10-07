import operator, itertools
from almacen.models.bienes_models import ItemEntradaAlmacen
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.db.models import F, Count, Sum
from almacen.serializers.reportes_serializers import EntradasInventarioGetSerializer, MovimientosIncautadosGetSerializer

class EntradasInventarioGetView(generics.ListAPIView):
    serializer_class=EntradasInventarioGetSerializer
    queryset=ItemEntradaAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter={}
        
        for key,value in request.query_params.items():
            if key in ['id_bodega','cod_tipo_bien','fecha_desde','fecha_hasta']:
                if key == 'cod_tipo_bien':
                    if value != '':
                        filter['id_bien__cod_tipo_bien']=value
                elif key == 'fecha_desde':
                    if value != '':
                        filter['id_entrada_almacen__fecha_entrada__gte']=value
                elif key == 'fecha_hasta':
                    if value != '':
                        filter['id_entrada_almacen__fecha_entrada__lte']=value
                else:
                    if value != '':
                        filter[key]=value
        
        items_entradas = self.queryset.filter(**filter).filter(id_bien__nivel_jerarquico=5)
        serializer = self.serializer_class(items_entradas, many=True)
        serializer_data = serializer.data
        
        data_output = []
        
        if items_entradas:
            items_entrada_data = sorted(serializer_data, key=operator.itemgetter("id_bodega", "nombre_bodega", "id_bien", "nombre_bien", "codigo_bien", "responsable_bodega"))
                
            for entrada, items in itertools.groupby(items_entrada_data, key=operator.itemgetter("id_bodega", "nombre_bodega", "id_bien", "nombre_bien", "codigo_bien", "responsable_bodega")):
                detalles = list(items)
                
                for detalle in detalles:
                    del detalle['id_bodega']
                    del detalle['nombre_bodega']
                    del detalle['id_bien']
                    del detalle['nombre_bien']
                    del detalle['codigo_bien']
                    del detalle['responsable_bodega']
                    
                items_data = {
                    "id_bodega": entrada[0],
                    "nombre_bodega": entrada[1],
                    "id_bien": entrada[2],
                    "nombre_bien": entrada[3],
                    "codigo_bien": entrada[4],
                    "cantidad_ingresada_total": sum(item['cantidad'] for item in detalles),
                    "responsable_bodega": entrada[5],
                    "detalle": detalles
                }
                
                data_output.append(items_data)

        return Response({'success':True,'detail':'Se encontró la siguiente información','data':data_output},status=status.HTTP_200_OK)

class MovimientosIncautadosGetView(generics.ListAPIView):
    serializer_class=MovimientosIncautadosGetSerializer
    queryset=ItemEntradaAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter={}
        
        for key,value in request.query_params.items():
            if key in ['fecha_desde','fecha_hasta']:
                if key == 'fecha_desde':
                    if value != '':
                        filter['id_entrada_almacen__fecha_entrada__gte']=value
                elif key == 'fecha_hasta':
                    if value != '':
                        filter['id_entrada_almacen__fecha_entrada__lte']=value
                else:
                    if value != '':
                        filter[key]=value
        
        items_entradas = self.queryset.filter(**filter).filter(id_entrada_almacen__id_tipo_entrada=8, id_bien__nivel_jerarquico=5)
        serializer = self.serializer_class(items_entradas, many=True)
        serializer_data = serializer.data
        
        data_output = []
        
        if items_entradas:
            # data_output = items_entradas.values(
            #     'id_bodega',
            #     'id_bien',
            #     'cantidad',
            #     nombre_bodega=F('id_bodega__nombre'),
            #     nombre_bien=F('id_bien__id_bien_padre__nombre'),
            #     codigo_bien=F('id_bien__codigo_bien'),
            #     tipo_activo=F('id_bien__get_cod_tipo_bien_display'),
            # ).annotate(
            #     cantidad_ingresada=Sum('cantidad')
            # )
            
            items_entrada_data = sorted(serializer_data, key=operator.itemgetter("id_bodega", "nombre_bodega", "id_bien", "nombre_bien", "codigo_bien", "tipo_activo"))
                
            for entrada, items in itertools.groupby(items_entrada_data, key=operator.itemgetter("id_bodega", "nombre_bodega", "id_bien", "nombre_bien", "codigo_bien", "tipo_activo")):
                items_list = list(items)
                
                items_data = {
                    "id_bodega": entrada[0],
                    "nombre_bodega": entrada[1],
                    "id_bien": entrada[2],
                    "nombre_bien": entrada[3],
                    "codigo_bien": entrada[4],
                    "tipo_activo": entrada[5],
                    "cantidad_ingresada": sum(item['cantidad'] for item in items_list)
                }
                
                data_output.append(items_data)

        return Response({'success':True,'detail':'Se encontró la siguiente información','data':data_output},status=status.HTTP_200_OK)