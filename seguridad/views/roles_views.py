from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from seguridad.models import Roles, User,UsuariosRol, Auditorias, Permisos, Modulos
from rest_framework import status,viewsets,mixins
from seguridad.serializers.roles_serializers import RolesSerializer, UsuarioRolesSerializers
from seguridad.serializers.user_serializers import UsuarioRolesLookSerializers
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from seguridad.permissions.permissions_roles import PermisoActualizarRoles,PermisoBorrarRoles,PermisoConsultarRoles,PermisoCrearRoles
from rest_framework.response import Response    
from rest_framework.generics import ListAPIView, CreateAPIView , RetrieveAPIView, DestroyAPIView, UpdateAPIView, RetrieveUpdateAPIView
from rest_framework import generics
from datetime import datetime
from seguridad.utils import Util
   
class GetRolesByUser(ListAPIView):
    serializer_class = UsuarioRolesLookSerializers
    def get_queryset(self):
        try:
            queryset = UsuariosRol.objects.all()
            query = self.request.query_params.get('keyword')
            if query == None:
                query = 0
        
            queryset = queryset.filter(id_usuario = query)
            return queryset
        except:
            return [] 
class GetUsersByRol(ListAPIView):
    serializer_class = UsuarioRolesLookSerializers
    def get_queryset(self):
        try:
            queryset = UsuariosRol.objects.all()
            query = self.request.query_params.get('keyword')
            if query == None:
                query = ''
            queryset = queryset.filter(
                Q(id_rol = query)
            )
            return queryset
        except:
            return []



class GetRolById(RetrieveAPIView):
    serializer_class=RolesSerializer
    permission_classes = [IsAuthenticated, PermisoConsultarRoles]
    queryset=Roles.objects.all()   
    
class GetRolByName(ListAPIView):
    serializer_class=RolesSerializer
    permission_classes = [IsAuthenticated, PermisoConsultarRoles]
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        queryset = Roles.objects.filter(nombre_rol__icontains = keyword)
        return queryset
    
class GetRol(ListAPIView):
    serializer_class=RolesSerializer
    permission_classes = [IsAuthenticated, PermisoConsultarRoles]
    queryset=Roles.objects.all()
    
class RegisterRol(CreateAPIView):
    serializer_class=RolesSerializer
    permission_classes = [IsAuthenticated, PermisoCrearRoles]
    queryset=Roles.objects.all()

#------------------------------------------------> Borrar un rol a un usuario
class DeleteUserRol(DestroyAPIView):
    serializer_class = UsuarioRolesSerializers
    queryset = UsuariosRol.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        try:
            id_usuarios_rol = UsuariosRol.objects.get(id_usuarios_rol=pk)
            pass
        except:
            return Response({'success':False,'detail': 'No se encontró ningún registro con el parámetro ingresado'},status=status.HTTP_404_NOT_FOUND)
        
        if id_usuarios_rol:
            id_usuarios_rol.delete()
            usuario = request.user.id_usuario
            descripcion =  {"id_usuarios_rol" : str(pk), "Usuario" : str(id_usuarios_rol.id_usuario.nombre_de_usuario), "Rol" : str(id_usuarios_rol.id_rol.nombre_rol)}
            dirip = Util.get_client_ip(request)
        
            auditoria_data = {
                'id_usuario': usuario,
                'id_modulo': 5,
                'cod_permiso': 'BO',
                'subsistema': 'SEGU',
                'dirip': dirip,
                'descripcion': descripcion
            }
            
            Util.save_auditoria(auditoria_data)
            
            return Response({'success':True,'detail':'El rol fue eliminado'},status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'success':False,'detail':'No existe el rol ingresado'},status=status.HTTP_404_NOT_FOUND)
            
#------------------------------------------------> Borrar un rol 
class DeleteRol(DestroyAPIView):
    serializer_class = RolesSerializer
    queryset = Roles.objects.all()
    
    def delete(self, request, pk):
        usuario_rol = UsuariosRol.objects.filter(id_rol=pk)
        
        if usuario_rol:
            return Response({'success':False,'detail':'No puede eliminar el rol porque ya está asignado a un usuario'},status=status.HTTP_403_FORBIDDEN)
        else:
            rol = Roles.objects.filter(id_rol=pk).first()
            
            if rol:
                #rol.delete()
                usuario = request.user.id_usuario
                user = User.objects.get(id_usuario = usuario)
                modulo = Modulos.objects.get(id_modulo = 5)
                permiso = Permisos.objects.get(cod_permiso = 'BO')
                direccion_ip = Util.get_client_ip(request)
                descripcion =  {"nombre" :  str(rol.nombre_rol)}
                Auditorias.objects.create(id_usuario = user, id_modulo = modulo, id_cod_permiso_accion = permiso, subsistema = "SEGU", dirip=direccion_ip, descripcion=descripcion, valores_actualizados='')  
                
                return Response({'success':True,'detail':'El rol fue eliminado'},status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'success':False,'detail':'No existe el rol ingresado'},status=status.HTTP_404_NOT_FOUND)
            
@api_view(['GET'])
def getRoles(request):
    roles = Roles.objects.all()
    serializer = RolesSerializer(roles, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getRolById(request, pk):
    rol = Roles.objects.get(id_rol=pk)
    serializer = RolesSerializer(rol, many=False)
    return Response(serializer.data)
    
@api_view(['POST'])
def registerRol(request):
    data = request.data
    try:
        rol = Roles.objects.create(
            nombre_rol = data['nombre_rol'],
            descripcion_rol = data['descripcion_rol']
        )
        
        serializer = RolesSerializer(rol, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        message = {'detail': ''}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


    

class UpdateRol(RetrieveUpdateAPIView):
    queryset=Roles.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarRoles]
    serializer_class=RolesSerializer

    def put(self, request, pk):
        usuario_rol = UsuariosRol.objects.filter(id_rol=pk).first()
        
        if usuario_rol:
            return Response({'success':False,'detail':'No puede actualizar el rol porque ya está asignado a un usuario'},status=status.HTTP_403_FORBIDDEN)
        else:
            rol = Roles.objects.filter(id_rol=pk).first()
            
            if rol:
                if rol.Rol_sistema == False:
                    serializer = self.serializer_class(rol, data=request.data, many=False)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response({'success':True,'detail':'El rol fue actualizado'},status=status.HTTP_201_CREATED)
                else:
                    return Response({'success':False,'detail': 'No se puede actualizar un rol precargado'},status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'success':False,'detail':'No existe el rol ingresado'},status=status.HTTP_404_NOT_FOUND)