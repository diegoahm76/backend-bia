from rest_framework.permissions import BasePermission
from seguridad.models import UsuariosRol, PermisosModuloRol
from django.db.models import Q

# MANIPULACIÓN DE TRÁMITES Y SERVICIOS
class PermisoConsultarManipulacionTramitesServicios(BasePermission):
    message = 'No tiene permiso para consultar en Manipulación de trámites y servicios'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=95))
            if permisos_modulo_rol:
                return True
        return False

# TRÁMITES Y SERVICIOS
class PermisoConsultarTramitesServicios(BasePermission):
    message = 'No tiene permiso para consultar en Trámites y servicios'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=100))
            if permisos_modulo_rol:
                return True
        return False

# DETERMINANTES AMBIENTALES
class PermisoConsultarDeterminantesAmbientales(BasePermission):
    message = 'No tiene permiso para consultar en Determinantes ambientales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=628))
            if permisos_modulo_rol:
                return True
        return False

# DETERMINANTES AMBIENTALES PLANES PARCIALES
class PermisoConsultarDeterminantesAmbientalesPlanesParciales(BasePermission):
    message = 'No tiene permiso para consultar en Determinantes ambientales planes parciales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=629))
            if permisos_modulo_rol:
                return True
        return False

# LICENCIAS
class PermisoConsultarLicencias(BasePermission):
    message = 'No tiene permiso para consultar en Licencias'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=630))
            if permisos_modulo_rol:
                return True
        return False

# APROVECHAMIENTO DE PRODUCTOS FORESTALES NO MADERABLES
class PermisoConsultarAprovechamientoProductosForestalesNoMaderables(BasePermission):
    message = 'No tiene permiso para consultar en Aprovechamiento de productos forestales no maderables'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=631))
            if permisos_modulo_rol:
                return True
        return False

# AUTORIZACION PARA APROVECHAMIENTO FORESTAL DE ÁRBOLES DOMÉSTICOS
class PermisoConsultarAutorizacionAprovechamientoForestalArbolesDomesticos(BasePermission):
    message = 'No tiene permiso para consultar en Autorización para aprovechamiento forestal de árboles domésticos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=632))
            if permisos_modulo_rol:
                return True
        return False

# CERTIFICACION AMBIENTAL PARA DESINTEGRACION VEHICULAR
class PermisoConsultarCertificacionAmbientalDesintegracionVehicular(BasePermission):
    message = 'No tiene permiso para consultar en Certificación ambiental para desintegración vehicular'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=633))
            if permisos_modulo_rol:
                return True
        return False

# CERTIFICACION PARA IMPORTAR O EXPORTAR PRODUCTOS FORESTALES
class PermisoConsultarCertificacionImportarExportarProductosForestales(BasePermission):
    message = 'No tiene permiso para consultar en Certificación para importar o exportar productos forestales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=635))
            if permisos_modulo_rol:
                return True
        return False

# CONCESIÓN DE AGUAS SUBTERRANEAS
class PermisoConsultarConcesionAguasSubterraneas(BasePermission):
    message = 'No tiene permiso para consultar en Concesión de aguas subterráneas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=636))
            if permisos_modulo_rol:
                return True
        return False

# CONCESIÓN DE AGUAS SUPERFICIALES Y VERTIMIENTOS
class PermisoConsultarConcesionAguasSuperficialesVertimientos(BasePermission):
    message = 'No tiene permiso para consultar en Concesión de Aguas Superficiales y Vertimientos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=637))
            if permisos_modulo_rol:
                return True
        return False

# PERMISO DE VERTIMIENTOS
class PermisoConsultarPermisoVertimientos(BasePermission):
    message = 'No tiene permiso para consultar en Permiso de vertimientos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=638))
            if permisos_modulo_rol:
                return True
        return False

# INSCRIPCIÓN COMO ACOPIADOR PRIMARIO DE ACEITES LUBRICANTES USADOS
class PermisoConsultarInscripcionAcopiadorPrimarioAceitesLubricantesUsados(BasePermission):
    message = 'No tiene permiso para consultar en Inscripción como acopiador primario de aceites lubricantes usados'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=639))
            if permisos_modulo_rol:
                return True
        return False

# INSCRIPCIÓN COMO GESTOR DE RESIDUOS DE CONSTRUCCIÓN Y DEMOLICIÓN
class PermisoConsultarInscripcionGestorResiduosConstruccionDemolicion(BasePermission):
    message = 'No tiene permiso para consultar en Inscripción como gestor de residuos de construcción y demolición'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=640))
            if permisos_modulo_rol:
                return True
        return False

# MEDIDAS DE MANEJO AMBIENTAL PARA PROYECTOS SISMICOS
class PermisoConsultarMedidasManejoAmbientalProyectosSismicos(BasePermission):
    message = 'No tiene permiso para consultar en Medidas de manejo ambiental para proyectos sísmicos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=641))
            if permisos_modulo_rol:
                return True
        return False

# PERMISO DE EMISIÓN ATMOSFÉRICA PARA FUENTES FIJAS
class PermisoConsultarPermisoEmisionAtmosfericaFuentesFijas(BasePermission):
    message = 'No tiene permiso para consultar en Permiso de emisión atmosférica para fuentes fijas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=642))
            if permisos_modulo_rol:
                return True
        return False

# PERMISO DE OCUPACIÓN DE CAUCE, PLAYA Y LECHOS
class PermisoConsultarPermisoOcupacionCaucePlayaLechos(BasePermission):
    message = 'No tiene permiso para consultar en Permiso de Ocupación de Cauce, Playa y Lechos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=643))
            if permisos_modulo_rol:
                return True
        return False

# PERMISO DE PROSPECCIÓN Y EXPLORACIÓN DE AGUAS SUBTERRANEAS
class PermisoConsultarPermisoProspeccionExploracionAguasSubterraneas(BasePermission):
    message = 'No tiene permiso para consultar en Permiso de prospección y exploración de aguas subterráneas'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=644))
            if permisos_modulo_rol:
                return True
        return False

# PERMISO DE RECOLECCIÓN DE ESPECIMENES DE ESPECIES SILVESTRES
class PermisoConsultarPermisoRecoleccionEspecimenesEspeciesSilvestres(BasePermission):
    message = 'No tiene permiso para consultar en Permiso de recolección de especímenes de especies silvestres'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=645))
            if permisos_modulo_rol:
                return True
        return False

# PERMISO DE VERTIMIENTOS AL SUELO
class PermisoConsultarPermisoVertimientosSuelo(BasePermission):
    message = 'No tiene permiso para consultar en Permiso de vertimientos al suelo'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=646))
            if permisos_modulo_rol:
                return True
        return False

# PERMISO DE APROVECHAMIENTO FORESTAL DE ÁRBOLES AISLADOS
class PermisoConsultarPermisoAprovechamientoForestalArbolesAislados(BasePermission):
    message = 'No tiene permiso para consultar en Permiso para Aprovechamiento Forestal de Árboles Aislados'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=647))
            if permisos_modulo_rol:
                return True
        return False

# PERMISO DE APROVECHAMIENTO FORESTAL DE BOSQUES NATURALES
class PermisoConsultarPermisoAprovechamientoForestalBosquesNaturales(BasePermission):
    message = 'No tiene permiso para consultar en Permiso para el aprovechamiento forestal de bosques naturales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=648))
            if permisos_modulo_rol:
                return True
        return False

# PROYECTOS INDUSTRIALES
class PermisoConsultarProyectosIndustriales(BasePermission):
    message = 'No tiene permiso para consultar en Proyectos industriales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=651))
            if permisos_modulo_rol:
                return True
        return False

# REGISTRO DE LIBRO DE OPERACIONES FORESTALES
class PermisoConsultarRegistroLibroOperacionesForestales(BasePermission):
    message = 'No tiene permiso para consultar en Registro de libro de operaciones forestales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=652))
            if permisos_modulo_rol:
                return True
        return False

# SOLICITUD PARA LA OBTENCIÓN DE PRODUCTOS
class PermisoConsultarSolicitudObtencionProductos(BasePermission):
    message = 'No tiene permiso para consultar en Solicitud para la obtención de productos'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=653))
            if permisos_modulo_rol:
                return True
        return False

# OTROS TRAMITES AMBIENTALES
class PermisoConsultarOtrosTramitesAmbientales(BasePermission):
    message = 'No tiene permiso para consultar en Otros Trámites Ambientales'
    def has_permission(self, request, view):
        id_user = request.user.id_usuario
        user_roles = UsuariosRol.objects.filter(id_usuario=id_user)

        for rol in user_roles:
            permisos_modulo_rol = PermisosModuloRol.objects.filter(Q(id_rol=rol.id_rol) & Q(id_permiso_modulo=660))
            if permisos_modulo_rol:
                return True
        return False