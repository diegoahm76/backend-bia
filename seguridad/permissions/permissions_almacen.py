from seguridad.choices.tipo_usuario_choices import tipo_usuario_CHOICES 
from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q


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


