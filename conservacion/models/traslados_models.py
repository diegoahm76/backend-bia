from django.db import models
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from conservacion.models import (
    Vivero,
)
from almacen.models import (
    CatalogoBienes,
    TiposEntradas
)
from transversal.models.personas_models import (
    Personas
)

class TrasladosViveros(models.Model):
    id_traslado = models.AutoField(primary_key=True, editable=False, db_column='T162IdTraslado')
    nro_traslado = models.IntegerField(db_column='T162nroTraslado', unique=True)
    id_vivero_destino = models.ForeignKey(Vivero, on_delete=models.CASCADE, db_column='T162Id_ViveroDestino', related_name='id_vivero_destino')
    id_vivero_origen = models.ForeignKey(Vivero, on_delete=models.CASCADE, db_column='T162Id_ViveroOrigen', related_name='id_vivero_origen')
    fecha_traslado = models.DateTimeField(db_column='T162fechaTraslado')
    observaciones = models.CharField(max_length=255, null=True, blank=True, db_column='T162observaciones')
    id_persona_traslada = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T162Id_PersonaTraslada', related_name='id_persona_traslada')
    traslado_anulado = models.BooleanField(default=False, db_column='T162trasladoAnulado')
    justificacion_anulacion = models.CharField(max_length=255, null=True, blank=True, db_column='T162justificacionAnulacion')
    fecha_anulado = models.DateTimeField(null=True, blank=True, db_column='T162fechaAnulado')
    id_persona_anula = models.ForeignKey(Personas, on_delete=models.SET_NULL, null=True, blank=True, db_column='T162Id_PersonaAnula', related_name='id_persona_anula_traslada')
    ruta_archivo_soporte = models.FileField(null=True, blank=True, max_length=255, upload_to='conservacion/traslados/', db_column='T162rutaArchivoSoporte')
    
    def __str__(self):
        return str(self.id_siembra)

    class Meta:
        db_table = 'T162TrasladosViveros'
        verbose_name = 'Traslados vivero'
        verbose_name_plural = 'Traslados vivero'
        
class ItemsTrasladoViveros(models.Model):
    id_item_traslado_viveros = models.AutoField(primary_key=True, editable=False, db_column='T163IdItem_TrasladoViveros')
    id_traslado = models.ForeignKey(TrasladosViveros, on_delete=models.CASCADE, db_column='T163Id_Traslado')
    id_bien_origen = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T163Id_BienOrigen ')
    agno_lote_origen = models.SmallIntegerField(null=True, blank=True, db_column='T163agnoLoteOrigen')
    nro_lote_origen = models.IntegerField(null=True, blank=True, db_column='T163nroLoteOrigen')
    cod_etapa_lote_origen = models.CharField(max_length=1, null=True, blank=True, choices=cod_etapa_lote_CHOICES, db_column='T163codEtapaLoteOrigen')
    agno_lote_destino_MV = models.SmallIntegerField(null=True, blank=True, db_column='T163agnoLoteDestinoMV')
    nro_lote_destino_MV = models.IntegerField(null=True, blank=True, db_column='T163nroLoteDestinoMV')
    cod_etapa_lote_destino_MV = models.CharField(max_length=1, null=True, blank=True, choices=cod_etapa_lote_CHOICES, db_column='T163codEtapaLoteDestinoMV')
    cantidad_a_trasladar = models.IntegerField(db_column='T163cantidadATrasladar')
    altura_lote_destion_en_cms = models.SmallIntegerField(null=True, blank=True, db_column='T163alturaLoteDestinoEnCms')
    nro_posicion = models.SmallIntegerField(db_column='T163nroPosicion')
    
    def __str__(self):
        return str(self.id_consumo_siembra)

    class Meta:
        db_table = 'T163Items_TrasladoViveros'
        verbose_name = 'Item traslados viveros'
        verbose_name_plural = 'Items traslados viveros'
        unique_together = ['id_traslado', 'id_bien_origen', 'agno_lote_origen', 'nro_lote_origen', 'cod_etapa_lote_origen']