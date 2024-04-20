from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q

# CUENCAS
class PermisoCrearCuencas(BasePermission):
    message = 'No tiene permiso para crear en Cuencas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=514))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarCuencas(BasePermission):
    message = 'No tiene permiso para actualizar en Cuencas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=515))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCuencas(BasePermission):
    message = 'No tiene permiso para consultar en Cuencas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=516))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarCuencas(BasePermission):
    message = 'No tiene permiso para borrar en Cuencas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=517))
            if permisos_modulo_rol:
                return True

        return False

# OBJETIVOS DESARROLLO SOSTENIBLE
class PermisoCrearObjetivosDesarrolloSostenible(BasePermission):
    message = 'No tiene permiso para crear en Objetivos de Desarrollo Sostenible'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=518))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarObjetivosDesarrolloSostenible(BasePermission):
    message = 'No tiene permiso para actualizar en Objetivos de Desarrollo Sostenible'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=519))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarObjetivosDesarrolloSostenible(BasePermission):
    message = 'No tiene permiso para consultar en Objetivos de Desarrollo Sostenible'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=520))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarObjetivosDesarrolloSostenible(BasePermission):
    message = 'No tiene permiso para borrar en Objetivos de Desarrollo Sostenible'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=521))
            if permisos_modulo_rol:
                return True

        return False

# TIPOS DE EJE ESTRATEGICO
class PermisoCrearTiposEjeEstrategico(BasePermission):
    message = 'No tiene permiso para crear en Tipos de Eje Estratégico'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=522))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarTiposEjeEstrategico(BasePermission):
    message = 'No tiene permiso para actualizar en Tipos de Eje Estratégico'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=523))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarTiposEjeEstrategico(BasePermission):
    message = 'No tiene permiso para consultar en Tipos de Eje Estratégico'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=524))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarTiposEjeEstrategico(BasePermission):
    message = 'No tiene permiso para borrar en Tipos de Eje Estratégico'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=525))
            if permisos_modulo_rol:
                return True

        return False

# ENTIDADES
class PermisoCrearEntidades(BasePermission):
    message = 'No tiene permiso para crear en Entidades'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=526))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarEntidades(BasePermission):
    message = 'No tiene permiso para actualizar en Entidades'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=527))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarEntidades(BasePermission):
    message = 'No tiene permiso para consultar en Entidades'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=528))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarEntidades(BasePermission):
    message = 'No tiene permiso para borrar en Entidades'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=529))
            if permisos_modulo_rol:
                return True

        return False

# MEDICION INDICADOR
class PermisoCrearMedicionIndicador(BasePermission):
    message = 'No tiene permiso para crear en Medición Indicador'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=530))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarMedicionIndicador(BasePermission):
    message = 'No tiene permiso para actualizar en Medición Indicador'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=531))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarMedicionIndicador(BasePermission):
    message = 'No tiene permiso para consultar en Medición Indicador'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=532))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarMedicionIndicador(BasePermission):
    message = 'No tiene permiso para borrar en Medición Indicador'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=533))
            if permisos_modulo_rol:
                return True

        return False

# TIPO INDICADOR
class PermisoCrearTipoIndicador(BasePermission):
    message = 'No tiene permiso para crear en Tipo Indicador'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=534))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarTipoIndicador(BasePermission):
    message = 'No tiene permiso para actualizar en Tipo Indicador'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=535))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarTipoIndicador(BasePermission):
    message = 'No tiene permiso para consultar en Tipo Indicador'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=536))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarTipoIndicador(BasePermission):
    message = 'No tiene permiso para borrar en Tipo Indicador'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=537))
            if permisos_modulo_rol:
                return True

        return False

# SECTOR
class PermisoCrearSector(BasePermission):
    message = 'No tiene permiso para crear en Sector'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=538))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarSector(BasePermission):
    message = 'No tiene permiso para actualizar en Sector'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=539))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarSector(BasePermission):
    message = 'No tiene permiso para consultar en Sector'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=540))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarSector(BasePermission):
    message = 'No tiene permiso para borrar en Sector'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=541))
            if permisos_modulo_rol:
                return True

        return False

# MODALIDADES
class PermisoCrearModalidades(BasePermission):
    message = 'No tiene permiso para crear en Modalidades'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=542))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarModalidades(BasePermission):
    message = 'No tiene permiso para actualizar en Modalidades'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=543))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarModalidades(BasePermission):
    message = 'No tiene permiso para consultar en Modalidades'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=544))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarModalidades(BasePermission):
    message = 'No tiene permiso para borrar en Modalidades'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=545))
            if permisos_modulo_rol:
                return True

        return False

# UBICACIONES
class PermisoCrearUbicaciones(BasePermission):
    message = 'No tiene permiso para crear en Ubicaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=546))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarUbicaciones(BasePermission):
    message = 'No tiene permiso para actualizar en Ubicaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=547))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarUbicaciones(BasePermission):
    message = 'No tiene permiso para consultar en Ubicaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=548))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarUbicaciones(BasePermission):
    message = 'No tiene permiso para borrar en Ubicaciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=549))
            if permisos_modulo_rol:
                return True

        return False

# FUENTES DE FINANCIACION PAA
class PermisoCrearFuentesFinanciacionPAA(BasePermission):
    message = 'No tiene permiso para crear en Fuentes de Financiación PAA'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=550))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarFuentesFinanciacionPAA(BasePermission):
    message = 'No tiene permiso para actualizar en Fuentes de Financiación PAA'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=551))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarFuentesFinanciacionPAA(BasePermission):
    message = 'No tiene permiso para consultar en Fuentes de Financiación PAA'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=552))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarFuentesFinanciacionPAA(BasePermission):
    message = 'No tiene permiso para borrar en Fuentes de Financiación PAA'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=553))
            if permisos_modulo_rol:
                return True

        return False

# INTERVALOS
class PermisoCrearIntervalos(BasePermission):
    message = 'No tiene permiso para crear en Intervalos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=554))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarIntervalos(BasePermission):
    message = 'No tiene permiso para actualizar en Intervalos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=555))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarIntervalos(BasePermission):
    message = 'No tiene permiso para consultar en Intervalos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=556))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarIntervalos(BasePermission):
    message = 'No tiene permiso para borrar en Intervalos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=557))
            if permisos_modulo_rol:
                return True

        return False

# ESTADOS VIGENCIA FUTURA
class PermisoCrearEstadosVigenciaFutura(BasePermission):
    message = 'No tiene permiso para crear en Estados Vigencia Futura'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=558))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarEstadosVigenciaFutura(BasePermission):
    message = 'No tiene permiso para actualizar en Estados Vigencia Futura'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=559))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarEstadosVigenciaFutura(BasePermission):
    message = 'No tiene permiso para consultar en Estados Vigencia Futura'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=560))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarEstadosVigenciaFutura(BasePermission):
    message = 'No tiene permiso para borrar en Estados Vigencia Futura'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=561))
            if permisos_modulo_rol:
                return True

        return False

# CODIGOS UNSPSC
class PermisoCrearCodigosUnspsc(BasePermission):
    message = 'No tiene permiso para crear en Códigos Unspsc'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=562))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarCodigosUnspsc(BasePermission):
    message = 'No tiene permiso para actualizar en Códigos Unspsc'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=563))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCodigosUnspsc(BasePermission):
    message = 'No tiene permiso para consultar en Códigos Unspsc'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=564))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarCodigosUnspsc(BasePermission):
    message = 'No tiene permiso para borrar en Códigos Unspsc'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=565))
            if permisos_modulo_rol:
                return True

        return False

# ADMINISTRACION PLANES
class PermisoCrearAdministracionPlanes(BasePermission):
    message = 'No tiene permiso para crear en Administración de Planes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=566))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarAdministracionPlanes(BasePermission):
    message = 'No tiene permiso para actualizar en Administración de Planes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=567))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarAdministracionPlanes(BasePermission):
    message = 'No tiene permiso para consultar en Administración de Planes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=568))
            if permisos_modulo_rol:
                return True

        return False

# OBJETIVOS
class PermisoCrearObjetivos(BasePermission):
    message = 'No tiene permiso para crear en Objetivos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=569))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarObjetivos(BasePermission):
    message = 'No tiene permiso para actualizar en Objetivos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=570))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarObjetivos(BasePermission):
    message = 'No tiene permiso para consultar en Objetivos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=571))
            if permisos_modulo_rol:
                return True

        return False

# EJES ESTRATEGICOS
class PermisoCrearEjesEstrategicos(BasePermission):
    message = 'No tiene permiso para crear en Ejes Estratégicos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=572))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarEjesEstrategicos(BasePermission):
    message = 'No tiene permiso para actualizar en Ejes Estratégicos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=573))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarEjesEstrategicos(BasePermission):
    message = 'No tiene permiso para consultar en Ejes Estratégicos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=574))
            if permisos_modulo_rol:
                return True

        return False

# PROGRAMAS
class PermisoCrearProgramas(BasePermission):
    message = 'No tiene permiso para crear en Programas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=575))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarProgramas(BasePermission):
    message = 'No tiene permiso para actualizar en Programas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=576))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarProgramas(BasePermission):
    message = 'No tiene permiso para consultar en Programas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=577))
            if permisos_modulo_rol:
                return True

        return False

# SUBPROGRAMAS
class PermisoCrearSubprogramas(BasePermission):
    message = 'No tiene permiso para crear en Subprogramas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=578))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarSubprogramas(BasePermission):
    message = 'No tiene permiso para actualizar en Subprogramas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=579))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarSubprogramas(BasePermission):
    message = 'No tiene permiso para consultar en Subprogramas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=580))
            if permisos_modulo_rol:
                return True

        return False

# PROYECTOS
class PermisoCrearProyectos(BasePermission):
    message = 'No tiene permiso para crear en Proyectos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=581))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarProyectos(BasePermission):
    message = 'No tiene permiso para actualizar en Proyectos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=582))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarProyectos(BasePermission):
    message = 'No tiene permiso para consultar en Proyectos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=583))
            if permisos_modulo_rol:
                return True

        return False

# PRODUCTOS
class PermisoCrearProductos(BasePermission):
    message = 'No tiene permiso para crear en Productos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=584))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarProductos(BasePermission):
    message = 'No tiene permiso para actualizar en Productos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=585))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarProductos(BasePermission):
    message = 'No tiene permiso para consultar en Productos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=586))
            if permisos_modulo_rol:
                return True

        return False

# ACTIVIDADES
class PermisoCrearActividades(BasePermission):
    message = 'No tiene permiso para crear en Actividades'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=587))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarActividades(BasePermission):
    message = 'No tiene permiso para actualizar en Actividades'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=588))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarActividades(BasePermission):
    message = 'No tiene permiso para consultar en Actividades'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=589))
            if permisos_modulo_rol:
                return True

        return False

# INDICADORES
class PermisoCrearIndicadores(BasePermission):
    message = 'No tiene permiso para crear en Indicadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=590))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarIndicadores(BasePermission):
    message = 'No tiene permiso para actualizar en Indicadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=591))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarIndicadores(BasePermission):
    message = 'No tiene permiso para consultar en Indicadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=592))
            if permisos_modulo_rol:
                return True

        return False

# FUENTES DE FINANCIACION INDICADORES
class PermisoCrearFuentesFinanciacionIndicadores(BasePermission):
    message = 'No tiene permiso para crear en Fuentes de Financiación Indicadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=593))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarFuentesFinanciacionIndicadores(BasePermission):
    message = 'No tiene permiso para actualizar en Fuentes de Financiación Indicadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=594))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarFuentesFinanciacionIndicadores(BasePermission):
    message = 'No tiene permiso para consultar en Fuentes de Financiación Indicadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=595))
            if permisos_modulo_rol:
                return True

        return False

# METAS
class PermisoCrearMetas(BasePermission):
    message = 'No tiene permiso para crear en Metas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=596))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarMetas(BasePermission):
    message = 'No tiene permiso para actualizar en Metas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=597))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarMetas(BasePermission):
    message = 'No tiene permiso para consultar en Metas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=598))
            if permisos_modulo_rol:
                return True

        return False

# SEGUIMIENTO TECNICO PAI
class PermisoCrearSeguimientoTecnicoPAI(BasePermission):
    message = 'No tiene permiso para crear en Seguimiento Técnico PAI'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=599))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarSeguimientoTecnicoPAI(BasePermission):
    message = 'No tiene permiso para actualizar en Seguimiento Técnico PAI'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=600))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarSeguimientoTecnicoPAI(BasePermission):
    message = 'No tiene permiso para consultar en Seguimiento Técnico PAI'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=601))
            if permisos_modulo_rol:
                return True

        return False

# SEGUIMIENTO POAI
class PermisoCrearSeguimientoPOAI(BasePermission):
    message = 'No tiene permiso para crear en Seguimiento POAI'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=602))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarSeguimientoPOAI(BasePermission):
    message = 'No tiene permiso para actualizar en Seguimiento POAI'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=603))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarSeguimientoPOAI(BasePermission):
    message = 'No tiene permiso para consultar en Seguimiento POAI'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=604))
            if permisos_modulo_rol:
                return True

        return False

# CONCEPTO POAI
class PermisoCrearConceptoPOAI(BasePermission):
    message = 'No tiene permiso para crear en Concepto POAI'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=605))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarConceptoPOAI(BasePermission):
    message = 'No tiene permiso para actualizar en Concepto POAI'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=606))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarConceptoPOAI(BasePermission):
    message = 'No tiene permiso para consultar en Concepto POAI'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=607))
            if permisos_modulo_rol:
                return True

        return False

# FUENTE FINANCIACION POAI
class PermisoCrearFuenteFinanciacionPOAI(BasePermission):
    message = 'No tiene permiso para crear en Fuente Financiación POAI'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=608))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarFuenteFinanciacionPOAI(BasePermission):
    message = 'No tiene permiso para actualizar en Fuente Financiación POAI'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=609))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarFuenteFinanciacionPOAI(BasePermission):
    message = 'No tiene permiso para consultar en Fuente Financiación POAI'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=610))
            if permisos_modulo_rol:
                return True

        return False

# BANCO PROYECTOS
class PermisoCrearBancoProyectos(BasePermission):
    message = 'No tiene permiso para crear en Banco de Proyectos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=611))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarBancoProyectos(BasePermission):
    message = 'No tiene permiso para actualizar en Banco de Proyectos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=612))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarBancoProyectos(BasePermission):
    message = 'No tiene permiso para consultar en Banco de Proyectos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=613))
            if permisos_modulo_rol:
                return True

        return False

# CONSULTAS GENERALES
class PermisoConsultarConsultasGenerales(BasePermission):
    message = 'No tiene permiso para consultar en Consultas Generales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=614))
            if permisos_modulo_rol:
                return True

        return False

# CONSULTAS PLAN
class PermisoConsultarConsultasPlan(BasePermission):
    message = 'No tiene permiso para consultar en Consultas Plan'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=615))
            if permisos_modulo_rol:
                return True

        return False

# CONSULTAS PAI
class PermisoConsultarConsultaPAI(BasePermission):
    message = 'No tiene permiso para consultar en Consulta PAI'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=616))
            if permisos_modulo_rol:
                return True

        return False

# CONSULTAS POAI
class PermisoConsultarConsultaPOAI(BasePermission):
    message = 'No tiene permiso para consultar en Consulta POAI'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=617))
            if permisos_modulo_rol:
                return True

        return False

# PLAN ANUAL DE ADQUISICIONES
class PermisoCrearPlanAnualAdquisiciones(BasePermission):
    message = 'No tiene permiso para crear en Plan Anual de Adquisiciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=618))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarPlanAnualAdquisiciones(BasePermission):
    message = 'No tiene permiso para actualizar en Plan Anual de Adquisiciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=619))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarPlanAnualAdquisiciones(BasePermission):
    message = 'No tiene permiso para consultar en Plan Anual de Adquisiciones'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=620))
            if permisos_modulo_rol:
                return True

        return False

# DETALLE DE INVERSION CUENTAS
class PermisoCrearDetalleInversionCuentas(BasePermission):
    message = 'No tiene permiso para crear en Detalle de Inversión Cuentas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=621))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarDetalleInversionCuentas(BasePermission):
    message = 'No tiene permiso para actualizar en Detalle de Inversión Cuentas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=622))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarDetalleInversionCuentas(BasePermission):
    message = 'No tiene permiso para consultar en Detalle de Inversión Cuentas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=623))
            if permisos_modulo_rol:
                return True

        return False

# RUBROS
class PermisoCrearRubros(BasePermission):
    message = 'No tiene permiso para crear en Rubros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=624))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarRubros(BasePermission):
    message = 'No tiene permiso para actualizar en Rubros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=625))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarRubros(BasePermission):
    message = 'No tiene permiso para consultar en Rubros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=626))
            if permisos_modulo_rol:
                return True

        return False