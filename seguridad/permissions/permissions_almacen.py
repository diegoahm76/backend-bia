from seguridad.choices.tipo_usuario_choices import tipo_usuario_CHOICES 
from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q

# MARCAS
class PermisoCrearMarcas(BasePermission):
    message = 'No tiene permiso para crear marcas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=25))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarMarcas(BasePermission):
    message = 'No tiene permiso para actualizar marcas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=26))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoConsultarMarcas(BasePermission):
    message = 'No tiene permiso para consultar marcas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=27))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoBorrarMarcas(BasePermission):
    message = 'No tiene permiso para borrar marcas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=28))
            if permisos_modulo_rol:
                return True

        return False

# BODEGAS
class PermisoCrearBodegas(BasePermission):
    message = 'No tiene permiso para crear bodegas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=29))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarBodegas(BasePermission):
    message = 'No tiene permiso para actualizar bodegas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=30))
            if permisos_modulo_rol:
                return True

        return False
class PermisoConsultarBodegas(BasePermission):
    message = 'No tiene permiso para consultar bodegas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=31))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoBorrarBodegas(BasePermission):
    message = 'No tiene permiso para borrar bodegas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=32))
            if permisos_modulo_rol:
                return True

        return False

# PORCENTAJES IVA
class PermisoCrearPorcentajeIva(BasePermission):
    message = 'No tiene permiso para crear porcentajes IVA'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=33))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarPorcentajeIva(BasePermission):
    message = 'No tiene permiso para actualizar porcentajes IVA'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=34))
            if permisos_modulo_rol:
                return True

        return False
class PermisoConsultarPorcentajeIva(BasePermission):
    message = 'No tiene permiso para consultar porcentajes IVA'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=35))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoBorrarPorcentajeIva(BasePermission):
    message = 'No tiene permiso para borrar porcentajes IVA'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=36))
            if permisos_modulo_rol:
                return True
        return False
    
# UNIDADES MEDIDA
class PermisoCrearUnidadesMedida(BasePermission):
    message = 'No tiene permiso para crear unidades de medida'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=37))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarUnidadesMedida(BasePermission):
    message = 'No tiene permiso para actualizar unidades de medida'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=38))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoConsultarUnidadesMedida(BasePermission):
    message = 'No tiene permiso para consultar unidades de medida'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=39))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoBorrarUnidadesMedida(BasePermission):
    message = 'No tiene permiso para borrar unidades de medida'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=40))
            if permisos_modulo_rol:
                return True
        return False

# HOJA DE VIDA COMPUTADORES
class PermisoConsultarHojasVidaComputadores(BasePermission):
    message = 'No tiene permiso para consultar hojas de vida de computadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=50))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarHojasVidaComputadores(BasePermission):
    message = 'No tiene permiso para actualizar hojas de vida de computadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=51))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoBorrarHojasVidaComputadores(BasePermission):
    message = 'No tiene permiso para borrar hojas de vida de computadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=52))
            if permisos_modulo_rol:
                return True
        return False

# HOJA DE VIDA VEHICULOS
class PermisoConsultarHojasVidaVehiculos(BasePermission):
    message = 'No tiene permiso para consultar hojas de vida de vehiculos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=53))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarHojasVidaVehiculos(BasePermission):
    message = 'No tiene permiso para actualizar hojas de vida de vehiculos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=54))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoBorrarHojasVidaVehiculos(BasePermission):
    message = 'No tiene permiso para borrar hojas de vida de vehiculos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=55))
            if permisos_modulo_rol:
                return True
        return False

# HOJA DE VIDA OTROS ACTIVOS
class PermisoConsultarHojasVidaOtrosActivos(BasePermission):
    message = 'No tiene permiso para consultar hojas de vida de otros activos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=56))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarHojasVidaOtrosActivos(BasePermission):
    message = 'No tiene permiso para actualizar hojas de vida de otros activos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=57))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoBorrarHojasVidaOtrosActivos(BasePermission):
    message = 'No tiene permiso para borrar hojas de vida de otros activos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=58))
            if permisos_modulo_rol:
                return True
        return False

# PROGRAMACION MANTENIMIENTO COMPUTADORES
class PermisoConsultarProgramacionMantenimientoComputadores(BasePermission):
    message = 'No tiene permiso para consultar programaciones de mantenimientos de computadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=59))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarProgramacionMantenimientoComputadores(BasePermission):
    message = 'No tiene permiso para actualizar programaciones de mantenimientos de computadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=60))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearProgramacionMantenimientoComputadores(BasePermission):
    message = 'No tiene permiso para crear programaciones de mantenimientos de computadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=61))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoAnularProgramacionMantenimientoComputadores(BasePermission):
    message = 'No tiene permiso para anular programaciones de mantenimientos de computadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=62))
            if permisos_modulo_rol:
                return True
        return False

# PROGRAMACION MANTENIMIENTO VEHICULOS
class PermisoConsultarProgramacionMantenimientoVehiculos(BasePermission):
    message = 'No tiene permiso para consultar programaciones de mantenimientos de vehiculos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=63))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarProgramacionMantenimientoVehiculos(BasePermission):
    message = 'No tiene permiso para actualizar programaciones de mantenimientos de vehiculos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=64))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearProgramacionMantenimientoVehiculos(BasePermission):
    message = 'No tiene permiso para crear programaciones de mantenimientos de vehiculos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=65))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoAnularProgramacionMantenimientoVehiculos(BasePermission):
    message = 'No tiene permiso para anular programaciones de mantenimientos de vehiculos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=66))
            if permisos_modulo_rol:
                return True
        return False

# PROGRAMACION MANTENIMIENTO OTROS ACTIVOS
class PermisoConsultarProgramacionMantenimientoOtrosActivos(BasePermission):
    message = 'No tiene permiso para consultar programaciones de mantenimientos de otros activos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=67))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarProgramacionMantenimientoOtrosActivos(BasePermission):
    message = 'No tiene permiso para actualizar programaciones de mantenimientos de otros activos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=68))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearProgramacionMantenimientoOtrosActivos(BasePermission):
    message = 'No tiene permiso para crear programaciones de mantenimientos de otros activos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=69))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoAnularProgramacionMantenimientoOtrosActivos(BasePermission):
    message = 'No tiene permiso para anular programaciones de mantenimientos de otros activos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=70))
            if permisos_modulo_rol:
                return True
        return False

# EJECUCION MANTENIMIENTO COMPUTADORES
class PermisoCrearEjecucionMantenimientoComputadores(BasePermission):
    message = 'No tiene permiso para crear ejecuciones de mantenimientos de computadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=71))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarEjecucionMantenimientoComputadores(BasePermission):
    message = 'No tiene permiso para actualizar ejecuciones de mantenimientos de computadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=72))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoBorrarEjecucionMantenimientoComputadores(BasePermission):
    message = 'No tiene permiso para borrar ejecuciones de mantenimientos de computadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=73))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarEjecucionMantenimientoComputadores(BasePermission):
    message = 'No tiene permiso para consultar ejecuciones de mantenimientos de computadores'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=74))
            if permisos_modulo_rol:
                return True

        return False

# EJECUCION MANTENIMIENTO VEHICULOS
class PermisoCrearEjecucionMantenimientoVehiculos(BasePermission):
    message = 'No tiene permiso para crear ejecuciones de mantenimientos de vehiculos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=75))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarEjecucionMantenimientoVehiculos(BasePermission):
    message = 'No tiene permiso para actualizar ejecuciones de mantenimientos de vehiculos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=76))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoBorrarEjecucionMantenimientoVehiculos(BasePermission):
    message = 'No tiene permiso para borrar ejecuciones de mantenimientos de vehiculos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=77))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarEjecucionMantenimientoVehiculos(BasePermission):
    message = 'No tiene permiso para consultar ejecuciones de mantenimientos de vehiculos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=78))
            if permisos_modulo_rol:
                return True

        return False

# EJECUCION MANTENIMIENTO OTROS ACTIVOS
class PermisoCrearEjecucionMantenimientoOtrosActivos(BasePermission):
    message = 'No tiene permiso para crear ejecuciones de mantenimientos de otros activos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=79))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarEjecucionMantenimientoOtrosActivos(BasePermission):
    message = 'No tiene permiso para actualizar ejecuciones de mantenimientos de otros activos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=80))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoBorrarEjecucionMantenimientoOtrosActivos(BasePermission):
    message = 'No tiene permiso para borrar ejecuciones de mantenimientos de otros activos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=81))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarEjecucionMantenimientoOtrosActivos(BasePermission):
    message = 'No tiene permiso para consultar ejecuciones de mantenimientos de otros activos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=82))
            if permisos_modulo_rol:
                return True

        return False

# CATALOGO BIENES
class PermisoCrearCatalogoBienes(BasePermission):
    message = 'No tiene permiso para crear en catalogo de bienes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=101))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarCatalogoBienes(BasePermission):
    message = 'No tiene permiso para actualizar en catalogo de bienes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=102))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoBorrarCatalogoBienes(BasePermission):
    message = 'No tiene permiso para borrar en catalogo de bienes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=103))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarCatalogoBienes(BasePermission):
    message = 'No tiene permiso para consultar en catalogo de bienes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=104))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearDespachoBienesConsumo(BasePermission):
    message = 'Almacén no puede crear los bienes de consumo de la entidad para su despacho'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=135))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarDespachoBienesConsumo(BasePermission):
    message = 'Almacén no puede consultar los bienes de consumo de la entidad para su despacho'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=136))
            if permisos_modulo_rol:
                return True
        return False
    
class PermisoActualizarDespachoBienesConsumo(BasePermission):
    message = 'Almacén no puede actualizar los bienes de consumo de la entidad para su despacho'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=137))
            if permisos_modulo_rol:
                return True
        return False

class PermisoAnularDespachoBienesConsumo(BasePermission):
    message = 'Almacén no puede anular los bienes de consumo de la entidad para su despacho'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=138))
            if permisos_modulo_rol:
                return True
        return False

class PermisoCrearEntregaDonacionesResarcimientosCompensacionesViveros(BasePermission):
    message = 'No se puede crear la entrega de los bienes de consumo de viveros que ingresaron mediante una Donación, Resarcimiento o Compensación'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=139))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarEntregaDonacionesResarcimientosCompensacionesViveros(BasePermission):
    message = 'No se puede consultar la entrega de los bienes de consumo de viveros que ingresaron mediante una Donación, Resarcimiento o Compensación'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=140))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarEntregaDonacionesResarcimientosCompensacionesViveros(BasePermission):
    message = 'No se puede actualizar la entrega de los bienes de consumo de viveros que ingresaron mediante una Donación, Resarcimiento o Compensación'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=141))
            if permisos_modulo_rol:
                return True
        return False

class PermisoAnularEntregaDonacionesResarcimientosCompensacionesViveros(BasePermission):
    message = 'No se puede anular la entrega de los bienes de consumo de viveros que ingresaron mediante una Donación, Resarcimiento o Compensación'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=142))
            if permisos_modulo_rol:
                return True
        return False

class PermisoCrearCierreSolicitudesBienesNoDisponibilidad(BasePermission):
    message = 'No se puede crear el cierre por parte de Almacén una solicitud de bienes por no tener disponibilidad de ninguno de los items solicitados'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=143))
            if permisos_modulo_rol:
                return True
        return False

class PermisoConsultarCierreSolicitudesBienesNoDisponibilidad(BasePermission):
    message = 'No se puede consultar el cierre por parte de Almacén una solicitud de bienes por no tener disponibilidad de ninguno de los items solicitados'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=144))
            if permisos_modulo_rol:
                return True
        return False

class PermisoActualizarCierreSolicitudesBienesNoDisponibilidad(BasePermission):
    message = 'No se puede actualizar el cierre por parte de Almacén una solicitud de bienes por no tener disponibilidad de ninguno de los items solicitados'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=145))
            if permisos_modulo_rol:
                return True
        return False


