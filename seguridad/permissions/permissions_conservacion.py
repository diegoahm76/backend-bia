from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q

class PermisoCrearAdministrarViveros(BasePermission):
    message = 'No tiene permiso para crear viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=127))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarAdministrarViveros(BasePermission):
    message = 'No tiene permiso para consultar viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=128))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoActualizarAdministrarViveros(BasePermission):
    message = 'No tiene permiso para actualizar viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=129))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoBorrarAdministrarViveros(BasePermission):
    message = 'No tiene permiso para borrar viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=130))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoIngresoRetiroCuarentena(BasePermission):
    message = 'No tiene permiso para ingresar o retirar viveros de cuarentena'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=131))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAperturaCierreVivero(BasePermission):
    message = 'No tiene permiso para abrir o cerrar viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=132))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoConsultarTipificaciónBienesConsumoViveros(BasePermission):
    message = 'No tiene permiso para consultar la tipificación de los bienes de consumo utilizables en viveros para la producción'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=133))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarTipificaciónBienesConsumoViveros(BasePermission):
    message = 'No tiene permiso para actualizar la tipificación de los bienes de consumo utilizables en viveros para la producción'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=134))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearRecepciónDistribuciónDespachosEntrantesVivero(BasePermission):
    message = 'No tiene permiso para distribuir las entradas de bienes de consumo de viveros en los diferentes viveros de la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=146))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarRecepciónDistribuciónDespachosEntrantesVivero(BasePermission):
    message = 'No tiene permiso para consultar las entradas de bienes de consumo de viveros en los diferentes viveros de la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=147))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarRecepciónDistribuciónDespachosEntrantesVivero(BasePermission):
    message = 'No tiene permiso para actualizar las entradas de bienes de consumo de viveros en los diferentes viveros de la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=148))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarRecepciónDistribuciónDespachosEntrantesVivero(BasePermission):
    message = 'No tiene permiso para borrar las entradas de bienes de consumo de viveros en los diferentes viveros de la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=149))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearAdministraciónCamasGerminación(BasePermission):
    message = 'No tiene permiso para crear la administración de las camas de germinación para los diferntes viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=150))
            if permisos_modulo_rol:
                return True

        return False
    
class PermisoConsultarAdministraciónCamasGerminación(BasePermission):
    message = 'No tiene permiso para consultar la administración de las camas de germinación para los diferntes viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=151))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarAdministraciónCamasGerminación(BasePermission):
    message = 'No tiene permiso para actualizar la administración de las camas de germinación para los diferntes viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=152))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarAdministraciónCamasGerminación(BasePermission):
    message = 'No tiene permiso para borrar la administración de las camas de germinación para los diferntes viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=153))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearSiembraSemillas(BasePermission):
    message = 'No tiene permiso para crear y administrar las siembras de semillas de material vegetal realizadas en los diferentes viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=154))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarSiembraSemillas(BasePermission):
    message = 'No tiene permiso para consultar las siembras de semillas de material vegetal realizadas en los diferentes viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=155))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarSiembraSemillas(BasePermission):
    message = 'No tiene permiso para actualizar las siembras de semillas de material vegetal realizadas en los diferentes viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=156))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarSiembraSemillas(BasePermission):
    message = 'No tiene permiso para borrar las siembras de semillas de material vegetal realizadas en los diferentes viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=157))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearCambioEtapaMaterialVegetal(BasePermission):
    message = 'No tiene permiso para crear el cambio de etapa de unidades de material vegetal de un lote específico'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=158))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarCambioEtapaMaterialVegetal(BasePermission):
    message = 'No tiene permiso para consultar el cambio de etapa de unidades de material vegetal de un lote específico'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=159))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarCambioEtapaMaterialVegetal(BasePermission):
    message = 'No tiene permiso para actualizar el cambio de etapa de unidades de material vegetal de un lote específico'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=160))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAnularCambioEtapaMaterialVegetal(BasePermission):
    message = 'No tiene permiso para anular el cambio de etapa de unidades de material vegetal de un lote específico'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=161))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearTrasladosEntreViveros(BasePermission):
    message = 'No tiene permiso para crear los traslados de bienes entre viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=162))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarTrasladosEntreViveros(BasePermission):
    message = 'No tiene permiso para borrar los traslados de bienes entre viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=163))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarTrasladosEntreViveros(BasePermission):
    message = 'No tiene permiso para actualizar los traslados de bienes entre viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=164))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAnularTrasladosEntreViveros(BasePermission):
    message = 'No tiene permiso para anular los traslados de bienes entre viveros'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=165))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearIngresoCuarentenaMaterialVegetal(BasePermission):
    message = 'No tiene permiso para crear el ingreso de plantas y plántulas de un lote de un vivero a cuarentena'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=166))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarIngresoCuarentenaMaterialVegetal(BasePermission):
    message = 'No tiene permiso para consultar el ingreso de plantas y plántulas de un lote de un vivero a cuarentena'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=167))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarIngresoCuarentenaMaterialVegetal(BasePermission):
    message = 'No tiene permiso para actualizar el ingreso de plantas y plántulas de un lote de un vivero a cuarentena'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=168))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAnularIngresoCuarentenaMaterialVegetal(BasePermission):
    message = 'No tiene permiso para anular el ingreso de plantas y plántulas de un lote de un vivero a cuarentena'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=169))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearLevantamientoCuarentenaMaterialVegetal(BasePermission):
    message = 'No tiene permiso para crear el levantamiento de plantas y plántulas de un lote de un vivero en cuarentena'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=170))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarLevantamientoCuarentenaMaterialVegetal(BasePermission):
    message = 'No tiene permiso para consultar el levantamiento de plantas y plántulas de un lote de un vivero en cuarentena'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=171))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarLevantamientoCuarentenaMaterialVegetal(BasePermission):
    message = 'No tiene permiso para actualizar el levantamiento de plantas y plántulas de un lote de un vivero en cuarentena'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=172))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAnularLevantamientoCuarentenaMaterialVegetal(BasePermission):
    message = 'No tiene permiso para anular el levantamiento de plantas y plántulas de un lote de un vivero en cuarentena'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=173))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearBajasHerramientasInsumosSemillas(BasePermission):
    message = 'No tiene permiso para crear la baja de elementos del tipo Herramientas, Insumos y Semillas del inventario'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=174))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarBajasHerramientasInsumosSemillas(BasePermission):
    message = 'No tiene permiso para consultar la baja de elementos del tipo Herramientas, Insumos y Semillas del inventario'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=175))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarBajasHerramientasInsumosSemillas(BasePermission):
    message = 'No tiene permiso para actualizar la baja de elementos del tipo Herramientas, Insumos y Semillas del inventario'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=176))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAnularBajasHerramientasInsumosSemillas(BasePermission):
    message = 'No tiene permiso para anular la baja de elementos del tipo Herramientas, Insumos y Semillas del inventario'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=177))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearMortalidadPlantasPlántulas(BasePermission):
    message = 'No tiene permiso para crear el registro de la mortalidad de plantas y plántulas de un vivero'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=178))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarMortalidadPlantasPlántulas(BasePermission):
    message = 'No tiene permiso para consultar el registro de la mortalidad de plantas y plántulas de un vivero'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=179))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarMortalidadPlantasPlántulas(BasePermission):
    message = 'No tiene permiso para actualizar el registro de la mortalidad de plantas y plántulas de un vivero'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=180))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAnularMortalidadPlantasPlántulas(BasePermission):
    message = 'No tiene permiso para anular el registro de la mortalidad de plantas y plántulas de un vivero'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=181))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearMezclas(BasePermission):
    message = 'No tiene permiso para crear los nombres de las mezclas en el sistema'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=182))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarMezclas(BasePermission):
    message = 'No tiene permiso para consultar los nombres de las mezclas en el sistema'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=183))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarMezclas(BasePermission):
    message = 'No tiene permiso para actualizar los nombres de las mezclas en el sistema'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=184))
            if permisos_modulo_rol:
                return True

        return False

class PermisoBorrarMezclas(BasePermission):
    message = 'No tiene permiso para borrar los nombres de las mezclas en el sistema'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=185))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearPreparacionMezclas(BasePermission):
    message = 'No tiene permiso para crear el registro de la preparación de mezclas a utilizar en un vivero'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=186))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarPreparacionMezclas(BasePermission):
    message = 'No tiene permiso para crear el registro de la preparación de mezclas a utilizar en un vivero'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=187))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarPreparacionMezclas(BasePermission):
    message = 'No tiene permiso para actualizar el registro de la preparación de mezclas a utilizar en un vivero'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=188))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAnularPreparacionMezclas(BasePermission):
    message = 'No tiene permiso para anular el registro de la preparación de mezclas a utilizar en un vivero'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=189))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearRegistroIncidenciasMaterialVegetal(BasePermission):
    message = 'No tiene permiso para crear el registro de las incidencias que se realicen o presenten sobre un lote de material vegetal de un vivero'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=190))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarRegistroIncidenciasMaterialVegetal(BasePermission):
    message = 'No tiene permiso para consultar el registro de las incidencias que se realicen o presenten sobre un lote de material vegetal de un vivero'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=191))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarRegistroIncidenciasMaterialVegetal(BasePermission):
    message = 'No tiene permiso para actualizar el registro de las incidencias que se realicen o presenten sobre un lote de material vegetal de un vivero'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=192))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAnularRegistroIncidenciasMaterialVegetal(BasePermission):
    message = 'No tiene permiso para anular el registro de las incidencias que se realicen o presenten sobre un lote de material vegetal de un vivero'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=193))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearSolicitudesPlantasInsumosViveros(BasePermission):
    message = 'No tiene permiso para crear el registro de las solicitudes de Plantas e Insumos de un Vivero determinado'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=194))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarSolicitudesPlantasInsumosViveros(BasePermission):
    message = 'No tiene permiso para consultar el registro de las solicitudes de Plantas e Insumos de un Vivero determinado'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=195))
            if permisos_modulo_rol:
                return True

        return False

class PermisoActualizarSolicitudesPlantasInsumosViveros(BasePermission):
    message = 'No tiene permiso para actualizar el registro de las solicitudes de Plantas e Insumos de un Vivero determinado'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=196))
            if permisos_modulo_rol:
                return True

        return False

class PermisoAnularSolicitudesPlantasInsumosViveros(BasePermission):
    message = 'No tiene permiso para anular el registro de las solicitudes de Plantas e Insumos de un Vivero determinado'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=197))
            if permisos_modulo_rol:
                return True

        return False

class PermisoCrearResponsablesViveros(BasePermission):
    message = 'No tiene permiso para crear la configuracion de los responsables de cada vivero en la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=217))
            if permisos_modulo_rol:
                return True

        return False

class PermisoConsultarResponsablesViveros(BasePermission):
    message = 'No tiene permiso para consultar la configuracion de los responsables de cada vivero en la entidad'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=218))
            if permisos_modulo_rol:
                return True

        return False
