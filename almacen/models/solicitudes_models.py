from django.db import models
from transversal.models.personas_models import Personas
from conservacion.models.viveros_models import Vivero
from transversal.models.organigrama_models import UnidadesOrganizacionales
from transversal.choices.tipo_unidad_choices import tipo_unidad_CHOICES
from almacen.models.generics_models import UnidadesMedida
from almacen.models.bienes_models import (
    EntradasAlmacen, 
    Bodegas,
    CatalogoBienes
)

class SolicitudesConsumibles(models.Model):
    id_solicitud_consumibles = models.AutoField(primary_key=True, db_column='T081IdSolicitudConsumibles')
    es_solicitud_de_conservacion = models.BooleanField(default=False, db_column='T081esSolicitudDeConservacion')
    nro_solicitud_por_tipo = models.IntegerField(db_column='T081nroSolicitudPorTipo')
    fecha_solicitud = models.DateTimeField(db_column='T081fechaSolicitud')
    motivo = models.CharField(max_length=255, db_column='T081motivo')
    observacion = models.CharField(max_length=255, db_column='T081observacion', null=True, blank=True)
    id_persona_solicita = models.ForeignKey(Personas, db_column='T081Id_PersonaSolicita', on_delete=models.CASCADE, related_name='persona_solicita_solicitud')
    id_vivero_solicita = models.ForeignKey(Vivero, db_column='T081Id_ViveroSolicita', on_delete=models.SET_NULL, blank=True, null=True, related_name='id_vivero_solicita_consumible')
    id_unidad_org_del_solicitante = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T081Id_UnidadOrgDelSolicitante', related_name='unidad_organizacional_solicitante')
    id_unidad_para_la_que_solicita = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T081Id_UnidadParaLaQueSolicita', related_name='unidad_para_la_que_solicita')
    id_funcionario_responsable_unidad = models.ForeignKey(Personas, db_column='T081Id_FuncionarioResponsableUnidad', on_delete=models.CASCADE, related_name='funcionario_responsable_unidad')
    id_unidad_org_del_responsable = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T081Id_UnidadOrgDelResponsable', related_name='unidad_org_del_responsable')
    solicitud_abierta = models.BooleanField(db_column='T081solicitudAbierta', default=True)
    fecha_cierre_solicitud = models.DateTimeField(db_column='T081fechaCierreSolicitud', null=True, blank=True)
    revisada_responsable = models.BooleanField(db_column='T081revisadaResponsable', default = False)
    estado_aprobacion_responsable = models.CharField(max_length=1, db_column='T081estadoAprobacionResponsable', null=True, blank=True)
    justificacion_rechazo_responsable = models.CharField(max_length=255, db_column='T081justificacionRechazoResponsable', null=True, blank=True)
    fecha_aprobacion_responsable = models.DateTimeField(db_column='T081fechaAprobacionResponsable', null=True, blank=True)
    gestionada_almacen = models.BooleanField(db_column='T081gestionadaAlmacen', default = False)
    id_despacho_consumo = models.ForeignKey('DespachoConsumo', on_delete=models.SET_NULL, db_column='T081Id_DespachoConsumo', null=True, blank=True)
    observacion_cierre_no_dispo_alm = models.CharField(max_length=255, null=True, blank=True, db_column='T081ObservCierreNoDispoAlm')
    fecha_cierre_no_dispo_alm = models.DateTimeField(null=True, blank=True, db_column='T081fechaCierreNoDispoAlm')
    id_persona_cierre_no_dispo_alm = models.ForeignKey(Personas, related_name='persona_cierre_no_disponible', null=True, blank=True, on_delete=models.SET_NULL, db_column='T081Id_PersonaCierreNoDispoAlm')
    rechazada_almacen = models.BooleanField(db_column='T081rechazadaAlmacen', null=True, blank=True)
    fecha_rechazo_almacen = models.DateTimeField(db_column='T081fechaRechazoAlmacen', null=True, blank=True)
    justificacion_rechazo_almacen = models.CharField(max_length=255, db_column='T081justificacionRechazoAlmacen', null=True, blank=True)
    id_persona_almacen_rechaza = models.ForeignKey(Personas, related_name='persona_rechaza_almacen', null=True, blank=True, on_delete=models.SET_NULL, db_column='T081Id_PersonaAlmacenRechaza')
    solicitud_anulada_solicitante = models.BooleanField(db_column='T081solicitudAnuladaSolicitante', null=True, blank=True)
    justificacion_anulacion_solicitante = models.CharField(max_length=255, db_column='T081justificacionAnulacionSolicitante', null=True, blank=True)
    fecha_anulacion_solicitante = models.DateTimeField(db_column='T081fechaAnulacionSolicitante', null=True, blank=True)
    
    def __str__(self):
        return str(self.id_solicitud_consumibles)

    class Meta:
        db_table = 'T081SolicitudesConsumibles'
        verbose_name = 'Solicitud de consumible'
        verbose_name_plural = 'Solicitudes de consumibles'
        unique_together = ['es_solicitud_de_conservacion', 'nro_solicitud_por_tipo']
        
class ItemsSolicitudConsumible(models.Model):
    id_item_solicitud_consumible = models.AutoField(primary_key=True, db_column='T082IdItem_SolicitudConsumible')
    id_solicitud_consumibles = models.ForeignKey(SolicitudesConsumibles, on_delete=models.CASCADE, db_column='T082Id_SolicitudConsumibles')
    id_bien = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T082Id_Bien')
    cantidad = models.SmallIntegerField(db_column='T082cantidad')
    id_unidad_medida = models.ForeignKey(UnidadesMedida, on_delete=models.CASCADE, db_column='T082Id_UnidadMedida')
    observaciones = models.CharField(max_length=30, db_column='T082observaciones', null=True, blank=True)
    nro_posicion = models.SmallIntegerField(db_column='T082nroPosicion')
    
    def __str__(self):
        return str(self.id_item_solicitud_consumible)

    class Meta:
        db_table = 'T082Items_SolicitudConsumible'
        verbose_name = 'Item de la solicitud del consumible'
        verbose_name_plural = 'Items de la solicitud del consumible'
        unique_together = ['id_solicitud_consumibles', 'id_bien']

class DespachoConsumo(models.Model):
    id_despacho_consumo = models.AutoField(primary_key=True, editable=False, db_column='T083IdDespachoConsumo')
    numero_despacho_consumo = models.IntegerField(unique=True, db_column='T083nroDespachoConsumo')
    id_solicitud_consumo = models.ForeignKey(SolicitudesConsumibles, null=True, blank=True, on_delete=models.SET_NULL, db_column='T083Id_SolicitudConsumo')
    numero_solicitud_por_tipo = models.IntegerField(null=True, blank=True, db_column='T083nroSolicitudPorTipo')
    fecha_solicitud = models.DateTimeField(null=True, blank=True, db_column='T083fechaSolicitud')
    fecha_despacho = models.DateTimeField(db_column='T083fechaDespacho')
    fecha_registro = models.DateTimeField(auto_now_add=True, db_column='T083fechaRegistro')    
    id_persona_despacha = models.ForeignKey(Personas, related_name='persona_despacha', on_delete=models.CASCADE, db_column='T083Id_PersonaDespacha')
    motivo = models.CharField(max_length=255, null=True, blank=True, db_column='T083motivo')
    id_persona_solicita = models.ForeignKey(Personas, related_name='persona_solicita', null=True, blank=True, on_delete=models.SET_NULL, db_column='T083Id_PersonaSolicita')
    id_vivero_solicita = models.ForeignKey(Vivero, db_column='T083Id_ViveroSolicita', on_delete=models.SET_NULL, blank=True, null=True, related_name='id_vivero_solicita_despacho')
    id_unidad_para_la_que_solicita = models.ForeignKey(UnidadesOrganizacionales, null=True, blank=True, on_delete=models.SET_NULL, db_column='T083Id_UnidadParaLaQueSolicita')
    id_funcionario_responsable_unidad = models.ForeignKey(Personas, related_name='persona_funcionario_responsable_unidad', null=True, blank=True, on_delete=models.SET_NULL, db_column='T083Id_FuncionarioResponsableUnidad')
    es_despacho_conservacion = models.BooleanField(default=False, db_column='T083esDespachoDeConservacion')
    id_entrada_almacen_cv = models.ForeignKey(EntradasAlmacen, null=True, blank=True, on_delete=models.SET_NULL, db_column='T083Id_EntradaAlmacenCV')
    id_bodega_general = models.ForeignKey(Bodegas, on_delete=models.SET_NULL, blank=True, null=True, db_column='T083Id_BodegaGral')
    despacho_anulado = models.BooleanField(null=True, blank=True, db_column='T083despachoAnulado')
    justificacion_anulacion = models.CharField(max_length=255, null=True, blank=True, db_column='T083justificacionAnulacion')
    fecha_anulacion = models.DateTimeField(null=True, blank=True, db_column='T083fechaAnulacion')
    id_persona_anula = models.ForeignKey(Personas, related_name='persona_anula_despacho', null=True, blank=True, on_delete=models.SET_NULL, db_column='T083Id_PersonaAnula')
    ruta_archivo_doc_con_recibido = models.FileField(db_column='T083rutaArchivoDocConRecibido', upload_to='almacen/despachos_consumo/', max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.numero_despacho_consumo)
    
    class Meta:
        db_table = 'T083DespachosConsumo'
        verbose_name = 'Despacho Consumo'
        verbose_name_plural = 'Despachos Consumo'

class ItemDespachoConsumo(models.Model):
    id_item_despacho_consumo = models.AutoField(primary_key=True, editable=False, db_column='T084IdItem_DespachoConsumo')
    id_despacho_consumo = models.ForeignKey(DespachoConsumo, on_delete=models.CASCADE, db_column='T084Id_DespachoConsumo')
    id_bien_despachado = models.ForeignKey(CatalogoBienes, related_name='bien_despachado', null=True, blank=True, on_delete=models.SET_NULL, db_column='T084Id_BienDespachado')
    id_bien_solicitado = models.ForeignKey(CatalogoBienes, related_name='bien_solicitado', null=True, blank=True, on_delete=models.SET_NULL, db_column='T084Id_BienSolicitado')
    id_entrada_almacen_bien = models.ForeignKey(EntradasAlmacen, null=True, blank=True, on_delete=models.SET_NULL, db_column='T084Id_EntradaAlmacenDelBien')
    id_bodega = models.ForeignKey(Bodegas, null=True, blank=True, on_delete=models.SET_NULL, db_column='T084Id_Bodega')
    cantidad_solicitada = models.IntegerField(null=True, blank=True, db_column='T084cantidadSolicitada')
    id_unidad_medida_solicitada = models.ForeignKey(UnidadesMedida, null=True, blank=True, on_delete=models.SET_NULL, db_column='T084Id_UnidadMedidaSolicitada')
    cantidad_despachada = models.IntegerField(db_column='T084cantidadDespachada')
    observacion = models.CharField(max_length=50, null=True, blank=True, db_column='T084observacion')
    numero_posicion_despacho = models.SmallIntegerField(db_column='T084nroPosicionEnDespacho')

    def __str__(self):
        return str(self.id_item_despacho_consumo)
    
    class Meta:
        db_table = 'T084Items_DespachoConsumo'
        verbose_name = 'Item Despacho Consumo'
        verbose_name_plural = 'Items Despachos Consumo'
        unique_together = ['id_despacho_consumo', 'id_bien_despachado', 'id_bien_solicitado', 'id_entrada_almacen_bien', 'id_bodega']