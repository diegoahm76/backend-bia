from calendar import c
from email import message
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from seguridad.models import Permisos, PermisosModulo, PermisosModuloRol, Modulos, User, Auditorias, Roles, UsuariosRol
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
    ModulosRolSerializer,
    ModulosRolEntornoSerializer
)
from rest_framework.generics import ListAPIView, CreateAPIView , RetrieveAPIView, DestroyAPIView, UpdateAPIView, RetrieveUpdateAPIView
from seguridad.utils import Util
from datetime import datetime
from django.template.loader import render_to_string
import operator, itertools

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

# class ListarPermisosModulo(ListAPIView):
#     serializer_class = PermisosModuloSerializer
#     def get_queryset(self):
#         return PermisosModulo.objects.all()

class ListarPermisosModulo(ListAPIView):
    serializer_class = GetPermisosRolSerializer
    queryset = PermisosModuloRol.objects.all()
    
    def get(self, request):
        # permisos_modulo_rol = self.queryset.all()
        # modulos_list = [permiso_modulo_rol.id_permiso_modulo.id_modulo.id_modulo for permiso_modulo_rol in permisos_modulo_rol]
        modulos = Modulos.objects.all()
        serializer_modulos = ModulosRolSerializer(modulos, many=True)
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
            
        return Response({'success':True,'detail':'Se encontraron los siguientes permisos por módulo', 'data':outputList}, status=status.HTTP_200_OK)

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
                    return Response({'success': False, 'detail':'No existe uno de los permisos, verifique'}, status=status.HTTP_400_BAD_REQUEST)
                
            return Response({'success': True, 'detail':'Se actualizaron los permisos del rol'}, status=status.HTTP_200_OK)     
        else:
            return Response({'success': False, 'detail':'No se encontró el rol'}, status=status.HTTP_404_NOT_FOUND)

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

class GetPermisosRolByEntorno(ListAPIView):
    serializer_class = GetPermisosRolSerializer
    queryset = PermisosModuloRol.objects.all()
    def get(self, request):
        id_usuario = request.query_params.get('id_usuario')
        tipo_entorno = request.query_params.get('tipo_entorno')
        
        if not id_usuario and not tipo_entorno:
            return Response({'success':False, 'detail':'Debe enviar los parámetros de búsqueda'}, status=status.HTTP_400_BAD_REQUEST)
        
        usuario_instance = User.objects.filter(id_usuario=id_usuario).first()
        supersusuario = User.objects.filter(id_usuario=1).first()
        
        tipos_entorno = ['L','C']
            
        roles_list = UsuariosRol.objects.filter(id_usuario=id_usuario)
        
        if not usuario_instance:
            return Response({'success':False, 'detail':'Debe ingresar un usuario que exista'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if usuario_instance.is_superuser:
                roles_list = roles_list.filter(id_rol=1)
                tipo_entorno = None
            else:
                if not tipo_entorno or tipo_entorno == '':
                    return Response({'success':False, 'detail':'Debe indicar el tipo de entorno'}, status=status.HTTP_400_BAD_REQUEST)
        
        if tipo_entorno:
            if tipo_entorno not in tipos_entorno:
                return Response({'success':False, 'detail':'Debe ingresar un tipo de entorno valido'}, status=status.HTTP_400_BAD_REQUEST)
        
            if tipo_entorno == 'C':
                roles_list = roles_list.filter(id_rol=2)
            elif tipo_entorno == 'L':
                if usuario_instance.persona.id_cargo is None or usuario_instance.persona.id_unidad_organizacional_actual is None or (usuario_instance.persona.fecha_a_finalizar_cargo_actual and usuario_instance.persona.fecha_a_finalizar_cargo_actual <= datetime.now()):
                    subject = "Intento de ingreso a entorno laboral"
                    template = "email-entorno.html"
                    
                    context = {'primer_nombre': usuario_instance.persona.primer_nombre}
                    template = render_to_string((template), context)
                    email_data = {'template': template, 'email_subject': subject, 'to_email': supersusuario.persona.email}
                    Util.send_email(email_data)
                    
                    return Response({'success':False, 'permitido':False, 'detail':'NO SE LE PERMITIRÁ TRABAJAR EN ENTORNO LABORAL, dado que la persona no está actualmente vinculada o la fecha final del cargo ha vencido'}, status=status.HTTP_403_FORBIDDEN)
                
                roles_list = roles_list.exclude(id_rol=2)
        
        roles_list = [rol.id_rol for rol in roles_list]
        
        permisos_modulo_rol = self.queryset.all().filter(id_rol__in=roles_list)
        modulos_list = [permiso_modulo_rol.id_permiso_modulo.id_modulo.id_modulo for permiso_modulo_rol in permisos_modulo_rol]
        modulos = Modulos.objects.filter(id_modulo__in=modulos_list)
        serializer_modulos = ModulosRolEntornoSerializer(modulos, many=True, context={'roles_list': roles_list})
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
            
        return Response({'success':True,'detail':'El tipo de entorno ingresado tiene acceso a lo siguiente', 'permitido':True, 'data':outputList}, status=status.HTTP_200_OK)
    
#----------------------------------------------------->Tabla Modulos

class ListarModulo(ListAPIView):
    serializer_class = ModulosSerializers
    def get_queryset(self):
        return Modulos.objects.all()

class DetailModulo(RetrieveAPIView):
    serializer_class = ModulosSerializers
    queryset = Modulos.objects.filter()