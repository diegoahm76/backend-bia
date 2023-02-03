from calendar import c
from email import message
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from seguridad.models import Permisos, PermisosModulo, PermisosModuloRol, Modulos, User, Auditorias, Roles
from rest_framework import status,viewsets,mixins
from rest_framework import status
from seguridad.serializers.permisos_serializers import (
    PermisosSerializer,
    PermisosModuloSerializer,
    PermisosModuloPostSerializer,
    PermisosModuloRolPostSerializer,
    PermisosModuloRolSerializer,
    ModulosSerializers,
    PermisosModuloRolSerializerHyper,
    GetPermisosRolSerializer,
    ModulosRolSerializer
)
from rest_framework.generics import ListAPIView, CreateAPIView , RetrieveAPIView, DestroyAPIView, UpdateAPIView, RetrieveUpdateAPIView
from seguridad.utils import Util
import datetime, operator, itertools

class ListarPermisos(ListAPIView):
    serializer_class = PermisosSerializer
    def get_queryset(self):
        return Permisos.objects.all()

class DetailPermisos(RetrieveAPIView):
    serializer_class = PermisosSerializer
    queryset = Permisos.objects.filter()

#====================================================>Vistas tabla PermisosModulo
# #----------------------------------------------------> Crear permisos por módulo
class PermisosModulosViewSet(viewsets.ModelViewSet):
    queryset = PermisosModulo.objects.all()
    serializer_class = PermisosModuloPostSerializer
    permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         usuario = request.user.nombre_de_usuario
#         print(usuario)
#         user = User.objects.get(nombre_de_usuario = usuario)
#         print(user)
#         modulo = Modulos.objects.get(id_modulo = 2)
#         permiso = Permisos.objects.get(cod_permiso = 'CR')
#         direccion_ip = Util.get_client_ip(request)
#         descripcion = []
#         for i in request.data:
#                 descripcion.append( "Usuario" + ":" + usuario + ";" + "Permisos(es):" + "=>")
#             print(i)
#             descripcion.append( "Modulo" + ":" + i["id_modulo"] + ";" + "Permiso" + ":" + i["cod_permiso"] )

#         print(descripcion)
#         Auditorias.objects.create(id_usuario = user, id_modulo = modulo, id_cod_permiso_accion = permiso, subsistema = "SEGU", dirip=direccion_ip, descripcion=descripcion, valores_actualizados='')
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# #------------------------------------------------> Borrar un permiso de un modulo
# class DeletePermisoModulo(DestroyAPIView):
#     serializer_class = PermisosModuloPostSerializer
#     queryset = PermisosModulo.objects.all()

#     def delete(self, request, pk):

#         data = PermisosModulo.objects.get(id_permisos_modulo=pk)

#         if data:
#             data.delete()
#             usuario = request.user.id_usuario
#             user = User.objects.get(id_usuario = usuario)
#             modulo = Modulos.objects.get(id_modulo = 2)
#             permiso = Permisos.objects.get(cod_permiso = 'BO')
#             direccion_ip = Util.get_client_ip(request)
#             descripcion =   "Modulo:" + str(data.id_modulo.nombre_modulo) + ";" + "Permiso:" + str(data.cod_permiso.nombre_permiso) + "."
#             print(descripcion)
#             Auditorias.objects.create(id_usuario = user, id_modulo = modulo, id_cod_permiso_accion = permiso, subsistema = "SEGU", dirip=direccion_ip, descripcion=descripcion, valores_actualizados='')

#             return Response({'detail':'El permiso fue eliminado del modulo'})
#         else:
#             return Response({'detail':'No existe el esa selección ingresada'})

#====================================================>Vistas tabla PermisosModuloRol
#----------------------------------------------------> Asignar un permiso de módulo a un rol
class PermisosModuloRolViewSet(viewsets.ModelViewSet):
    queryset = PermisosModuloRol.objects.all()
    serializer_class = PermisosModuloRolPostSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class UpdatePermisoModulo(RetrieveUpdateAPIView):
    serializer_class = PermisosModuloPostSerializer
    queryset = PermisosModulo.objects.all()

class ListarPermisosModulo(ListAPIView):
    serializer_class = PermisosModuloSerializer
    def get_queryset(self):
        return PermisosModulo.objects.all()

class DetailPermisosModulo(RetrieveAPIView):
    serializer_class = PermisosModuloSerializer
    queryset = PermisosModulo.objects.filter()

class UpdatePermisoModuloRol(RetrieveUpdateAPIView):
    serializer_class = PermisosModuloRolPostSerializer
    queryset = PermisosModuloRol.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        rol = Roles.objects.filter(id_rol=pk).first()
        permisos_modulo = request.data
        if rol:
            permisos_modulo_eliminar = PermisosModuloRol.objects.filter(id_rol=pk)
            permisos_modulo_eliminar.delete()
            
            for permiso_modulo in permisos_modulo:
                permiso_modulo_instance = PermisosModulo.objects.filter(id_permisos_modulo=permiso_modulo["id_permisos_modulo"]).first()
                if permiso_modulo_instance:
                    PermisosModuloRol.objects.create(
                        id_rol = rol,
                        id_permiso_modulo = permiso_modulo_instance
                    )
                else:
                    return Response({'success': False, 'detail':'No existe uno de los permisos, verifique'}, status=status.HTTP_204_NO_CONTENT)
                
            return Response({'success': True, 'detail':'Se actualizaron los permisos del rol'}, status=status.HTTP_200_OK)     
        else:
            return Response({'success': False, 'detail':'No se encontró el rol'}, status=status.HTTP_204_NO_CONTENT)

class ListarPermisosModuloRol(ListAPIView):
    serializer_class = PermisosModuloRolSerializer
    def get_queryset(self):
        return PermisosModuloRol.objects.all()

class DetailPermisosModuloRol(RetrieveAPIView):
    serializer_class = PermisosModuloRolSerializer
    queryset = PermisosModuloRol.objects.filter()
    
class ListarPermisosModuloRolByRol(ListAPIView):
    serializer_class = PermisosModuloRolSerializer
    queryset = PermisosModuloRol
    def get(self, request, pk):
        permisos_modulo_rol = PermisosModuloRol.objects.filter(id_rol=pk)
        serializer = self.serializer_class(permisos_modulo_rol, many=True)
        return Response({'success':True,'data':serializer.data}, status=status.HTTP_200_OK)

class GetPermisosRolByRol(ListAPIView):
    serializer_class = GetPermisosRolSerializer
    queryset = PermisosModuloRol.objects.all()
    def get(self, request, id_rol):
        permisos_modulo_rol = self.queryset.all().filter(id_rol=id_rol)
        modulos_list = [permiso_modulo_rol.id_permiso_modulo.id_modulo.id_modulo for permiso_modulo_rol in permisos_modulo_rol]
        modulos = Modulos.objects.filter(id_modulo__in=modulos_list)
        serializer_modulos = ModulosRolSerializer(modulos, many=True, context={'id_rol': id_rol})
        modulos_data = serializer_modulos.data
        
        modulos_data = sorted(modulos_data, key=operator.itemgetter("subsistema", "desc_subsistema"))
        outputList = []
        
        for subsistema, info_modulos in itertools.groupby(modulos_data, key=operator.itemgetter("subsistema", "desc_subsistema")):
            modulos = list(info_modulos)
            
            for modulo in modulos:
                del modulo['subsistema']
                del modulo['desc_subsistema']
                
            subsistema_data = {
                "subsistema": subsistema[0],
                "desc_subsistema": subsistema[1],
                "modulos": modulos
            }
            outputList.append(subsistema_data)
            
        return Response({'success':True,'detail':'El rol ingresado tiene acceso a lo siguiente', 'data':outputList}, status=status.HTTP_200_OK)

#----------------------------------------------------->Tabla Modulos

class ListarModulo(ListAPIView):
    serializer_class = ModulosSerializers
    def get_queryset(self):
        return Modulos.objects.all()

class DetailModulo(RetrieveAPIView):
    serializer_class = ModulosSerializers
    queryset = Modulos.objects.filter()