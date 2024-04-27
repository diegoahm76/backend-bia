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

# ENTRADA DE BIENES
class PermisoCrearEntradaAlmacen(BasePermission):
    message = 'No tiene permiso para crear entradas en almacén de bienes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=105))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarEntradaAlmacen(BasePermission):
    message = 'No tiene permiso para consultar entradas en almacén de bienes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=106))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoActualizarEntradaAlmacen(BasePermission):
    message = 'No tiene permiso para actualizar entradas en almacén de bienes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=107))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAnularEntradaAlmacen(BasePermission):
    message = 'No tiene permiso para anular entradas en almacén de bienes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=108))
            if permisos_modulo_rol:
                return True

        return False    

# SOLICITUDES DE CONSUMO
class PermisoCrearSolicitudConsumo(BasePermission):
    message = 'No tiene permiso para crear solicitudes de bienes de consumo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=109))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarSolicitudConsumo(BasePermission):
    message = 'No tiene permiso para consultar solicitudes de bienes de consumo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=110))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoActualizarSolicitudConsumo(BasePermission):
    message = 'No tiene permiso para actualizar solicitudes de bienes de consumo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=111))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAnularSolicitudConsumo(BasePermission):
    message = 'No tiene permiso para anular solicitudes de bienes de consumo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=112))
            if permisos_modulo_rol:
                return True

        return False

# SOLICITUDES DE CONSUMO PARA VIVEROS
class PermisoCrearSolicitudConsumoViveros(BasePermission):
    message = 'No tiene permiso para crear solicitudes de bienes de consumo para viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=113))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarSolicitudConsumoViveros(BasePermission):
    message = 'No tiene permiso para consultar solicitudes de bienes de consumo para viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=114))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoActualizarSolicitudConsumoViveros(BasePermission):
    message = 'No tiene permiso para actualizar solicitudes de bienes de consumo para viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=115))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAnularSolicitudConsumoViveros(BasePermission):
    message = 'No tiene permiso para anular solicitudes de bienes de consumo para viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=116))
            if permisos_modulo_rol:
                return True

        return False

# APROBACIONES DE SOLICITUDES DE BIENES
class PermisoCrearAprobacionSolicitudesBienes(BasePermission):
    message = 'No tiene permiso para crear aprobaciones de solicitudes de bienes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=117))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarAprobacionSolicitudesBienes(BasePermission):
    message = 'No tiene permiso para consultar aprobaciones de solicitudes de bienes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=118))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoActualizarAprobacionSolicitudesBienes(BasePermission):
    message = 'No tiene permiso para actualizar aprobaciones de solicitudes de bienes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=119))
            if permisos_modulo_rol:
                return True

        return False

# APROBACIONES DE SOLICITUDES DE CONSUMO PARA VIVEROS
class PermisoCrearAprobacionSolicitudesConsumoVivero(BasePermission):
    message = 'No tiene permiso para crear aprobaciones de solicitudes de consumo para vivero'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=120))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarAprobacionSolicitudesConsumoVivero(BasePermission):
    message = 'No tiene permiso para consultar aprobaciones de solicitudes de consumo para vivero'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=121))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoActualizarAprobacionSolicitudesConsumoVivero(BasePermission):
    message = 'No tiene permiso para actualizar aprobaciones de solicitudes de consumo para vivero'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=122))
            if permisos_modulo_rol:
                return True

        return False

# RECHAZOS DE SOLICITUDES DE BIENES
class PermisoCrearRechazoSolicitudesBienesAlmacen(BasePermission):
    message = 'No tiene permiso para crear rechazos de solicitudes de bienes desde almacén'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=123))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarRechazoSolicitudesBienesAlmacen(BasePermission):
    message = 'No tiene permiso para consultar rechazos de solicitudes de bienes desde almacén'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=124))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoActualizarRechazoSolicitudesBienesAlmacen(BasePermission):
    message = 'No tiene permiso para actualizar rechazos de solicitudes de bienes desde almacén'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=125))
            if permisos_modulo_rol:
                return True

        return False

# SOLICITUDES DE BIENES PENDIENTES POR DESPACHAR
class PermisoConsultarSolicitudesPendientesDespachar(BasePermission):
    message = 'No tiene permiso para consultar el listado de solicitudes de bienes pendientes por despachar'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=126))
            if permisos_modulo_rol:
                return True

        return False

# DESPACHO DE BIENES DE CONSUMO
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

# ENTREGA DONACIONES RESARCIMIENTOS
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

# CIERRE SOLICITUDES BIENES NO DISPONIBILIDAD
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

# VEHICULOS ARRENDADOS
class PermisoCrearVehiculosArrendados(BasePermission):
    message = 'No tiene permiso para crear vehículos arrendados'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=300))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarVehiculosArrendados(BasePermission):
    message = 'No tiene permiso para actualizar vehículos arrendados'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=301))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoConsultarVehiculosArrendados(BasePermission):
    message = 'No tiene permiso para consultar vehículos arrendados'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=302))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarVehiculosArrendados(BasePermission):
    message = 'No tiene permiso para borrar vehículos arrendados'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=303))
            if permisos_modulo_rol:
                return True

        return False

# CONTROL DE INVENTARIO DE ALMACEN
class PermisoConsultarControlInventarioAlmacen(BasePermission):
    message = 'No tiene permiso para consultar el control de inventario de almacén'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=424))
            if permisos_modulo_rol:
                return True

        return False

# TABLERO DE CONTROL DE ALMACEN
class PermisoConsultarTableroControlAlmacen(BasePermission):
    message = 'No tiene permiso para consultar el tablero de control de almacén'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=425))
            if permisos_modulo_rol:
                return True

        return False

# CENTRAL DE REPORTES
class PermisoConsultarCentralReportes(BasePermission):
    message = 'No tiene permiso para consultar la central de reportes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=426))
            if permisos_modulo_rol:
                return True

        return False

# SOLICITUDES DE VIAJES
class PermisoCrearSolicitudesViajes(BasePermission):
    message = 'No tiene permiso para crear solicitudes de viajes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=684))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarSolicitudesViajes(BasePermission):
    message = 'No tiene permiso para actualizar solicitudes de viajes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=685))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoConsultarSolicitudesViajes(BasePermission):
    message = 'No tiene permiso para consultar solicitudes de viajes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=686))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarSolicitudesViajes(BasePermission):
    message = 'No tiene permiso para borrar solicitudes de viajes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=687))
            if permisos_modulo_rol:
                return True

        return False

# ASIGNACIONES DE VEHICULOS
class PermisoCrearAsignacionVehiculo(BasePermission):
    message = 'No tiene permiso para crear asignaciones de vehículo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=688))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarAsignacionVehiculo(BasePermission):
    message = 'No tiene permiso para consultar asignaciones de vehículo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=689))
            if permisos_modulo_rol:
                return True

        return False

# INSPECCIONES DE VEHICULOS
class PermisoCrearInspeccionVehiculos(BasePermission):
    message = 'No tiene permiso para crear inspecciones de vehículos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=690))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarInspeccionVehiculos(BasePermission):
    message = 'No tiene permiso para actualizar inspecciones de vehículos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=691))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarInspeccionVehiculos(BasePermission):
    message = 'No tiene permiso para consultar inspecciones de vehículos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=692))
            if permisos_modulo_rol:
                return True

        return False

# AGENDAMIENTOS DE VEHICULOS
class PermisoCrearAgendamientoVehiculos(BasePermission):
    message = 'No tiene permiso para crear agendamientos de vehículos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=693))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarAgendamientoVehiculos(BasePermission):
    message = 'No tiene permiso para actualizar agendamientos de vehículos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=694))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoConsultarAgendamientoVehiculos(BasePermission):
    message = 'No tiene permiso para consultar agendamientos de vehículos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=695))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarAgendamientoVehiculos(BasePermission):
    message = 'No tiene permiso para borrar agendamientos de vehículos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=696))
            if permisos_modulo_rol:
                return True

        return False

# BITACORAS DE VIAJES
class PermisoCrearBitacoraViajes(BasePermission):
    message = 'No tiene permiso para crear bitácoras de viajes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=697))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarBitacoraViajes(BasePermission):
    message = 'No tiene permiso para consultar bitácoras de viajes'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=698))
            if permisos_modulo_rol:
                return True

        return False

# REVISIONES DE INSPECCIONES DE VEHICULOS
class PermisoCrearRevisionInspeccionVehiculos(BasePermission):
    message = 'No tiene permiso para crear revisiones de inspecciones de vehículos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=714))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarRevisionInspeccionVehiculos(BasePermission):
    message = 'No tiene permiso para consultar revisiones de inspecciones de vehículos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=715))
            if permisos_modulo_rol:
                return True

        return False
