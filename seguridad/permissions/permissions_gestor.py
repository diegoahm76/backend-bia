from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q

# CUADRO CLASIFICACION DOCUMENTAL - CCD
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

# ACTIVACION INSTRUMENTOS ARCHIVISTICOS
class PermisoEjecutarActivacionInstrumentoArchivisticos(BasePermission):
    message = 'No tiene permiso para ejecutar la activación de instrumentos archivisticos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=89))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarActivacionInstrumentoArchivisticos(BasePermission):
    message = 'No tiene permiso para consultar la activación de instrumentos archivisticos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=90))
            if permisos_modulo_rol:
                return True

        return False

# TABLA RETENCION DOCUMENTAL - TRD
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

# TABLA CONTROL ACCESO - TCA
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

# PERSONAS DESDE VENTANILLA
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

# TIPOLOGIAS DOCUMENTALES
class PermisoCrearTipologiasDocumentales(BasePermission):
    message = 'No tiene permiso para crear tipologías documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=230))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarTipologiasDocumentales(BasePermission):
    message = 'No tiene permiso para actualizar tipologías documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=231))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarTipologiasDocumentales(BasePermission):
    message = 'No tiene permiso para consultar tipologías documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=232))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarTipologiasDocumentales(BasePermission):
    message = 'No tiene permiso para borrar tipologías documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=233))
            if permisos_modulo_rol:
                return True

        return False

# FORMATOS DE ARCHIVOS
class PermisoCrearFormatosArchivos(BasePermission):
    message = 'No tiene permiso para crear formatos de archivos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=234))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarFormatosArchivos(BasePermission):
    message = 'No tiene permiso para actualizar formatos de archivos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=235))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarFormatosArchivos(BasePermission):
    message = 'No tiene permiso para consultar formatos de archivos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=236))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarFormatosArchivos(BasePermission):
    message = 'No tiene permiso para borrar formatos de archivos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=237))
            if permisos_modulo_rol:
                return True

        return False

# DEPOSITO ARCHIVO
class PermisoCrearDepositosArchivo(BasePermission):
    message = 'No tiene permiso para crear depósitos de archivo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=334))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarDepositosArchivo(BasePermission):
    message = 'No tiene permiso para actualizar depósitos de archivo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=335))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarDepositosArchivo(BasePermission):
    message = 'No tiene permiso para consultar depósitos de archivo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=336))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarDepositosArchivo(BasePermission):
    message = 'No tiene permiso para borrar depósitos de archivo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=337))
            if permisos_modulo_rol:
                return True

        return False

# ESTANTE POR DEPOSITO ARCHIVO
class PermisoCrearEstantesDepositosArchivo(BasePermission):
    message = 'No tiene permiso para crear estantes por depósitos de archivo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=354))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarEstantesDepositosArchivo(BasePermission):
    message = 'No tiene permiso para actualizar estantes por depósitos de archivo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=355))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarEstantesDepositosArchivo(BasePermission):
    message = 'No tiene permiso para consultar estantes por depósitos de archivo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=356))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarEstantesDepositosArchivo(BasePermission):
    message = 'No tiene permiso para borrar estantes por depósitos de archivo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=357))
            if permisos_modulo_rol:
                return True

        return False

# CAJAS ARCHIVO DOCUMENTAL
class PermisoCrearCajasArchivoDocumental(BasePermission):
    message = 'No tiene permiso para crear cajas de archivo documental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=360))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarCajasArchivoDocumental(BasePermission):
    message = 'No tiene permiso para actualizar cajas de archivo documental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=361))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCajasArchivoDocumental(BasePermission):
    message = 'No tiene permiso para consultar cajas de archivo documental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=362))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarCajasArchivoDocumental(BasePermission):
    message = 'No tiene permiso para borrar cajas de archivo documental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=363))
            if permisos_modulo_rol:
                return True

        return False

# CONFIGURACION ALERTAS GESTION DOCUMENTAL
class PermisoActualizarConfiguracionAlertasGestionDocumental(BasePermission):
    message = 'No tiene permiso para actualizar la configuración de alertas de gestión documental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=364))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarConfiguracionAlertasGestionDocumental(BasePermission):
    message = 'No tiene permiso para consultar la configuración de alertas de gestión documental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=365))
            if permisos_modulo_rol:
                return True

        return False

# PERMISOS SERIES DOCUMENTALES
class PermisoCrearPermisosSeriesDocumentales(BasePermission):
    message = 'No tiene permiso para crear permisos en series documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=370))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarPermisosSeriesDocumentales(BasePermission):
    message = 'No tiene permiso para actualizar permisos en series documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=371))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarPermisosSeriesDocumentales(BasePermission):
    message = 'No tiene permiso para consultar permisos en series documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=372))
            if permisos_modulo_rol:
                return True

        return False

# CONTROL DE ACCESO CLASIFICACION EXPEDIENTES
class PermisoCrearControlAccesoClasificacionExpedientes(BasePermission):
    message = 'No tiene permiso para crear control de acceso de clasificación de expedientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=373))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarControlAccesoClasificacionExpedientes(BasePermission):
    message = 'No tiene permiso para actualizar control de acceso de clasificación de expedientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=374))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarControlAccesoClasificacionExpedientes(BasePermission):
    message = 'No tiene permiso para consultar control de acceso de clasificación de expedientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=375))
            if permisos_modulo_rol:
                return True

        return False

# HOMOLOGACION SECCIONES PERSISTENTES CCD
class PermisoCrearHomologacionSeccionesPersistentesCCD(BasePermission):
    message = 'No tiene permiso para crear homologación secciones persistentes del CCD'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=376))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarHomologacionSeccionesPersistentesCCD(BasePermission):
    message = 'No tiene permiso para actualizar homologación secciones persistentes del CCD'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=377))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarHomologacionSeccionesPersistentesCCD(BasePermission):
    message = 'No tiene permiso para consultar homologación secciones persistentes del CCD'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=378))
            if permisos_modulo_rol:
                return True

        return False

# ASIGNACION SECCIONES RESPONSABLES CCD
class PermisoCrearAsignacionSeccionesResponsablesCCD(BasePermission):
    message = 'No tiene permiso para crear asignación de secciones responsables del CCD'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=379))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarAsignacionSeccionesResponsablesCCD(BasePermission):
    message = 'No tiene permiso para actualizar asignación de secciones responsables del CCD'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=380))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarAsignacionSeccionesResponsablesCCD(BasePermission):
    message = 'No tiene permiso para consultar asignación de secciones responsables del CCD'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=381))
            if permisos_modulo_rol:
                return True

        return False

# DELEGACION OFICINAS RESPONSABLES EXPEDIENTES
class PermisoCrearDelegacionOficinasResponsablesExpedientes(BasePermission):
    message = 'No tiene permiso para crear delegación de oficinas responsables de expedientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=382))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarDelegacionOficinasResponsablesExpedientes(BasePermission):
    message = 'No tiene permiso para actualizar delegación de oficinas responsables de expedientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=383))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarDelegacionOficinasResponsablesExpedientes(BasePermission):
    message = 'No tiene permiso para consultar delegación de oficinas responsables de expedientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=384))
            if permisos_modulo_rol:
                return True

        return False

# CARPETAS DE ARCHIVO DOCUMENTAL
class PermisoCrearCarpetasArchivoDocumental(BasePermission):
    message = 'No tiene permiso para crear carpetas de archivo documental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=385))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarCarpetasArchivoDocumental(BasePermission):
    message = 'No tiene permiso para actualizar carpetas de archivo documental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=386))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCarpetasArchivoDocumental(BasePermission):
    message = 'No tiene permiso para consultar carpetas de archivo documental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=387))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarCarpetasArchivoDocumental(BasePermission):
    message = 'No tiene permiso para borrar carpetas de archivo documental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=388))
            if permisos_modulo_rol:
                return True

        return False

# ADMINISTRADOR PLANTILLAS DOCUMENTALES
class PermisoCrearAdministradorPlantillasDocumentales(BasePermission):
    message = 'No tiene permiso para crear administrador de plantillas documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=389))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarAdministradorPlantillasDocumentales(BasePermission):
    message = 'No tiene permiso para actualizar administrador de plantillas documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=390))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarAdministradorPlantillasDocumentales(BasePermission):
    message = 'No tiene permiso para consultar administrador de plantillas documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=391))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarAdministradorPlantillasDocumentales(BasePermission):
    message = 'No tiene permiso para borrar administrador de plantillas documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=392))
            if permisos_modulo_rol:
                return True

        return False

# CENTRO PLANTILLAS DOCUMENTALES
class PermisoConsultarCentroPlantillasDocumentales(BasePermission):
    message = 'No tiene permiso para consultar centro de plantillas documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=393))
            if permisos_modulo_rol:
                return True

        return False

# CONFIGURACION TIPOS RADICADO ACTUALES
class PermisoActualizarConfiguracionTiposRadicadoActuales(BasePermission):
    message = 'No tiene permiso para actualizar configuración de tipos de radicado actuales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=394))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarConfiguracionTiposRadicadoActuales(BasePermission):
    message = 'No tiene permiso para consultar configuración de tipos de radicado actuales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=395))
            if permisos_modulo_rol:
                return True

        return False

# CONFIGURACION TIPOS RADICADO PRROXIMO AÑO
class PermisoActualizarConfiguracionTiposRadicadoProximoAnio(BasePermission):
    message = 'No tiene permiso para actualizar configuración de tipos de radicado próximo año'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=396))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarConfiguracionTiposRadicadoProximoAnio(BasePermission):
    message = 'No tiene permiso para consultar configuración de tipos de radicado próximo año'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=397))
            if permisos_modulo_rol:
                return True

        return False

# REPORTE PERMISOS DOCUMENTACION
class PermisoConsultarReportePermisosDocumentacion(BasePermission):
    message = 'No tiene permiso para consultar reporte de permisos sobre la documentación'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=398))
            if permisos_modulo_rol:
                return True

        return False

# CIERRE EXPEDIENTES DOCUMENTALES
class PermisoCrearCierreExpedientesDocumentales(BasePermission):
    message = 'No tiene permiso para crear cierre de expedientes documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=399))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCierreExpedientesDocumentales(BasePermission):
    message = 'No tiene permiso para consultar cierre de expedientes documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=400))
            if permisos_modulo_rol:
                return True

        return False

# CONFIGURACION TIPOS EXPEDIENTES ACTUALES
class PermisoCrearConfiguracionTiposExpedientesActuales(BasePermission):
    message = 'No tiene permiso para crear configuración de tipos de expedientes actuales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=401))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarConfiguracionTiposExpedientesActuales(BasePermission):
    message = 'No tiene permiso para actualizar configuración de tipos de expedientes actuales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=402))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarConfiguracionTiposExpedientesActuales(BasePermission):
    message = 'No tiene permiso para consultar configuración de tipos de expedientes actuales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=403))
            if permisos_modulo_rol:
                return True

        return False

# REGISTRAR CAMBIOS TIPOS EXPEDIENTES PROXIMO AÑO
class PermisoCrearRegistrarCambiosTiposExpedientesProximoAnio(BasePermission):
    message = 'No tiene permiso para crear registrar cambios en tipos de expedientes del próximo año'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=404))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarRegistrarCambiosTiposExpedientesProximoAnio(BasePermission):
    message = 'No tiene permiso para actualizar registrar cambios en tipos de expedientes del próximo año'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=405))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarRegistrarCambiosTiposExpedientesProximoAnio(BasePermission):
    message = 'No tiene permiso para consultar registrar cambios en tipos de expedientes del próximo año'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=406))
            if permisos_modulo_rol:
                return True

        return False

# REAPERTURA EXPEDIENTES DOCUMENTALES
class PermisoCrearReaperturaExpedientesDocumentales(BasePermission):
    message = 'No tiene permiso para crear reapertura de expedientes documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=407))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarReaperturaExpedientesDocumentales(BasePermission):
    message = 'No tiene permiso para consultar reapertura de expedientes documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=408))
            if permisos_modulo_rol:
                return True

        return False

# FIRMA Y CIERRE DE INDICE ELECTRONICO
class PermisoCrearFirmaCierreIndiceElectronico(BasePermission):
    message = 'No tiene permiso para crear firma y cierre de índice electrónico'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=409))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarFirmaCierreIndiceElectronico(BasePermission):
    message = 'No tiene permiso para consultar firma y cierre de índice electrónico'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=410))
            if permisos_modulo_rol:
                return True

        return False

# CONSULTA DE INDICES ELECTRONICOS
class PermisoConsultarConsultaIndicesElectronicos(BasePermission):
    message = 'No tiene permiso para consultar consulta de índices electrónicos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=411))
            if permisos_modulo_rol:
                return True

        return False

# CONSULTA DE EXPEDIENTES DOCUMENTALES
class PermisoConsultarConsultaExpedientesDocumentales(BasePermission):
    message = 'No tiene permiso para consultar consulta de expedientes documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=412))
            if permisos_modulo_rol:
                return True

        return False

# TIPOS DE PQRSDF
class PermisoActualizarTiposPQRSDF(BasePermission):
    message = 'No tiene permiso para actualizar tipos de PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=413))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarTiposPQRSDF(BasePermission):
    message = 'No tiene permiso para consultar tipos de PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=414))
            if permisos_modulo_rol:
                return True

        return False

# TIPOS DE MEDIOS DE SOLICITUD
class PermisoCrearTiposMediosSolicitud(BasePermission):
    message = 'No tiene permiso para crear tipos de medios de solicitud'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=415))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarTiposMediosSolicitud(BasePermission):
    message = 'No tiene permiso para actualizar tipos de medios de solicitud'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=416))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarTiposMediosSolicitud(BasePermission):
    message = 'No tiene permiso para consultar tipos de medios de solicitud'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=417))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarTiposMediosSolicitud(BasePermission):
    message = 'No tiene permiso para borrar tipos de medios de solicitud'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=418))
            if permisos_modulo_rol:
                return True

        return False

# METADATOS PERSONALIZADOS
class PermisoCrearMetadatosPersonalizados(BasePermission):
    message = 'No tiene permiso para crear metadatos personalizados'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=419))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarMetadatosPersonalizados(BasePermission):
    message = 'No tiene permiso para actualizar metadatos personalizados'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=420))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarMetadatosPersonalizados(BasePermission):
    message = 'No tiene permiso para consultar metadatos personalizados'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=421))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarMetadatosPersonalizados(BasePermission):
    message = 'No tiene permiso para borrar metadatos personalizados'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=422))
            if permisos_modulo_rol:
                return True

        return False

# CONSULTA DEL ARCHIVO FISICO
class PermisoConsultarConsultaArchivoFisico(BasePermission):
    message = 'No tiene permiso para consultar consulta del archivo físico'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=423))
            if permisos_modulo_rol:
                return True

        return False

# APERTURA DE EXPEDIENTES
class PermisoCrearAperturaExpedientes(BasePermission):
    message = 'No tiene permiso para crear apertura de expedientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=427))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarAperturaExpedientes(BasePermission):
    message = 'No tiene permiso para actualizar apertura de expedientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=428))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarAperturaExpedientes(BasePermission):
    message = 'No tiene permiso para consultar apertura de expedientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=429))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarAperturaExpedientes(BasePermission):
    message = 'No tiene permiso para borrar apertura de expedientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=430))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAnularAperturaExpedientes(BasePermission):
    message = 'No tiene permiso para anular apertura de expedientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=431))
            if permisos_modulo_rol:
                return True

        return False

# INDEXACION DOCUMENTOS
class PermisoCrearIndexacionDocumentos(BasePermission):
    message = 'No tiene permiso para crear indexación de documentos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=432))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarIndexacionDocumentos(BasePermission):
    message = 'No tiene permiso para actualizar indexación de documentos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=433))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarIndexacionDocumentos(BasePermission):
    message = 'No tiene permiso para consultar indexación de documentos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=434))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarIndexacionDocumentos(BasePermission):
    message = 'No tiene permiso para borrar indexación de documentos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=435))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAnularIndexacionDocumentos(BasePermission):
    message = 'No tiene permiso para anular indexación de documentos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=436))
            if permisos_modulo_rol:
                return True

        return False

# PQRSDF
class PermisoCrearPQRSDF(BasePermission):
    message = 'No tiene permiso para crear PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=437))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarPQRSDF(BasePermission):
    message = 'No tiene permiso para actualizar PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=438))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarPQRSDF(BasePermission):
    message = 'No tiene permiso para consultar PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=439))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarPQRSDF(BasePermission):
    message = 'No tiene permiso para borrar PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=440))
            if permisos_modulo_rol:
                return True

        return False

# CONFIGURACION TIEMPOS RESPUESTA
class PermisoActualizarConfiguracionTiemposRespuesta(BasePermission):
    message = 'No tiene permiso para actualizar configuración de tiempos de respuesta'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=441))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarConfiguracionTiemposRespuesta(BasePermission):
    message = 'No tiene permiso para consultar configuración de tiempos de respuesta'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=442))
            if permisos_modulo_rol:
                return True

        return False

# CONFIGURACION TIPOLOGIAS DOCUMENTALES AÑO ACTUAL
class PermisoCrearConfiguracionTipologiasDocumentalesActual(BasePermission):
    message = 'No tiene permiso para crear configuración de tipologías documentales para el año actual'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=443))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarConfiguracionTipologiasDocumentalesActual(BasePermission):
    message = 'No tiene permiso para actualizar configuración de tipologías documentales para el año actual'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=444))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarConfiguracionTipologiasDocumentalesActual(BasePermission):
    message = 'No tiene permiso para consultar configuración de tipologías documentales para el año actual'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=445))
            if permisos_modulo_rol:
                return True

        return False

# REGISTRAR CAMBIOS TIPOLOGIAS DOCS PARA EL PROXIMO AÑO
class PermisoCrearRegistrarCambiosTipologiasProximoAnio(BasePermission):
    message = 'No tiene permiso para crear registrar cambios de tipologías documentales para el próximo año'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=446))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarRegistrarCambiosTipologiasProximoAnio(BasePermission):
    message = 'No tiene permiso para actualizar registrar cambios de tipologías documentales para el próximo año'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=447))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarRegistrarCambiosTipologiasProximoAnio(BasePermission):
    message = 'No tiene permiso para consultar registrar cambios de tipologías documentales para el próximo año'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=448))
            if permisos_modulo_rol:
                return True

        return False

# REUBICACION FISICA EXPEDIENTES
class PermisoActualizarReubicacionFisicaExpedientes(BasePermission):
    message = 'No tiene permiso para actualizar reubicación física de expedientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=449))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarReubicacionFisicaExpedientes(BasePermission):
    message = 'No tiene permiso para consultar reubicación física de expedientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=450))
            if permisos_modulo_rol:
                return True

        return False

# ADMINISTRADOR DE ENCUESTAS
class PermisoCrearAdminEncuestas(BasePermission):
    message = 'No tiene permiso para crear administrador de encuestas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=451))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarAdminEncuestas(BasePermission):
    message = 'No tiene permiso para actualizar administrador de encuestas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=452))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarAdminEncuestas(BasePermission):
    message = 'No tiene permiso para consultar administrador de encuestas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=453))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarAdminEncuestas(BasePermission):
    message = 'No tiene permiso para borrar administrador de encuestas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=454))
            if permisos_modulo_rol:
                return True

        return False

# ESTADISTICAS ENCUESTAS
class PermisoConsultarEstadisticasEncuestas(BasePermission):
    message = 'No tiene permiso para consultar estadísticas de encuestas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=455))
            if permisos_modulo_rol:
                return True

        return False

# CONCESION ACCESO EXPEDIENTES
class PermisoActualizarConcesionAccesoExpedientes(BasePermission):
    message = 'No tiene permiso para actualizar concesión de acceso a expedientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=456))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarConcesionAccesoExpedientes(BasePermission):
    message = 'No tiene permiso para consultar concesión de acceso a expedientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=457))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarConcesionAccesoDocumentos(BasePermission):
    message = 'No tiene permiso para actualizar concesión de acceso a documentos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=458))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarConcesionAccesoDocumentos(BasePermission):
    message = 'No tiene permiso para consultar concesión de acceso a documentos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=459))
            if permisos_modulo_rol:
                return True

        return False

# SOLICITUD DE PQRSDF
class PermisoCrearSolicitudPQRSDF(BasePermission):
    message = 'No tiene permiso para crear solicitud de PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=460))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarSolicitudPQRSDF(BasePermission):
    message = 'No tiene permiso para actualizar solicitud de PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=461))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarSolicitudPQRSDF(BasePermission):
    message = 'No tiene permiso para consultar solicitud de PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=462))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarSolicitudPQRSDF(BasePermission):
    message = 'No tiene permiso para borrar solicitud de PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=463))
            if permisos_modulo_rol:
                return True

        return False

# IMPRESION DE ROTULOS DE RADICADOS
class PermisoConsultarImpresionRotulosRadicados(BasePermission):
    message = 'No tiene permiso para consultar impresión de rótulos de radicados'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=464))
            if permisos_modulo_rol:
                return True

        return False

# CENTRAL DIGITALIZACION
class PermisoCrearCentralDigitalizacion(BasePermission):
    message = 'No tiene permiso para crear central de digitalización'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=465))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarCentralDigitalizacion(BasePermission):
    message = 'No tiene permiso para actualizar central de digitalización'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=466))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCentralDigitalizacion(BasePermission):
    message = 'No tiene permiso para consultar central de digitalización'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=467))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarCentralDigitalizacion(BasePermission):
    message = 'No tiene permiso para borrar central de digitalización'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=468))
            if permisos_modulo_rol:
                return True

        return False

# COMPLEMENTOS SOBRE PQRSDF
class PermisoCrearComplementoSobrePQRSDF(BasePermission):
    message = 'No tiene permiso para crear complementos sobre PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=474))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarComplementoSobrePQRSDF(BasePermission):
    message = 'No tiene permiso para actualizar complementos sobre PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=475))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarComplementoSobrePQRSDF(BasePermission):
    message = 'No tiene permiso para consultar complementos sobre PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=476))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarComplementoSobrePQRSDF(BasePermission):
    message = 'No tiene permiso para borrar complementos sobre PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=477))
            if permisos_modulo_rol:
                return True

        return False

# PANEL DE VENTANILLA
class PermisoConsultarPanelVentanilla(BasePermission):
    message = 'No tiene permiso para consultar el panel de ventanilla'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=478))
            if permisos_modulo_rol:
                return True

        return False

# SOLICITUD DE COMPLEMENTO DE INFORMACION AL USUARIO SOBRE UNA PQRSDF
class PermisoCrearSolicitudComplementoPQRSDF(BasePermission):
    message = 'No tiene permiso para crear solicitud de complemento de información al usuario sobre una PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=479))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarSolicitudComplementoPQRSDF(BasePermission):
    message = 'No tiene permiso para consultar solicitud de complemento de información al usuario sobre una PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=480))
            if permisos_modulo_rol:
                return True

        return False

# RESPUESTA DEL USUARIO A UNA SOLICITUD DE LA ENTIDAD
class PermisoCrearRespuestaSolicitudEntidad(BasePermission):
    message = 'No tiene permiso para crear respuestas del usuario a una solicitud de la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=481))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarRespuestaSolicitudEntidad(BasePermission):
    message = 'No tiene permiso para actualizar respuestas del usuario a una solicitud de la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=482))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarRespuestaSolicitudEntidad(BasePermission):
    message = 'No tiene permiso para consultar respuestas del usuario a una solicitud de la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=483))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarRespuestaSolicitudEntidad(BasePermission):
    message = 'No tiene permiso para borrar respuestas del usuario a una solicitud de la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=484))
            if permisos_modulo_rol:
                return True

        return False

# ASIGNACIONES A SUBSECCIONES O GRUPOS DE GESTION
class PermisoCrearAsignacionSubseccion(BasePermission):
    message = 'No tiene permiso para crear asignaciones a subsecciones o grupos de gestión'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=485))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarAsignacionSubseccion(BasePermission):
    message = 'No tiene permiso para consultar asignaciones a subsecciones o grupos de gestión'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=486))
            if permisos_modulo_rol:
                return True

        return False

# # REQUERIMIENTOS A UNA PQRSDF
class PermisoCrearRequerimientoPQRSDF(BasePermission):
    message = 'No tiene permiso para crear requerimientos sobre una PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=487))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarRequerimientoPQRSDF(BasePermission):
    message = 'No tiene permiso para consultar requerimientos sobre una PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=488))
            if permisos_modulo_rol:
                return True

        return False

# RESPUESTA A UNA SOLICITUD DE LA ENTIDAD
class PermisoCrearRespuestaSolicitudPQRSDF(BasePermission):
    message = 'No tiene permiso para crear respuestas a una solicitud PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=489))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarRespuestaSolicitudPQRSDF(BasePermission):
    message = 'No tiene permiso para consultar respuestas a una solicitud PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=490))
            if permisos_modulo_rol:
                return True

        return False

# OTROS
class PermisoCrearOtros(BasePermission):
    message = 'No tiene permiso para crear elementos en la categoría de "Otros"'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=491))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarOtros(BasePermission):
    message = 'No tiene permiso para actualizar elementos en la categoría de "Otros"'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=492))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarOtros(BasePermission):
    message = 'No tiene permiso para consultar elementos en la categoría de "Otros"'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=493))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarOtros(BasePermission):
    message = 'No tiene permiso para borrar elementos en la categoría de "Otros"'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=494))
            if permisos_modulo_rol:
                return True

        return False

# SOLICITUDES OTROS
class PermisoCrearSolicitudesOtros(BasePermission):
    message = 'No tiene permiso para crear solicitudes en la categoría de "Otros"'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=495))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarSolicitudesOtros(BasePermission):
    message = 'No tiene permiso para actualizar solicitudes en la categoría de "Otros"'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=496))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarSolicitudesOtros(BasePermission):
    message = 'No tiene permiso para consultar solicitudes en la categoría de "Otros"'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=497))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarSolicitudesOtros(BasePermission):
    message = 'No tiene permiso para borrar solicitudes en la categoría de "Otros"'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=498))
            if permisos_modulo_rol:
                return True

        return False

# CREACION DE ENCUESTAS
class PermisoCrearCreacionEncuestas(BasePermission):
    message = 'No tiene permiso para crear encuestas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=499))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarCreacionEncuestas(BasePermission):
    message = 'No tiene permiso para actualizar encuestas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=500))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCreacionEncuestas(BasePermission):
    message = 'No tiene permiso para consultar encuestas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=501))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarCreacionEncuestas(BasePermission):
    message = 'No tiene permiso para borrar encuestas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=502))
            if permisos_modulo_rol:
                return True

        return False

# RESPONDER ENCUESTA
class PermisoCrearResponderEncuesta(BasePermission):
    message = 'No tiene permiso para crear respuestas a encuestas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=503))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarResponderEncuesta(BasePermission):
    message = 'No tiene permiso para consultar respuestas a encuestas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=504))
            if permisos_modulo_rol:
                return True

        return False

# RESPONDER ENCUESTASS
class PermisoCrearResponderEncuestas(BasePermission):
    message = 'No tiene permiso para crear respuestas a encuestas múltiples'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=505))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarResponderEncuestas(BasePermission):
    message = 'No tiene permiso para consultar respuestas a encuestas múltiples'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=506))
            if permisos_modulo_rol:
                return True

        return False

# BANDEJA DE TAREAS
class PermisoCrearBandejaTareas(BasePermission):
    message = 'No tiene permiso para crear tareas en la bandeja de tareas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=507))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarBandejaTareas(BasePermission):
    message = 'No tiene permiso para consultar la bandeja de tareas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=508))
            if permisos_modulo_rol:
                return True

        return False

# REPORTES PQRSDF POR ESTADO
class PermisoConsultarReportesPQRSDFPorEstado(BasePermission):
    message = 'No tiene permiso para consultar reportes de PQRSDF por estado'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=509))
            if permisos_modulo_rol:
                return True

        return False

# TRANSFERENCIAS DOCUMENTALES
class PermisoCrearTransferenciasDocumentales(BasePermission):
    message = 'No tiene permiso para crear transferencias documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=510))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarTransferenciasDocumentales(BasePermission):
    message = 'No tiene permiso para consultar transferencias documentales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=511))
            if permisos_modulo_rol:
                return True

        return False

# ESTADO DE SOLICITUDES - USUARIO INTERNO
class PermisoConsultarEstadoSolicitudUsuarioInterno(BasePermission):
    message = 'No tiene permiso para consultar el estado de una solicitud como usuario interno'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=512))
            if permisos_modulo_rol:
                return True

        return False

# ESTADO DE SOLICITUDES - USUARIO EXTERNO
class PermisoConsultarEstadoSolicitudUsuarioExternoLogueado(BasePermission):
    message = 'No tiene permiso para consultar el estado de una solicitud como usuario externo logueado'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=513))
            if permisos_modulo_rol:
                return True

        return False

# FLUJO DE TRABAJO DE PQRSDF
class PermisoConsultarWorkFlowPQRSDF(BasePermission):
    message = 'No tiene permiso para consultar el flujo de trabajo de una PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=627))
            if permisos_modulo_rol:
                return True

        return False

# ELIMINACION DOCUMENTAL
class PermisoCrearEliminacionDocumental(BasePermission):
    message = 'No tiene permiso para crear en eliminación documental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=654))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarEliminacionDocumental(BasePermission):
    message = 'No tiene permiso para actualizar en eliminación documental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=655))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarEliminacionDocumental(BasePermission):
    message = 'No tiene permiso para consultar en eliminación documental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=656))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarEliminacionDocumental(BasePermission):
    message = 'No tiene permiso para borrar en eliminación documental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=657))
            if permisos_modulo_rol:
                return True

        return False

# RADICACION DE EMAILS
class PermisoConsultarRadicacionEmail(BasePermission):
    message = 'No tiene permiso para consultar la radicación de emails'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=658))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarRadicacionEmail(BasePermission):
    message = 'No tiene permiso para borrar la radicación de emails'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=659))
            if permisos_modulo_rol:
                return True

        return False

# INDICADORES PQRSDF
class PermisoConsultarIndicadoresPQRSDF(BasePermission):
    message = 'No tiene permiso para consultar los indicadores de PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=683))
            if permisos_modulo_rol:
                return True

        return False

# REPORTES GENERALES GESTOR DOCUMENTAL
class PermisoConsultarReportesGeneralesGestorDocumental(BasePermission):
    message = 'No tiene permiso para consultar los reportes generales del gestor documental'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=716))
            if permisos_modulo_rol:
                return True

        return False

# RESPONDER REQUERIMIENTO OPA
class PermisoCrearResponderRequerimientoOPA(BasePermission):
    message = 'No tiene permiso para crear en responder requerimiento OPA'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=717))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarResponderRequerimientoOPA(BasePermission):
    message = 'No tiene permiso para actualizar en responder requerimiento OPA'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=718))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarResponderRequerimientoOPA(BasePermission):
    message = 'No tiene permiso para consultar en responder requerimiento OPA'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=719))
            if permisos_modulo_rol:
                return True

        return False

# REPORTES PQRSDF
class PermisoConsultarReportesPQRSDF(BasePermission):
    message = 'No tiene permiso para consultar los reportes de PQRSDF'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=720))
            if permisos_modulo_rol:
                return True

        return False

# VITAL
class PermisoConsultarVital(BasePermission):
    message = 'No tiene permiso para consultar Vital'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=796))
            if permisos_modulo_rol:
                return True

        return False
