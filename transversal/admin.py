from django.contrib import admin

# Register your models here.
from transversal.models.base_models import (
    ApoderadoPersona,
    Cargos,
    ClasesTercero,
    ClasesTerceroPersona,
    HistoricoDireccion,
    HistoricoEmails,
    Municipio,
    Departamento,
    Paises,
    EstadoCivil,
    Shortener,
    TipoDocumento
)
from transversal.models.personas_models import Personas

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cod_municipio',)
    list_display_links = list_display
    search_fields = (
        'nombre',
    )
    
@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cod_departamento',)
    list_display_links = list_display
    search_fields = (
        'nombre',
    )
    
@admin.register(Paises)
class PaisesAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cod_pais',)
    list_display_links = list_display
    search_fields = (
        'nombre',
    )
    
@admin.register(EstadoCivil)
class EstadoCivilAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cod_estado_civil', 'precargado')
    list_display_links = list_display
    search_fields = (
        'nombre',
        'cod_estado_civil',
    )

@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('cod_tipo_documento','nombre', 'precargado')
    list_display_links = list_display
    search_fields = (
        'nombre',
    )

@admin.register(Cargos)
class CargosAdmin(admin.ModelAdmin):
    list_display = ('id_cargo','nombre',)
    list_display_links = list_display

@admin.register(ClasesTercero)
class ClasesTerceroAdmin(admin.ModelAdmin):
    list_display = ('id_clase_tercero','nombre', )
    list_display_links = list_display
    search_fields = (
        'nombre',
    )

@admin.register(Personas)
class PersonasAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'email', 'sexo', 'tipo_persona', 'municipio_residencia')
    list_display_links = list_display
    search_fields = (
        'numero_documento', 
        'email', 
        'sexo', 
        'tipo_persona',
    )
    list_filter = (
        'tipo_persona', 
        'estado_civil', 
        'sexo',
    )

@admin.register(ClasesTerceroPersona)
class ClasesTerceroPersonaAdmin(admin.ModelAdmin):
    list_display = ('id_persona','id_clase_tercero',)
    list_display_links = list_display
    search_fields = (
        'id_persona',
        'id_clase_tercero',
    )

    
@admin.register(ApoderadoPersona)
class ApoderadoPersonaAdmin(admin.ModelAdmin):
    list_display = ('id_proceso','persona_poderdante','persona_apoderada', 'fecha_inicio',)
    list_display_links = list_display
    search_fields = (
        'id_proceso',
        'persona_poderdante',
        'persona_apoderada',
    )
    list_filter = ('fecha_inicio',)
   
@admin.register(HistoricoDireccion)
class HistoricoDireccionAdmin(admin.ModelAdmin):
    list_display = ('id_persona','direccion','tipo_direccion','fecha_cambio',)
    list_display_links = list_display
    search_fields = (
        'direccion',
        'id_persona'
    )
    filter_fields = (
        'tipo_direccion',
    )
    list_filter = (
        'tipo_direccion',
    )

@admin.register(HistoricoEmails)
class HistoricoEmailsAdmin(admin.ModelAdmin):
    list_display = ('id_persona','email_notificacion','fecha_cambio',)
    list_display_links = list_display
    search_fields = (
        'id_persona',
        'cod_pais_exterior',
    )
    
@admin.register(Shortener)
class ShortenerAdmin(admin.ModelAdmin):
    list_display = ('long_url','short_url',)
    list_display_links = list_display