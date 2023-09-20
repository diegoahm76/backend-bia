from almacen.models.bienes_models import CatalogoBienes
from almacen.models.generics_models import Bodegas
from rest_framework import generics, status
from rest_framework.views import APIView
from almacen.models.inventario_models import Inventario
from almacen.serializers.generics_serializers import (
    SerializersMarca
    )   
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from almacen.serializers.inventario_serializers import BusquedaBienesSerializer, ControlInventarioTodoSerializer

class BusquedaBienesView(generics.ListAPIView):
    serializer_class=BusquedaBienesSerializer
    queryset=CatalogoBienes.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter={}
        
        for key,value in request.query_params.items():
            if key in ['codigo_bien','serial','nombre_bien','cod_tipo_activo', 'nombre_marca']:
                if key == 'serial':
                    if value != '':
                        filter['doc_identificador_nro__icontains']=value
                elif key == 'nombre_bien':
                    if value != '':
                        filter['nombre__icontains']=value
                elif key == 'nombre_marca':
                    if value != '':
                        filter['id_marca__nombre__icontains']=value
                elif key == 'codigo_bien':
                    if value != '':
                        filter['codigo_bien__icontains']=value
                else:
                    if value != '':
                        filter[key]=value
        
        catalogo_bienes = self.queryset.filter(**filter).filter(cod_tipo_bien='A')
        
        serializer = self.serializer_class(catalogo_bienes, many=True)

        return Response({'success':True,'detail':'Se encontró la siguiente información','data':serializer.data},status=status.HTTP_200_OK)


class ControlActivosFijosGetListView(generics.ListAPIView):
    serializer_class=ControlInventarioTodoSerializer
    queryset=Inventario.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter={}
        
        for key,value in request.query_params.items():
            if key in ['id_bodega','cod_estado_activo','ubicacion','propiedad','cod_tipo_activo', 'realizo_baja', 'realizo_salida']:
                if key == 'cod_tipo_activo':
                    if value != '':
                        filter['id_bien__cod_tipo_activo']=value
                elif key == 'ubicacion':
                    if value == 'Asignado':
                        filter['ubicacion_asignado']=True
                    elif value == 'Prestado':
                        filter['ubicacion_prestado']=True
                    elif value == 'En Bodega':
                        filter['ubicacion_en_bodega']=True
                elif key == 'propiedad':
                    if value == 'Propio':
                        filter['cod_tipo_entrada__constituye_propiedad']=True
                    elif value == 'No Propio':
                        filter['cod_tipo_entrada__constituye_propiedad']=False
                elif key == 'realizo_baja':
                    if value.lower() == 'true':
                        filter['realizo_baja']=True
                elif key == 'realizo_salida':
                    if value.lower() == 'true':
                        filter['realizo_salida']=True
                else:
                    if value != '':
                        filter[key]=value
        
        inventarios = self.queryset.filter(**filter).filter(id_bien__cod_tipo_bien='A')
        
        serializer = self.serializer_class(inventarios, many=True)

        return Response({'success':True,'detail':'Se encontró la siguiente información','data':serializer.data},status=status.HTTP_200_OK)

class ControlActivosFijosGetByIdBienView(generics.ListAPIView):
    serializer_class=ControlInventarioTodoSerializer
    queryset=Inventario.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request,id_bien):
        inventario = self.queryset.filter(id_bien=id_bien).first()
        serializer = self.serializer_class(inventario)

        return Response({'success':True,'detail':'Se encontró la siguiente información','data':serializer.data},status=status.HTTP_200_OK)
