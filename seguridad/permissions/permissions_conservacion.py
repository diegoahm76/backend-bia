from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q

class PermisoCrearAdministrarViveros(BasePermission):
    message = 'No tiene permiso para crear viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=127))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarAdministrarViveros(BasePermission):
    message = 'No tiene permiso para consultar viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=128))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoActualizarAdministrarViveros(BasePermission):
    message = 'No tiene permiso para actualizar viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=129))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoBorrarAdministrarViveros(BasePermission):
    message = 'No tiene permiso para borrar viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=130))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoIngresoRetiroCuarentena(BasePermission):
    message = 'No tiene permiso para ingresar o retirar viveros de cuarentena'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=131))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAperturaCierreVivero(BasePermission):
    message = 'No tiene permiso para abrir o cerrar viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=132))
            if permisos_modulo_rol:
                return True

        return False