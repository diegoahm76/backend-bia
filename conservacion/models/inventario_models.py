from conservacion.models.mezclas_models import Mezclas
from django.db import models
from django.db.models import Q
from django.db.models.constraints import UniqueConstraint
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from conservacion.models import (
    Vivero,
)
from almacen.models import (
    CatalogoBienes,
    TiposEntradas
)
from conservacion.models.siembras_models import (
    Siembras
)

class InventarioViveros(models.Model):
    id_inventario_vivero = models.AutoField(primary_key=True, editable=False, db_column='T156IdInventarioViveros')
    id_vivero = models.ForeignKey(Vivero, on_delete=models.CASCADE, db_column='T156Id_Vivero')
    id_bien = models.ForeignKey(CatalogoBienes, on_delete=models.SET_NULL, null=True, blank=True, db_column='T156Id_Bien')
    id_mezcla = models.ForeignKey(Mezclas,on_delete=models.SET_NULL,null=True, blank=True, db_column='T156Id_Mezcla')
    agno_lote = models.SmallIntegerField(null=True, blank=True, db_column='T156agnoLote')
    nro_lote = models.IntegerField(null=True, blank=True, db_column='T156nroLote')
    cod_etapa_lote = models.CharField(max_length=1, choices=cod_etapa_lote_CHOICES, null=True, blank=True, db_column='T156codEtapaLote')
    es_produccion_propia_lote = models.BooleanField(null=True, blank=True, db_column='T156esProduccionPropiaLote')
    cod_tipo_entrada_alm_lote = models.ForeignKey(TiposEntradas, on_delete=models.SET_NULL, null=True, blank=True, db_column='T156cod_TipoEntradaAlmLote')
    nro_entrada_alm_lote = models.IntegerField(null=True, blank=True, db_column='T156nroEntradaAlmLote')
    fecha_ingreso_lote_etapa = models.DateTimeField(null=True, blank=True, db_column='T156fechaIngresoLoteALaEtapa')
    ult_altura_lote = models.SmallIntegerField(null=True, blank=True, db_column='T156ultAlturaLote')
    fecha_ult_altura_lote = models.DateTimeField(null=True, blank=True, db_column='T156fechaUltAlturaLote')
    porc_cuarentena_lote_germinacion = models.SmallIntegerField(null=True, blank=True, db_column='T156porcCuarentenaLoteGerminacion')
    id_siembra_lote_germinacion =  models.ForeignKey(Siembras, null=True, blank=True, on_delete=models.SET_NULL, db_column='T156Id_SiembraLoteGerminacion')
    siembra_lote_cerrada = models.BooleanField(null=True, blank=True, db_column='T156siembraLoteCerrada')
    cantidad_entrante = models.IntegerField(null=True, blank=True, db_column='T156cantidadEntrante')
    cantidad_bajas = models.IntegerField(null=True, blank=True, db_column='T156cantidadBajas')
    cantidad_consumos_internos = models.IntegerField(null=True, blank=True, db_column='T156cantidadConsumosInternos')
    cantidad_traslados_lote_produccion_distribucion = models.IntegerField(null=True, blank=True, db_column='T156cantidadTrasladosLoteProdADistri')
    cantidad_salidas = models.IntegerField(null=True, blank=True, db_column='T156cantidadSalidas')
    cantidad_lote_cuarentena = models.IntegerField(null=True, blank=True, db_column='T156cantidadLoteEnCuarentena')
    
    def __str__(self):
        return str(self.id_inventario_vivero)

    class Meta:
        db_table = 'T156InventarioViveros'
        verbose_name = 'Inventario Vivero'
        verbose_name_plural = 'Inventario Viveros'
        constraints = [
            UniqueConstraint(fields=['id_vivero', 'id_bien', 'agno_lote', 'nro_lote', 'cod_etapa_lote', 'id_mezcla'],
                             name='unique_with_optional'),
            UniqueConstraint(fields=['id_vivero', 'id_bien', 'agno_lote', 'nro_lote', 'cod_etapa_lote'],
                             condition=Q(id_mezcla=None),
                             name='unique_without_optional'),
        ]