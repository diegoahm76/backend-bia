from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from seguridad.models import Roles, UsuariosRol,User, Personas, UsuariosRol
from rest_framework import status
from seguridad.serializers.roles_serializers import RolesSerializer, UsuarioRolesSerializers,RolesByIdUsuarioSerializer
from seguridad.serializers.user_serializers import UsuarioRolesLookSerializers
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from seguridad.permissions.permissions_roles import PermisoActualizarRoles,PermisoBorrarRoles,PermisoConsultarRoles,PermisoCrearRoles
from rest_framework.response import Response    
from rest_framework.generics import ListAPIView, CreateAPIView , RetrieveAPIView, DestroyAPIView, UpdateAPIView, RetrieveUpdateAPIView
from rest_framework import generics
from seguridad.utils import Util
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

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
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_rol):
        queryset = UsuariosRol.objects.filter(id_rol=id_rol)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success':True, 'detail':'Se encontraron los siguientes usuarios por el rol elegido', 'data': serializer.data}, status=status.HTTP_200_OK)


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
    permission_classes = [IsAuthenticated]
    queryset=Roles.objects.all().exclude(id_rol=1).order_by('id_rol')
    
class RegisterRol(CreateAPIView):
    serializer_class=RolesSerializer
    permission_classes = [IsAuthenticated]
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
            raise NotFound('No se encontró ningún registro con el parámetro ingresado')
        
        if id_usuarios_rol:
            id_usuarios_rol.delete()
            usuario = request.user.id_usuario
            descripcion =  {"IdUsuariosRol" : str(pk), "NombreUsuario" : str(id_usuarios_rol.id_usuario.nombre_de_usuario), "Rol" : str(id_usuarios_rol.id_rol.nombre_rol)}
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
            
            return Response({'success':True, 'detail':'El rol fue eliminado'},status=status.HTTP_200_OK)
        else:
            raise NotFound('No existe el rol ingresado')
 
 
# Borrar Rol    

class DeleteRol(generics.RetrieveDestroyAPIView):
    serializer_class = RolesSerializer
    queryset = Roles.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_rol):

        usuario_rol = UsuariosRol.objects.filter(id_rol=id_rol).first()
        if usuario_rol:
            raise PermissionDenied('No puede eliminar el rol porque ya está asignado a un usuario')
        
        rol = Roles.objects.filter(id_rol=id_rol).first()
        rolsito = rol
        if not rol:
            raise NotFound('No existe el rol ingresado')
        
        rol.delete()
        
        #Auditoria Eliminar Roles
        usuario = request.user.id_usuario
        descripcion = {"Nombre": str(rolsito.nombre_rol)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 5,
            "cod_permiso": "BO",
            "subsistema": 'SEGU',
            "dirip": direccion,
            "descripcion": descripcion, 
        }
        Util.save_auditoria(auditoria_data)
        return Response({'success':True, 'detail':'El rol fue eliminado'},status=status.HTTP_200_OK)




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

# class UpdateRol(RetrieveUpdateAPIView):
#     queryset=Roles.objects.all()
#     permission_classes = [IsAuthenticated, PermisoActualizarRoles]
#     serializer_class=RolesSerializer

#     def put(self, request, pk):
#         usuario_rol = UsuariosRol.objects.filter(id_rol=pk).first()
        
#         if usuario_rol:
#             raise PermissionDenied('No puede actualizar el rol porque ya está asignado a un usuario')
#         else:
#             rol = Roles.objects.filter(id_rol=pk).first()
            
#             if rol:
#                 if rol.Rol_sistema == False:
#                     serializer = self.serializer_class(rol, data=request.data, many=False)
#                     serializer.is_valid(raise_exception=True)
#                     serializer.save()
#                     return Response({'success':True, 'detail':'El rol fue actualizado'},status=status.HTTP_201_CREATED)
#                 else:
#                     raise PermissionDenied('No se puede actualizar un rol precargado')
#             else:
#                 raise NotFound('No existe el rol ingresado')
            

class UpdateRol(RetrieveUpdateAPIView):
    queryset=Roles.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarRoles]
    serializer_class=RolesSerializer

    def put(self, request, pk):
        # usuario_rol = UsuariosRol.objects.filter(id_rol=pk).first()
        
        # if usuario_rol:
        #     raise PermissionDenied('No puede actualizar el rol porque ya está asignado a un usuario')
        # else:
        rol = Roles.objects.filter(id_rol=pk).first()
        
        if rol:
            if rol.Rol_sistema == False:
                serializer = self.serializer_class(rol, data=request.data, many=False)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'success':True, 'detail':'El rol fue actualizado'},status=status.HTTP_201_CREATED)
            else:
                raise PermissionDenied('No se puede actualizar un rol precargado')
        else:
            raise NotFound('No existe el rol ingresado')
            

class GetRolesByIdPersona(generics.ListAPIView):
    serializer_class = RolesByIdUsuarioSerializer
    queryset= Roles.objects.all()    
    
    def get(self,request,id_usuario):
        
        usuario=User.objects.filter(persona = id_usuario).first()
        
        representante_legal=Personas.objects.filter(representante_legal=usuario.persona.id_persona)
        list_representante_legal=[representante.id_persona for representante in representante_legal]
        
        usuarios=User.objects.filter(persona__in=list_representante_legal)
        
        list_usuarios=[usuario.id_usuario for usuario in usuarios]
        list_usuarios_representante_legal=list_usuarios.copy()
        list_usuarios.append(usuario.id_usuario)

        usuario_rol = UsuariosRol.objects.filter(id_usuario__in=list_usuarios)
        
        roles=[]
        for rol in usuario_rol:
            rol_usuario = rol.id_rol
            if rol.id_usuario.id_usuario in list_usuarios_representante_legal:
                rol_usuario.representante_legal = True
                rol_usuario.nombre_empresa = rol.id_usuario.persona.razon_social
            roles.append(rol_usuario)
        serializador= self.serializer_class(roles, many= True)
            
        return Response({'success':True, 'detail':'Correcto','data':serializador.data},status=status.HTTP_200_OK)