from almacen.models.bienes_models import CatalogoBienes
from almacen.models.generics_models import Bodegas
from rest_framework import generics, status
from rest_framework.views import APIView
from almacen.models.inventario_models import Inventario, TiposEntradas
from almacen.serializers.generics_serializers import (
    SerializersMarca
    )   
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.db.models import F, Count
import operator, itertools

from almacen.serializers.inventario_serializers import BusquedaBienesConsumoSerializer, BusquedaBienesSerializer, ControlBienesConsumoGetListSerializer, ControlInventarioByTipoSerializer, ControlInventarioTodoSerializer, OrigenesListGetSerializer

class OrigenesListGetView(generics.ListAPIView):
    serializer_class=OrigenesListGetSerializer
    queryset=TiposEntradas.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        queryset = self.queryset.all().order_by('cod_tipo_entrada')
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success':True, 'message':'Se encontraron los siguientes tipos de origenes', 'data':serializer.data}, status=status.HTTP_200_OK)

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

class BusquedaBienesConsumoView(generics.ListAPIView):
    serializer_class=BusquedaBienesConsumoSerializer
    queryset=CatalogoBienes.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter={}
        
        for key,value in request.query_params.items():
            if key in ['codigo_bien','nombre_bien','cod_tipo_elemento_vivero', 'solicitable_vivero']:
                if key == 'nombre_bien':
                    if value != '':
                        filter['nombre__icontains']=value
                elif key == 'codigo_bien':
                    if value != '':
                        filter['codigo_bien__icontains']=value
                elif key == 'solicitable_vivero':
                    if value != '':
                        filter['solicitable_vivero']=True if value.lower() == 'true' else False
                else:
                    if value != '':
                        filter[key]=value
        
        catalogo_bienes = self.queryset.filter(**filter).filter(cod_tipo_bien='C')
        
        serializer = self.serializer_class(catalogo_bienes, many=True)

        return Response({'success':True,'detail':'Se encontró la siguiente información','data':serializer.data},status=status.HTTP_200_OK)

class ControlActivosFijosGetByIdBienView(generics.ListAPIView):
    serializer_class=ControlInventarioTodoSerializer
    queryset=Inventario.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request,id_bien):
        inventario = self.queryset.filter(id_bien=id_bien).first()
        serializer = self.serializer_class(inventario)

        return Response({'success':True,'detail':'Se encontró la siguiente información','data':serializer.data},status=status.HTTP_200_OK)

class ControlActivosFijosGetListView(generics.ListAPIView):
    serializer_class=ControlInventarioTodoSerializer
    queryset=Inventario.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter={}
        
        for key,value in request.query_params.items():
            if key in ['id_bodega','cod_estado_activo','ubicacion','propiedad','cod_tipo_activo', 'realizo_baja', 'realizo_salida', 'cod_tipo_entrada']:
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
        
        if request.query_params.get('cod_tipo_entrada', '') != '':
            inventarios = inventarios.order_by('cod_tipo_entrada__nombre')
        
        serializer = self.serializer_class(inventarios, many=True)

        return Response({'success':True,'detail':'Se encontró la siguiente información','data':serializer.data},status=status.HTTP_200_OK)

class ControlActivosFijosGetByCategoriaView(generics.ListAPIView):
    serializer_class=ControlInventarioTodoSerializer
    queryset=Inventario.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter={}
        
        for key,value in request.query_params.items():
            if key in ['id_bodega','cod_tipo_activo']:
                if key == 'cod_tipo_activo':
                    if value != '':
                        filter['id_bien__cod_tipo_activo']=value
                else:
                    if value != '':
                        filter[key]=value
                        
        inventarios = self.queryset.filter(**filter).filter(id_bien__cod_tipo_bien='A')
        
        serializer = self.serializer_class(inventarios, many=True)
        inventarios_data = serializer.data
        
        inventarios_data = sorted(inventarios_data, key=operator.itemgetter("constituye_propiedad", "propiedad"))
        data_output = []
        
        for propiedad, inventarios_obj in itertools.groupby(inventarios_data, key=operator.itemgetter("constituye_propiedad", "propiedad")):
            inventarios_propiedad = list(inventarios_obj)
            for inventario in inventarios_propiedad:
                del inventario['constituye_propiedad']
                del inventario['propiedad']
                
            items_data = {
                "constituye_propiedad": propiedad[0],
                "propiedad": propiedad[1],
                "inventario": inventarios_propiedad
            }
            
            data_output.append(items_data)

        return Response({'success':True,'detail':'Se encontró la siguiente información','data':data_output}, status=status.HTTP_200_OK)

class ControlActivosFijosGetPropioView(generics.ListAPIView):
    serializer_class=ControlInventarioTodoSerializer
    queryset=Inventario.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter={}
        agrupado = request.query_params.get('agrupado', '')
        agrupado = True if agrupado.lower() == 'true' else False
        
        for key,value in request.query_params.items():
            if key in ['id_bodega','cod_tipo_activo']:
                if key == 'cod_tipo_activo':
                    if value != '':
                        filter['id_bien__cod_tipo_activo']=value
                else:
                    if value != '':
                        filter[key]=value
                        
        inventarios = self.queryset.filter(**filter).filter(id_bien__cod_tipo_bien='A')
        
        serializer = self.serializer_class(inventarios, many=True)
        inventarios_data = serializer.data
        
        inventarios_data = sorted(inventarios_data, key=operator.itemgetter("cod_tipo_activo", "categoria"))
        data_output = []
        
        if agrupado:
            for categoria, inventarios_obj in itertools.groupby(inventarios_data, key=operator.itemgetter("cod_tipo_activo", "categoria")):
                inventarios_categoria = list(inventarios_obj)
                for inventario in inventarios_categoria:
                    del inventario['cod_tipo_activo']
                    del inventario['categoria']
                    
                items_data = {
                    "cod_tipo_activo": categoria[0],
                    "categoria": categoria[1],
                    "inventario": inventarios_categoria
                }
                
                data_output.append(items_data)
        else:
            data_output = serializer.data

        return Response({'success':True,'detail':'Se encontró la siguiente información','data':data_output}, status=status.HTTP_200_OK)

class ControlActivosFijosGetByTipoView(generics.ListAPIView):
    serializer_class=ControlInventarioByTipoSerializer
    queryset=Inventario.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        
        id_bodega = request.query_params.get('id_bodega', '')
        resultados_entidad = request.query_params.get('resultados_entidad', '')
        resultados_entidad = True if resultados_entidad.lower() == 'true' else False
                        
        inventarios = self.queryset.filter(id_bien__cod_tipo_bien='A')
        inventarios = inventarios.filter(id_bodega=id_bodega) if id_bodega != '' else inventarios
        
        data_output = []
        
        if resultados_entidad:
            inventarios_data = inventarios.values(
                'id_bodega',
                nombre_bodega=F('id_bodega__nombre'),
                id_bien_padre=F('id_bien__id_bien_padre__id_bien'),
                tipo_bien=F('id_bien__id_bien_padre__nombre'),
                codigo_bien=F('id_bien__codigo_bien'),
                id_marca=F('id_bien__id_bien_padre__id_marca__id_marca'),
                nombre_marca=F('id_bien__id_bien_padre__id_marca__nombre'),
            ).annotate(
                cantidad=Count('id_bodega')
            )
            
            inventarios_data = sorted(inventarios_data, key=operator.itemgetter("id_bodega", "nombre_bodega"))
            
            for bodega, inventarios_obj in itertools.groupby(inventarios_data, key=operator.itemgetter("id_bodega", "nombre_bodega")):
                inventarios_categoria = list(inventarios_obj)
                    
                items_data = {
                    "id_bodega": bodega[0],
                    "nombre_bodega": bodega[1],
                    "inventario": inventarios_categoria
                }
                
                data_output.append(items_data)
        else:
            data_output = inventarios.values(
                id_bien_padre=F('id_bien__id_bien_padre__id_bien'),
                tipo_bien=F('id_bien__id_bien_padre__nombre'),
                codigo_bien=F('id_bien__codigo_bien'),
                id_marca=F('id_bien__id_bien_padre__id_marca__id_marca'),
                nombre_marca=F('id_bien__id_bien_padre__id_marca__nombre'),
            ).annotate(
                cantidad=Count('id_bodega')
            )

        return Response({'success':True,'detail':'Se encontró la siguiente información','data':data_output}, status=status.HTTP_200_OK)

class ControlBienesConsumoGetListView(generics.ListAPIView):
    serializer_class=ControlBienesConsumoGetListSerializer
    queryset=Inventario.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter={}
        agrupado = request.query_params.get('agrupado', '')
        agrupado = True if agrupado.lower() == 'true' else False
        
        for key,value in request.query_params.items():
            if key in ['id_bodega','id_bien','solicitable_vivero']:
                if key == 'solicitable_vivero':
                    if value != '':
                        filter['id_bien__solicitable_vivero']=True if value.lower() == 'true' else False
                else:
                    if value != '':
                        filter[key]=value
        
        inventarios = self.queryset.filter(**filter).filter(id_bien__cod_tipo_bien='C')
        
        serializer = self.serializer_class(inventarios, many=True)
        inventarios_data = serializer.data
        
        inventarios_data = sorted(inventarios_data, key=operator.itemgetter("id_bodega", "nombre_bodega"))
        data_output = []
        
        if agrupado:
            for bodegas, inventarios_obj in itertools.groupby(inventarios_data, key=operator.itemgetter("id_bodega", "nombre_bodega")):
                inventarios_bodega = list(inventarios_obj)
                for inventario in inventarios_bodega:
                    del inventario['id_bodega']
                    del inventario['nombre_bodega']
                    
                items_data = {
                    "id_bodega": bodegas[0],
                    "nombre_bodega": bodegas[1],
                    "inventario": inventarios_bodega
                }
                
                data_output.append(items_data)
        else:
            data_output = serializer.data

        return Response({'success':True,'detail':'Se encontró la siguiente información','data':data_output},status=status.HTTP_200_OK)
