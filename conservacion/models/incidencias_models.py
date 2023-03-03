from almacen.models.bienes_models import CatalogoBienes
from conservacion.models.viveros_models import Vivero
from seguridad.models import Personas
from conservacion.models.mezclas_models import Mezclas
from django.db import models
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from conservacion.choices.tipo_incidencia_choices import tipo_incidencia_CHOICES

class IncidenciasMatVegetal (models.Model):
    id_incidencias_mat_vegetal = models.AutoField(primary_key=True,editable=False,db_column='T171IdIncidenciasMatVegetal')
    id_vivero = models.ForeignKey(Vivero,on_delete=models.CASCADE,db_column='T171Id_Vivero')
    id_bien = models.ForeignKey(CatalogoBienes,on_delete=models.CASCADE,db_column='T171Id_Bien')
    agno_lote = models.SmallIntegerField(db_column='T171agnoLote')
    nro_lote = models.IntegerField(db_column='T171nroLote')
    cod_etapa_lote = models.CharField(max_length=1,choices=cod_etapa_lote_CHOICES,db_column='T171codEtapaLote')
    consec_por_lote_etapa = models.SmallIntegerField(db_column='T171consecPorLoteEtapa')
    consec_cuaren_lote_etapa = models.SmallIntegerField(blank=True,null=True,db_column='T171consecCuarenLoteEtapa')
    fecha_incidencia = models.DateTimeField(db_column='T171fechaIncidencia')
    fecha_registro = models.DateTimeField(auto_now_add=True,db_column='T171fechaRegistro')
    cod_tipo_incidencia = models.CharField(max_length=1,choices=tipo_incidencia_CHOICES,db_column='T171codTipoIncidencia')
    nombre_incidencia = models.CharField(max_length=30,db_column='T171nombreIncidencia')
    descripcion = models.CharField(max_length=255,db_column='T171descripcion')
    altura_lote_en_cms = models.SmallIntegerField(blank=True,null=True,db_column='T171alturaLoteEnCms')
    id_persona_registra =models.ForeignKey(Personas,on_delete=models.CASCADE,db_column='T171Id_PersonaRegistra',related_name='id_persona_registra_incidencias')
    incidencia_anulacion = models.BooleanField(default=False,db_column='T171incidenciaAnulada')
    justificacion_anulacion = models.CharField(max_length=255,blank=True,null=True,db_column='T171justificacionAnulacion')
    fecha_anulacion = models.DateTimeField(blank=True,null=True,db_column='T171fechaAnulacion')
    id_persona_anula = models.ForeignKey(Personas,on_delete=models.SET_NULL,blank=True,null=True,db_column='T171Id_PersonaAnula',related_name='id_persona_anula_incidencias')
    ruta_archivos_soporte = models.FileField(blank=True,null=True,db_column='T171rutaArchivoSoporte')
    
    def __str__(self):
        return str(self.id_incidencias_mat_vegetal)
    
    class Meta:
        db_table = 'T171IncidenciasMatVegetal'
        verbose_name = 'Incidencia Material Vegetal'
        verbose_name_plural = 'Incidencias Material Vegetal'
        unique_together = ['id_vivero','id_bien','agno_lote','nro_lote','cod_etapa_lote','consec_por_lote_etapa']
    
class ConsumosIncidenciasMV(models.Model):
    id_consumo_insidenciaMV = models.AutoField(primary_key=True,editable=False,db_column='T172IdConsumo_IncidenciaMV')
    id_incidencia_mat_vegetal = models.ForeignKey(IncidenciasMatVegetal,on_delete=models.CASCADE,db_column='T172Id_IncidenciaMatVegetal')
    id_bien = models.ForeignKey(CatalogoBienes,on_delete=models.SET_NULL,blank=True,null=True,db_column='T172Id_Bien')
    id_mezcla = models.ForeignKey(Mezclas,on_delete=models.SET_NULL,blank=True,null=True,db_column='T172Id_Mezcla')
    cantidad_consumida = models.IntegerField(db_column='T172cantidadConsumida')
    observaciones = models.CharField(max_length=30,db_column='T172observaciones',blank=True,null=True)
    nro_posicion = models.SmallIntegerField(db_column='T172nroPosicion')
    
    def __str__(self):
        return str(self.id_consumo_insidenciaMV)
    
    class Meta: 
        db_table = 'T172Consumos_IncidenciasMV'
        verbose_name = 'Consumo incidencia material vegetal'
        verbose_name_plural = 'Consumos incidencia material vegetal'
        unique_together = ['id_incidencia_mat_vegetal','id_bien','id_mezcla']
        
