from django.db import models
from seguridad.choices.municipios_choices import municipios_CHOICES
from conservacion.choices.tipo_vivero_choices import tipo_vivero_CHOICES
from conservacion.choices.origen_recursos_vivero_choices import origen_recursos_vivero_CHOICES
from seguridad.models import (
    Personas,
)
class Vivero(models.Model):
    id_vivero = models.AutoField(primary_key=True, editable=False, db_column='T150IdVivero')
    nombre = models.CharField(max_length=30, unique=True, db_column='T150nombre')
    cod_municipio = models.CharField(max_length=5, choices=municipios_CHOICES, db_column='T150Cod_Municipio')
    direccion = models.CharField(max_length=255, db_column='T150direccion')
    area_mt2 = models.PositiveIntegerField(db_column='T150areaMt2')
    area_propagacion_mt2 = models.PositiveIntegerField(db_column='T150areaPropagacionMt2')
    tiene_area_produccion = models.BooleanField(default=False, db_column='T150tieneAreaProduccion')
    tiene_areas_pep_sustrato = models.BooleanField(default=False, db_column='T150tieneAreasPrepSustrato')
    tiene_area_embolsado = models.BooleanField(default=False, db_column='T150tieneAreaEmbolsado')
    cod_tipo_vivero = models.CharField(max_length=2, choices=tipo_vivero_CHOICES, db_column='T150codTipoVivero')
    id_viverista_actual = models.ForeignKey(Personas, related_name='id_persona_viverista_actual', on_delete=models.SET_NULL, null=True, blank=True, db_column='T150Id_ViveristaActual')
    fecha_inicio_viverista_actual = models.DateTimeField(null=True, blank=True, db_column='T150fechaInicioViveristaActual')
    cod_origen_recursos_vivero = models.CharField(max_length=2, choices=origen_recursos_vivero_CHOICES, db_column='T150codOrigenRecursosVivero')
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column='T150fechaCreacion')
    id_persona_crea = models.ForeignKey(Personas, related_name='persona_crea_vivero', on_delete=models.CASCADE, db_column='T150Id_PersonaCrea')
    en_funcionamiento = models.BooleanField(null=True, blank=True, db_column='T150enFuncionamiento')
    fecha_ultima_apertura = models.DateTimeField(null=True, blank=True, db_column='T150fechaUltimaApertura')
    id_persona_abre = models.ForeignKey(Personas, related_name='persona_abre_vivero', on_delete=models.SET_NULL, null=True, blank=True, db_column='T150Id_PersonaAbre')
    justificacion_apertura = models.CharField(max_length=255, null=True, blank=True, db_column='T150justificacionApertura')
    fecha_cierre_actual = models.DateTimeField(null=True, blank=True, db_column='T150fechaCierreActual')
    id_persona_cierra = models.ForeignKey(Personas, related_name='persona_cierra_vivero', on_delete=models.SET_NULL, null=True, blank=True, db_column='T150Id_PersonaCierra')
    justificacion_cierre = models.CharField(max_length=255, null=True, blank=True, db_column='T150justificacionCierre')
    vivero_en_cuarentena = models.BooleanField(null=True, blank=True, db_column='T150viveroEnCuarentena')
    fecha_inicio_cuarentena = models.DateTimeField(null=True, blank=True, db_column='T150fechaInicioCuarentena')
    id_persona_cuarentena = models.ForeignKey(Personas, related_name='persona_cuarentena_vivero', on_delete=models.SET_NULL, null=True, blank=True, db_column='T150Id_PersonaCuarentena')
    justificacion_cuarentena = models.CharField(max_length=255, null=True, blank=True, db_column='T150justificacionCuarentena')
    ruta_archivo_creacion = models.FileField(db_column='T150rutaArchivoCreación')
    activo = models.BooleanField(default=True, db_column='T150activo')
    item_ya_usado = models.BooleanField(default=True, db_column='T150itemYaUsado')
    
    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T150Viveros'
        verbose_name = 'Vivero'
        verbose_name_plural = 'Viveros'

class HistorialAperturaViveros(models.Model):
    id_historial_apertura_vivero = models.AutoField(primary_key=True,db_column='T151IdHistorialAperturaVivero')
    id_vivero=models.ForeignKey(Vivero,on_delete=models.CASCADE, db_column='T151Id_Vivero')
    fecha_apertura_anterior=models.DateTimeField(db_column='T151fechaAperturaAnterior')
    fecha_cierre_correspondiente=models.DateTimeField(db_column='T151fechaCierreCorrespondiente')
    id_persona_apertura_anterior=models.ForeignKey(Personas, on_delete=models.CASCADE,db_column='T151Id_PersonaAperturaAnterior',related_name='persona_apertura_anterior')
    id_persona_cierre_correspondiente=models.ForeignKey(Personas, on_delete=models.CASCADE,db_column='T151Id_PersonaCierreCorrespondiente',related_name='persona_cierre_correspondiente')
    justificacion_apertura_anterior=models.CharField(max_length=255, db_column='T151justificacionAperturaAnterior')
    justificacion_cierre_correspondiente=models.CharField(max_length=255, db_column='T151justificacionCierreCorrespondiente')

    def __str__(self):
        return str(self.id_historial_apertura_vivero)
        
    class Meta:
        db_table = 'T151HistorialAperturaViveros'
        verbose_name = 'Historial apertura viveros'
        verbose_name_plural = 'Historial apertura viveros'

class HistorialCuarentenaViveros(models.Model):
    id_historial_cuarentena_vivero=models.AutoField(primary_key=True,db_column='T152IdHistorialCuarentenaVivero')
    id_vivero=models.ForeignKey(Vivero,on_delete=models.CASCADE,db_column='T152Id_Vivero')
    fecha_inicio_cuarentena=models.DateTimeField(auto_now=True,db_column='T152fechaInicioCuarentena')
    id_persona_inicia_cuarentena=models.ForeignKey(Personas,on_delete=models.CASCADE,db_column='T152Id_PersonaIniciaCuarentena',related_name='persona_inicia_cuarentena')
    justificacion_inicio_cuarentena=models.CharField(max_length=255,db_column='T152justificacionInicioCuarentena')
    fecha_fin_cuarentena=models.DateTimeField(db_column='T152fechaFinCuarentena')
    id_persona_finaliza_cuarentena=models.ForeignKey(Personas,on_delete=models.CASCADE,db_column='T152Id_PersonaFinalizaCuarentena',related_name='persona_finaliza_cuarentena')
    justifiacion_fin_cuarentena=models.CharField(max_length=255,db_column='T152justificacionFinCuarentena')
    
    def __str__(self):
        return str(self.id_historial_cuarentena_vivero)
        
    class Meta:
        db_table = 'T152HistorialCuarentenaViveros'
        verbose_name = 'Historial cuarentena viveros'
        verbose_name_plural = 'Historial cuarentena viveros'
