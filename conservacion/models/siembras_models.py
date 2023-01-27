from django.db import models
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from conservacion.models import (
    Vivero,
)
from almacen.models import (
    CatalogoBienes,
    TiposEntradas
)
from seguridad.models import (
    Personas
)

class Siembras(models.Model):
    id_siembra = models.AutoField(primary_key=True, editable=False, db_column='T157IdSiembra')
    id_vivero = models.ForeignKey(Vivero, on_delete=models.CASCADE, db_column='T157Id_Vivero')
    id_bien_sembrado = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T157Id_BienSembrado')
    agno_lote = models.PositiveSmallIntegerField(db_column='T157agnoLote')
    nro_lote = models.PositiveIntegerField(db_column='T157nroLote')
    fecha_siembra = models.DateTimeField(db_column='T157fechaSiembra')
    fecha_registro = models.DateTimeField(db_column='T157fechaRegistro')
    observaciones = models.CharField(max_length=255, null=True, blank=True, db_column='T157observaciones')
    distancia_entre_semillas = models.PositiveSmallIntegerField(db_column='T157distanciaEntreSemillas')
    id_persona_siembra = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T157Id_PersonaSiembra')
    ruta_archivo_soporte = models.FileField(null=True, blank=True, db_column='T157rutaArchivoSoporte')
    
    def __str__(self):
        return str(self.id_siembra)

    class Meta:
        db_table = 'T157Siembras'
        verbose_name = 'Siembras vivero'
        verbose_name_plural = 'Siembras vivero'
        
class ConsumosSiembra(models.Model):
    id_consumo_siembra = models.AutoField(primary_key=True, editable=False, db_column='T158IdConsumoSiembra')
    id_siembra = models.ForeignKey(Siembras, on_delete=models.CASCADE, db_column='T158Id_Siembra')
    id_bien_consumido = models.ForeignKey(CatalogoBienes, null=True, blank=True, on_delete=models.SET_NULL, db_column='T158Id_BienConsumido')
    cantidad = models.PositiveSmallIntegerField(db_column='T158cantidad')
    observaciones = models.CharField(max_length=255, null=True, blank=True, db_column='T158observaciones')
    id_mezcla_consumida = models.PositiveSmallIntegerField(db_column='T158Id_MezclaConsumida')
    
    def __str__(self):
        return str(self.id_consumo_siembra)

    class Meta:
        db_table = 'T158Consumos_Siembra'
        verbose_name = 'Consumos siembra'
        verbose_name_plural = 'Consumos siembra'
        unique_together = ['id_siembra', 'id_bien_consumido', 'id_mezcla_consumida']
        
class CamasGerminacionVivero(models.Model):
    id_cama_germinacion_vivero = models.AutoField(primary_key=True, editable=False, db_column='T159IdCamaGerminacion_Vivero')
    id_vivero = models.ForeignKey(Vivero, on_delete=models.CASCADE, db_column='T159Id_Vivero')
    nombre = models.CharField(max_length=50, db_column='T159nombre')
    nro_de_orden = models.PositiveSmallIntegerField(db_column='T159nroDeOrden')
    observacion = models.CharField(max_length=255, null=True, blank=True, db_column='T159observacion')
    item_activo = models.BooleanField(default=True, db_column='T159itemActivo')
    item_ya_usado = models.BooleanField(default=False, db_column='T159itemYaUsado')

    def __str__(self):
        return str(self.id_cama_germinacion_vivero)

    class Meta:
        db_table = 'T159CamasGerminacion_Vivero'
        verbose_name = 'Cama de germinacion vivero'
        verbose_name_plural = 'Camas de germinacion Vivero'
        
class CamasGerminacionViveroSiembra(models.Model):
    id_cama_germinacion_vivero_siembra = models.AutoField(primary_key=True, editable=False, db_column='T160IdCamaGerminacion_Vivero_Siembra')
    id_siembra = models.ForeignKey(Siembras, on_delete=models.CASCADE, db_column='T160Id_Siembra')
    id_cama_germinacion_vivero = models.ForeignKey(CamasGerminacionVivero, on_delete=models.CASCADE, db_column='T160Id_CamaGerminacion_Vivero')

    def __str__(self):
        return str(self.id_cama_germinacion_vivero_siembra)

    class Meta:
        db_table = 'T160CamasGerminacion_Vivero_Siembra'
        verbose_name = 'Cama de germinacion vivero siembra'
        verbose_name_plural = 'Camas de germinacion vivero siembra'

class CambiosDeEtapa(models.Model):
    id_cambio_de_etapa = models.AutoField(primary_key=True, editable=False, db_column='T161IdCambioDeEtapa')
    id_vivero = models.ForeignKey(Vivero, on_delete=models.CASCADE, db_column='T161Id_Vivero')
    id_bien = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T161Id_Bien')
    agno_lote = models.PositiveSmallIntegerField(db_column='T161agnoLote')
    nro_lote = models.PositiveIntegerField(db_column='T161nroLote')
    cod_etapa_lote_origen = models.CharField(max_length=1, null=True, blank=True, choices=cod_etapa_lote_CHOICES, db_column='T161codEtapaLoteOrigen')
    consec_por_lote_etapa = models.PositiveIntegerField(db_column='T161consecPorLoteEtapa')
    fecha_cambio = models.DateTimeField(db_column='T161fechaCambio')
    fecha_registro = models.DateTimeField(db_column='T161fechaRegistro')
    cantidad_movida = models.PositiveIntegerField(db_column='T161cantidadMovida')
    cantidad_disponible_al_crear = models.PositiveIntegerField(db_column='T161cantidadDispoAlCrear')
    altura_lote_en_cms = models.PositiveSmallIntegerField(db_column='T161alturaLoteEnCms')
    observaciones = models.CharField(max_length=255, null=True, blank=True, db_column='T161observaciones')
    id_persona_cambia = models.ForeignKey(Personas, on_delete=models.SET_NULL, null=True, blank=True, db_column='T161Id_PersonaCambia', related_name='id_persona_cambia')
    cambio_anulado = models.BooleanField(null=True, blank=True, db_column='T161cambioAnulado')
    justificacion_anulacion = models.CharField(max_length=255, null=True, blank=True, db_column='T161justificacionAnulacion')
    fecha_anulacion = models.DateTimeField(null=True, blank=True, db_column='T161fechaAnulacion')
    id_persona_anula = models.ForeignKey(Personas, on_delete=models.SET_NULL, null=True, blank=True, db_column='T161Id_PersonaAnula', related_name='id_persona_anula')
    ruta_archivo_soporte = models.FileField(null=True, blank=True, db_column='T161rutaArchivoSoporte')
    
    def __str__(self):
        return str(self.id_cambio_de_etapa)

    class Meta:
        db_table = 'T161CambiosDeEtapa'
        verbose_name = 'Cambio de etapa'
        verbose_name_plural = 'Cambios de etapa'
        unique_together = ['id_vivero', 'id_bien', 'agno_lote', 'nro_lote', 'cod_etapa_lote_origen', 'consec_por_lote_etapa']