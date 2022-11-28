from almacen.models.generics_models import UnidadesMedida
from almacen.models.generics_models import Magnitudes
from almacen.models.generics_models import Bodegas
from rest_framework import generics
from rest_framework.views import APIView
from almacen.serializers.generics_serializers import (
    SerializersMarca,
    SerializersPostMarca,
    SerializersPutMarca,
    SerializerPorcentajesIVA,
    SerializerPostPorcentajesIVA,
    SerializerPutPorcentajesIVA,
    SerializersUnidadesMedida,
    SerializersPostUnidadesMedida,
    SerializersPutUnidadesMedida,
    SerializerBodegas,
    SerializerPostBodegas,
    SerializerPutBodegas,
    
    SerializerMagnitudes,
    SerializersEstadosArticulo
    )   
from almacen.models.generics_models import Marcas, PorcentajesIVA
from almacen.models.bienes_models import EstadosArticulo
from almacen.choices.estados_articulo_choices import estados_articulo_CHOICES
from almacen.choices.magnitudes_choices import magnitudes_CHOICES
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


#_______Marca
class RegisterMarca(generics.CreateAPIView):
    serializer_class=SerializersPostMarca
    queryset=Marcas.objects.all()
    
class UpdateMarca(generics.UpdateAPIView):
    serializer_class=SerializersPutMarca
    queryset=Marcas.objects.all()
    
class DeleteMarca(generics.DestroyAPIView):
    serializer_class=SerializersMarca
    queryset=Marcas.objects.all()

class GetMarcaById(generics.RetrieveAPIView):
    serializer_class=SerializersMarca
    queryset=Marcas.objects.all()

class GetMarcaList(generics.ListAPIView):
    serializer_class=SerializersMarca
    queryset=Marcas.objects.all()
    
    
# Estado Articulos  
class GetEstadosArticuloById(generics.RetrieveAPIView):
    serializer_class=SerializersEstadosArticulo
    queryset=EstadosArticulo.objects.all()

class GetEstadosArticuloList(generics.ListAPIView):
    serializer_class=SerializersEstadosArticulo
    queryset=EstadosArticulo.objects.all()

#Bodega

class RegisterBodega(generics.CreateAPIView):
    serializer_class=SerializerPostBodegas
    queryset=Bodegas.objects.all()
    
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        
        es_principal = serializer.validated_data.get('es_principal')
        
        bodega_principal = Bodegas.objects.filter(es_principal=es_principal).first()
        
        if bodega_principal and es_principal:
            return Response({'success': False, 'detail':'Ya existe una bodega principal'})
        else:
            serializer.save()
            return Response({'success': True, 'data':serializer.data})
    
class UpdateBodega(generics.UpdateAPIView):
    serializer_class=SerializerPutBodegas
    queryset=Bodegas.objects.all()
    
    def put(self, request, pk):
        data = request.data
        bodega = Bodegas.objects.filter(id_bodega=pk).first()
        if bodega:
            serializer = self.serializer_class(bodega, data=data, many=False)
            serializer.is_valid(raise_exception=True)
            
            es_principal = serializer.validated_data.get('es_principal')
            
            bodega_principal = Bodegas.objects.filter(es_principal=es_principal).first()
            
            if bodega_principal and es_principal:
                return Response({'success': False, 'detail':'Ya existe una bodega principal'})
            else:
                serializer.save()
                return Response({'success': True, 'data':serializer.data})
        else:
            return Response({'success': False, 'detail':'La bodega ingresada no existe'})
    
class DeleteBodega(generics.DestroyAPIView):
    serializer_class=SerializerBodegas
    queryset=Bodegas.objects.all()

class GetBodegaById(generics.RetrieveAPIView):
    serializer_class=SerializerBodegas
    queryset=Bodegas.objects.all()

class GetBodegaList(generics.ListAPIView):
    serializer_class=SerializerBodegas
    queryset=Bodegas.objects.all()

#Magnitudes

class GetMagnitudesById(generics.RetrieveAPIView):
    serializer_class=SerializerMagnitudes
    queryset=Magnitudes.objects.all()

class GetMagnitudesList(generics.ListAPIView):
    serializer_class=SerializerMagnitudes
    queryset=Magnitudes.objects.all()

#Porcentajes IVA
class RegisterPorcentaje(generics.CreateAPIView):
    serializer_class=SerializerPostPorcentajesIVA
    queryset=PorcentajesIVA.objects.all()
    
class UpdatePorcentaje(generics.UpdateAPIView):
    serializer_class=SerializerPutPorcentajesIVA
    queryset=PorcentajesIVA.objects.all()
    
    def put(self, request, pk):
        data = request.data
        porcentaje = PorcentajesIVA.objects.filter(id_porcentaje_iva=pk).first()
        if porcentaje:
            if porcentaje.registro_precargado == False:
                porcentaje_serializer = self.serializer_class(porcentaje, data)
                porcentaje_serializer.is_valid(raise_exception=True)
                porcentaje_serializer.save()
                return Response({'success':True, 'data': porcentaje_serializer.data})
            else:
                return Response({'success':False, 'detail': 'No puedes actualizar un porcentaje precargado'})
        else:
            return Response({'success':False, 'detail': 'No existe el porcentaje'})
    
class DeletePorcentaje(generics.DestroyAPIView):
    serializer_class=SerializerPorcentajesIVA
    queryset=PorcentajesIVA.objects.all()
    
    def delete(self, request, pk):
        porcentaje = PorcentajesIVA.objects.filter(id_porcentaje_iva=pk).first()
        if porcentaje:
            if porcentaje.registro_precargado == False:
                porcentaje.delete()
                return Response({'success':True, 'detail': 'Se ha eliminado exitosamente'})
            else:
                return Response({'success':False, 'detail': 'No puedes eliminar un porcentaje precargado'})
        else:
            return Response({'success':False, 'detail': 'No existe el porcentaje'})

class GetPorcentajeById(generics.RetrieveAPIView):
    serializer_class=SerializerPorcentajesIVA
    queryset=PorcentajesIVA.objects.all()

class GetPorcentajeList(generics.ListAPIView):
    serializer_class=SerializerPorcentajesIVA
    queryset=PorcentajesIVA.objects.all()
    
#UnidadesMedida
class RegisterUnidadMedida(generics.CreateAPIView):
    serializer_class=SerializersPostUnidadesMedida
    queryset=UnidadesMedida.objects.all()
    
class UpdateUnidadMedida(generics.UpdateAPIView):
    serializer_class=SerializersPutUnidadesMedida
    queryset=UnidadesMedida.objects.all()
    
    def put(self,request,pk):
        
        try:
            unidad_medida=UnidadesMedida.objects.get(id_unidad_medida=pk)
            data=request.data
            print(unidad_medida.precargado)
            if unidad_medida.precargado==True:
                return Response({"success":False, "detail":"No se puede actualizar porque es una unidad de medida precargado"})
            
            try:
                if unidad_medida.precargado==False:
                    unidad_medida_serializer=self.serializer_class(unidad_medida,data)
                    unidad_medida_serializer.is_valid(raise_exception=True)
                    unidad_medida_serializer.save()
                    return Response({'success':True, 'data': unidad_medida_serializer.data})
            except Exception as e:
                print(e)
                return Response({'detail': e.detail})
        except:
            return Response({'success':False, 'detail': 'No existe la unidad de medida'})
class DeleteUnidadMedida(generics.DestroyAPIView):
    serializer_class=SerializersUnidadesMedida
    queryset=UnidadesMedida.objects.all()
    
    def delete(self, request, pk):
        
        try:
            unidad_medida=UnidadesMedida.objects.get(id_unidad_medida=pk)
            
            if unidad_medida.precargado==False:
                unidad_medida.delete()
                
                return Response({'success':True,'detail': 'Se ha eliminado la unidad de medida' })
            else:
                return Response({'success':False, 'detail': 'No puede eliminar una unidad de medida precargado'})

        except:
                return Response({'success':False, 'detail': 'No existe la unidad de medida'})

class GetUnidadMedidaById(generics.RetrieveAPIView):
    serializer_class=SerializersUnidadesMedida
    queryset=UnidadesMedida.objects.all()

class GetUnidadMedidaList(generics.ListAPIView):
    serializer_class=SerializersUnidadesMedida
    queryset=UnidadesMedida.objects.all()