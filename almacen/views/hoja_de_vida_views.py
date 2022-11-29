from almacen.models.generics_models import Bodegas
from rest_framework import generics, status
from almacen.serializers.hoja_de_vida_serializers import (
    SerializersHojaDeVidaComputadores, SerializersHojaDeVidaVehiculos, SerializersHojaDeVidaOtrosActivos
    )   
from almacen.models.hoja_de_vida_models import (
    HojaDeVidaVehiculos, HojaDeVidaComputadores, HojaDeVidaOtrosActivos
    )   
from almacen.models.bienes_models import (
    CatalogoBienes
    )   
from almacen.models.mantenimientos_models import (
    RegistroMantenimientos,
    ProgramacionMantenimientos
    )   
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


class CreateHojaDeVidaComputadores(generics.CreateAPIView):
    serializer_class=SerializersHojaDeVidaComputadores
    queryset=HojaDeVidaComputadores.objects.all()

    def post(self,request):
        data=request.data
        serializer = self.serializer_class(data=data)
        id_articulo=data['id_articulo']
        articulo_existentes=CatalogoBienes.objects.filter(id_bien=id_articulo).first()
        if not articulo_existentes:
            return Response({'success':False,'detail':'El bien ingresado no existe'},status=status.HTTP_400_BAD_REQUEST)
        if articulo_existentes.cod_tipo_bien == 'C':
            return Response({'success':False,'detail':'No se puede crear una hoja de vida a un bien tipo consumo'},status=status.HTTP_403_FORBIDDEN)
        if articulo_existentes.cod_tipo_bien != 'Com':
            return Response({'success':False,'detail':'No se puede crear una hoja de vida a este bien ya que no es computador'},status=status.HTTP_403_FORBIDDEN)
        hoja_vida_articulo=HojaDeVidaComputadores.objects.filter(id_articulo=id_articulo)
        if hoja_vida_articulo:
            return Response({'success':False,'detail':'El bien ingresado ya tiene hoja de vida'})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'Hoja de vida creada:': serializer.data})

class DeleteHojaDeVidaComputadores(generics.DestroyAPIView):
    serializer_class=SerializersHojaDeVidaComputadores
    queryset=HojaDeVidaComputadores.objects.all()
    
    def delete(self, request, pk):
        hv_a_borrar = HojaDeVidaComputadores.objects.filter(id_hoja_de_vida=pk).first()
        if hv_a_borrar == None:
            return Response({'success': False, 'detail': 'No se encuentra la hoja de vida'}, status=status.HTTP_403_FORBIDDEN)
    
        mtto_registrado = RegistroMantenimientos.objects.filter(id_articulo=hv_a_borrar.id_articulo.id_articulo).first()
        mtto_programado = ProgramacionMantenimientos.objects.filter(id_articulo=hv_a_borrar.id_articulo.id_articulo).first()
        
        if mtto_programado != None or mtto_registrado != None:
            return Response({'success': False, 'detail': 'No se puede eliminar una hoja de vida que ya tiene mantenimientos programados o ejecutados'}, status=status.HTTP_403_FORBIDDEN)
        else:
            hv_a_borrar.delete()
            return Response({'success': True, 'detail': 'Se eliminó la hoja de vida del computador seleccionado'}, status=status.HTTP_403_FORBIDDEN)
        
class DeleteHojaDeVidaVehiculos(generics.DestroyAPIView):
    serializer_class=SerializersHojaDeVidaVehiculos
    queryset=HojaDeVidaVehiculos.objects.all()
    
    def delete(self, request, pk):
        hv_a_borrar = HojaDeVidaVehiculos.objects.filter(id_hoja_de_vida=pk).first()
        if hv_a_borrar == None:
            return Response({'success': False, 'detail': 'No se encuentra la hoja de vida'}, status=status.HTTP_403_FORBIDDEN)
    
        mtto_registrado = RegistroMantenimientos.objects.filter(id_articulo=hv_a_borrar.id_articulo.id_articulo).first()
        mtto_programado = ProgramacionMantenimientos.objects.filter(id_articulo=hv_a_borrar.id_articulo.id_articulo).first()
        
        if mtto_programado != None or mtto_registrado != None:
            return Response({'success': False, 'detail': 'No se puede eliminar una hoja de vida que ya tiene mantenimientos programados o ejecutados'}, status=status.HTTP_403_FORBIDDEN)
        else:
            hv_a_borrar.delete()
            return Response({'success': True, 'detail': 'Se eliminó la hoja de vida del vehículo seleccionado'}, status=status.HTTP_403_FORBIDDEN)
        
class DeleteHojaDeVidaOtrosActivos(generics.DestroyAPIView):
    serializer_class=SerializersHojaDeVidaOtrosActivos
    queryset=HojaDeVidaOtrosActivos.objects.all()
    
    def delete(self, request, pk):
        hv_a_borrar = HojaDeVidaOtrosActivos.objects.filter(id_hoja_de_vida=pk).first()
        if hv_a_borrar == None:
            return Response({'success': False, 'detail': 'No se encuentra la hoja de vida'}, status=status.HTTP_403_FORBIDDEN)
    
        mtto_registrado = RegistroMantenimientos.objects.filter(id_articulo=hv_a_borrar.id_articulo.id_articulo).first()
        mtto_programado = ProgramacionMantenimientos.objects.filter(id_articulo=hv_a_borrar.id_articulo.id_articulo).first()
        
        if mtto_programado != None or mtto_registrado != None:
            return Response({'success': False, 'detail': 'No se puede eliminar una hoja de vida que ya tiene mantenimientos programados o ejecutados'}, status=status.HTTP_403_FORBIDDEN)
        else:
            hv_a_borrar.delete()
            return Response({'success': True, 'detail': 'Se eliminó la hoja de vida del activo seleccionado'}, status=status.HTTP_403_FORBIDDEN)
        
