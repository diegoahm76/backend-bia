from almacen.models.generics_models import UnidadesMedida
from almacen.models.generics_models import Magnitudes
from almacen.models.generics_models import Bodegas
from rest_framework import generics, status
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
from seguridad.permissions.permissions_almacen import PermisoActualizarBodegas, PermisoActualizarMarcas, PermisoActualizarPorcentajeIva, PermisoActualizarUnidadesMedida, PermisoBorrarBodegas, PermisoBorrarMarcas, PermisoBorrarPorcentajeIva, PermisoBorrarUnidadesMedida, PermisoCrearBodegas, PermisoCrearMarcas, PermisoCrearPorcentajeIva, PermisoCrearUnidadesMedida
from transversal.models.personas_models import Personas
from django.db.models import Q
from almacen.choices.estados_articulo_choices import estados_articulo_CHOICES
from almacen.choices.magnitudes_choices import magnitudes_CHOICES
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated


#_______Marca
class RegisterMarca(generics.CreateAPIView):
    serializer_class=SerializersPostMarca
    queryset=Marcas.objects.all()
    permission_classes = [IsAuthenticated, PermisoCrearMarcas]
    
class UpdateMarca(generics.UpdateAPIView):
    serializer_class=SerializersPutMarca
    queryset=Marcas.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarMarcas]
    
    def put(self, request, pk):
        data = request.data
        marca = self.queryset.filter(id_marca=pk).first()
        if marca:
            if marca.item_ya_usado:
                raise PermissionDenied('No puedes actualizar una marca que haya sido usada')
            else:
                marca_serializer = self.serializer_class(marca, data)
                marca_serializer.is_valid(raise_exception=True)
                marca_serializer.save()
                return Response({'success':True, 'detail':'Se ha actualizado la marca exitosamente', 'data': marca_serializer.data}, status=status.HTTP_201_CREATED)
        else:
            raise NotFound('No existe el porcentaje ingresado')
    
class DeleteMarca(generics.DestroyAPIView):
    serializer_class=SerializersMarca
    queryset=Marcas.objects.all()
    permission_classes = [IsAuthenticated, PermisoBorrarMarcas]
    
    def delete(self, request, pk):
        marca = self.queryset.filter(id_marca=pk).first()
        if marca:
            if marca.item_ya_usado:
                raise PermissionDenied('No puedes eliminar una marca que haya sido usada')
            else:
                marca.delete()
                return Response({'success':True, 'detail':'Se ha eliminado exitosamente'}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No existe la marca ingresada')

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
    permission_classes = [IsAuthenticated, PermisoCrearBodegas]
    
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        
        es_principal = serializer.validated_data.get('es_principal')
        id_responsable = data.get('id_responsable')
        
        if id_responsable:
            responsable = Personas.objects.filter(id_persona=data['id_responsable']).filter(~Q(id_cargo=None) and ~Q(id_unidad_organizacional_actual=None) and Q(es_unidad_organizacional_actual=True))
            if not responsable:
                raise ValidationError('La persona debe tener un cargo y tener asignada una Unidad Organizacional')
        
        bodega_principal = Bodegas.objects.filter(es_principal=es_principal).first()
        
        if bodega_principal and es_principal:
            raise ValidationError('Ya existe una bodega principal')
        else:
            serializer.save()
            return Response({'success':True, 'detail':'Se creado la bodega con éxito', 'data':serializer.data}, status=status.HTTP_201_CREATED)

        
class UpdateBodega(generics.UpdateAPIView):
    serializer_class=SerializerPutBodegas
    queryset=Bodegas.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarBodegas]
    
    def put(self, request, pk):
        data = request.data
        bodega = Bodegas.objects.filter(id_bodega=pk).first()
        if bodega:
            serializer = self.serializer_class(bodega, data=data, many=False)
            serializer.is_valid(raise_exception=True)
            
            es_principal = serializer.validated_data.get('es_principal')
            id_responsable = data.get('id_responsable')
        
            if id_responsable:
                responsable = Personas.objects.filter(id_persona=data['id_responsable']).filter(~Q(id_cargo=None) and ~Q(id_unidad_organizacional_actual=None) and Q(es_unidad_organizacional_actual=True))
                if not responsable:
                    raise ValidationError('La persona debe tener un cargo y tener asignada una Unidad Organizacional')

            bodega_principal = Bodegas.objects.filter(es_principal=es_principal).first()
            
            if bodega_principal and es_principal:
                raise ValidationError('Ya existe una bodega principal')
            else:
                serializer.save()
                return Response({'success':True, 'detail':'Se ha actualizado la bodega', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        else:
            raise NotFound('La bodega ingresada no existe')
    
class DeleteBodega(generics.DestroyAPIView):
    serializer_class=SerializerBodegas
    queryset=Bodegas.objects.all()
    permission_classes = [IsAuthenticated, PermisoBorrarBodegas]
    
    def delete(self, request, pk):
        bodega = self.queryset.filter(id_bodega=pk).first()
        if bodega:
            if not bodega.item_ya_usado:
                bodega.delete()
                return Response({'success':True, 'detail':'Se ha eliminado exitosamente'}, status=status.HTTP_200_OK)
            else:
                raise PermissionDenied('No puedes eliminar una bodega que esté o haya sido usada')
        else:
            raise NotFound('La bodega ingresada no existe')

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
    permission_classes = [IsAuthenticated, PermisoCrearPorcentajeIva]
    
class UpdatePorcentaje(generics.UpdateAPIView):
    serializer_class=SerializerPutPorcentajesIVA
    queryset=PorcentajesIVA.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarPorcentajeIva]
    
    def put(self, request, pk):
        data = request.data
        porcentaje = PorcentajesIVA.objects.filter(id_porcentaje_iva=pk).first()
        if porcentaje:
            if porcentaje.registro_precargado or porcentaje.item_ya_usado:
                raise PermissionDenied('No puedes actualizar un porcentaje precargado o que haya sido usado')
            else:
                porcentaje_serializer = self.serializer_class(porcentaje, data)
                porcentaje_serializer.is_valid(raise_exception=True)
                porcentaje_serializer.save()
                return Response({'success':True, 'detail':'Se ha actualizado el porcentaje exitosamente','data': porcentaje_serializer.data}, status=status.HTTP_201_CREATED)
        else:
            raise NotFound('No existe el porcentaje ingresado')
    
class DeletePorcentaje(generics.DestroyAPIView):
    serializer_class=SerializerPorcentajesIVA
    queryset=PorcentajesIVA.objects.all()
    permission_classes = [IsAuthenticated, PermisoBorrarPorcentajeIva]
    
    def delete(self, request, pk):
        porcentaje = PorcentajesIVA.objects.filter(id_porcentaje_iva=pk).first()
        if porcentaje:
            if porcentaje.registro_precargado or porcentaje.item_ya_usado:
                raise PermissionDenied('No puedes eliminar un porcentaje precargado o que haya sido usado')
            else:
                porcentaje.delete()
                return Response({'success':True, 'detail':'Se ha eliminado exitosamente'}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No existe el porcentaje ingresado')

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
    permission_classes = [IsAuthenticated, PermisoCrearUnidadesMedida]
    
class UpdateUnidadMedida(generics.UpdateAPIView):
    serializer_class=SerializersPutUnidadesMedida
    queryset=UnidadesMedida.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarUnidadesMedida]
    
    def put(self,request,pk):
        unidad_medida=self.queryset.filter(id_unidad_medida=pk).first()
        data=request.data
        if unidad_medida:
            if unidad_medida.precargado or unidad_medida.item_ya_usado:
                raise PermissionDenied("No se puede actualizar una unidad de medida precargada o que haya sido usada")
            else:
                unidad_medida_serializer=self.serializer_class(unidad_medida,data)
                unidad_medida_serializer.is_valid(raise_exception=True)
                unidad_medida_serializer.save()
                return Response({'success':True, 'detail':'Se ha actualizado la unidad de medida exitosamente', 'data': unidad_medida_serializer.data}, status=status.HTTP_201_CREATED)
        else:    
            raise NotFound('No existe la unidad de medida ingresada')
        
class DeleteUnidadMedida(generics.DestroyAPIView):
    serializer_class=SerializersUnidadesMedida
    queryset=UnidadesMedida.objects.all()
    permission_classes = [IsAuthenticated, PermisoBorrarUnidadesMedida]
    
    def delete(self, request, pk):
        unidad_medida=self.queryset.filter(id_unidad_medida=pk).first()
        if unidad_medida:
            if unidad_medida.precargado or unidad_medida.item_ya_usado:
                raise PermissionDenied("No se puede actualizar una unidad de medida precargada o que haya sido usada")
            else:
                unidad_medida.delete()
                return Response({'success':True, 'detail':'Se ha eliminado la unidad de medida exitosamente'}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No existe la unidad de medida ingresada')
        
class GetUnidadMedidaById(generics.RetrieveAPIView):
    serializer_class=SerializersUnidadesMedida
    queryset=UnidadesMedida.objects.all()

class GetUnidadMedidaList(generics.ListAPIView):
    serializer_class=SerializersUnidadesMedida
    queryset=UnidadesMedida.objects.all()