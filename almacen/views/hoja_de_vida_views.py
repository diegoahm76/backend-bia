from almacen.models.generics_models import Bodegas
from rest_framework import generics, status
from django.db.models import Q
from seguridad.permissions.permissions_almacen import PermisoActualizarHojasVidaComputadores, PermisoActualizarHojasVidaOtrosActivos, PermisoActualizarHojasVidaVehiculos, PermisoBorrarHojasVidaComputadores, PermisoBorrarHojasVidaOtrosActivos, PermisoBorrarHojasVidaVehiculos
from seguridad.utils import Util
from rest_framework.permissions import IsAuthenticated
from almacen.serializers.bienes_serializers import CatalogoBienesSerializer
from almacen.choices.estados_articulo_choices import estados_articulo_CHOICES
from almacen.serializers.hoja_de_vida_serializers import (
    SerializersHojaDeVidaComputadores,
    SerializersHojaDeVidaVehiculos,
    SerializersHojaDeVidaOtrosActivos,
    SerializersPutHojaDeVidaComputadores,
    SerializersPutHojaDeVidaVehiculos,
    SerializersPutHojaDeVidaOtrosActivos
    )   
from almacen.models.hoja_de_vida_models import (
    DocumentosVehiculo, HojaDeVidaVehiculos, HojaDeVidaComputadores, HojaDeVidaOtrosActivos
    )   
from almacen.models.bienes_models import (
    CatalogoBienes
    )
from almacen.models.generics_models import (
    Marcas
    )
from almacen.models.inventario_models import (
    Inventario
    )  
from almacen.models.mantenimientos_models import (
    RegistroMantenimientos,
    ProgramacionMantenimientos
    )   
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated
from seguridad.utils import Util
import copy

from transversal.models.alertas_models import ConfiguracionClaseAlerta
from transversal.views.alertas_views import AlertasProgramadasCreate


class CreateHojaDeVidaComputadores(generics.CreateAPIView):
    serializer_class=SerializersHojaDeVidaComputadores
    queryset=HojaDeVidaComputadores.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarHojasVidaComputadores]
    def post(self,request):
        data=request.data
        serializer = self.serializer_class(data=data)
        id_articulo=data['id_articulo']
        articulo_existentes=CatalogoBienes.objects.filter(Q(id_bien=id_articulo) & ~Q(nro_elemento_bien=None)).first()
        print('ARTICULO',articulo_existentes)
        if not articulo_existentes:
            raise ValidationError('El bien ingresado no existe')
        if articulo_existentes.cod_tipo_bien == 'C':
            raise PermissionDenied('No se puede crear una hoja de vida a un bien tipo consumo')
        if articulo_existentes.cod_tipo_activo and articulo_existentes.cod_tipo_activo.cod_tipo_activo != 'Com':
            raise PermissionDenied('No se puede crear una hoja de vida a este bien ya que no es de la categoría computador')
        hoja_vida_articulo=HojaDeVidaComputadores.objects.filter(id_articulo=id_articulo).first()
        if hoja_vida_articulo:
            raise PermissionDenied('El bien ingresado ya tiene hoja de vida')
        
        articulo_existentes.tiene_hoja_vida=True
        articulo_existentes.save()

        # auditoria crear hoja de vida computadores
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
        return Response({'success':True, 'detail':'Hoja de vida creada','data': serializer.data},status=status.HTTP_200_OK)

class CreateHojaDeVidaVehiculos(generics.CreateAPIView):
    serializer_class=SerializersHojaDeVidaVehiculos
    queryset=HojaDeVidaVehiculos.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarHojasVidaVehiculos]
    def post(self,request):
        data=request.data
        serializer = self.serializer_class(data=data)
        id_articulo=data['id_articulo']
        articulo_existentes=CatalogoBienes.objects.filter(Q(id_bien=id_articulo) & ~Q(nro_elemento_bien=None)).first()

        if not articulo_existentes:
            raise ValidationError('El bien ingresado no existe')
        if articulo_existentes.cod_tipo_bien == 'C':
            raise PermissionDenied('No se puede crear una hoja de vida a un bien tipo consumo')
        if articulo_existentes.cod_tipo_activo and articulo_existentes.cod_tipo_activo.cod_tipo_activo != 'Veh':
            raise PermissionDenied('No se puede crear una hoja de vida a este bien ya que no es de la categoría de vehículo')
        hoja_vida_articulo=HojaDeVidaVehiculos.objects.filter(id_articulo=id_articulo)
        if hoja_vida_articulo:
            raise PermissionDenied('El bien ingresado ya tiene hoja de vida')
        
        articulo_existentes.tiene_hoja_vida=True
        articulo_existentes.save()
        
        # auditoria crear hoja de vida vehiculos
        usuario = request.user.id_usuario
        descripcion = {"NombreElemento": str(articulo_existentes.nombre), "Serial": str(articulo_existentes.doc_identificador_nro)}
        direccion=Util.get_client_ip(request)

        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 19,
            "cod_permiso": "CR",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion, 
        }
        Util.save_auditoria(auditoria_data)


    
        serializer.is_valid(raise_exception=True)
        instance =serializer.save()
        #print(articulo_existentes)

        #GENERACION DE ALERTA
        documentos = DocumentosVehiculo.objects.filter(id_articulo=articulo_existentes)

        conf = ConfiguracionClaseAlerta.objects.filter(cod_clase_alerta='Alm_VeDocV').first()
        if conf :
            crear_alerta=AlertasProgramadasCreate()
            for documento in documentos:
                data_alerta = {
                'cod_clase_alerta':'Alm_VeDocV',
                'dia_cumplimiento':documento.fecha_expiracion.day,
                'mes_cumplimiento':documento.fecha_expiracion.month,
                'age_cumplimiento':documento.fecha_expiracion.year,
                'id_elemento_implicado':documento.id_documentos_vehiculos,
                "tiene_implicado":False
                }

                response_alerta=crear_alerta.crear_alerta_programada(data_alerta)
                if response_alerta.status_code!=status.HTTP_201_CREATED:
                    return response_alerta

        return Response({'success':True, 'detail':'Hoja de vida creada','data': serializer.data},status=status.HTTP_200_OK)

class CreateHojaDeVidaOtros(generics.CreateAPIView):
    serializer_class=SerializersHojaDeVidaOtrosActivos
    queryset=HojaDeVidaOtrosActivos.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarHojasVidaOtrosActivos]
    def post(self,request):
        data=request.data
        serializer = self.serializer_class(data=data)
        id_articulo=data['id_articulo']
        articulo_existentes=CatalogoBienes.objects.filter(Q(id_bien=id_articulo) & ~Q(nro_elemento_bien=None)).first()
        if not articulo_existentes:
            raise ValidationError('El bien ingresado no existe')
        if articulo_existentes.cod_tipo_bien == 'C':
            raise PermissionDenied('No se puede crear una hoja de vida a un bien tipo consumo')
        if articulo_existentes.cod_tipo_activo and articulo_existentes.cod_tipo_activo.cod_tipo_activo != 'OAc':
            raise PermissionDenied('No se puede crear una hoja de vida a este bien ya que no es de la categoría otro activo')
        hoja_vida_articulo=HojaDeVidaOtrosActivos.objects.filter(id_articulo=id_articulo)
        if hoja_vida_articulo:
            raise PermissionDenied('El bien ingresado ya tiene hoja de vida')
        
        articulo_existentes.tiene_hoja_vida=True
        articulo_existentes.save()
        
        # auditoria crear hoja de vida otros
        usuario = request.user.id_usuario
        descripcion = {"NombreElemento": str(articulo_existentes.nombre), "Serial": str(articulo_existentes.doc_identificador_nro)}
        direccion=Util.get_client_ip(request)

        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 20,
            "cod_permiso": "CR",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion, 
        }
        Util.save_auditoria(auditoria_data)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success':True, 'detail':'Hoja de vida creada','data': serializer.data},status=status.HTTP_200_OK)

class DeleteHojaDeVidaComputadores(generics.DestroyAPIView):
    serializer_class=SerializersHojaDeVidaComputadores
    queryset=HojaDeVidaComputadores.objects.all()
    permission_classes = [IsAuthenticated, PermisoBorrarHojasVidaComputadores]
    
    def delete(self, request, pk):
        hv_a_borrar = HojaDeVidaComputadores.objects.filter(id_hoja_de_vida=pk).first()
        if hv_a_borrar == None:
            raise PermissionDenied('No se encuentra la hoja de vida')
    
        mtto_registrado = RegistroMantenimientos.objects.filter(id_articulo=hv_a_borrar.id_articulo.id_bien).first()
        mtto_programado = ProgramacionMantenimientos.objects.filter(id_articulo=hv_a_borrar.id_articulo.id_bien).first()
        articulo_existentes=CatalogoBienes.objects.filter(Q(id_bien=hv_a_borrar.id_articulo.id_bien) & ~Q(nro_elemento_bien=None)).first()
        print({'articulo_existenteeeeee':articulo_existentes.nombre,'articulo_doc':articulo_existentes.doc_identificador_nro})
        
        if mtto_programado != None or mtto_registrado != None:
            raise PermissionDenied('No se puede eliminar una hoja de vida que ya tiene mantenimientos programados o ejecutados')
        else:
            hv_a_borrar.delete()
            
            # auditoria delete hoja de vida computadores
            usuario = request.user.id_usuario
            descripcion = {"NombreElemento": str(articulo_existentes.nombre), "Serial": str(articulo_existentes.doc_identificador_nro)}
            direccion=Util.get_client_ip(request)

            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 18,
                "cod_permiso": "BO",
                "subsistema": 'ALMA',
                "dirip": direccion,
                "descripcion": descripcion, 
            }
            Util.save_auditoria(auditoria_data)
            raise PermissionDenied('Se eliminó la hoja de vida del computador seleccionado')
        
class DeleteHojaDeVidaVehiculos(generics.DestroyAPIView):
    serializer_class=SerializersHojaDeVidaVehiculos
    queryset=HojaDeVidaVehiculos.objects.all()
    permission_classes = [IsAuthenticated, PermisoBorrarHojasVidaVehiculos]
    
    def delete(self, request, pk):
        hv_a_borrar = HojaDeVidaVehiculos.objects.filter(id_hoja_de_vida=pk).first()
        if hv_a_borrar == None:
            raise PermissionDenied('No se encuentra la hoja de vida')
    
        mtto_registrado = RegistroMantenimientos.objects.filter(id_articulo=hv_a_borrar.id_articulo.id_bien).first()
        mtto_programado = ProgramacionMantenimientos.objects.filter(id_articulo=hv_a_borrar.id_articulo.id_bien).first()
        articulo_existentes=CatalogoBienes.objects.filter(Q(id_bien=hv_a_borrar.id_articulo.id_bien) & ~Q(nro_elemento_bien=None)).first()
        if mtto_programado != None or mtto_registrado != None:
            raise PermissionDenied('No se puede eliminar una hoja de vida que ya tiene mantenimientos programados o ejecutados')
        else:
            hv_a_borrar.delete()
            
            # auditoria delete hoja de vida Vehículos
            usuario = request.user.id_usuario
            descripcion = {"NombreElemento": str(articulo_existentes.nombre), "Serial": str(articulo_existentes.doc_identificador_nro)}
            direccion=Util.get_client_ip(request)

            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 19,
                "cod_permiso": "BO",
                "subsistema": 'ALMA',
                "dirip": direccion,
                "descripcion": descripcion, 
            }
            Util.save_auditoria(auditoria_data)
            raise PermissionDenied('Se eliminó la hoja de vida del vehículo seleccionado')
        
class DeleteHojaDeVidaOtrosActivos(generics.DestroyAPIView):
    serializer_class=SerializersHojaDeVidaOtrosActivos
    queryset=HojaDeVidaOtrosActivos.objects.all()
    permission_classes = [IsAuthenticated, PermisoBorrarHojasVidaOtrosActivos]
    
    def delete(self, request, pk):
        hv_a_borrar = HojaDeVidaOtrosActivos.objects.filter(id_hoja_de_vida=pk).first()
        if hv_a_borrar == None:
            raise PermissionDenied('No se encuentra la hoja de vida')
    
        mtto_registrado = RegistroMantenimientos.objects.filter(id_articulo=hv_a_borrar.id_articulo.id_bien).first()
        mtto_programado = ProgramacionMantenimientos.objects.filter(id_articulo=hv_a_borrar.id_articulo.id_bien).first()
        articulo_existentes=CatalogoBienes.objects.filter(Q(id_bien=hv_a_borrar.id_articulo.id_bien) & ~Q(nro_elemento_bien=None)).first()
        
        if mtto_programado != None or mtto_registrado != None:
            raise PermissionDenied('No se puede eliminar una hoja de vida que ya tiene mantenimientos programados o ejecutados')
        else:
            hv_a_borrar.delete()
            
            # auditoria delete hoja de vida Otros activos
            usuario = request.user.id_usuario
            descripcion = {"NombreElemento": str(articulo_existentes.nombre), "Serial": str(articulo_existentes.doc_identificador_nro)}
            direccion=Util.get_client_ip(request)

            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 20,
                "cod_permiso": "BO",
                "subsistema": 'ALMA',
                "dirip": direccion,
                "descripcion": descripcion, 
            }
            Util.save_auditoria(auditoria_data)
            raise PermissionDenied('Se eliminó la hoja de vida del activo seleccionado')
        
class UpdateHojaDeVidaComputadores(generics.UpdateAPIView):
    serializer_class=SerializersPutHojaDeVidaComputadores
    queryset=HojaDeVidaComputadores.objects.all()
    permission_classes=[IsAuthenticated, PermisoActualizarHojasVidaComputadores]

    def put(self,request,pk):
        data=request.data
        hoja_vida_computador = HojaDeVidaComputadores.objects.filter(id_hoja_de_vida=pk).first()
        if hoja_vida_computador:
            hoja_vida_computador_previous = copy.copy(hoja_vida_computador)
            bien = CatalogoBienes.objects.filter(id_bien=hoja_vida_computador.id_articulo.id_bien).first()
            inventario = Inventario.objects.filter(id_bien=hoja_vida_computador.id_articulo.id_bien).first()
            
            # ACTUALIZAR MARCA EN CATALOGO BIENES
            marca = data.get('id_marca')
            marca_existe = None
            
            if marca:
                marca_existe = Marcas.objects.filter(id_marca=marca).first()
                if marca_existe:
                    bien.id_marca = marca_existe
                    bien.save()
            
            serializer = self.serializer_class(hoja_vida_computador, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            data_serializada = serializer.data
            diccionario_cod_estado_activo=dict((x,y) for x,y in estados_articulo_CHOICES) # transforma un choices en un diccionario
            estado=inventario.cod_estado_activo if inventario else None
            
            data_serializada['codigo_bien'] = bien.codigo_bien
            data_serializada['nombre'] = bien.nombre
            data_serializada['doc_identificador_nro'] = bien.doc_identificador_nro
            data_serializada['id_marca'] = marca
            data_serializada['marca'] = marca_existe.nombre
            data_serializada['estado'] = diccionario_cod_estado_activo[estado.cod_estado] if estado else None
                
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
            
            return Response({'success':True, 'detail':'Se ha actualizado la hoja de vida', 'data':data_serializada}, status=status.HTTP_201_CREATED)
        else:
            raise NotFound('No existe la hoja de vida ingresada')

class UpdateHojaDeVidaVehiculos(generics.UpdateAPIView):
    serializer_class=SerializersPutHojaDeVidaVehiculos
    queryset=HojaDeVidaVehiculos.objects.all()
    permission_classes=[IsAuthenticated, PermisoActualizarHojasVidaVehiculos]

    def put(self,request,pk):
        data=request.data
        hoja_vida_vehiculo = HojaDeVidaVehiculos.objects.filter(id_hoja_de_vida=pk).first()
        if hoja_vida_vehiculo:
            hoja_vida_vehiculo_previous = copy.copy(hoja_vida_vehiculo)
            bien = CatalogoBienes.objects.filter(id_bien=hoja_vida_vehiculo.id_articulo.id_bien).first()
            inventario = Inventario.objects.filter(id_bien=hoja_vida_vehiculo.id_articulo.id_bien).first()
            
            # ACTUALIZAR MARCA EN CATALOGO BIENES
            marca = data.get('id_marca')
            marca_existe = None
            
            if marca:
                marca_existe = Marcas.objects.filter(id_marca=marca).first()
                if marca_existe:
                    bien.id_marca = marca_existe
                    bien.save()
            
            serializer = self.serializer_class(hoja_vida_vehiculo, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            data_serializada = serializer.data
            diccionario_cod_estado_activo=dict((x,y) for x,y in estados_articulo_CHOICES) # transforma un choices en un diccionario
            estado=inventario.cod_estado_activo if inventario else None
            
            data_serializada['codigo_bien'] = bien.codigo_bien
            data_serializada['nombre'] = bien.nombre
            data_serializada['doc_identificador_nro'] = bien.doc_identificador_nro
            data_serializada['id_marca'] = marca
            data_serializada['marca'] = marca_existe.nombre
            data_serializada['estado'] = diccionario_cod_estado_activo[estado.cod_estado] if estado else None
            
            # Auditoria
            usuario = request.user.id_usuario
            descripcion = {"nombre": str(bien.nombre), "serial": str(bien.doc_identificador_nro)}
            direccion=Util.get_client_ip(request)
            valores_actualizados={'previous':hoja_vida_vehiculo_previous, 'current':hoja_vida_vehiculo}
            auditoria_data = {
                'id_usuario': usuario,
                'id_modulo': 19,
                'cod_permiso': 'AC',
                'subsistema': 'ALMA',
                'dirip': direccion,
                'descripcion': descripcion,
                'valores_actualizados': valores_actualizados
            }
            Util.save_auditoria(auditoria_data)

            
            
            return Response({'success':True, 'detail':'Se ha actualizado la hoja de vida', 'data':data_serializada}, status=status.HTTP_201_CREATED)
        else:
            raise NotFound('No existe la hoja de vida ingresada')

class UpdateHojaDeVidaOtrosActivos(generics.UpdateAPIView):
    serializer_class=SerializersPutHojaDeVidaOtrosActivos
    queryset=HojaDeVidaOtrosActivos.objects.all()
    permission_classes=[IsAuthenticated, PermisoActualizarHojasVidaOtrosActivos]

    def put(self,request,pk):
        data=request.data
        hoja_vida_otros = HojaDeVidaOtrosActivos.objects.filter(id_hoja_de_vida=pk).first()
        if hoja_vida_otros:
            hoja_vida_otros_previous = copy.copy(hoja_vida_otros)
            bien = CatalogoBienes.objects.filter(id_bien=hoja_vida_otros.id_articulo.id_bien).first()
            inventario = Inventario.objects.filter(id_bien=hoja_vida_otros.id_articulo.id_bien).first()
            
            # ACTUALIZAR MARCA EN CATALOGO BIENES
            marca = data.get('id_marca')
            marca_existe = None
            
            if marca:
                marca_existe = Marcas.objects.filter(id_marca=marca).first()
                if marca_existe:
                    bien.id_marca = marca_existe
                    bien.save()
            
            serializer = self.serializer_class(hoja_vida_otros, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            data_serializada = serializer.data
            diccionario_cod_estado_activo=dict((x,y) for x,y in estados_articulo_CHOICES) # transforma un choices en un diccionario
            estado=inventario.cod_estado_activo if inventario else None
            
            data_serializada['codigo_bien'] = bien.codigo_bien
            data_serializada['nombre'] = bien.nombre
            data_serializada['doc_identificador_nro'] = bien.doc_identificador_nro
            data_serializada['id_marca'] = marca
            data_serializada['marca'] = marca_existe.nombre
            data_serializada['estado'] = diccionario_cod_estado_activo[estado.cod_estado] if estado else None
            
            # Auditoria
            usuario = request.user.id_usuario
            descripcion = {"nombre": str(bien.nombre), "serial": str(bien.doc_identificador_nro)}
            direccion=Util.get_client_ip(request)
            valores_actualizados={'previous':hoja_vida_otros_previous, 'current':hoja_vida_otros}
            auditoria_data = {
                'id_usuario': usuario,
                'id_modulo': 20,
                'cod_permiso': 'AC',
                'subsistema': 'ALMA',
                'dirip': direccion,
                'descripcion': descripcion,
                'valores_actualizados': valores_actualizados
            }
            Util.save_auditoria(auditoria_data)
            
            return Response({'success':True, 'detail':'Se ha actualizado la hoja de vida', 'data':data_serializada}, status=status.HTTP_201_CREATED)
        else:
            raise NotFound('No existe la hoja de vida ingresada')

class GetHojaDeVidaComputadoresById(generics.RetrieveAPIView):
    serializer_class=SerializersHojaDeVidaComputadores
    queryset=HojaDeVidaComputadores.objects.all()
    
    def get(self, request, pk):
        hoja_vida_computador = HojaDeVidaComputadores.objects.filter(id_hoja_de_vida=pk).first()
        if hoja_vida_computador:
            serializador = self.serializer_class(hoja_vida_computador)
            return Response({'success':True, 'detail':'Se encontró la hoja de vida', 'data':serializador.data}, status=status.HTTP_200_OK)
        else:
            try:
                raise NotFound('No se encontró la hoja de vida')
            except NotFound as e:
                return Response({'success':False, 'detail':'No se encontró la hoja de vida', 'data':[]}, status=status.HTTP_404_NOT_FOUND)

class GetHojaDeVidaVehiculosById(generics.RetrieveAPIView):
    serializer_class=SerializersHojaDeVidaVehiculos
    queryset=HojaDeVidaVehiculos.objects.all()
    
    def get(self, request, pk):
        hoja_vida_vehiculo = HojaDeVidaVehiculos.objects.filter(id_hoja_de_vida=pk).first()
        if hoja_vida_vehiculo:
            serializador = self.serializer_class(hoja_vida_vehiculo)
            return Response({'success':True, 'detail':'Se encontró la hoja de vida', 'data':serializador.data}, status=status.HTTP_200_OK)
        else:
            try:
                raise NotFound('No se encontró la hoja de vida')
            except NotFound as e:
                return Response({'success':False, 'detail':'No se encontró la hoja de vida', 'data':[]}, status=status.HTTP_404_NOT_FOUND)

class GetHojaDeVidaOtrosActivosById(generics.RetrieveAPIView):
    serializer_class=SerializersHojaDeVidaOtrosActivos
    queryset=HojaDeVidaOtrosActivos.objects.all()
    
    def get(self, request, pk):
        hoja_vida_otros = HojaDeVidaOtrosActivos.objects.filter(id_hoja_de_vida=pk).first()
        if hoja_vida_otros:
            serializador = self.serializer_class(hoja_vida_otros)
            return Response({'success':True, 'detail':'Se encontró la hoja de vida', 'data':serializador.data}, status=status.HTTP_200_OK)
        else:
            try:
                raise NotFound('No se encontró la hoja de vida')
            except NotFound as e:
                return Response({'success':False, 'detail':'No se encontró la hoja de vida', 'data':[]}, status=status.HTTP_404_NOT_FOUND)

class GetHojaDeVidaComputadoresByIdBien(generics.RetrieveAPIView):
    serializer_class=SerializersHojaDeVidaComputadores
    queryset=HojaDeVidaComputadores.objects.all()
    
    def get(self, request, id_bien):
        hoja_vida_computador = HojaDeVidaComputadores.objects.filter(id_articulo=id_bien).first()
        if hoja_vida_computador:
            serializador = self.serializer_class(hoja_vida_computador)
            inventario = Inventario.objects.filter(id_bien=hoja_vida_computador.id_articulo.id_bien).first()
            
            data_serializada = serializador.data
            diccionario_cod_estado_activo=dict((x,y) for x,y in estados_articulo_CHOICES) # transforma un choices en un diccionario
            estado=inventario.cod_estado_activo if inventario else None
            data_serializada['estado'] = diccionario_cod_estado_activo[estado.cod_estado] if estado else None
            
            return Response({'success':True, 'detail':'Se encontró la hoja de vida', 'data':data_serializada}, status=status.HTTP_200_OK)
        else:
            try:
                raise NotFound('No se encontró la hoja de vida')
            except NotFound as e:
                return Response({'success':False, 'detail':'No se encontró la hoja de vida', 'data':[]}, status=status.HTTP_404_NOT_FOUND)

class GetHojaDeVidaVehiculosByIdBien(generics.RetrieveAPIView):
    serializer_class=SerializersHojaDeVidaVehiculos
    queryset=HojaDeVidaVehiculos.objects.all()
    
    def get(self, request, id_bien):
        hoja_vida_vehiculo = HojaDeVidaVehiculos.objects.filter(id_articulo=id_bien).first()
        if hoja_vida_vehiculo:
            serializador = self.serializer_class(hoja_vida_vehiculo)
            inventario = Inventario.objects.filter(id_bien=hoja_vida_vehiculo.id_articulo.id_bien).first()
            
            data_serializada = serializador.data
            diccionario_cod_estado_activo=dict((x,y) for x,y in estados_articulo_CHOICES) # transforma un choices en un diccionario
            estado=inventario.cod_estado_activo if inventario else None
            data_serializada['estado'] = diccionario_cod_estado_activo[estado.cod_estado] if estado else None
            
            return Response({'success':True, 'detail':'Se encontró la hoja de vida', 'data':data_serializada}, status=status.HTTP_200_OK)
        else:
            try:
                raise NotFound('No se encontró la hoja de vida')
            except NotFound as e:
                return Response({'success':False, 'detail':'No se encontró la hoja de vida', 'data':[]}, status=status.HTTP_404_NOT_FOUND)

class GetHojaDeVidaOtrosActivosByIdBien(generics.RetrieveAPIView):
    serializer_class=SerializersHojaDeVidaOtrosActivos
    queryset=HojaDeVidaOtrosActivos.objects.all()
    
    def get(self, request, id_bien):
        hoja_vida_otros = HojaDeVidaOtrosActivos.objects.filter(id_articulo=id_bien).first()
        if hoja_vida_otros:
            serializador = self.serializer_class(hoja_vida_otros)
            inventario = Inventario.objects.filter(id_bien=hoja_vida_otros.id_articulo.id_bien).first()
            
            data_serializada = serializador.data
            diccionario_cod_estado_activo=dict((x,y) for x,y in estados_articulo_CHOICES) # transforma un choices en un diccionario
            estado=inventario.cod_estado_activo if inventario else None
            data_serializada['estado'] = diccionario_cod_estado_activo[estado.cod_estado] if estado else None
            
            return Response({'success':True, 'detail':'Se encontró la hoja de vida', 'data':data_serializada}, status=status.HTTP_200_OK)
        else:
            try:
                raise NotFound('No se encontró la hoja de vida')
            except NotFound as e:
                return Response({'success':False, 'detail':'No se encontró la hoja de vida', 'data':[]}, status=status.HTTP_404_NOT_FOUND)