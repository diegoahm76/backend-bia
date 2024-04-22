from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q

# ESTACIONES HIDROMETEOROLOGICAS
class PermisoCrearEstacionesHidrometeorologicasRecu(BasePermission):
    message = 'No tiene permiso para crear en Estaciones Hidrometeorológicas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=243))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarEstacionesHidrometeorologicasRecu(BasePermission):
    message = 'No tiene permiso para actualizar en Estaciones Hidrometeorológicas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=244))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarEstacionesHidrometeorologicasRecu(BasePermission):
    message = 'No tiene permiso para consultar en Estaciones Hidrometeorológicas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=245))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarEstacionesHidrometeorologicasRecu(BasePermission):
    message = 'No tiene permiso para borrar en Estaciones Hidrometeorológicas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=246))
            if permisos_modulo_rol:
                return True

        return False

# PARAMETROS DE REFERENCIA SENSORES
class PermisoActualizarParametrosReferenciaSensoresRecu(BasePermission):
    message = 'No tiene permiso para actualizar en Parámetros de Referencia Sensores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=247))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarParametrosReferenciaSensoresRecu(BasePermission):
    message = 'No tiene permiso para consultar en Parámetros de Referencia Sensores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=248))
            if permisos_modulo_rol:
                return True

        return False

# MENSAJES DE ALERTA EXTERNOS
class PermisoCrearMensajesAlertaExternosRecu(BasePermission):
    message = 'No tiene permiso para crear en Mensajes de Alerta Externos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=249))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarMensajesAlertaExternosRecu(BasePermission):
    message = 'No tiene permiso para actualizar en Mensajes de Alerta Externos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=250))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarMensajesAlertaExternosRecu(BasePermission):
    message = 'No tiene permiso para consultar en Mensajes de Alerta Externos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=251))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarMensajesAlertaExternosRecu(BasePermission):
    message = 'No tiene permiso para borrar en Mensajes de Alerta Externos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=252))
            if permisos_modulo_rol:
                return True

        return False

# USUARIOS POR ESTACIÓN
class PermisoCrearUsuariosEstacion(BasePermission):
    message = 'No tiene permiso para crear en Usuarios por Estación'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=253))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarUsuariosEstacion(BasePermission):
    message = 'No tiene permiso para actualizar en Usuarios por Estación'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=254))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarUsuariosEstacion(BasePermission):
    message = 'No tiene permiso para consultar en Usuarios por Estación'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=255))
            if permisos_modulo_rol:
                return True
        return False

class PermisoBorrarUsuariosEstacion(BasePermission):
    message = 'No tiene permiso para borrar en Usuarios por Estación'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=256))
            if permisos_modulo_rol:
                return True
        return False

# GEOLOCALIZACION
class PermisoConsultarGeolocalizacion(BasePermission):
    message = 'No tiene permiso para consultar en Geolocalización'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=257))
            if permisos_modulo_rol:
                return True
        return False

# EMISION DE DATOS SENSOR
class PermisoConsultarEmisionDatosSensor(BasePermission):
    message = 'No tiene permiso para consultar en Emisión de Datos Sensor'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=258))
            if permisos_modulo_rol:
                return True
        return False

# VALORES EXTREMOS SENSOR
class PermisoConsultarValoresExtremosSensor(BasePermission):
    message = 'No tiene permiso para consultar en Valores Extremos Sensor'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=259))
            if permisos_modulo_rol:
                return True
        return False

# HISTORIAL DE DATOS
class PermisoConsultarHistorialDatos(BasePermission):
    message = 'No tiene permiso para consultar en Historial de Datos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=260))
            if permisos_modulo_rol:
                return True
        return False

# HISTORIAL DE ALERTAS EMITIDAS A INTERESADOS
class PermisoConsultarHistorialAlertasInteresados(BasePermission):
    message = 'No tiene permiso para consultar en Historial de Alertas Emitidas a Interesados'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=261))
            if permisos_modulo_rol:
                return True
        return False

# HISTORIAL DE ALERTAS INTERNAS
class PermisoConsultarHistorialAlertasInternas(BasePermission):
    message = 'No tiene permiso para consultar en Historial de Alertas Internas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=262))
            if permisos_modulo_rol:
                return True
        return False

# COMPORTAMIENTOS VARIABLES DE ESTACION
class PermisoConsultarComportamientoVariablesEstacion(BasePermission):
    message = 'No tiene permiso para consultar en Comportamiento Variables de Estación'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=263))
            if permisos_modulo_rol:
                return True
        return False

# COMPARATIVA VARIABLE DE ESTACION EN RANGO DE FECHAS
class PermisoConsultarComparativaVariableEstacionRangoFechas(BasePermission):
    message = 'No tiene permiso para consultar en Comparativa Variable de Estación en Rango de Fechas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=264))
            if permisos_modulo_rol:
                return True
        return False
    
# CONTENIDO PROGRAMATICO PORH
class PermisoCrearContenidoProgramaticoPORH(BasePermission):
    message = 'No tiene permiso para crear en Contenido Programático PORH'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=306))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarContenidoProgramaticoPORH(BasePermission):
    message = 'No tiene permiso para actualizar en Contenido Programático PORH'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=307))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarContenidoProgramaticoPORH(BasePermission):
    message = 'No tiene permiso para consultar en Contenido Programático PORH'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=308))
            if permisos_modulo_rol:
                return True
        return False

class PermisoBorrarContenidoProgramaticoPORH(BasePermission):
    message = 'No tiene permiso para borrar en Contenido Programático PORH'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=309))
            if permisos_modulo_rol:
                return True
        return False

# REGISTRO DE AVANCES DE PROYECTOS
class PermisoCrearRegistroAvancesProyectos(BasePermission):
    message = 'No tiene permiso para crear en Registro de Avances de Proyectos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=310))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarRegistroAvancesProyectos(BasePermission):
    message = 'No tiene permiso para actualizar en Registro de Avances de Proyectos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=311))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarRegistroAvancesProyectos(BasePermission):
    message = 'No tiene permiso para consultar en Registro de Avances de Proyectos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=312))
            if permisos_modulo_rol:
                return True
        return False

# CONFIGURACION DE ALERTAS DE RECURSO HIDRICO
class PermisoActualizarConfiguracionAlertasRecursoHidrico(BasePermission):
    message = 'No tiene permiso para actualizar en Configuración de Alertas de Recurso Hídrico'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=313))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarConfiguracionAlertasRecursoHidrico(BasePermission):
    message = 'No tiene permiso para consultar en Configuración de Alertas de Recurso Hídrico'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=314))
            if permisos_modulo_rol:
                return True
        return False

# REGISTRO DE SECCIONES DE BIBLIOTECA
class PermisoCrearRegistroSeccionesBiblioteca(BasePermission):
    message = 'No tiene permiso para crear en Registro de Secciones de Biblioteca'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=327))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarRegistroSeccionesBiblioteca(BasePermission):
    message = 'No tiene permiso para actualizar en Registro de Secciones de Biblioteca'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=328))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarRegistroSeccionesBiblioteca(BasePermission):
    message = 'No tiene permiso para consultar en Registro de Secciones de Biblioteca'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=329))
            if permisos_modulo_rol:
                return True
        return False

class PermisoBorrarRegistroSeccionesBiblioteca(BasePermission):
    message = 'No tiene permiso para borrar en Registro de Secciones de Biblioteca'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=330))
            if permisos_modulo_rol:
                return True
        return False

# BIBLIOTECA DE RECURSO HIDRICO
class PermisoConsultarBibliotecaRecursoHidrico(BasePermission):
    message = 'No tiene permiso para consultar en Biblioteca Recurso Hídrico'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=331))
            if permisos_modulo_rol:
                return True
        return False

# ADMINISTRACION DE INSTRUMENTOS DE BIBLIOTECA
class PermisoCrearAdministracionInstrumentosBiblioteca(BasePermission):
    message = 'No tiene permiso para crear en Administración de Instrumentos de Biblioteca'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=338))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarAdministracionInstrumentosBiblioteca(BasePermission):
    message = 'No tiene permiso para actualizar en Administración de Instrumentos de Biblioteca'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=339))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarAdministracionInstrumentosBiblioteca(BasePermission):
    message = 'No tiene permiso para consultar en Administración de Instrumentos de Biblioteca'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=340))
            if permisos_modulo_rol:
                return True
        return False

class PermisoBorrarAdministracionInstrumentosBiblioteca(BasePermission):
    message = 'No tiene permiso para borrar en Administración de Instrumentos de Biblioteca'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=341))
            if permisos_modulo_rol:
                return True
        return False

# REGISTRO DE CUENCAS
class PermisoCrearRegistroCuencas(BasePermission):
    message = 'No tiene permiso para crear en Registro de Cuencas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=342))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarRegistroCuencas(BasePermission):
    message = 'No tiene permiso para actualizar en Registro de Cuencas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=343))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarRegistroCuencas(BasePermission):
    message = 'No tiene permiso para consultar en Registro de Cuencas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=344))
            if permisos_modulo_rol:
                return True
        return False

class PermisoBorrarRegistroCuencas(BasePermission):
    message = 'No tiene permiso para borrar en Registro de Cuencas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=345))
            if permisos_modulo_rol:
                return True
        return False

# REGISTRO DE POZOS
class PermisoCrearRegistroPozos(BasePermission):
    message = 'No tiene permiso para crear en Registro de Pozos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=346))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarRegistroPozos(BasePermission):
    message = 'No tiene permiso para actualizar en Registro de Pozos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=347))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarRegistroPozos(BasePermission):
    message = 'No tiene permiso para consultar en Registro de Pozos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=348))
            if permisos_modulo_rol:
                return True
        return False

class PermisoBorrarRegistroPozos(BasePermission):
    message = 'No tiene permiso para borrar en Registro de Pozos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=349))
            if permisos_modulo_rol:
                return True
        return False

# REGISTRO DE PARAMETROS DE LABORATORIO
class PermisoCrearRegistroParametrosLaboratorio(BasePermission):
    message = 'No tiene permiso para crear en Registro de Parámetros de Laboratorio'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=350))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarRegistroParametrosLaboratorio(BasePermission):
    message = 'No tiene permiso para actualizar en Registro de Parámetros de Laboratorio'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=351))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarRegistroParametrosLaboratorio(BasePermission):
    message = 'No tiene permiso para consultar en Registro de Parámetros de Laboratorio'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=352))
            if permisos_modulo_rol:
                return True
        return False

class PermisoBorrarRegistroParametrosLaboratorio(BasePermission):
    message = 'No tiene permiso para borrar en Registro de Parámetros de Laboratorio'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=353))
            if permisos_modulo_rol:
                return True
        return False

# INFORMACIÓN DE RIOS
class PermisoCrearInformacionRios(BasePermission):
    message = 'No tiene permiso para crear en Información de Ríos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=661))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarInformacionRios(BasePermission):
    message = 'No tiene permiso para actualizar en Información de Ríos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=662))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarInformacionRios(BasePermission):
    message = 'No tiene permiso para consultar en Información de Ríos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=663))
            if permisos_modulo_rol:
                return True
        return False

class PermisoBorrarInformacionRios(BasePermission):
    message = 'No tiene permiso para borrar en Información de Ríos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=664))
            if permisos_modulo_rol:
                return True
        return False