from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from transversal.models.personas_models import Personas
from .managers import CustomUserManager
from rest_framework_simplejwt.tokens import RefreshToken
from transversal.choices.paises_choices import paises_CHOICES
from transversal.choices.municipios_choices import municipios_CHOICES
from seguridad.choices.cod_permiso_choices import cod_permiso_CHOICES
from transversal.choices.tipo_persona_choices import tipo_persona_CHOICES
from transversal.choices.sexo_choices import sexo_CHOICES
from transversal.choices.tipo_direccion_choices import tipo_direccion_CHOICES
from seguridad.choices.subsistemas_choices import subsistemas_CHOICES
from seguridad.choices.tipo_usuario_choices import tipo_usuario_CHOICES
from seguridad.choices.opciones_usuario_choices import opciones_usuario_CHOICES
from transversal.choices.cod_naturaleza_empresa_choices import cod_naturaleza_empresa_CHOICES
from transversal.models.organigrama_models import (
    UnidadesOrganizacionales
)

# Modelos proveedores para Persona


# class HistoricoUnidadesOrgPersona(models.Model):
#     id_historico_unidad_persona = models.AutoField(primary_key=True, editable=False, db_column='T020IdHistoUnidad_Persona')
#     id_persona = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T020Id_Persona')
#     id_unidad_organizacional = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T020Id_UnidadOrganizativa')
#     justificacion_cambio = models.CharField(max_length=255, db_column='T020justificacionDelCambio')
#     fecha_inicio = models.DateTimeField(db_column='T020fechaInicio')
#     fecha_final = models.DateTimeField(db_column='T020fechaFinal')

#     def __str__(self):
#         return str(self.id_historico_unidad_persona)

#     class Meta:
#         db_table = 'T020HistoricoUnidadesOrg_Persona'
#         verbose_name = 'Historico Unidad Org Persona'
#         verbose_name_plural = 'Historicos Unidades org Personas'


# Tablas para proveer Usuarios

class OperacionesSobreUsuario(models.Model):
    cod_operacion = models.CharField(max_length=1, primary_key=True, editable=False, db_column='T008CodOperacion')
    nombre = models.CharField(max_length=20, unique=True, db_column='T008nombre')

    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T008OperacionesSobreUsuario'
        verbose_name = 'Operacion sobre usuario'
        verbose_name_plural = 'Operaciones sobre usuario'


class Permisos(models.Model):
    cod_permiso = models.CharField(max_length=2, primary_key=True, choices=cod_permiso_CHOICES, db_column='TzCodPermiso')
    nombre_permiso = models.CharField(max_length=20, unique=True, db_column='Tznombre')

    def __str__(self):
        return str(self.nombre_permiso)

    class Meta:
        db_table = "TzPermisos"
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        
    
class Roles(models.Model):
    id_rol = models.SmallAutoField(primary_key=True, editable=False, db_column='TzIdRol')
    nombre_rol = models.CharField(max_length=100, unique=True, db_column='Tznombre')
    descripcion_rol = models.CharField(max_length=255, db_column='Tzdescripcion')
    Rol_sistema = models.BooleanField(default=False, db_column='TzrolDelSistema')
    
    def __str__(self):
        return str(self.nombre_rol)
    
    class Meta:
        db_table= 'TzRoles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

class EstructuraMenus(models.Model): 
    id_menu = models.SmallAutoField(primary_key=True, editable=False, db_column='TzIdMenu')
    nombre = models.CharField(max_length=50, db_column='Tznombre')
    nivel_jerarquico = models.SmallIntegerField(db_column='TznivelJerarquico')
    id_menu_padre = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, db_column='TzId_MenuPadre')
    orden_por_padre = models.SmallIntegerField(db_column='TzordenPorPadre')
    subsistema = models.CharField(max_length=4, choices=subsistemas_CHOICES, db_column='Tzsubsistema')
    
    def __str__(self):
        return str(self.id_menu)
    
    class Meta:
        db_table= 'TzEstructuraMenus'
        verbose_name = 'Estructura Menus'
        verbose_name_plural = 'Estructura Menus'
        unique_together = ['id_menu_padre', 'nombre']
        
class Modulos(models.Model): 
    id_modulo = models.SmallAutoField(primary_key=True, editable=False, db_column='TzIdModulo')
    nombre_modulo = models.CharField(max_length=70, unique=True, db_column='Tznombre')
    descripcion = models.CharField(max_length=255, db_column='Tzdescripcion')
    subsistema = models.CharField(max_length=4, choices=subsistemas_CHOICES, db_column='Tzsubsistema')
    ruta_formulario = models.CharField(max_length=255, blank=True, null=True, db_column='TzrutaFormulario')
    nombre_icono = models.CharField(max_length=30, blank=True, null=True, db_column='TznombreIcono')
    id_menu = models.ForeignKey(EstructuraMenus, on_delete=models.SET_NULL, null=True, blank=True, db_column='TzId_Menu')
    
    def __str__(self):
        return str(self.nombre_modulo)
    
    class Meta:
        db_table= 'TzModulos'
        verbose_name = 'Modulo'
        verbose_name_plural = 'Modulos'       
    
class PermisosModulo(models.Model):
    id_permisos_modulo= models.SmallAutoField(primary_key=True, db_column='TzIdPermisos_Modulo' )
    id_modulo = models.ForeignKey(Modulos, on_delete=models.CASCADE, db_column='TzId_Modulo')
    cod_permiso = models.ForeignKey(Permisos, on_delete=models.CASCADE, db_column='TzCod_Permiso')
  
    def __str__(self):
        return str(self.id_modulo) + ' ' + str(self.cod_permiso)
    
    class Meta:
        db_table= 'TzPermisos_Modulo'
        verbose_name = 'Permiso de módulo'
        verbose_name_plural = 'Permisos de módulo'
        unique_together = (('id_modulo', 'cod_permiso'),)

class PermisosModuloRol(models.Model):
    id_permiso_modulo_rol = models.SmallAutoField(primary_key=True, db_column='TzIdPermisos_Modulo_Rol')
    id_rol = models.ForeignKey(Roles, on_delete=models.CASCADE, db_column='TzId_Rol')
    id_permiso_modulo = models.ForeignKey(PermisosModulo, on_delete=models.CASCADE, db_column='TzId_Permisos_Modulo')
    
    def __str__(self):
        return str(self.id_rol) + ' ' + str(self.id_permiso_modulo) + ' ' + str(self.id_permiso_modulo_rol)
    
    class Meta:
        db_table= 'TzPermisos_Modulo_Rol'
        verbose_name = 'Permiso de modulo de rol'
        verbose_name_plural = 'Permisos de modulo de roles'
        unique_together = (('id_rol', 'id_permiso_modulo'),)
        
class User(AbstractBaseUser, PermissionsMixin):   
    id_usuario = models.AutoField(primary_key=True, editable=False, db_column='TzIdUsuario')
    nombre_de_usuario = models.CharField(max_length=30, unique=True, db_column='TznombreUsuario')
    persona = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='TzId_Persona')
    password = models.CharField(db_column='Tzcontrasegna', max_length=255)
    is_active = models.BooleanField(default=False, db_column='Tzactivo')
    is_staff = models.BooleanField(default=False, db_column='Tzstaff')#Añadido por Juan
    is_superuser = models.BooleanField(default=False, db_column='TzsuperUser')  #Añadido por Juan
    is_blocked = models.BooleanField(default=False, db_column='Tzbloqueado')
    creado_por_portal = models.BooleanField(default=False, db_column='TzcreadoPorPortal')
    id_usuario_creador = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True ,db_column="TzId_UsuarioCreador")
    created_at = models.DateTimeField(auto_now_add=True, db_column='TzfechaCreacion')
    activated_at = models.DateTimeField(blank=True, null=True, db_column='TzfechaActivacionInicial')
    last_login = models.DateTimeField(blank=True, null=True, db_column='TzfechaUltimoLogin')
    tipo_usuario = models.CharField(max_length=1, default='E', choices=tipo_usuario_CHOICES, db_column='TztipoUsuario')
    profile_img = models.ImageField(null=True, blank=True, default='/placeholder.png', upload_to='seguridad/usuarios/', db_column='TzrutaFoto') #Juan Camilo Text Choices
    # email = models.EmailField(blank=True,null=True db_column='TzemailUsuario') #Añadido por Juan
    
    USERNAME_FIELD = 'nombre_de_usuario'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

    def __str__(self):
        return str(self.nombre_de_usuario)
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        roles = self.usuariosrol_set.all().values_list('id_rol__nombre_rol', flat=True)
        refresh['roles'] = list(roles)
        return{'refresh': str(refresh), 'access': str(refresh.access_token)}
    
    class Meta:
        db_table = 'TzUsuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

# Tablas generadas a partir de User
class UsuarioErroneo(models.Model):
    id_usuario_error = models.AutoField(primary_key=True, editable=False, db_column='TzIdUsuarioError')
    campo_usuario = models.CharField(max_length=30, db_column='TzcampoUsuario')
    dirip = models.GenericIPAddressField(db_column='TzdirIP')
    dispositivo_conexion = models.CharField(max_length=30, db_column='TzdispositivoConexion')
    fecha_login_error = models.DateTimeField(auto_now_add=True, db_column='TzfechaLoginError')

    def __str__(self):
        return str(self.campo_usuario)
    
    class Meta:
        db_table = 'TzUsuarioErroneo'
        verbose_name = 'Usuario Erroneo'
        verbose_name_plural = 'Usuarios Erroneos' 


class Login(models.Model):
    id_login = models.AutoField(primary_key=True, editable=False, db_column='TzIdLogin')
    id_usuario = models.ForeignKey(User, on_delete=models.CASCADE, db_column='TzId_Usuario')
    dirip = models.GenericIPAddressField(db_column='TzdirIP')
    dispositivo_conexion = models.CharField(max_length=30, db_column='TzdispositivoConexion')
    fecha_login = models.DateTimeField(auto_now=True, db_column='TzfechaLogin')
    fecha_hora_cierre_sesion = models.DateTimeField(blank=True, null=True, db_column='TzfechaCierreSesion')
    
    def __str__(self):
        return str(self.id_usuario)
    
    class Meta:
        db_table = 'TzLogin'
        verbose_name = 'Login'
        verbose_name_plural = 'Login'   

    
class LoginErroneo(models.Model):
    id_login_error = models.AutoField(primary_key=True, editable=False, db_column='TzIdLoginError')
    id_usuario = models.OneToOneField(User, on_delete=models.CASCADE, db_column='TzId_Usuario')
    dirip = models.GenericIPAddressField(db_column='TzdirIP')
    dispositivo_conexion = models.CharField(max_length=30, db_column='TzdispositivoConexion')
    fecha_login_error = models.DateTimeField(auto_now=True, db_column='TzfechaLoginError')
    contador = models.SmallIntegerField(db_column='Tzcontador')
    
    def __str__(self):
        return str(self.id_usuario)
    
    class Meta:
        db_table = 'TzLoginErroneo'
        verbose_name = 'Login Erroneo'
        verbose_name_plural = 'Login Erroneo'
        

class UsuariosRol(models.Model):
    id_usuarios_rol = models.AutoField(primary_key=True, editable=False, db_column='TzIdUsuarios_Rol')
    id_rol = models.ForeignKey(Roles, on_delete=models.CASCADE, db_column='TzId_Rol')
    id_usuario = models.ForeignKey(User, on_delete=models.CASCADE, db_column='TzId_Usuario')

    def __str__(self):
        return str(self.id_rol) + ' ' + str(self.id_usuario)

    class Meta:
        db_table = 'TzUsuarios_Rol'
        verbose_name = 'Rol de usuario'
        verbose_name_plural = 'Roles de usuario'
        unique_together = (('id_rol', 'id_usuario'),)

class Auditorias(models.Model):
    id_auditoria = models.AutoField(db_column='TzIdAuditoria', primary_key=True, editable=False)
    id_usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_column='TzId_Usuario') ##No tiene definido tipo de relacion
    id_modulo = models.ForeignKey(Modulos, on_delete=models.CASCADE, db_column='TzId_Modulo')
    subsistema = models.CharField(max_length=4, choices=subsistemas_CHOICES, db_column='Tzsubsistema')
    id_cod_permiso_accion = models.ForeignKey(Permisos, on_delete=models.CASCADE, db_column='TzCod_PermisoAccion')
    fecha_accion = models.DateTimeField(db_column='TzfechaAccion', auto_now=True)
    dirip = models.GenericIPAddressField(db_column='TzdirIp')
    descripcion = models.TextField(db_column='Tzdescripcion')
    valores_actualizados = models.TextField(null=True, blank=True, db_column='TzvaloresActualizados')

    def __str__(self):
        return str(self.descripcion) 
  
    class Meta: 
        db_table ='TzAuditorias'
        verbose_name = 'Auditoría'
        verbose_name_plural = 'Auditorías'
        
     
class HistoricoActivacion(models.Model):
    id_historico = models.AutoField(primary_key=True, editable=False, db_column='T014IdHistorico')
    id_usuario_afectado = models.ForeignKey(User, on_delete=models.CASCADE, db_column='T014Id_UsuarioAfectado')
    cod_operacion = models.ForeignKey(OperacionesSobreUsuario, on_delete=models.CASCADE, db_column='T014Cod_Operacion')
    fecha_operacion = models.DateTimeField(auto_now=True, db_column='T014fechaOperacion')
    justificacion = models.CharField(db_column='T014justificacion', max_length=255)
    usuario_operador = models.ForeignKey(User, related_name='usuarioOperador', on_delete=models.CASCADE, db_column='T014Id_UsuarioOperador')  #Añadido por Juan

    def __str__(self):
        return str(self.cod_operacion)

    class Meta:
        db_table = 'T014HistoricoActivacion'  
        verbose_name = 'Histórico de activación'
        verbose_name_plural = 'Histórico de activaciones'