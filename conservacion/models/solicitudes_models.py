from django.db import models
from conservacion.models.viveros_models import Vivero
from transversal.choices.municipios_choices import municipios_CHOICES
from conservacion.choices.estado_aprobacion_choices import estado_aprobacion_CHOICES
from transversal.models.base_models import Municipio
from transversal.models.personas_models import Personas
from transversal.models.organigrama_models import UnidadesOrganizacionales
from almacen.models.bienes_models import CatalogoBienes


class SolicitudesViveros(models.Model):
    id_solicitud_vivero = models.AutoField(primary_key=True, editable=False, db_column='T173IdSolicitudAViveros')
    nro_solicitud = models.IntegerField(unique=True, db_column='T173nroSolicitud')
    fecha_solicitud = models.DateTimeField(auto_now_add=True, db_column='T173fechaSolicitud')
    motivo = models.CharField(max_length=30, db_column='T173motivo')
    observaciones = models.CharField(max_length=255, blank=True, null=True, db_column='T173observaciones')
    id_vivero_solicitud = models.ForeignKey(Vivero, on_delete=models.CASCADE, db_column='T173Id_ViveroSolicitud')
    con_municipio_destino = models.ForeignKey(Municipio, on_delete=models.CASCADE, db_column='T173Cod_MunicipioDestino')
    direccion_destino = models.CharField(max_length=255, db_column='T173direccionDestino')
    nombre_predio_destino = models.CharField(max_length=255, db_column='T173nombrePredioDestino')
    coordenadas_destino_lat = models.DecimalField(max_digits=18, decimal_places=13, db_column='T173coordenadasDestinoLat')
    coordenadas_destino_lon = models.DecimalField(max_digits=18, decimal_places=13, db_column='T173coordenadasDestinoLon')
    fecha_retiro_material = models.DateField(db_column='T173fechaRetiroMaterial')
    nro_info_tecnico = models.CharField(max_length=30, db_column='T173nroInfoTecnico')
    ruta_archivo_info_tecnico = models.FileField(max_length=255, upload_to='conservacion/solicitudes/', blank=True, null=True, db_column='T173rutaArchivoInfoTecnico')
    id_persona_solicita = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T173Id_PersonaSolicita', related_name='id_persona_solicita_viveros')
    id_unidad_org_del_solicitante = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T173Id_UnidadOrgDelSolicitante', related_name='id_unidad_org_del_solicitante_viveros')
    id_unidad_para_la_que_solicita = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T173Id_UnidadParaLaQueSolicita', related_name='id_unidad_para_la_que_solicita_viveros') 
    id_funcionario_responsable_und_destino = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T173Id_FuncionarioResponsableUndDestino', related_name='id_funcionario_responsable_und_destino_solicitud')   
    id_unidad_org_del_responsable = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T173Id_UnidadOrgDelResponsable', related_name='id_unidad_org_del_responsable_viveros')
    solicitud_abierta = models.BooleanField(default=True, db_column='T173solicitudAbierta')
    fecha_cierra_solicitud = models.DateTimeField(blank=True, null=True, db_column='T173fechaCierreSolicitud')
    revisada_responsable = models.BooleanField(default=False, db_column='T173revisadaResponsable')
    estado_aprobacion_responsable = models.CharField(max_length=1, choices=estado_aprobacion_CHOICES, null=True, blank=True, db_column='T173estadoAprobacionResponsable')
    justificacion_aprobacion_responsable = models.CharField(max_length=255, blank=True, null=True, db_column='T173justificacionAprobacionResponsable')
    fecha_aprobacion_responsable = models.DateTimeField(null=True, blank=True, db_column='T173fechaAprobacionResponsable')
    gestionada_viveros = models.BooleanField(default=True, db_column='T173gestionadaViveros')
    id_despacho_viveros = models.ForeignKey('conservacion.DespachoViveros', on_delete=models.SET_NULL, blank=True, null=True, db_column='T173Id_DespachoDeViveros')
    observacion_cierre_no_dispo_viveros = models.CharField(max_length=255, blank=True, null=True, db_column='T173observacionCierreNoDispoViveros')
    fecha_cierre_no_dispo = models.DateTimeField(blank=True, null=True, db_column='T173fechaCierreNoDispo')
    id_persona_cierre_no_dispo_viveros = models.ForeignKey(Personas, on_delete=models.SET_NULL, blank=True, null=True, db_column='T173Id_PersonaCierreNoDispoViveros', related_name='id_persona_cierre_no_dispo_viveros_solicitud')
    revisada_coord_viveros = models.BooleanField(default=False, db_column='T173revisadaCoordViveros')
    estado_aprobacion_coord_viveros = models.CharField(max_length=1, choices=estado_aprobacion_CHOICES, null=True, blank=True, db_column='T173estadoAprobacionCoordViveros')
    justificacion_aprobacion_coord_viveros = models.CharField(max_length=255, blank=True, null=True, db_column='T173justificacionAprobacionCoordViv')
    fecha_aprobacion_coord_viv = models.DateTimeField(blank=True, null=True, db_column='T173fechaAprobacionCoordViv')
    id_persona_coord_viveros = models.ForeignKey(Personas, on_delete=models.SET_NULL, blank=True, null=True, db_column='T173Id_PersonaCoordViveros', related_name='id_persona_coord_viveros_solicitd')
    solicitud_anulada_solicitante = models.BooleanField(default=False, db_column='T173solicitudAnuladaSolicitante')
    justificacion_anulacion_solicitante = models.CharField(max_length=255, blank=True, null=True, db_column='T173justificacionAnulacionSolicitante')
    fecha_anulacion_solicitante = models.DateTimeField(blank=True, null=True, db_column='T173fechaAnulacionSolicitante')
    
    def __str__(self):
        return str(self.id_solicitud_vivero)
    
    class Meta:
        db_table = 'T173SolicitudesAViveros'
        verbose_name = 'Solicitud vivero'
        verbose_name_plural = 'Solicitudes vivero'

class ItemSolicitudViveros(models.Model):
    id_item_solicitud_viveros = models.AutoField(primary_key=True, editable=False, db_column='T174IdItem_SolicitudAViveros')
    id_solicitud_viveros = models.ForeignKey(SolicitudesViveros, on_delete=models.CASCADE, db_column='T174Id_SolicitudAViveros')
    id_bien = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T174Id_Bien')
    cantidad = models.IntegerField(db_column='T174cantidad')
    observaciones = models.CharField(max_length=30, blank=True, null=True, db_column='T174observaciones')
    nro_posicion = models.SmallIntegerField(db_column='T174nroPosicion')
    
    def __str__(self):
        return str(self.id_item_solicitud_viveros)
    
    class Meta:
        db_table = 'T174Items_SolicitudAViveros'
        verbose_name = 'Item solicitud vivero'
        verbose_name_plural = 'items solicitud viveros'
        unique_together = ['id_solicitud_viveros','id_bien']
        