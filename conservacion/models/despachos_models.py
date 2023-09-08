from django.db import models
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from transversal.models.personas_models import (
    Personas,
)
from conservacion.models import (
    Vivero
)
from conservacion.models.solicitudes_models import (
    SolicitudesViveros
)
from almacen.models.bienes_models import (
    CatalogoBienes,
    EntradasAlmacen,
)
from almacen.models.solicitudes_models import (
    DespachoConsumo
)
from seguridad.models import (
    UnidadesOrganizacionales
)

class DespachoEntrantes(models.Model):
    id_despacho_entrante=models.AutoField(primary_key=True, editable=False, db_column='T153IdDespachoEntrante')
    id_despacho_consumo_alm=models.ForeignKey(DespachoConsumo, on_delete=models.CASCADE, db_column='T153Id_DespachoConsumoAlm')
    fecha_ingreso=models.DateTimeField(db_column='T153fechaIngreso')
    distribucion_confirmada=models.BooleanField(db_column='T153distribucionConfirmada')
    fecha_confirmacion_distribucion=models.DateTimeField(db_column='T153fechaConfirmacionDistribucion', blank=True, null=True)
    observacion_distribucion=models.CharField(max_length=255, blank=True, null=True, db_column='T153observacionDistribucion')
    id_persona_distribuye=models.ForeignKey(Personas, on_delete=models.SET_NULL, blank=True, null=True, db_column='T153Id_PersonaDistribuye')
    
    def __str__(self):
        return str(self.id_despacho_entrante)

    class Meta:
        db_table = 'T153DespachosEntrantes'
        verbose_name = 'Despacho entrante'
        verbose_name_plural = 'Despachos entrantes'
    
class ItemsDespachoEntrante(models.Model):
    id_item_despacho_entrante=models.AutoField(primary_key=True, editable=False, db_column='T154IdItem_DespachoEntrante')
    id_despacho_entrante=models.ForeignKey(DespachoEntrantes, on_delete=models.CASCADE, db_column='T154Id_DespachoEntrante')
    id_bien=models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T154Id_Bien')
    id_entrada_alm_del_bien=models.ForeignKey(EntradasAlmacen, on_delete=models.SET_NULL, blank=True, null=True, db_column='T154Id_EntradaAlmDelBien')
    fecha_ingreso=models.DateTimeField(db_column='T154fechaIngreso')
    cantidad_entrante=models.IntegerField(db_column='T154cantidadEntrante')
    cantidad_distribuida=models.IntegerField(db_column='T154cantidadDistribuida')
    observacion=models.CharField(max_length=50, db_column='T154observacion', blank=True, null=True)

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
    cantidad_asignada = models.IntegerField(db_column='T155cantidadAsignada')
    cod_etapa_lote_al_ingresar = models.CharField(max_length=1, choices=cod_etapa_lote_CHOICES, null=True, blank=True, db_column='T155codEtapaAIngresarMV')
    fecha_distribucion = models.DateTimeField(auto_now=True, db_column='T155fechaDistribucion')
    
    def __str__(self):
        return str(self.id_distribucion_item_despacho_entrante)

    class Meta:
        db_table = 'T155Distribuciones_Item_DespachoEntrante'
        verbose_name = 'Distribución Item Despacho Entrante'
        verbose_name_plural = 'Distribuciones Item Despacho Entrante'
        unique_together = ['id_item_despacho_entrante', 'id_vivero']

class DespachoViveros(models.Model):
    id_despacho_viveros  = models.AutoField(primary_key=True, editable=False, db_column='T175IdDespachoViveros')
    nro_despachos_viveros = models.IntegerField(unique=True, db_column='T175nroDespachoDeViveros')
    id_solicitud_a_viveros = models.ForeignKey(SolicitudesViveros, on_delete=models.CASCADE, db_column='T175id_SolicitudAViveros')
    fecha_solicitud_a_viveros = models.DateTimeField(db_column='T175fechaSolicitudAViveros')
    nro_solicitud_a_viveros = models.IntegerField(db_column='T175nroSolicitudAViveros')
    fecha_solicitud_retiro_material = models.DateField(db_column='T175fechaSolicitudRetiroMaterial')
    fecha_despacho = models.DateTimeField(db_column='T175fechaDespacho')
    fecha_registro = models.DateTimeField(auto_now=True, db_column='T175fechaRegistro')
    id_vivero = models.ForeignKey(Vivero, on_delete=models.CASCADE, db_column='T175Id_Vivero')
    id_persona_despacha = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T175Id_PersonaDespacha', related_name='persona_despacha_vivero')
    motivo = models.CharField(max_length=255, db_column='T175motivo')
    id_persona_solicita = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T175Id_PersonaSolicita', related_name='persona_solicita_vivero')
    id_unidad_para_la_que_solicita = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T175Id_UnidadParaLaQueSolicita')
    id_funcionario_responsable_unidad = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T175Id_FuncionarioResponsableUnidad', related_name='funcionario_responsable_unidad_vivero')
    despacho_anulado = models.BooleanField(default=False, db_column="T175despachoAnulado")
    justificacion_anulacion = models.CharField(max_length=255, blank=True, null=True, db_column='T175justificacionAnulacion')
    fecha_anulacion = models.DateTimeField(blank=True, null=True, db_column='T175fechaAnulacion')
    id_persona_anula = models.ForeignKey(Personas, blank=True, null=True, on_delete=models.SET_NULL, db_column='T175Id_PersonaAnula', related_name='persona_anula_vivero')
    ruta_archivo_con_recibido = models.FileField(db_column='T175rutaArchivoConRecibido', upload_to='conservacion/despachos/', max_length=255, blank=True, null=True)
    
    def __str__(self):
        return str(self.id_despacho_viveros)

    class Meta:
        db_table = 'T175DespachoViveros'
        verbose_name = 'Despacho vivero'
        verbose_name_plural = 'Despachos vivero'
        
class ItemsDespachoViveros(models.Model):
    id_item_despacho_viveros  = models.AutoField(primary_key=True, editable=False, db_column='T176IdItem_DespachoDeViveros')
    id_despacho_viveros = models.ForeignKey(DespachoViveros, on_delete=models.CASCADE, db_column='T176Id_DespachoDeViveros')
    id_bien = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T176Id_Bien')
    agno_lote = models.SmallIntegerField(blank=True, null=True, db_column='T176agnoLote')
    nro_lote = models.IntegerField(blank=True, null=True, db_column='T176nroLote')
    cod_etapa_lote = models.CharField(max_length=1, choices=cod_etapa_lote_CHOICES, blank=True, null=True, db_column='T176codEtapaLote')
    cantidad_solicitada = models.IntegerField(db_column='T176cantidadSolicitada')
    cantidad_despachada = models.IntegerField(db_column='T176cantidadDespachada')
    observacion_del_despacho = models.CharField(max_length=30, blank=True, null=True, db_column='T176observacionDelDespacho')
    nro_posicion_en_despacho = models.SmallIntegerField(blank=True, null=True, db_column='T176nroPosicionEnDespacho')
    
    def __str__(self):
        return str(self.id_item_despacho_viveros)

    class Meta:
        db_table = 'T176Items_DespachoDeViveros'
        verbose_name = 'Item despacho vivero'
        verbose_name_plural = 'Items despacho vivero'
        unique_together = ['id_despacho_viveros', 'id_bien', 'agno_lote', 'nro_lote', 'cod_etapa_lote']