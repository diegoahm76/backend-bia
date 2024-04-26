from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q

# ADMINISTRACIÓN DE PERSONAS
class PermisoCrearAdministracionPersonas(BasePermission):
    message = 'No tiene permiso para crear en Administración de Personas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=1))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarAdministracionPersonas(BasePermission):
    message = 'No tiene permiso para actualizar en Administración de Personas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=2))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarAdministracionPersonas(BasePermission):
    message = 'No tiene permiso para consultar en Administración de Personas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=3))
            if permisos_modulo_rol:
                return True
        return False

# ESTADO CIVIL
class PermisoActualizarEstadoCivil(BasePermission):
    message = 'No tiene permiso para actualizar en Estado Civil'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=15))
            if permisos_modulo_rol:
                return True
        return False

class PermisoBorrarEstadoCivil(BasePermission):
    message = 'No tiene permiso para borrar en Estado Civil'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=16))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarEstadoCivil(BasePermission):
    message = 'No tiene permiso para consultar en Estado Civil'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=17))
            if permisos_modulo_rol:
                return True
        return False

class PermisoCrearEstadoCivil(BasePermission):
    message = 'No tiene permiso para crear en Estado Civil'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=18))
            if permisos_modulo_rol:
                return True
        return False

# TIPOS DE DOCUMENTOS DE ID
class PermisoActualizarTiposDocumentosID(BasePermission):
    message = 'No tiene permiso para actualizar en Tipos de Documentos de ID'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=19))
            if permisos_modulo_rol:
                return True
        return False

class PermisoBorrarTiposDocumentosID(BasePermission):
    message = 'No tiene permiso para borrar en Tipos de Documentos de ID'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=20))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarTiposDocumentosID(BasePermission):
    message = 'No tiene permiso para consultar en Tipos de Documentos de ID'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=21))
            if permisos_modulo_rol:
                return True
        return False

class PermisoCrearTiposDocumentosID(BasePermission):
    message = 'No tiene permiso para crear en Tipos de Documentos de ID'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=22))
            if permisos_modulo_rol:
                return True
        return False

# ORGANIGRAMAS
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

# CAMBIO DE ORGANIGRAMA ACTUAL
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

# CARGOS
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

# AUTORIZACIÓN DE NOTIFICACIONES OTRAS CUENTAS
class PermisoConsultarAutorizacionNotificacionesOtrasCuentas(BasePermission):
    message = 'No tiene permiso para consultar en Autorización de Notificaciones Otras Cuentas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=221))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarAutorizacionNotificacionesOtrasCuentas(BasePermission):
    message = 'No tiene permiso para actualizar en Autorización de Notificaciones Otras Cuentas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=222))
            if permisos_modulo_rol:
                return True
        return False

# VINCULACIÓN COLABORADORES
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
    
# DATOS PERSONALES DE MODIFICACIÓN RESTRINGIDA
class PermisoConsultarDatosPersonalesModificacionRestringida(BasePermission):
    message = 'No tiene permiso para consultar en Datos Personales de Modificación Restringida'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=228))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarDatosPersonalesModificacionRestringida(BasePermission):
    message = 'No tiene permiso para actualizar en Datos Personales de Modificación Restringida'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=229))
            if permisos_modulo_rol:
                return True
        return False

# CONFIGURACIÓN DE LA ENTIDAD
class PermisoActualizarConfiguracionEntidad(BasePermission):
    message = 'No tiene permiso para actualizar en Configuración de la Entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=304))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarConfiguracionEntidad(BasePermission):
    message = 'No tiene permiso para consultar en Configuración de la Entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=305))
            if permisos_modulo_rol:
                return True
        return False

# SUCURSALES DE LA ENTIDAD
class PermisoCrearSucursalesEntidad(BasePermission):
    message = 'No tiene permiso para crear en Sucursales de la Entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=315))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarSucursalesEntidad(BasePermission):
    message = 'No tiene permiso para actualizar en Sucursales de la Entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=316))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarSucursalesEntidad(BasePermission):
    message = 'No tiene permiso para consultar en Sucursales de la Entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=317))
            if permisos_modulo_rol:
                return True
        return False

class PermisoBorrarSucursalesEntidad(BasePermission):
    message = 'No tiene permiso para borrar en Sucursales de la Entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=318))
            if permisos_modulo_rol:
                return True
        return False

# TRASLADO MASIVO DE UNIDADES POR ENTIDAD (PREVIO)
class PermisoActualizarTrasladoMasivoUnidadesEntidad(BasePermission):
    message = 'No tiene permiso para actualizar en Traslado Masivo de Unidades por Entidad (previo)'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=319))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarTrasladoMasivoUnidadesEntidad(BasePermission):
    message = 'No tiene permiso para consultar en Traslado Masivo de Unidades por Entidad (previo)'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=320))
            if permisos_modulo_rol:
                return True
        return False

class PermisoEjecutarTrasladoMasivoUnidadesEntidad(BasePermission):
    message = 'No tiene permiso para ejecutar en Traslado Masivo de Unidades por Entidad (previo)'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=321))
            if permisos_modulo_rol:
                return True
        return False

# TRASLADO MASIVO DE UNIDAD A UNIDAD
class PermisoConsultarTrasladoMasivoUnidadUnidad(BasePermission):
    message = 'No tiene permiso para consultar en Traslado Masivo de Unidad a Unidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=322))
            if permisos_modulo_rol:
                return True
        return False

class PermisoEjecutarTrasladoMasivoUnidadUnidad(BasePermission):
    message = 'No tiene permiso para ejecutar en Traslado Masivo de Unidad a Unidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=323))
            if permisos_modulo_rol:
                return True
        return False

# LIDERES POR UNIDAD ORGANIZACIONAL
class PermisoCrearLideresUnidadOrganizacional(BasePermission):
    message = 'No tiene permiso para crear en Líderes por Unidad Organizacional'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=324))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarLideresUnidadOrganizacional(BasePermission):
    message = 'No tiene permiso para actualizar en Líderes por Unidad Organizacional'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=325))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarLideresUnidadOrganizacional(BasePermission):
    message = 'No tiene permiso para consultar en Líderes por Unidad Organizacional'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=326))
            if permisos_modulo_rol:
                return True
        return False