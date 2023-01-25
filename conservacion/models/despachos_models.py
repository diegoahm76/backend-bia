from django.db import models
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from seguridad.models import (
    Personas,
)
from conservacion.models import (
    Vivero
)
from almacen.models.bienes_models import (
    CatalogoBienes,
    EntradasAlmacen,
)
from almacen.models.solicitudes_models import (
    DespachoConsumo
)

class DespachoEntrantes(models.Model):
    id_despacho_entrante=models.AutoField(primary_key=True,editable=False,db_column='T153IdDespachoEntrante')
    id_despacho_consumo_alm=models.ForeignKey(DespachoConsumo,on_delete=models.CASCADE,db_column='T153Id_DespachoConsumoAlm')
    fecha_ingreso=models.DateTimeField(db_column='T153fechaIngreso')
    distribucion_confirmada=models.BooleanField(db_column='T153distribucionConfirmada')
    fecha_confirmacion_distribucion=models.DateTimeField(db_column='T153fechaConfirmacionDistribucion',blank=True,null=True)
    observacion_distribucion=models.CharField(max_length=255,blank=True,null=True,db_column='T153observacionDistribucion')
    id_persona_distribuye=models.ForeignKey(Personas,on_delete=models.SET_NULL,blank=True,null=True,db_column='T153Id_PersonaDistribuye')
    
    def __str__(self):
        return str(self.id_despacho_entrante)

    class Meta:
        db_table = 'T153DespachosEntrantes'
        verbose_name = 'Despacho entrante'
        verbose_name_plural = 'Despachos entrantes'
    
class ItemsDespachoEntrante(models.Model):
    id_item_despacho_entrante=models.AutoField(primary_key=True,editable=False,db_column='T154IdItem_DespachoEntrante')
    id_despacho_entrante=models.ForeignKey(DespachoEntrantes,on_delete=models.CASCADE,db_column='T154Id_DespachoEntrante')
    id_bien=models.ForeignKey(CatalogoBienes,on_delete=models.CASCADE,db_column='T154Id_Bien')
    id_entrada_alm_del_bien=models.ForeignKey(EntradasAlmacen,on_delete=models.SET_NULL,blank=True,null=True,db_column='T154Id_EntradaAlmDelBien')
    fecha_ingreso=models.DateTimeField(db_column='T154fechaIngreso')
    cantidad_entrante=models.IntegerField(db_column='T154cantidadEntrante')
    cantidad_distribuida=models.IntegerField(db_column='T154cantidadDistribuida')
    observacion=models.CharField(max_length=50,db_column='T154observacion',blank=True,null=True)

    def __str__(self):
        return str(self.id_item_despacho_entrante)

    class Meta:
        db_table = 'T154Items_DespachoEntrante'
        verbose_name = 'Items despacho entrante'
        verbose_name_plural = 'Items despachos entrantes'
        unique_together = ['id_despacho_entrante', 'id_bien','id_entrada_alm_del_bien']

class DistribucionesItemDespachoEntrante(models.Model):
    id_distribucion_item_despacho_entrante = models.AutoField(primary_key=True, editable=False, db_column='T155IdDistribucion_ItemDespachoEntrante')
    id_item_despacho_entrante = models.ForeignKey(ItemsDespachoEntrante, on_delete=models.CASCADE, db_column='T155IdItem_DespachoEntrante')
    id_vivero = models.ForeignKey(Vivero, on_delete=models.CASCADE, db_column='T155Id_Vivero')
    cantidad_asignada = models.PositiveIntegerField(db_column='T155cantidadAsignada')
    cod_etapa_lote_al_ingresar = models.CharField(max_length=1, choices=cod_etapa_lote_CHOICES, null=True, blank=True, db_column='T155codEtapaAIngresarMV')
    fecha_distribucion = models.DateTimeField(auto_now=True, db_column='T155fechaDistribucion')
    
    def __str__(self):
        return str(self.id_distribucion_item_despacho_entrante)

    class Meta:
        db_table = 'T155Distribuciones_Item_DespachoEntrante'
        verbose_name = 'Distribución Item Despacho Entrante'
        verbose_name_plural = 'Distribuciones Item Despacho Entrante'
        unique_together = ['id_item_despacho_entrante', 'id_vivero']