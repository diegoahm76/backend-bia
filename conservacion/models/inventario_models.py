from django.db import models
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from conservacion.models import (
    Vivero,
)
from almacen.models import (
    CatalogoBienes,
    TiposEntradas
)

class InventarioViveros(models.Model):
    id_inventario_vivero = models.AutoField(primary_key=True, editable=False, db_column='T156IdInventarioViveros')
    id_vivero = models.ForeignKey(Vivero, on_delete=models.CASCADE, db_column='T156Id_Vivero')
    id_bien = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T156Id_Bien')
    agno_lote = models.PositiveSmallIntegerField(null=True, blank=True, db_column='T156agnoLote')
    nro_lote = models.PositiveIntegerField(null=True, blank=True, db_column='T156nroLote')
    cod_etapa_lote = models.CharField(max_length=1, choices=cod_etapa_lote_CHOICES, null=True, blank=True, db_column='T156codEtapaLote')
    es_produccion_propia_lote = models.BooleanField(null=True, blank=True, db_column='T156esProduccionPropiaLote')
    cod_tipo_entrada_alm_lote = models.ForeignKey(TiposEntradas, on_delete=models.SET_NULL, null=True, blank=True, db_column='T156cod_TipoEntradaAlmLote')
    nro_entrada_alm_lote = models.PositiveIntegerField(null=True, blank=True, db_column='T156nroEntradaAlmLote')
    fecha_ingreso_lote_etapa = models.DateTimeField(null=True, blank=True, db_column='T156fechaIngresoLoteALaEtapa')
    ult_altura_lote = models.PositiveSmallIntegerField(null=True, blank=True, db_column='T156ultAlturaLote')
    fecha_ult_altura_lote = models.DateTimeField(null=True, blank=True, db_column='T156fechaUltAlturaLote')
    porc_cuarentena_lote_germinacion = models.PositiveSmallIntegerField(null=True, blank=True, db_column='T156porcCuarentenaLoteGerminacion')
    id_siembra_lote_germinacion = models.PositiveIntegerField(null=True, blank=True, db_column='T156Id_SiembraLoteGerminacion')
    siembra_lote_cerrada = models.BooleanField(null=True, blank=True, db_column='T156siembraLoteCerrada')
    cantidad_entrante = models.PositiveIntegerField(null=True, blank=True, db_column='T156cantidadEntrante')
    cantidad_bajas = models.PositiveIntegerField(null=True, blank=True, db_column='T156cantidadBajas')
    cantidad_consumos_internos = models.PositiveIntegerField(null=True, blank=True, db_column='T156cantidadConsumosInternos')
    cantidad_traslados_lote_produccion_distribucion = models.PositiveIntegerField(null=True, blank=True, db_column='T156cantidadTrasladosLoteProdADistri')
    cantidad_salidas = models.PositiveIntegerField(null=True, blank=True, db_column='T156cantidadSalidas')
    cantidad_lote_cuarentena = models.PositiveIntegerField(null=True, blank=True, db_column='T156cantidadLoteEnCuarentena')
    id_mezcla = models.PositiveSmallIntegerField(null=True, blank=True, db_column='T156Id_Mezcla')
    
    def __str__(self):
        return str(self.id_inventario_vivero)

    class Meta:
        db_table = 'T156InventarioViveros'
        verbose_name = 'Inventario Vivero'
        verbose_name_plural = 'Inventario Viveros'
        unique_together = ['id_vivero', 'id_bien', 'agno_lote', 'nro_lote', 'cod_etapa_lote', 'id_mezcla']