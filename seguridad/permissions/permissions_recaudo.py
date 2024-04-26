from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q

# CONSTRUCTOR DE FORMULAS PARA LIQUIDACIÓN
class PermisoCrearConstructorFormulas(BasePermission):
    message = 'No tiene permiso para crear en Constructor de Fórmulas para Liquidación'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=265))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarConstructorFormulas(BasePermission):
    message = 'No tiene permiso para actualizar en Constructor de Fórmulas para Liquidación'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=266))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarConstructorFormulas(BasePermission):
    message = 'No tiene permiso para consultar en Constructor de Fórmulas para Liquidación'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=267))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarConstructorFormulas(BasePermission):
    message = 'No tiene permiso para borrar en Constructor de Fórmulas para Liquidación'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=268))
            if permisos_modulo_rol:
                return True

        return False

# LISTADO DE OBLIGACIONES
class PermisoConsultarListadoObligaciones(BasePermission):
    message = 'No tiene permiso para consultar en Listado de Obligaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=269))
            if permisos_modulo_rol:
                return True

        return False

# CONSULTA DE DEUDORES
class PermisoConsultarConsultaDeudores(BasePermission):
    message = 'No tiene permiso para consultar en Consulta de Deudores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=270))
            if permisos_modulo_rol:
                return True

        return False

# SOLICITUD DE FACILIDAD DE PAGO
class PermisoCrearSolicitudFacilidadPago(BasePermission):
    message = 'No tiene permiso para crear en Solicitud de Facilidad de Pago'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=271))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarSolicitudFacilidadPago(BasePermission):
    message = 'No tiene permiso para actualizar en Solicitud de Facilidad de Pago'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=272))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarSolicitudFacilidadPago(BasePermission):
    message = 'No tiene permiso para consultar en Solicitud de Facilidad de Pago'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=273))
            if permisos_modulo_rol:
                return True

        return False

# SOLICITUDES DE FACILIDAD DE PAGO PENDIENTES
class PermisoActualizarSolicitudesFacilidadesPagoPendientes(BasePermission):
    message = 'No tiene permiso para actualizar en Solicitudes de Facilidades de Pago Pendientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=274))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarSolicitudesFacilidadesPagoPendientes(BasePermission):
    message = 'No tiene permiso para consultar en Solicitudes de Facilidades de Pago Pendientes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=275))
            if permisos_modulo_rol:
                return True

        return False

# SOLICITUDES DE FACILIDAD DE PAGO ASIGNADAS
class PermisoConsultarSolicitudesFacilidadPagoAsignadas(BasePermission):
    message = 'No tiene permiso para consultar en Solicitudes de Facilidad de Pago Asignadas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=276))
            if permisos_modulo_rol:
                return True

        return False

# GESTIÓN DE SOLICITUD DE FACILIDAD DE PAGO
class PermisoCrearGestionSolicitudFacilidadPago(BasePermission):
    message = 'No tiene permiso para crear en Gestión de Solicitud de Facilidad de Pago'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=277))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarGestionSolicitudFacilidadPago(BasePermission):
    message = 'No tiene permiso para actualizar en Gestión de Solicitud de Facilidad de Pago'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=278))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarGestionSolicitudFacilidadPago(BasePermission):
    message = 'No tiene permiso para consultar en Gestión de Solicitud de Facilidad de Pago'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=279))
            if permisos_modulo_rol:
                return True

        return False

# CREACIÓN DE PLAN DE PAGO
class PermisoCrearCreacionPlanPagos(BasePermission):
    message = 'No tiene permiso para crear en Creación de Plan de Pagos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=280))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarCreacionPlanPagos(BasePermission):
    message = 'No tiene permiso para actualizar en Creación de Plan de Pagos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=281))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCreacionPlanPagos(BasePermission):
    message = 'No tiene permiso para consultar en Creación de Plan de Pagos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=282))
            if permisos_modulo_rol:
                return True

        return False

# CREACIÓN DE RESOLUCIÓN DE FACILIDAD DE PAGO
class PermisoCrearCreacionResolucionFacilidadPago(BasePermission):
    message = 'No tiene permiso para crear en Creación de Resolución de Facilidad de Pago'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=283))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarCreacionResolucionFacilidadPago(BasePermission):
    message = 'No tiene permiso para actualizar en Creación de Resolución de Facilidad de Pago'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=284))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCreacionResolucionFacilidadPago(BasePermission):
    message = 'No tiene permiso para consultar en Creación de Resolución de Facilidad de Pago'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=285))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAprobarCreacionResolucionFacilidadPago(BasePermission):
    message = 'No tiene permiso para aprobar en Creación de Resolución de Facilidad de Pago'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=286))
            if permisos_modulo_rol:
                return True

        return False

# LISTADO DE FACILIDADES DE PAGO
class PermisoConsultarListadoFacilidadesPago(BasePermission):
    message = 'No tiene permiso para consultar en Listado de Facilidades de Pago'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=287))
            if permisos_modulo_rol:
                return True

        return False

# DETALLE DE FACILIDAD DE PAGO
class PermisoConsultarDetalleFacilidadPago(BasePermission):
    message = 'No tiene permiso para consultar en Detalle de Facilidad de Pago'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=288))
            if permisos_modulo_rol:
                return True

        return False

# COMPENDIO DATOS RECAUDO
class PermisoConsultarCompendioDatosRecaudo(BasePermission):
    message = 'No tiene permiso para consultar en Compendio Datos Recaudo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=289))
            if permisos_modulo_rol:
                return True

        return False

# ETAPAS DEL PROCESO DE RENTAS
class PermisoActualizarEtapasProcesoRentas(BasePermission):
    message = 'No tiene permiso para actualizar en Etapas del Proceso de Rentas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=290))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarEtapasProcesoRentas(BasePermission):
    message = 'No tiene permiso para consultar en Etapas del Proceso de Rentas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=291))
            if permisos_modulo_rol:
                return True

        return False

# FLUJO DEL PROCESO DE RENTAS
class PermisoCrearFlujoProcesoRecaudo(BasePermission):
    message = 'No tiene permiso para crear en Flujo del Proceso'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=292))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarFlujoProcesoRecaudo(BasePermission):
    message = 'No tiene permiso para actualizar en Flujo del Proceso'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=293))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarFlujoProcesoRecaudo(BasePermission):
    message = 'No tiene permiso para consultar en Flujo del Proceso'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=294))
            if permisos_modulo_rol:
                return True

        return False

# GESTION DE CARTERA
class PermisoCrearGestionCartera(BasePermission):
    message = 'No tiene permiso para crear en Gestión de Cartera'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=295))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarGestionCartera(BasePermission):
    message = 'No tiene permiso para consultar en Gestión de Cartera'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=296))
            if permisos_modulo_rol:
                return True

        return False

# FACILIDADES DE PAGO
class PermisoConsultarFacilidadesPago(BasePermission):
    message = 'No tiene permiso para consultar en Facilidades de Pago'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=297))
            if permisos_modulo_rol:
                return True

        return False

# LISTADO DE CARTERA DETALLADO
class PermisoConsultarListadoCarteraDetallado(BasePermission):
    message = 'No tiene permiso para consultar en Listado de Cartera Detallado'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=298))
            if permisos_modulo_rol:
                return True

        return False

# CARTERA TOTALIZADA A FECHA
class PermisoConsultarCarteraTotalizadaFecha(BasePermission):
    message = 'No tiene permiso para consultar en Cartera Totalizada a Fecha'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=299))
            if permisos_modulo_rol:
                return True

        return False

# CONFIGURACIÓN DE ALERTAS DE RECAUDO
class PermisoActualizarConfiguracionAlertasRecaudo(BasePermission):
    message = 'No tiene permiso para actualizar en Configuración de Alertas de Recaudo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=332))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarConfiguracionAlertasRecaudo(BasePermission):
    message = 'No tiene permiso para consultar en Configuración de Alertas de Recaudo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=333))
            if permisos_modulo_rol:
                return True

        return False

# GENERADOR DE LIQUIDACIONES
class PermisoCrearGeneradorLiquidacionesRecaudo(BasePermission):
    message = 'No tiene permiso para crear en Generador de Liquidaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=469))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarGeneradorLiquidacionesRecaudo(BasePermission):
    message = 'No tiene permiso para actualizar en Generador de Liquidaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=470))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarGeneradorLiquidacionesRecaudo(BasePermission):
    message = 'No tiene permiso para consultar en Generador de Liquidaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=471))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarGeneradorLiquidacionesRecaudo(BasePermission):
    message = 'No tiene permiso para borrar en Generador de Liquidaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=472))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAnularGeneradorLiquidacionesRecaudo(BasePermission):
    message = 'No tiene permiso para anular en Generador de Liquidaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=473))
            if permisos_modulo_rol:
                return True

        return False

# CONFIGURACIÓN DE VARIABLES
class PermisoCrearConfiguracionVariablesRecaudo(BasePermission):
    message = 'No tiene permiso para crear en Configuración de Variables'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=665))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarConfiguracionVariablesRecaudo(BasePermission):
    message = 'No tiene permiso para actualizar en Configuración de Variables'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=666))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarConfiguracionVariablesRecaudo(BasePermission):
    message = 'No tiene permiso para consultar en Configuración de Variables'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=667))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarConfiguracionVariablesRecaudo(BasePermission):
    message = 'No tiene permiso para borrar en Configuración de Variables'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=668))
            if permisos_modulo_rol:
                return True

        return False

# GENERADOR DE DOCUMENTOS
class PermisoCrearGeneradorDocumentosRecaudo(BasePermission):
    message = 'No tiene permiso para crear en Generador de Documentos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=669))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarGeneradorDocumentosRecaudo(BasePermission):
    message = 'No tiene permiso para actualizar en Generador de Documentos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=670))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarGeneradorDocumentosRecaudo(BasePermission):
    message = 'No tiene permiso para consultar en Generador de Documentos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=671))
            if permisos_modulo_rol:
                return True

        return False

# HISTORICO DE DOCUMENTOS
class PermisoConsultarHistoricoDocumentosRecaudo(BasePermission):
    message = 'No tiene permiso para consultar en Historico de Documentos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=672))
            if permisos_modulo_rol:
                return True

        return False

# CONFIGURACIÓN DE SUBETAPAS
class PermisoCrearConfiguracionSubetapasRecaudo(BasePermission):
    message = 'No tiene permiso para crear en Configuración de Subetapas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=673))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarConfiguracionSubetapasRecaudo(BasePermission):
    message = 'No tiene permiso para actualizar en Configuración de Subetapas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=674))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarConfiguracionSubetapasRecaudo(BasePermission):
    message = 'No tiene permiso para consultar en Configuración de Subetapas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=675))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarConfiguracionSubetapasRecaudo(BasePermission):
    message = 'No tiene permiso para borrar en Configuración de Subetapas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=676))
            if permisos_modulo_rol:
                return True

        return False

# FORMULARIO DE AGUA CAPTADA
class PermisoCrearFormularioAguaCaptadaRecaudo(BasePermission):
    message = 'No tiene permiso para crear en Formulario de Agua captada'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=677))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarFormularioAguaCaptadaRecaudo(BasePermission):
    message = 'No tiene permiso para consultar en Formulario de Agua captada'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=678))
            if permisos_modulo_rol:
                return True

        return False

# FACTOR REGIONAL
class PermisoCrearFactorRegionalRecaudo(BasePermission):
    message = 'No tiene permiso para crear en Factor Regional'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=679))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarFactorRegionalRecaudo(BasePermission):
    message = 'No tiene permiso para actualizar en Factor Regional'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=680))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarFactorRegionalRecaudo(BasePermission):
    message = 'No tiene permiso para consultar en Factor Regional'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=681))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarFactorRegionalRecaudo(BasePermission):
    message = 'No tiene permiso para borrar en Factor Regional'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=682))
            if permisos_modulo_rol:
                return True

        return False

# CONFIGURACION CONSECUTIVO
class PermisoCrearConfiguracionConsecutivoRecaudo(BasePermission):
    message = 'No tiene permiso para crear en Configuracion de consecutivo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=699))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarConfiguracionConsecutivoRecaudo(BasePermission):
    message = 'No tiene permiso para actualizar en Configuracion de consecutivo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=700))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarConfiguracionConsecutivoRecaudo(BasePermission):
    message = 'No tiene permiso para consultar en Configuracion de consecutivo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=701))
            if permisos_modulo_rol:
                return True

        return False

# HISTORIAL CONSECUTIVO
class PermisoActualizarHistorialConsecutivoRecaudo(BasePermission):
    message = 'No tiene permiso para actualizar en Historial de consecutivo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=702))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarHistorialConsecutivoRecaudo(BasePermission):
    message = 'No tiene permiso para consultar en Historial de consecutivo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=703))
            if permisos_modulo_rol:
                return True

        return False

# INDICADORES DE GESTION
class PermisoCrearIndicadoresGestionRecaudo(BasePermission):
    message = 'No tiene permiso para crear en Indicadores de Gestión'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=738))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarIndicadoresGestionRecaudo(BasePermission):
    message = 'No tiene permiso para actualizar en Indicadores de Gestión'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=739))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarIndicadoresGestionRecaudo(BasePermission):
    message = 'No tiene permiso para consultar en Indicadores de Gestión'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=740))
            if permisos_modulo_rol:
                return True

        return False

# PROFESIONALES
class PermisoCrearProfesionalesRecaudo(BasePermission):
    message = 'No tiene permiso para crear en Profesionales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=779))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarProfesionalesRecaudo(BasePermission):
    message = 'No tiene permiso para actualizar en Profesionales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=780))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarProfesionalesRecaudo(BasePermission):
    message = 'No tiene permiso para consultar en Profesionales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=781))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarProfesionalesRecaudo(BasePermission):
    message = 'No tiene permiso para borrar en Profesionales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=782))
            if permisos_modulo_rol:
                return True

        return False

# REPORTES E INDICADORES
class PermisoCrearReportesIndicadoresRecaudo(BasePermission):
    message = 'No tiene permiso para crear en Reportes e Indicadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=794))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarReportesIndicadoresRecaudo(BasePermission):
    message = 'No tiene permiso para consultar en Reportes e Indicadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=795))
            if permisos_modulo_rol:
                return True

        return False