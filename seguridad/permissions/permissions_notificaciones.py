from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q

# GENERADOR DE DOCUMENTOS NOTIFICACIONES
class PermisoCrearGeneradorDocumentosNotificaciones(BasePermission):
    message = 'No tiene permiso para crear en Generador de Documentos Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=741))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarGeneradorDocumentosNotificaciones(BasePermission):
    message = 'No tiene permiso para actualizar en Generador de Documentos Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=742))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarGeneradorDocumentosNotificaciones(BasePermission):
    message = 'No tiene permiso para consultar en Generador de Documentos Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=743))
            if permisos_modulo_rol:
                return True

        return False

# GESTION DE SOLICITUDES NOTIFICACIONES
class PermisoActualizarGestionSolicitudesNotificaciones(BasePermission):
    message = 'No tiene permiso para actualizar en Gestión de Solicitudes de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=744))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarGestionSolicitudesNotificaciones(BasePermission):
    message = 'No tiene permiso para consultar en Gestión de Solicitudes de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=745))
            if permisos_modulo_rol:
                return True

        return False

# VISUALIZADOR DE NOTIFICACIONES
class PermisoActualizarVisualizadorNotificaciones(BasePermission):
    message = 'No tiene permiso para actualizar en Visualizador de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=746))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarVisualizadorNotificaciones(BasePermission):
    message = 'No tiene permiso para consultar en Visualizador de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=747))
            if permisos_modulo_rol:
                return True

        return False

# RECHAZAR NOTIFICACIONES
class PermisoActualizarRechazarNotificaciones(BasePermission):
    message = 'No tiene permiso para actualizar en Rechazar Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=748))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarRechazarNotificaciones(BasePermission):
    message = 'No tiene permiso para consultar en Rechazar Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=749))
            if permisos_modulo_rol:
                return True

        return False

# CREAR NOTIFICACIONES
class PermisoCrearCrearNotificaciones(BasePermission):
    message = 'No tiene permiso para crear en Crear Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=750))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCrearNotificaciones(BasePermission):
    message = 'No tiene permiso para consultar en Crear Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=751))
            if permisos_modulo_rol:
                return True

        return False

# ASIGNACION DE TAREAS DE NOTIFICACIONES
class PermisoCrearAsignacionTareasNotificaciones(BasePermission):
    message = 'No tiene permiso para crear en Asignación de Tareas de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=752))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarAsignacionTareasNotificaciones(BasePermission):
    message = 'No tiene permiso para consultar en Asignación de Tareas de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=753))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarAsignacionTareasNotificaciones(BasePermission):
    message = 'No tiene permiso para actualizar en Asignación de Tareas de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=754))
            if permisos_modulo_rol:
                return True

        return False

# AUTORIZAR ASIGNACIONES
class PermisoConsultarAutorizarAsignaciones(BasePermission):
    message = 'No tiene permiso para consultar en Autorizar Asignaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=755))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarAutorizarAsignaciones(BasePermission):
    message = 'No tiene permiso para actualizar en Autorizar Asignaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=756))
            if permisos_modulo_rol:
                return True

        return False

# TIPOS DE NOTIFICACIONES
class PermisoCrearTiposNotificaciones(BasePermission):
    message = 'No tiene permiso para crear en Tipos de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=757))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarTiposNotificaciones(BasePermission):
    message = 'No tiene permiso para actualizar en Tipos de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=758))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarTiposNotificaciones(BasePermission):
    message = 'No tiene permiso para consultar en Tipos de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=759))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarTiposNotificaciones(BasePermission):
    message = 'No tiene permiso para borrar en Tipos de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=760))
            if permisos_modulo_rol:
                return True

        return False

# ESTADO DE NOTIFICACIONES
class PermisoCrearEstadosNotificaciones(BasePermission):
    message = 'No tiene permiso para crear en Estados de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=761))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarEstadosNotificaciones(BasePermission):
    message = 'No tiene permiso para actualizar en Estados de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=762))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarEstadosNotificaciones(BasePermission):
    message = 'No tiene permiso para consultar en Estados de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=763))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarEstadosNotificaciones(BasePermission):
    message = 'No tiene permiso para borrar en Estados de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=764))
            if permisos_modulo_rol:
                return True

        return False

# CAUSAS Y ANOMALIAS DE NOTIFICACIONES
class PermisoCrearCausasAnomaliasNotificaciones(BasePermission):
    message = 'No tiene permiso para crear en Causas o Anomalias de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=765))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarCausasAnomaliasNotificaciones(BasePermission):
    message = 'No tiene permiso para actualizar en Causas o Anomalias de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=766))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCausasAnomaliasNotificaciones(BasePermission):
    message = 'No tiene permiso para consultar en Causas o Anomalias de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=767))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarCausasAnomaliasNotificaciones(BasePermission):
    message = 'No tiene permiso para borrar en Causas o Anomalias de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=768))
            if permisos_modulo_rol:
                return True

        return False

# TIPOS DE ANEXOS DE NOTIFICACIONES
class PermisoCrearTiposAnexosNotificaciones(BasePermission):
    message = 'No tiene permiso para crear en Tipos de Anexos de Soporte de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=769))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarTiposAnexosNotificaciones(BasePermission):
    message = 'No tiene permiso para actualizar en Tipos de Anexos de Soporte de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=770))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarTiposAnexosNotificaciones(BasePermission):
    message = 'No tiene permiso para consultar en Tipos de Anexos de Soporte de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=771))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarTiposAnexosNotificaciones(BasePermission):
    message = 'No tiene permiso para borrar en Tipos de Anexos de Soporte de Notificaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=772))
            if permisos_modulo_rol:
                return True

        return False

# PUBLICAR EN LA GACETA AMBIENTAL
class PermisoCrearPublicarGacetaAmbiental(BasePermission):
    message = 'No tiene permiso para crear en Publicar en la Gaceta Ambiental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=773))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarPublicarGacetaAmbiental(BasePermission):
    message = 'No tiene permiso para consultar en Publicar en la Gaceta Ambiental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=774))
            if permisos_modulo_rol:
                return True

        return False

# TIPOS DE DOCUMENTOS
class PermisoCrearTiposDocumentoNoti(BasePermission):
    message = 'No tiene permiso para crear en Tipos de Documento'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=775))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarTiposDocumentoNoti(BasePermission):
    message = 'No tiene permiso para actualizar en Tipos de Documento'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=776))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarTiposDocumentoNoti(BasePermission):
    message = 'No tiene permiso para consultar en Tipos de Documento'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=777))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarTiposDocumentoNoti(BasePermission):
    message = 'No tiene permiso para borrar en Tipos de Documento'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=778))
            if permisos_modulo_rol:
                return True

        return False