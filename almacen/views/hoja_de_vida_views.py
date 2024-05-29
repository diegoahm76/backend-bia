from almacen.models.generics_models import Bodegas
from rest_framework import generics, status
from django.db.models import Q
from almacen.models.vehiculos_models import VehiculosArrendados
from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.utils import UtilsGestor
from seguridad.permissions.permissions_almacen import PermisoActualizarHojasVidaComputadores, PermisoActualizarHojasVidaOtrosActivos, PermisoActualizarHojasVidaVehiculos, PermisoBorrarHojasVidaComputadores, PermisoBorrarHojasVidaOtrosActivos, PermisoBorrarHojasVidaVehiculos
from seguridad.utils import Util
from rest_framework.permissions import IsAuthenticated
from almacen.serializers.bienes_serializers import CatalogoBienesSerializer
from almacen.serializers.hoja_de_vida_serializers import CatalogoBienesGetVehSerializer, VehiculosArrendadosSerializer
from almacen.choices.estados_articulo_choices import estados_articulo_CHOICES
from almacen.serializers.hoja_de_vida_serializers import (
    SerializersHojaDeVidaComputadores,
    SerializersHojaDeVidaComputadoresGet,
    SerializersHojaDeVidaOtrosActivosGet,
    SerializersHojaDeVidaVehiculos,
    SerializersHojaDeVidaOtrosActivos,
    SerializersHojaDeVidaVehiculosGet,
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
        ruta_imagen_foto = request.FILES.get('ruta_imagen_foto')
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

        # CREAR ARCHIVO EN T238
        if ruta_imagen_foto:
            archivo_creado = UtilsGestor.create_archivo_digital(ruta_imagen_foto, "HojaVidaComputadores")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            data['ruta_imagen_foto'] = archivo_creado_instance.id_archivo_digital
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

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
        return Response({'success':True, 'detail':'Hoja de vida creada','data': serializer.data},status=status.HTTP_200_OK)
    
class SearchArticulosByNombreDocIdentificadorHV(generics.ListAPIView):
    serializer_class = CatalogoBienesGetVehSerializer
    serializer_vehiculos_class = VehiculosArrendadosSerializer
    queryset = CatalogoBienes.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}
        filter_vehiculos = {}

        # Filtro catalogo
        for key, value in request.query_params.items():
            if key in ['cod_tipo_activo', 'nombre', 'doc_identificador_nro']:
                if key != 'cod_tipo_activo':
                    filter[key+'__icontains'] = value
                else:
                    filter[key] = value
        if not filter.get('cod_tipo_activo'):
            raise NotFound('Debe enviar el parametro del tipo de activo')
        
        # Filtro vehiculos arrendados
        if filter.get('cod_tipo_activo') == 'Veh':
            for key, value in request.query_params.items():
                if key == 'nombre':
                    filter_vehiculos[key+'__icontains'] = value
                if key == 'doc_identificador_nro':
                    filter_vehiculos['placa__icontains'] = value

        bien = CatalogoBienes.objects.filter(**filter).filter(nivel_jerarquico=5).exclude(nro_elemento_bien=None)
        vehiculos_arrendados = VehiculosArrendados.objects.filter(**filter_vehiculos)

        data_serializado = []

        if not bien and not vehiculos_arrendados:
            try:
                raise NotFound('No se encontró elementos')
            except NotFound as e:
                return Response({'success':False, 'detail':'No se encontró elementos', 'data': bien}, status=status.HTTP_404_NOT_FOUND)

        if bien:
            serializer = self.serializer_class(bien, many=True)
            data_serializado = serializer.data
            id_bien_list = [item.id_bien for item in bien]
            inventario = Inventario.objects.filter(id_bien__in=id_bien_list)
            # transforma un choices en un diccionario
            diccionario_cod_estado_activo = dict(
                (x, y) for x, y in estados_articulo_CHOICES)

            for item in data_serializado:
                inventario_instance = inventario.filter(
                    id_bien=item['id_bien']).first()
                estado = inventario_instance.cod_estado_activo if inventario_instance else None
                item['estado'] = diccionario_cod_estado_activo[estado.cod_estado] if estado else None
        
        if vehiculos_arrendados:
            # Añadir vehiculos arrendados si se encuentran
            if vehiculos_arrendados:
                serializer_vehiculos = self.serializer_vehiculos_class(vehiculos_arrendados, many=True)
                data_serializado.extend(serializer_vehiculos.data)

        return Response({'success':True, 'detail':'Se encontraron elementos', 'Elementos': data_serializado}, status=status.HTTP_200_OK)

class SearchArticuloByDocIdentificadorHV(generics.ListAPIView):
    serializer_class = CatalogoBienesGetVehSerializer
    serializer_arrendados_class = VehiculosArrendadosSerializer
    queryset = CatalogoBienes.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}
        filter_vehiculos = {}

        # Filtro catalogo
        for key, value in request.query_params.items():
            if key in ['cod_tipo_activo', 'doc_identificador_nro']:
                filter[key] = value
        if not filter.get('doc_identificador_nro'):
            raise NotFound('Debe enviar el parametro de número de identificación del bien')
        if not filter.get('cod_tipo_activo'):
            raise NotFound('Debe enviar el parametro del tipo de activo')
        
        # Filtro vehiculos arrendados
        if filter.get('cod_tipo_activo') == 'Veh':
            for key, value in request.query_params.items():
                if key == 'doc_identificador_nro':
                    filter_vehiculos['placa'] = value

        bien = CatalogoBienes.objects.filter(**filter).filter(nivel_jerarquico=5).exclude(nro_elemento_bien=None).first()
        vehiculo_arrendado = VehiculosArrendados.objects.filter(**filter_vehiculos).first()
        if bien:
            serializer = self.serializer_class(bien)
            data_serializado = serializer.data
            inventario = Inventario.objects.filter(
                id_bien=bien.id_bien).first()
            # transforma un choices en un diccionario
            diccionario_cod_estado_activo = dict(
                (x, y) for x, y in estados_articulo_CHOICES)
            estado = diccionario_cod_estado_activo[inventario.cod_estado_activo.cod_estado] if inventario else None
            data_serializado['estado'] = estado
            return Response({'success':True, 'detail':'Se encontraron elementos', 'Elementos': data_serializado}, status=status.HTTP_200_OK)
        elif vehiculo_arrendado:
            serializer_veh = self.serializer_arrendados_class(vehiculo_arrendado)
            data_serializado = serializer_veh.data
            return Response({'success':True, 'detail':'Se encontraron elementos', 'Elementos': data_serializado}, status=status.HTTP_200_OK)
        try:
            raise NotFound('No se encontró elementos')
        except NotFound as e:
            return Response({'success':False, 'detail':'No se encontró elementos', 'data': None}, status=status.HTTP_404_NOT_FOUND)

class CreateHojaDeVidaVehiculos(generics.CreateAPIView):
    serializer_class=SerializersHojaDeVidaVehiculos
    queryset=HojaDeVidaVehiculos.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarHojasVidaVehiculos]
    def post(self,request):
        data=request.data
        ruta_imagen_foto = request.FILES.get('ruta_imagen_foto')

        id_articulo=data.get('id_articulo')
        id_vehiculo_arrendado=data.get('id_vehiculo_arrendado')

        descripcion = {}
        
        if id_articulo:
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

            data['id_vehiculo_arrendado'] = None

            descripcion = {"NombreElemento": str(articulo_existentes.nombre), "Serial": str(articulo_existentes.doc_identificador_nro)}
        else:
            vehiculo_arrendado = VehiculosArrendados.objects.filter(id_vehiculo_arrendado=id_vehiculo_arrendado).first()
            if not vehiculo_arrendado:
                raise ValidationError('El vehiculo arrendado ingresado no existe')
            
            hoja_vida_articulo=HojaDeVidaVehiculos.objects.filter(id_vehiculo_arrendado=id_vehiculo_arrendado)
            if hoja_vida_articulo:
                raise PermissionDenied('El vehiculo arrendado ingresado ya tiene hoja de vida')
            
            vehiculo_arrendado.tiene_hoja_de_vida=True
            vehiculo_arrendado.save()
            
            data['id_articulo'] = None

            descripcion = {"NombreElemento": str(vehiculo_arrendado.nombre), "Serial": str(vehiculo_arrendado.placa)}

        # CREAR ARCHIVO EN T238
        if ruta_imagen_foto:
            archivo_creado = UtilsGestor.create_archivo_digital(ruta_imagen_foto, "HojaVidaVehiculos")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            data['ruta_imagen_foto'] = archivo_creado_instance.id_archivo_digital

        serializer = self.serializer_class(data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance =serializer.save()
        
        # auditoria crear hoja de vida vehiculos
        usuario = request.user.id_usuario
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
        #print(articulo_existentes)

        if id_articulo:
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
        ruta_imagen_foto = request.FILES.get('ruta_imagen_foto')
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

        # CREAR ARCHIVO EN T238
        if ruta_imagen_foto:
            archivo_creado = UtilsGestor.create_archivo_digital(ruta_imagen_foto, "HojaVidaOtros")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            data['ruta_imagen_foto'] = archivo_creado_instance.id_archivo_digital
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
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
            hv_a_borrar.ruta_imagen_foto.ruta_archivo.delete()
            hv_a_borrar.ruta_imagen_foto.delete()
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
            return Response({'success':True, 'detail':'Se eliminó la hoja de vida del computador seleccionado'}, status=status.HTTP_200_OK)
        
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
            hv_a_borrar.ruta_imagen_foto.ruta_archivo.delete()
            hv_a_borrar.ruta_imagen_foto.delete()
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
            return Response({'success':True, 'detail':'Se eliminó la hoja de vida del vehículo seleccionado'}, status=status.HTTP_200_OK)
        
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
            hv_a_borrar.ruta_imagen_foto.ruta_archivo.delete()
            hv_a_borrar.ruta_imagen_foto.delete()
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
            return Response({'success':True, 'detail':'Se eliminó la hoja de vida del activo seleccionado'}, status=status.HTTP_200_OK)
        
class UpdateHojaDeVidaComputadores(generics.UpdateAPIView):
    serializer_class=SerializersPutHojaDeVidaComputadores
    queryset=HojaDeVidaComputadores.objects.all()
    permission_classes=[IsAuthenticated, PermisoActualizarHojasVidaComputadores]

    def put(self,request,pk):
        data=request.data
        ruta_imagen_foto = request.FILES.get('ruta_imagen_foto')
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

            # ACTUALIZAR ARCHIVO
            if ruta_imagen_foto:
                if hoja_vida_computador.ruta_imagen_foto:
                    hoja_vida_computador.ruta_imagen_foto.ruta_archivo.delete()
                    hoja_vida_computador.ruta_imagen_foto.delete()

                archivo_creado = UtilsGestor.create_archivo_digital(ruta_imagen_foto, "HojaVidaComputadores")
                archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
                
                data['ruta_imagen_foto'] = archivo_creado_instance.id_archivo_digital
            # elif not archivo_soporte and hoja_vida_computador.ruta_imagen_foto:
            #     hoja_vida_computador.ruta_imagen_foto.ruta_archivo.delete()
            #     hoja_vida_computador.ruta_imagen_foto.delete()
            
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
        ruta_imagen_foto = request.FILES.get('ruta_imagen_foto')
        hoja_vida_vehiculo = HojaDeVidaVehiculos.objects.filter(id_hoja_de_vida=pk).first()
        if hoja_vida_vehiculo:
            hoja_vida_vehiculo_previous = copy.copy(hoja_vida_vehiculo)

            vehiculo = None
            inventario = None

            if hoja_vida_vehiculo.id_articulo:
                vehiculo = hoja_vida_vehiculo.id_articulo if hoja_vida_vehiculo.id_articulo else None
                inventario = Inventario.objects.filter(id_bien=hoja_vida_vehiculo.id_articulo.id_bien).first()
            else:
                vehiculo = hoja_vida_vehiculo.id_vehiculo_arrendado if hoja_vida_vehiculo.id_vehiculo_arrendado else None
            
            # ACTUALIZAR MARCA EN CATALOGO BIENES
            marca = data.get('id_marca')
            marca_existe = None
            
            if marca:
                marca_existe = Marcas.objects.filter(id_marca=marca).first()
                if marca_existe:
                    vehiculo.id_marca = marca_existe
                    vehiculo.save()
                else:
                    raise ValidationError('No existe la marca ingresada')

            # ACTUALIZAR ARCHIVO
            if ruta_imagen_foto:
                if hoja_vida_vehiculo.ruta_imagen_foto:
                    hoja_vida_vehiculo.ruta_imagen_foto.ruta_archivo.delete()
                    hoja_vida_vehiculo.ruta_imagen_foto.delete()

                archivo_creado = UtilsGestor.create_archivo_digital(ruta_imagen_foto, "HojaVidaVehiculos")
                archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
                
                data['ruta_imagen_foto'] = archivo_creado_instance.id_archivo_digital
            # elif not archivo_soporte and hoja_vida_vehiculo.ruta_imagen_foto:
            #     hoja_vida_vehiculo.ruta_imagen_foto.ruta_archivo.delete()
            #     hoja_vida_vehiculo.ruta_imagen_foto.delete()
            
            serializer = self.serializer_class(hoja_vida_vehiculo, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            data_serializada = serializer.data
            diccionario_cod_estado_activo=dict((x,y) for x,y in estados_articulo_CHOICES) # transforma un choices en un diccionario
            estado=inventario.cod_estado_activo if inventario else None
            
            data_serializada['codigo_bien'] = vehiculo.codigo_bien if hoja_vida_vehiculo.id_articulo else None
            data_serializada['nombre'] = vehiculo.nombre
            data_serializada['doc_identificador_nro'] = vehiculo.doc_identificador_nro if hoja_vida_vehiculo.id_articulo else vehiculo.placa
            data_serializada['id_marca'] = marca
            data_serializada['marca'] = marca_existe.nombre
            data_serializada['estado'] = diccionario_cod_estado_activo[estado.cod_estado] if estado else None
            
            # Auditoria
            usuario = request.user.id_usuario
            descripcion = {"Nombre": str(vehiculo.nombre), "SerialPlaca": str(vehiculo.doc_identificador_nro if hoja_vida_vehiculo.id_articulo else vehiculo.placa)}
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
        ruta_imagen_foto = request.FILES.get('ruta_imagen_foto')
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

            # ACTUALIZAR ARCHIVO
            if ruta_imagen_foto:
                if hoja_vida_otros.ruta_imagen_foto:
                    hoja_vida_otros.ruta_imagen_foto.ruta_archivo.delete()
                    hoja_vida_otros.ruta_imagen_foto.delete()

                archivo_creado = UtilsGestor.create_archivo_digital(ruta_imagen_foto, "HojaVidaOtros")
                archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
                
                data['ruta_imagen_foto'] = archivo_creado_instance.id_archivo_digital
            # elif not archivo_soporte and hoja_vida_otros.ruta_imagen_foto:
            #     hoja_vida_otros.ruta_imagen_foto.ruta_archivo.delete()
            #     hoja_vida_otros.ruta_imagen_foto.delete()
            
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
    serializer_class=SerializersHojaDeVidaComputadoresGet
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
    serializer_class=SerializersHojaDeVidaVehiculosGet
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
    serializer_class=SerializersHojaDeVidaOtrosActivosGet
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
    serializer_class=SerializersHojaDeVidaComputadoresGet
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
    serializer_class=SerializersHojaDeVidaVehiculosGet
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

class GetHojaDeVidaVehiculosByIdVehiculoArrendado(generics.RetrieveAPIView):
    serializer_class=SerializersHojaDeVidaVehiculosGet
    queryset=HojaDeVidaVehiculos.objects.all()
    
    def get(self, request, id_vehiculo_arrendado):
        hoja_vida_vehiculo = HojaDeVidaVehiculos.objects.filter(id_vehiculo_arrendado=id_vehiculo_arrendado).first()
        if hoja_vida_vehiculo:
            serializador = self.serializer_class(hoja_vida_vehiculo)
            
            data_serializada = serializador.data
            data_serializada['estado'] = None
            
            return Response({'success':True, 'detail':'Se encontró la hoja de vida', 'data':data_serializada}, status=status.HTTP_200_OK)
        else:
            try:
                raise NotFound('No se encontró la hoja de vida')
            except NotFound as e:
                return Response({'success':False, 'detail':'No se encontró la hoja de vida', 'data':[]}, status=status.HTTP_404_NOT_FOUND)

class GetHojaDeVidaOtrosActivosByIdBien(generics.RetrieveAPIView):
    serializer_class=SerializersHojaDeVidaOtrosActivosGet
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