from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q

class PermisoActualizarUsuarios(BasePermission):
    message = 'No tiene permiso para actualizar usuarios'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=4))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarUsuarios(BasePermission):
    message = 'No tiene permiso para consultar usuarios'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=5))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearUsuarios(BasePermission):
    message = 'No tiene permiso para crear usuarios'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=6))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarInterno(BasePermission):
    message = 'No tiene permiso para actualizar los datos de un usuario interno'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=7))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarInterno(BasePermission):
    message = 'No tiene permiso para consultar los datos de un usuario interno'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=8))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarExterno(BasePermission):
    message = 'No tiene permiso para actualizar los datos de un usuario externo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=9))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarExterno(BasePermission):
    message = 'No tiene permiso para consultar los datos de un usuario externo'
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
        unidad_org_actual = request.user.persona.es_unidad_organizacional_actual
        
        if unidad_org_actual:
            return True
        
        return False

class PermisoConsultarAutorizaciónNotificacionesCuentaPropia(BasePermission):
    message = 'No tiene permiso para consultar las autorizaciones de una persona acerca de las notificaciones de la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=219))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarAutorizaciónNotificacionesCuentaPropia(BasePermission):
    message = 'No tiene permiso para actualizar las autorizaciones de una persona acerca de las notificaciones de la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=220))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoConsultarAutorizaciónNotificacionesOtrasCuentas(BasePermission):
    message = 'No tiene permiso para consultar las autorizaciones de las personas acerca de las notificaciones de la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=221))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoActualizarAutorizaciónNotificacionesOtrasCuentas(BasePermission):
    message = 'No tiene permiso para actualizar las autorizaciones de las personas acerca de las notificaciones de la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=222))
            if permisos_modulo_rol:
                return True

        return False


