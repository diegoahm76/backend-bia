from django.db import models
from conservacion.models.viveros_models import Vivero
from almacen.models.bienes_models import CatalogoBienes
from seguridad.models import Personas
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from conservacion.choices.tipo_baja_choices import tipo_baja_CHOICES


class CuarentenaMatVegetal(models.Model):
    id_cuarentena_mat_vegetal = models.AutoField(primary_key=True,db_column='T164IdCuarentenaMatVegetal')
    id_vivero = models.ForeignKey(Vivero,on_delete=models.CASCADE,db_column='T164Id_Vivero')
    id_bien = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE,db_column='T164Id_Bien')
    agno_lote = models.SmallIntegerField(db_column='T164agnoLote')
    nro_lote = models.IntegerField(db_column='T164nroLote')
    cod_etapa_lote = models.CharField(max_length=1,choices=cod_etapa_lote_CHOICES,db_column='T164codEtapaLote')
    consec_cueren_por_lote_etapa = models.SmallIntegerField(db_column='T164consecCuarenPorLoteEtapa')
    fecha_cuarentena = models.DateTimeField(db_column='T164fechaCuarentena')
    fecha_registro = models.DateTimeField(auto_now_add=True,db_column='T164fechaRegistro')
    cantidad_cuarentena = models.IntegerField(db_column='T164cantidadCuarentena')
    descrip_corta_diferenciable = models.CharField(max_length=30,db_column='T164descripCortaDiferenciable')
    motivo = models.CharField(max_length=255,db_column='T164motivo')
    id_persona_cuarentena = models.ForeignKey(Personas,on_delete=models.CASCADE,db_column='T164Id_PersonaCuarentena')
    cantidad_levantada = models.IntegerField(db_column='T164cantidadLevantada')
    cantidad_bajas = models.IntegerField(db_column='T164cantidadBajas')
    cuarentena_abierta = models.BooleanField(default=True,db_column='T164cuarentenaAbierta')
    cuarentena_anulada = models.BooleanField(default=False,db_column='T164cuarentenaAnulada')
    justificacion_anulacion = models.CharField(max_length=255,blank=True,null=True,db_column='T164justificacionAnulacion')
    fecha_anulacion = models.DateTimeField(db_column='T164fechaAnulacion', blank=True,null=True)
    id_persona_anula = models.ForeignKey(Personas,on_delete=models.SET_NULL,related_name='persona_anula_cuarentena',blank=True,null=True,db_column='T164Id_PersonaAnula')
    ruta_archivo_soporte = models.FileField(max_length=255,db_column='T164rutaArchivoSoporte',blank=True,null=True)
    
    def __str__(self):  
        return str(self.id_cuarentena_mat_vegetal)
    
    class Meta:    
        db_table ='T164CuarentenaMatVegetal'
        verbose_name = 'Cuarentena material vegetal'
        verbose_name_plural = 'Cuarentenas material vegetal'
        unique_together = ['id_vivero','id_bien','agno_lote','nro_lote','consec_cueren_por_lote_etapa']
    
class ItemsLevantaCuarentena(models.Model):
    id_item_levanta_cuarentena = models.AutoField(primary_key=True,db_column='T165IdItem_LevantaCuarentena')
    id_cuarentena_mat_material = models.ForeignKey(CuarentenaMatVegetal,on_delete=models.CASCADE,db_column='T165Id_CuarentenaMatVegetal')
    consec_levan_por_cuaren = models.SmallIntegerField(db_column='T165consecLevanPorCuaren')
    fecha_levantamiento = models.DateTimeField(db_column='T165fechaLevantamiento')
    fecha_registro = models.DateTimeField(auto_now_add=True,db_column='T165fechaRegistro')
    cantidad_a_levantar = models.IntegerField(db_column='T165cantidadALevantar')
    observaciones = models.CharField(max_length=255,db_column='T165observaciones')
    id_persona_levanta = models.ForeignKey(Personas,on_delete=models.CASCADE,db_column='T165Id_PersonaLevanta')
    levantamiento_anulado = models.BooleanField(default=False,db_column='T165levantamientoAnulado')
    justificacion_anulacion = models.CharField(max_length=255,blank=True,null=True,db_column='T165justificacionAnulacion')
    fecha_anulacion = models.DateTimeField(blank=True,null=True,db_column='T165fechaAnulacion')
    id_persona_anula = models.ForeignKey(Personas,on_delete=models.SET_NULL,blank=True,null=True,db_column='T165Id_PersonaAnula',related_name='id_persona_anula_items')
    
    def __str__(self):
        return str(self.id_item_levanta_cuarentena)
    
    class Meta:
        db_table = 'T165Items_LevantaCuarentena'
        verbose_name = 'item levanta cuarentena'
        verbose_name_plural = 'items levanta cuarentena'
        unique_together = ['id_item_levanta_cuarentena','id_cuarentena_mat_material']
    
    
        

class BajasVivero(models.Model):
    id_baja = models.AutoField(primary_key=True,db_column='T166IdBaja')
    tipo_baja = models.CharField(max_length=1, choices=tipo_baja_CHOICES,db_column='T166tipoBaja')
    nro_baja_por_tipo = models.IntegerField(db_column='T166nroBajaPorTipo')
    id_vivero = models.ForeignKey(Vivero,on_delete=models.CASCADE,db_column='T166Id_Vivero')
    fecha_baja = models.DateTimeField(db_column='T166fechaBaja')
    fecha_registro = models.DateTimeField(auto_now_add=True,db_column='T166fechaRegistro')
    motivo = models.CharField(max_length=255,db_column='T166motivo')
    id_persona_baja = models.ForeignKey(Personas,on_delete=models.CASCADE,db_column='T166Id_PersonaBaja')
    baja_anulado = models.BooleanField(default=False,db_column='T166bajaAnulado')
    justificacion_anulacion = models.CharField(max_length=255,blank=True,null=True,db_column='T166justificacionAnulacion')
    fecha_anulacion = models.DateTimeField(db_column='T166fechaAnulacion',blank=True,null=True)
    id_persona_anula = models.ForeignKey(Personas,on_delete=models.SET_NULL,blank=True,null=True,related_name='persona_anula_bajas',db_column='T166Id_PersonaAnula')
    ruta_archivo_soporte = models.FileField(null=True, blank=True,db_column='T166rutaArchivoSoporte')
    
    def __str__(self):
        return str(self.id_baja)
    
    class Meta:
        db_table = 'T166BajasViveros'
        verbose_name = 'Baja vivero'
        verbose_name_plural = 'Bajas viveros'
        unique_together = ['tipo_baja','nro_baja_por_tipo']    
        
class ItemsBajasVivero (models.Model):
    id_item_baja_viveros = models.AutoField(primary_key=True,db_column='T167IdItem_BajaViveros')
    id_baja = models.ForeignKey(BajasVivero,on_delete=models.CASCADE,db_column='T167Id_Baja')
    id_bien = models.ForeignKey(CatalogoBienes,on_delete=models.CASCADE,db_column='T167Id_Bien')
    agno_lote = models.SmallIntegerField(blank=True,null=True,db_column='T167agnoLote')
    nro_lote = models.IntegerField(blank=True,null=True,db_column='T167nroLote')
    cod_etapa_lote = models.CharField(max_length=1,choices=cod_etapa_lote_CHOICES,db_column='T167codEtapaLote')
    consec_cuaren_por_lote_etapa = models.SmallIntegerField(blank=True,null=True,db_column='T167consecCuarenPorLoteEtapa')
    cantidad_baja = models.IntegerField(db_column='T167cantidadBaja')
    observaciones = models.CharField(max_length=30,blank=True,null=True,db_column='T167observaciones')
    nro_posicion = models.SmallIntegerField(db_column='T167nroPosicion')
    
    def __str__(self):
        return str(self.id_item_baja_viveros)
    
    class Meta:
        db_table = 'T167Items_BajaViveros'
        verbose_name = 'Item baja vivero'
        verbose_name_plural = 'Items bajas vivero'
        unique_together = ['id_baja','id_bien','agno_lote','nro_lote','cod_etapa_lote','consec_cuaren_por_lote_etapa']