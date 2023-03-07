from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q

class PermisoCrearOrganigramas(BasePermission):
    message = 'No tiene permiso para crear organigramas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=41))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarOrganigramas(BasePermission):
    message = 'No tiene permiso para actualizar organigramas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=42))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarOrganigramas(BasePermission):
    message = 'No tiene permiso para consultar organigramas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=43))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCambiarOrganigrama(BasePermission):
    message = 'No tiene permiso para cambiar un organigrama actual'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=44))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCambioOrg(BasePermission):
    message = 'No tiene permiso para consultar el cambio de un organigrama actual'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=45))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearCargos(BasePermission):
    message = 'No tiene permiso para crear cargos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=46))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarCargos(BasePermission):
    message = 'No tiene permiso para actualizar cargos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=47))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCargos(BasePermission):
    message = 'No tiene permiso para consultar cargos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=48))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarCargos(BasePermission):
    message = 'No tiene permiso para borrar cargos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=49))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearCCD(BasePermission):
    message = 'No tiene permiso para crear un CCD'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=86))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarCCD(BasePermission):
    message = 'No tiene permiso para actualizar un CCD'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=87))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCCD(BasePermission):
    message = 'No tiene permiso para consultar un CCD'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=88))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCambioCCD(BasePermission):
    message = 'No tiene permiso para cambiar un CCD actual'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=89))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCambioCCD(BasePermission):
    message = 'No tiene permiso para consultar el cambio de un CCD actual'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=90))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearTRD(BasePermission):
    message = 'No tiene permiso para crear una TRD'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=91))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarTRD(BasePermission):
    message = 'No tiene permiso para actualizar una TRD'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=92))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarTRD(BasePermission):
    message = 'No tiene permiso para consultar una TRD'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=93))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCambioTRD(BasePermission):
    message = 'No tiene permiso para cambiar una TRD actual'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=94))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCambioTRD(BasePermission):
    message = 'No tiene permiso para consultar el cambio de una TRD actual'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=95))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearTCA(BasePermission):
    message = 'No tiene permiso para crear una TCA'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=96))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarTCA(BasePermission):
    message = 'No tiene permiso para actualizar una TCA'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=97))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarTCA(BasePermission):
    message = 'No tiene permiso para consultar una TCA'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=98))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCambioTCA(BasePermission):
    message = 'No tiene permiso para cambiar una TCA actual'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=99))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCambioTCA(BasePermission):
    message = 'No tiene permiso para consultar el cambio de una TCA actual'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=100))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCreaciónPersonasDesdeVentanilla(BasePermission):
    message = 'No tiene permiso para crear personas que van a solicitar desde la ventanilla algún servicio a la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=223))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarPersonasDesdeVentanilla(BasePermission):
    message = 'No tiene permiso para consultar personas que van a solicitar desde la ventanilla algún servicio a la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=224))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarPersonasDesdeVentanilla(BasePermission):
    message = 'No tiene permiso para actualizar personas que van a solicitar desde la ventanilla algún servicio a la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=225))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarVinculaciónColaboradores(BasePermission):
    message = 'No tiene permiso para consultar vinculación o desvinculación de personas como colaboradores de la entidad en el sistema'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=226))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarVinculaciónColaboradores(BasePermission):
    message = 'No tiene permiso para actualizar vinculación o desvinculación de personas como colaboradores de la entidad en el sistema'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=227))
            if permisos_modulo_rol:
                return True

        return False

