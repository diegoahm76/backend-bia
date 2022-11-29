from almacen.models.generics_models import Bodegas
from rest_framework import generics, status
from django.db.models import Q
from seguridad.utils import Util
from rest_framework.permissions import IsAuthenticated
from almacen.serializers.hoja_de_vida_serializers import (
    SerializersHojaDeVidaComputadores,
    SerializersHojaDeVidaVehiculos,
    SerializersHojaDeVidaOtrosActivos,
    SerializersPutHojaDeVidaComputadores
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
from rest_framework.permissions import IsAuthenticated
from seguridad.utils import Util
import copy


class CreateHojaDeVidaComputadores(generics.CreateAPIView):
    serializer_class=SerializersHojaDeVidaComputadores
    queryset=HojaDeVidaComputadores.objects.all()
    permission_classes = [IsAuthenticated]
    def post(self,request):
        data=request.data
        serializer = self.serializer_class(data=data)
        id_articulo=data['id_articulo']
        articulo_existentes=CatalogoBienes.objects.filter(Q(id_bien=id_articulo) & ~Q(nro_elemento_bien=None)).first()
        if not articulo_existentes:
            return Response({'success':False,'detail':'El bien ingresado no existe'},status=status.HTTP_400_BAD_REQUEST)
        if articulo_existentes.cod_tipo_bien == 'C':
            return Response({'success':False,'detail':'No se puede crear una hoja de vida a un bien tipo consumo'},status=status.HTTP_403_FORBIDDEN)
        if articulo_existentes.cod_tipo_activo != 'Com':
            return Response({'success':False,'detail':'No se puede crear una hoja de vida a este bien ya que no es computador'},status=status.HTTP_403_FORBIDDEN)
        hoja_vida_articulo=HojaDeVidaComputadores.objects.filter(id_articulo=id_articulo).first()
        if hoja_vida_articulo:
            return Response({'success':False,'detail':'El bien ingresado ya tiene hoja de vida'},status=status.HTTP_403_FORBIDDEN)
        
        # auditoria crear persona
        usuario = request.user.id_usuario
        descripcion = {"NombreElemento": str(articulo_existentes.nombre), "Serial": str(articulo_existentes.doc_identificador_nro)}
        direccion=Util.get_client_ip(request)

        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 18,
            "cod_permiso": "CR",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion, 
        }
        Util.save_auditoria(auditoria_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success':True,'detail':'Hoja de vida creada','data': serializer.data},status=status.HTTP_200_OK)

class CreateHojaDeVidaVehiculos(generics.CreateAPIView):
    serializer_class=SerializersHojaDeVidaVehiculos
    queryset=HojaDeVidaVehiculos.objects.all()
    permission_classes = [IsAuthenticated]
    def post(self,request):
        data=request.data
        serializer = self.serializer_class(data=data)
        id_articulo=data['id_articulo']
        articulo_existentes=CatalogoBienes.objects.filter(Q(id_bien=id_articulo) & ~Q(nro_elemento_bien=None)).first()
        if not articulo_existentes:
            return Response({'success':False,'detail':'El bien ingresado no existe'},status=status.HTTP_400_BAD_REQUEST)
        if articulo_existentes.cod_tipo_bien == 'C':
            return Response({'success':False,'detail':'No se puede crear una hoja de vida a un bien tipo consumo'},status=status.HTTP_403_FORBIDDEN)
        if articulo_existentes.cod_tipo_activo != 'Veh':
            return Response({'success':False,'detail':'No se puede crear una hoja de vida a este bien ya que no es un vehículo'},status=status.HTTP_403_FORBIDDEN)
        hoja_vida_articulo=HojaDeVidaComputadores.objects.filter(id_articulo=id_articulo)
        if hoja_vida_articulo:
            return Response({'success':False,'detail':'El bien ingresado ya tiene hoja de vida'})
        
        # auditoria crear persona
        usuario = request.user.id_usuario
        descripcion = {"NombreElemento": str(articulo_existentes.nombre), "Serial": str(articulo_existentes.doc_identificador_nro)}
        direccion=Util.get_client_ip(request)

        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 19,
            "cod_permiso": "CR",
            "subsistema": 'TRSV',
            "dirip": direccion,
            "descripcion": descripcion, 
        }
        Util.save_auditoria(auditoria_data)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'Hoja de vida creada:': serializer.data})

class CreateHojaDeVidaOtros(generics.CreateAPIView):
    serializer_class=SerializersHojaDeVidaOtrosActivos
    queryset=HojaDeVidaOtrosActivos.objects.all()
    permission_classes = [IsAuthenticated]
    def post(self,request):
        data=request.data
        serializer = self.serializer_class(data=data)
        id_articulo=data['id_articulo']
        articulo_existentes=CatalogoBienes.objects.filter(Q(id_bien=id_articulo) & ~Q(nro_elemento_bien=None)).first()
        if not articulo_existentes:
            return Response({'success':False,'detail':'El bien ingresado no existe'},status=status.HTTP_400_BAD_REQUEST)
        if articulo_existentes.cod_tipo_bien == 'C':
            return Response({'success':False,'detail':'No se puede crear una hoja de vida a un bien tipo consumo'},status=status.HTTP_403_FORBIDDEN)
        if articulo_existentes.cod_tipo_activo != 'OAc':
            return Response({'success':False,'detail':'No se puede crear una hoja de vida a este bien ya que no es de la categoría otro activo'},status=status.HTTP_403_FORBIDDEN)
        hoja_vida_articulo=HojaDeVidaComputadores.objects.filter(id_articulo=id_articulo)
        if hoja_vida_articulo:
            return Response({'success':False,'detail':'El bien ingresado ya tiene hoja de vida'})
        
        # auditoria crear persona
        usuario = request.user.id_usuario
        descripcion = {"NombreElemento": str(articulo_existentes.nombre), "Serial": str(articulo_existentes.doc_identificador_nro)}
        direccion=Util.get_client_ip(request)

        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 20,
            "cod_permiso": "CR",
            "subsistema": 'TRSV',
            "dirip": direccion,
            "descripcion": descripcion, 
        }
        Util.save_auditoria(auditoria_data)
        
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
        
class UpdateHojaDeVidaComputadores(generics.UpdateAPIView):
    serializer_class=SerializersPutHojaDeVidaComputadores
    queryset=HojaDeVidaComputadores.objects.all()
    permission_classes=[IsAuthenticated]

    def put(self,request,pk):
        data=request.data
        hoja_vida_computador = HojaDeVidaComputadores.objects.filter(id_hoja_de_vida=pk).first()
        if hoja_vida_computador:
            hoja_vida_computador_previous = copy.copy(hoja_vida_computador)
            bien = CatalogoBienes.objects.filter(id_bien=hoja_vida_computador.id_articulo.id_bien).first()
            
            serializer = self.serializer_class(hoja_vida_computador, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            # Auditoria
            usuario = request.user.id_usuario
            descripcion = {"nombre": str(bien.nombre), "serial": str(bien.doc_identificador_nro)}
            direccion=Util.get_client_ip(request)
            valores_actualizados={'previous':hoja_vida_computador_previous, 'current':hoja_vida_computador}
            auditoria_data = {
                'id_usuario': usuario,
                'id_modulo': 18,
                'cod_permiso': 'AC',
                'subsistema': 'ALMA',
                'dirip': direccion,
                'descripcion': descripcion,
                'valores_actualizados': valores_actualizados
            }
            Util.save_auditoria(auditoria_data)
            
            return Response({'success':True, 'detail':'Se ha actualizado la hoja de vida'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success':False, 'detail':'No existe la hoja de vida ingresada'}, status=status.HTTP_404_NOT_FOUND)