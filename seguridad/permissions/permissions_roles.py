from seguridad.choices.tipo_usuario_choices import tipo_usuario_CHOICES 
from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q



class PermisoActualizarRoles(BasePermission):
   def has_permission(self, request, view):
    id_user = request.user.id_usuario
    user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

    for rol in user_roles:
        permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=11))
        if permisos_modulo_rol:
            return True
    return False

class PermisoBorrarRoles(BasePermission):
   def has_permission(self, request, view):
    id_user = request.user.id_usuario
    user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

    for rol in user_roles:
        id_rol=  rol.id_rol
        permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=id_rol) & Q(id_permiso_modulo=12))
        if permisos_modulo_rol:
            return True

    return False

class PermisoConsultarRoles(BasePermission):
   def has_permission(self, request, view):
    id_user = request.user.id_usuario
    user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

    for rol in user_roles:
        id_rol=  rol.id_rol
        permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=id_rol) & Q(id_permiso_modulo=13))
        if permisos_modulo_rol:
            return True

    return False

class PermisoCrearRoles(BasePermission):
   def has_permission(self, request, view):
    id_user = request.user.id_usuario
    user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

    for rol in user_roles:
        id_rol=  rol.id_rol
        permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=id_rol) & Q(id_permiso_modulo=14))
        if permisos_modulo_rol:
            return True

    return False

class PermisoDelegarRolSuperUsuario(BasePermission):
   def has_permission(self, request, view):
    id_user = request.user.id_usuario
    user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

    for rol in user_roles:
        id_rol=  rol.id_rol
        permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=id_rol) & Q(id_permiso_modulo=23))
        if permisos_modulo_rol:
            return True

    return False

class PermisoConsultarDelegacionSuperUsuario(BasePermission):
   def has_permission(self, request, view):
    id_user = request.user.id_usuario
    user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

    for rol in user_roles:
        id_rol=  rol.id_rol
        permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=id_rol) & Q(id_permiso_modulo=24))
        if permisos_modulo_rol:
            return True

    return False
