from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q

class PermisoActualizarUsuarios(BasePermission):
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=4))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarUsuarios(BasePermission):
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=5))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearUsuarios(BasePermission):
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=6))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarInterno(BasePermission):
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=7))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarInterno(BasePermission):
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=8))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarExterno(BasePermission):
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=9))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarExterno(BasePermission):
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=10))
            if permisos_modulo_rol:
                return True

        return False

class PermisoUnidadOrgActual(BasePermission):
    message = 'No tiene asignado una unidad organizacional de un organigrama actual'
    def has_permission(self, request, view):
        unidad_org = request.user.persona.id_unidad_organizacional_actual
        
        if unidad_org:
            org_actual = unidad_org.id_organigrama.actual
            if org_actual:
                return True
        
        return False