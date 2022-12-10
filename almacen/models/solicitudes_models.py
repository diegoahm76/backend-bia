from django.db import models
from seguridad.models import Personas
from almacen.models.organigrama_models import UnidadesOrganizacionales
from almacen.models.bienes_models import CatalogoBienes
from almacen.choices.tipo_unidad_choices import tipo_unidad_CHOICES
from almacen.models.generics_models import UnidadesMedida

class SolicitudesConsumibles(models.Model):
    id_solicitud_consumible = models.AutoField(primary_key=True, db_column='T081IdSolicitudConsumibles')
    es_solicitud_de_conservacion = models.BooleanField(default = False, db_column='T081esSolicitudDeConservacion')
    nro_solicitud_por_tipo = models.IntegerField(db_column='T081nroSolicitudPorTipo')
    fecha_solicitud = models.DateField(db_column='T081fechaSolicitud')
    motivo = models.CharField(max_length=255, db_column='T081motivo')
    observacion = models.CharField(max_length=255, db_column='T081observacion', null=True, blank=True)
    id_persona_solicita = models.ForeignKey(Personas, db_column='T081Id_PersonaSolicita', on_delete=models.CASCADE, related_name='persona_solicita')
    id_unidad_org_del_solicitante = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T081Id_UnidadOrgDelSolicitante', related_name='unidad_organizacional_solicitante')
    id_unidad_para_la_que_solicita = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T081Id_UnidadParaLaQueSolicita', related_name='funcionario_responsable_unidad')
    id_funcionario_responsable_unidad = models.ForeignKey(Personas, db_column='T081Id_FuncionarioResponsableUnidad', on_delete=models.CASCADE, related_name='funcionario_responsable_unidad')
    id_unidad_org_del_responsable = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T081Id_UnidadOrgDelResponsable', related_name='unidad_org_del_responsable')
    solicitud_abierta = models.BooleanField(db_column='T081solicitudAbierta', null=True, blank=True)
    fecha_cierre_solicitud = models.DateField(db_column='T081fechaCierreSolicitud', null=True, blank=True)
    revisada_responsable = models.BooleanField(db_column='T081revisadaResponsable', default = False)
    estado_aprobacion_responsable = models.CharField(max_length=1, db_column='T081estadoAprobacionResponsable', null=True, blank=True)
    justificacion_rechazo_responsable = models.CharField(max_length=255, db_column='T081justificacionRechazoResponsable', null=True, blank=True)
    fecha_aprobacion_responsable = models.DateField(db_column='T081fechaAprbacionResponsable', null=True, blank=True)
    gestionada_almacen = models.BooleanField(db_column='T081gestionadaAlmacen', default = False)
    id_despacho_consumo = models.CharField(max_length=255, db_column='T081Id_DespachoConsumo', null=True, blank=True)
    rechazada_almacen = models.BooleanField(db_column='T081rechazadaAlmacen', null=True, blank=True)
    fecha_rechazo_almacen = models.DateField(db_column='T081fechaRechazoAlmacen', null=True, blank=True)
    justificacion_rechazo_almacen = models.CharField(max_length=255, db_column='T081justificacionRechazoAlmacen', null=True, blank=True)
    solicitud_anulada_solicitante = models.BooleanField(db_column='T081solicitudAnuladaSolicitante', null=True, blank=True)
    justificacion_anulacion_solicitante = models.CharField(max_length=255, db_column='T081justificacionAnulacionSolicitante', null=True, blank=True)
    fecha_anulacion_solicitante = models.DateField(db_column='T081fechaAnulacionSolicitante', null=True, blank=True)
    
    def __str__(self):
        return str(self.id_solicitud_consumible)

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