from almacen.models.generics_models import Bodegas
from rest_framework import generics, status
from almacen.serializers.hoja_de_vida_serializers import (
    SerializersHojaDeVidaComputadores, SerializersHojaDeVidaVehiculos, SerializersHojaDeVidaOtrosActivos
    )   
from almacen.models.hoja_de_vida_models import (
    HojaDeVidaVehiculos, HojaDeVidaComputadores, HojaDeVidaOtrosActivos
    )   
from almacen.models.articulos_models import (
    Articulos
    )   
from almacen.models.mantenimientos_models import (
    RegistroMantenimientos,
    ProgramacionMantenimientos
    )   
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

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
        
