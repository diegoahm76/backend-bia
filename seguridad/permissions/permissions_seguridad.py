from seguridad.choices.tipo_usuario_choices import tipo_usuario_CHOICES 
from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q

# ADMINISTRACIÓN DE USUARIOS
class PermisoCrearAdministracionUsuarios(BasePermission):
    message = 'No tiene permiso para crear en Administración de Usuarios'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=4))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarAdministracionUsuarios(BasePermission):
    message = 'No tiene permiso para actualizar en Administración de Usuarios'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=5))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarAdministracionUsuarios(BasePermission):
    message = 'No tiene permiso para consultar en Administración de Usuarios'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=6))
            if permisos_modulo_rol:
                return True
        return False

# ADMINISTRACIÓN DE DATOS CUENTA PROPIA USUARIO INTERNO
class PermisoActualizarAdministracionDatosCuentaPropiaUsuarioInterno(BasePermission):
    message = 'No tiene permiso para actualizar en Administración de Datos Cuenta Propia Usuario Interno'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=7))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarAdministracionDatosCuentaPropiaUsuarioInterno(BasePermission):
    message = 'No tiene permiso para consultar en Administración de Datos Cuenta Propia Usuario Interno'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=8))
            if permisos_modulo_rol:
                return True
        return False

# ADMINISTRACIÓN DE DATOS CUENTA PROPIA USUARIO EXTERNO
class PermisoActualizarAdministracionDatosCuentaPropiaUsuarioExterno(BasePermission):
    message = 'No tiene permiso para actualizar en Administración de Datos Cuenta Propia Usuario Externo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=9))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarAdministracionDatosCuentaPropiaUsuarioExterno(BasePermission):
    message = 'No tiene permiso para consultar en Administración de Datos Cuenta Propia Usuario Externo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=10))
            if permisos_modulo_rol:
                return True
        return False

# ROLES
class PermisoActualizarRoles(BasePermission):
    message = 'No tiene permiso para actualizar roles'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=11))
            if permisos_modulo_rol:
                return True
        return False

class PermisoBorrarRoles(BasePermission):
    message = 'No tiene permiso para borrar roles'
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
    message = 'No tiene permiso para consultar roles'
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
    message = 'No tiene permiso para crear roles'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            id_rol=  rol.id_rol
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=id_rol) & Q(id_permiso_modulo=14))
            if permisos_modulo_rol:
                return True

        return False

# DELEGACIÓN DEL ROL DE SUPER USUARIO
class PermisoConsultarDelegacionSuperUsuario(BasePermission):
    message = 'No tiene permiso para consultar la delegación del rol de super usuario'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            id_rol=  rol.id_rol
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=id_rol) & Q(id_permiso_modulo=23))
            if permisos_modulo_rol:
                return True

        return False

class PermisoDelegarRolSuperUsuario(BasePermission):
    message = 'No tiene permiso para delegar el rol de super usuario a otra persona'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            id_rol=  rol.id_rol
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=id_rol) & Q(id_permiso_modulo=24))
            if permisos_modulo_rol:
                return True

        return False
    
# AUTORIZACIÓN DE NOTIFICACIONES CUENTA PROPIA
class PermisoConsultarAutorizacionNotificacionesCuentaPropia(BasePermission):
    message = 'No tiene permiso para consultar en Autorización de Notificaciones Cuenta Propia'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=219))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarAutorizacionNotificacionesCuentaPropia(BasePermission):
    message = 'No tiene permiso para actualizar en Autorización de Notificaciones Cuenta Propia'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=220))
            if permisos_modulo_rol:
                return True
        return False

# AUDITORIA
class PermisoConsultarAuditoria(BasePermission):
    message = 'No tiene permiso para consultar en Auditoría'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=242))
            if permisos_modulo_rol:
                return True
        return False