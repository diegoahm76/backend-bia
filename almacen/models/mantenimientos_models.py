from django.db import models
from almacen.choices.tipo_mantenimiento_choices import tipo_mantenimiento_CHOICES
from almacen.choices.tipo_doc_ultimo_choices import tipo_doc_ultimo_CHOICES
# from seguridad.models import Personas
from almacen.models.bienes_models import CatalogoBienes, EstadosArticulo

class ProgramacionMantenimientos(models.Model):
    id_programacion_mtto = models.AutoField(primary_key=True, db_column='T069IdProgramacionMtto')
    id_articulo = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T069Id_Articulo')
    cod_tipo_mantenimiento = models.CharField(max_length=1, choices=tipo_mantenimiento_CHOICES, db_column='T069codTipoMantenimiento')
    fecha_generada = models.DateTimeField(db_column='T069fechaGenerada')
    fecha_programada = models.DateField(db_column='T069fechaProgramada', blank=True, null=True)
    kilometraje_programado = models.IntegerField(db_column='T069kilometrajeProgramado', blank=True, null=True)
    motivo_mantenimiento = models.CharField(max_length=255, db_column='T069motivoMantenimiento')
    observaciones = models.CharField(max_length=255, db_column='T069observaciones', blank=True, null=True)
    id_persona_solicita = models.ForeignKey('transversal.Personas', on_delete=models.SET_NULL, db_column='T069Id_PersonaSolicita', blank=True, null=True, related_name='persona_solicita_programacion')
    fecha_solicitud = models.DateField(db_column='T069fechaSolicitud', blank=True, null=True)
    fecha_anulacion = models.DateTimeField(db_column='T069fechaAnulacion', blank=True, null=True)
    justificacion_anulacion = models.CharField(max_length=255, db_column='T069justificacionAnulacion', blank=True, null=True)
    id_persona_anula = models.ForeignKey('transversal.Personas', on_delete=models.SET_NULL, db_column='T069Id_PersonaAnula', blank=True, null=True, related_name='persona_anula')
    ejecutado = models.BooleanField(db_column='T069ejecutado', default=False)
    
    def __str__(self):
        return str(self.id_programacion_mtto)

    class Meta:
        db_table = 'T069ProgramacionMantenimientos'
        verbose_name = 'Programacion Mantenimientos'
        verbose_name_plural = 'Programaciones Mantenimientos'

class RegistroMantenimientos(models.Model):
    id_registro_mtto = models.AutoField(primary_key=True, db_column='T070IdRegistroMtto')
    id_articulo = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T070Id_Articulo')
    fecha_registrado = models.DateTimeField(db_column='T070fechaRegistrado')
    fecha_ejecutado = models.DateTimeField(db_column='T070fechaEjecutado')
    cod_tipo_mantenimiento = models.CharField(max_length=1, choices=tipo_mantenimiento_CHOICES, db_column='T070codTipoMantenimiento')
    acciones_realizadas = models.TextField(db_column='T070accionesRealizadas')
    dias_empleados = models.SmallIntegerField(db_column='T070diasEmpleados')
    observaciones = models.CharField(max_length=255, db_column='T070observaciones', blank=True, null=True)
    cod_estado_final = models.ForeignKey(EstadosArticulo, db_column='T070Cod_EstadoFinal', on_delete=models.CASCADE, related_name='cod_estado_final_Registro')
    id_programacion_mtto = models.ForeignKey(ProgramacionMantenimientos, on_delete=models.SET_NULL, db_column='T070Id_ProgramacionMtto', blank=True, null=True)
    valor_mantenimiento = models.DecimalField(db_column='T070valorMantenimiento', max_digits=12, decimal_places=2, blank=True, null=True)
    contrato_mantenimiento = models.CharField(max_length=20, db_column='T070contratoMantenimiento', blank=True, null=True)
    id_persona_realiza = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, db_column='T070Id_PersonaRealiza', related_name='id_persona_realiza')
    id_persona_diligencia = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, db_column='T070Id_PersonaDiligencia', related_name='id_persona_diligencia')
    ruta_documentos_soporte = models.FileField(db_column='T070rutaDocumentoSoporte', max_length=255, upload_to='almacen/registro_mantenimientos/', blank=True, null=True)
    cod_estado_anterior = models.ForeignKey(EstadosArticulo, db_column='T070codEstadoAnterior', on_delete=models.CASCADE, related_name='cod_estado_anterior')
    fecha_estado_anterior = models.DateTimeField(db_column='T070fechaAnteriorMov')
    tipo_doc_anterior_mov = models.CharField(max_length=5, choices=tipo_doc_ultimo_CHOICES, db_column='T070tipoDocAnteriorMov')
    id_reg_en_doc_anterior_mov = models.IntegerField(db_column='T070IdRegEnDocAnteriorMov')
    
    def __str__(self):
        return str(self.id_programacion_mtto)

    class Meta:
        db_table = 'T070RegistroMantenimientos'
        verbose_name = 'Registro Mantenimiento'
        verbose_name_plural = 'Registros Mantenimientos'