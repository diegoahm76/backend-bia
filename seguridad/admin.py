from django.contrib import admin
from .models import (
    User,
    HistoricoActivacion,
    OperacionesSobreUsuario,
    Permisos,
    Modulos, 
    PermisosModuloRol,
    UsuariosRol,
    Roles,
    PermisosModulo,
    Auditorias,
    Login,
    LoginErroneo
)
    
    
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('persona', 'nombre_de_usuario', 'id_usuario_creador', 'tipo_usuario', 'created_at', 'is_active',)
    list_display_links = list_display
    search_fields = (
        'nombre_de_usuario',
    )
    list_filter = (
        'is_active',
        'is_blocked',
        'is_superuser',
        'tipo_usuario',
    )
    
    
@admin.register(HistoricoActivacion)
class HistoricoActivacionAdmin(admin.ModelAdmin):
    list_display = ('id_usuario_afectado','cod_operacion', 'usuario_operador', 'justificacion',)
    list_display_links = list_display
    search_fields = (
        'justificacion',
    )
    list_filter = (
        'cod_operacion',
    )   


@admin.register(OperacionesSobreUsuario)
class OperacionesSobreUsuarioAdmin(admin.ModelAdmin):
    list_display = ('cod_operacion','nombre',)
    list_display_links = list_display
    search_fields = (
        'nombre',
    )
    
    
@admin.register(Permisos)
class PermisosAdmin(admin.ModelAdmin):
    list_display = ('nombre_permiso','cod_permiso',)
    list_display_links = list_display
    search_fields = (
        'nombre_permiso',
    )
    
    
@admin.register(Modulos)
class ModulosAdmin(admin.ModelAdmin):
    list_display = ('nombre_modulo','subsistema', 'descripcion',)
    list_display_links = list_display
    search_fields = (
        'nombre_modulo',
        'descripcion'
    )
    list_filter = (
        'subsistema',
    )
    

@admin.register(PermisosModulo)
class PermisosModuloAdmin(admin.ModelAdmin):
    list_display = ('id_modulo','cod_permiso',)
    list_display_links = list_display


@admin.register(PermisosModuloRol)
class PermisosModuloRolAdmin(admin.ModelAdmin):
    list_display = ('id_rol','id_permiso_modulo_rol','id_permiso_modulo')
    list_display_links = list_display


@admin.register(UsuariosRol)
class UsuariosRolAdmin(admin.ModelAdmin):
    list_display = ('id_rol','id_usuario',)
    list_display_links = list_display
    
    
@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    list_display = ('id_rol','nombre_rol', 'descripcion_rol',)
    list_display_links = list_display
    search_fields = (
        'nombre_rol',
        'descripcion_rol',
    )


@admin.register(Auditorias)
class AuditoriasAdmin(admin.ModelAdmin):
    list_display = ('id_usuario','id_modulo', 'id_cod_permiso_accion', 'subsistema', 'descripcion',)
    list_display_links = list_display
    search_fields = (
        'dirip',
        'descripcion',
        'valores_actualizados',
    )
    filter_fields = (
        'fecha_accion',
        'subsistema',
    )
    

@admin.register(Login)
class LoginAdmin(admin.ModelAdmin):
    list_display = ('id_usuario','dirip', 'dispositivo_conexion', 'fecha_login',)
    list_display_links = list_display
    search_fields = (
        'dirip',
        'disposito_conexion',
    )
    
    
@admin.register(LoginErroneo)
class LoginErroneoAdmin(admin.ModelAdmin):
    list_display = ('id_usuario','dirip', 'dispositivo_conexion', 'contador',)
    list_display_links = list_display