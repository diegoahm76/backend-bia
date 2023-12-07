from django.db import models
from gestion_documental.models.expedientes_models import ArchivosDigitales, ExpedientesDocumentales
from gestion_documental.models.radicados_models import EstadosSolicitudes, MediosSolicitud, T262Radicados
from gestion_documental.models.trd_models import ConsecPorNivelesTipologiasDocAgno
from transversal.models.entidades_models import SucursalesEmpresas
from tramites.choices.cod_tipo_operacion_tramite_choices import cod_tipo_operacion_tramite_CHOICES
from gestion_documental.choices.codigo_relacion_titular_choices import cod_relacion_persona_titular_CHOICES
from tramites.choices.cod_calendario_habiles_choices import cod_calendario_habiles_CHOICES
from tramites.choices.cod_tipo_permiso_ambiental_choices import cod_tipo_permiso_ambiental_CHOICES

from transversal.models.personas_models import Personas

class SolicitudesTramites(models.Model):
    id_solicitud_tramite = models.AutoField(primary_key=True, db_column='T273IdSolicitudTramite')
    id_persona_titular = models.ForeignKey(Personas, on_delete=models.CASCADE, related_name='id_persona_titular_tramite', db_column='T273Id_PersonaTitular')
    id_persona_interpone = models.ForeignKey(Personas, on_delete=models.CASCADE, related_name='id_persona_interpone_tramite', db_column='T273Id_PersonaInterpone')
    cod_relacion_con_el_titular = models.CharField(max_length=2, choices=cod_relacion_persona_titular_CHOICES, db_column='T273codRelacionConElTitular')
    cod_tipo_operacion_tramite = models.CharField(max_length=1, choices=cod_tipo_operacion_tramite_CHOICES, db_column='T273codTipoOperacionTramite')
    nombre_proyecto = models.CharField(max_length=255, db_column='T273nombreProyecto')
    costo_proyecto = models.DecimalField(max_digits=19, decimal_places=2, db_column='T273costoProyecto')
    pago = models.BooleanField(default=False, db_column='T273pago')
    id_pago_evaluacion = models.IntegerField(null=True, blank=True, db_column='T273Id_PagoEvaluacion')
    id_medio_solicitud = models.ForeignKey(MediosSolicitud, on_delete=models.CASCADE, db_column='T273Id_MedioSolicitud')
    fecha_registro = models.DateTimeField(auto_now_add=True, blank=True, db_column='T273fechaRegistro')
    fecha_envio_solicitud = models.DateTimeField(null=True, blank=True, db_column='T273fechaEnvioSolicitud')
    fecha_finalizada_solicitud = models.DateTimeField(null=True, blank=True, db_column='T273fechaFinalizadaSolicitud')
    id_persona_registra = models.ForeignKey(Personas, on_delete=models.CASCADE, related_name="id_persona_registra_tramite", db_column='T273Id_PersonaRegistra')
    cantidad_predios = models.IntegerField(null=True, blank=True, db_column='T273cantidadPredios')
    solicitud_enviada = models.BooleanField(default=False, db_column='T273solicitudEnviada')
    id_sucursal_recepcion_fisica = models.ForeignKey(SucursalesEmpresas, on_delete=models.SET_NULL, null=True, blank=True, db_column='T273Id_Sucursal_RecepcionFisica')
    id_radicado = models.ForeignKey(T262Radicados, on_delete=models.SET_NULL, null=True, blank=True, db_column='T273Id_Radicado')
    fecha_radicado = models.DateTimeField(null=True, blank=True, db_column='T273fechaRadicado')
    id_expediente = models.ForeignKey(ExpedientesDocumentales, on_delete=models.SET_NULL, null=True, blank=True, db_column='T273Id_Expediente')
    fecha_expediente = models.DateTimeField(null=True, blank=True, db_column='T273fechaExpediente')
    id_auto_inicio = models.ForeignKey('ActosAdministrativos', on_delete=models.SET_NULL, null=True, blank=True, db_column='T273Id_AutoInicio')
    fecha_inicio = models.DateTimeField(null=True, blank=True, db_column='T273fechaInicio')
    requiere_digitalizacion = models.BooleanField(default=False, db_column='T273requiereDigitalizacion')
    fecha_envio_definitivo_a_digitalizacion = models.DateTimeField(null=True, blank=True, db_column='T273fechaEnvioDefinitivoADigitalizacion')
    fecha_digitalizacion_completada = models.DateTimeField(null=True, blank=True, db_column='T273fechaDigitalizacionCompletada')
    fecha_rta_final_gestion = models.DateTimeField(null=True, blank=True, db_column='T273fechaRtaFinalGestion')
    id_persona_rta_final_gestion = models.ForeignKey(Personas, on_delete=models.SET_NULL, null=True, blank=True, related_name='id_persona_rta_final_gestion_tramite', db_column='T273Id_PersonaRtaFinalGestion')
    id_estado_actual_solicitud = models.ForeignKey(EstadosSolicitudes, on_delete=models.CASCADE, db_column='T273Id_EstadoActualSolicitud')
    fecha_ini_estado_actual = models.DateTimeField(db_column='T273fechaIniEstadoActual')

    def __str__(self):
        return str(self.id_solicitud_tramite)
    
    class Meta:
        db_table = 'T273SolicitudesTramites'
        verbose_name = 'Solicitud Trámite'
        verbose_name_plural = 'Solicitudes Trámites'

class PermisosAmbSolicitudesTramite(models.Model):
    id_permiso_amb_solicitud_tramite = models.AutoField(primary_key=True, db_column='T280IdPermisoAmbSolicitudTramite')
    id_permiso_ambiental = models.ForeignKey('PermisosAmbientales', on_delete=models.CASCADE, db_column='T280Id_PermisoAmbiental')
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, on_delete=models.CASCADE, db_column='T280Id_SolicitudTramite')
    descripcion_direccion = models.CharField(max_length=250, null=True, blank=True, db_column='T280descripcionDireccion')
    coordenada_x = models.CharField(max_length=20, null=True, blank=True, db_column='T280coordenadaX')
    coordenada_y = models.CharField(max_length=20, null=True, blank=True, db_column='T280coordenadaY')

    def __str__(self):
        return str(self.id_permiso_amb_solicitud_tramite)

    class Meta:
        db_table = 'T280PermisosAmbSolicitudesTramite'

class PermisosAmbientales(models.Model):
    id_permiso_ambiental = models.AutoField(primary_key=True, db_column='T281IdPermisoAmbiental')
    cod_tipo_permiso_ambiental = models.CharField(max_length=1, choices=cod_tipo_permiso_ambiental_CHOICES, db_column='T281codTipoPermisoAmbiental')
    nombre = models.CharField(max_length=250, db_column='T281nombre')
    tiene_pago = models.BooleanField(default=True, db_column='T281tienePago')

    def __str__(self):
        return str(self.id_permiso_ambiental)

    class Meta:
        db_table = 'T281PermisosAmbientales'

class ActosAdministrativos(models.Model):
    id_acto_administrativo = models.AutoField(primary_key=True, db_column='T294IdActoAdministrativo')
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, on_delete=models.CASCADE, db_column='T294Id_SolicitudTramite')
    id_tipo_acto_administrativo = models.ForeignKey('TiposActosAdministrativos', on_delete=models.CASCADE, db_column='T294Id_TipoActoAdministrativo')
    fecha_acto_administrativo = models.DateTimeField(null=True, blank=True, db_column='T294fechaActoAdministrativo')
    id_consec_por_nivel_tipologias_doc_agno = models.ForeignKey(ConsecPorNivelesTipologiasDocAgno, on_delete=models.CASCADE, db_column='T294Id_ConsecPorNivel_TipologiasDocAgno')
    id_notificacion = models.IntegerField(db_column='T294Id_Notificacion')
    fecha_notificacion = models.DateTimeField(db_column='T294fechaNotificacion')
    procede_reposicion = models.BooleanField(null=True, blank=True, db_column='T294procedeReposicion')
    fecha_limite_reposicion = models.DateTimeField(null=True, blank=True, db_column='T294fechaLimiteReposicion')
    id_archivo_acto_administrativo = models.ForeignKey(ArchivosDigitales, on_delete=models.CASCADE, db_column='T294Id_ArchivoActoAdministrativo')
    id_persona_publica_acto = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T294Id_PersonaPublicaActo')
    estado_actual = models.IntegerField(db_column='T294estadoActual')

    def __str__(self):
        return str(self.id_acto_administrativo)

    class Meta:
        db_table = 'T294ActosAdministrativos'
        verbose_name = 'Acto Administrativo'
        verbose_name_plural = 'Actos Administrativos'
        
class TiposActosAdministrativos(models.Model):
    id_tipo_acto_administrativo = models.AutoField(primary_key=True, db_column='T295IdTipoActoAdministrativo')
    tipo_acto_administrativo = models.CharField(max_length=255, db_column='T295tipoActoAdministrativo')
    notifiquese = models.BooleanField(default=False, db_column='T295notifiquese')
    comuniquese = models.BooleanField(default=False, db_column='T295comuniquese')
    publiquese = models.BooleanField(default=False, db_column='T295publiquese')
    cumplase = models.BooleanField(default=False, db_column='T295cumplase')
    procede_reposicion = models.BooleanField(null=True, blank=True, db_column='T295procedeReposicion')
    dias_procede_reposicion = models.IntegerField(db_column='T295diasProcedeReposicion')
    cod_calendario_habiles = models.CharField(max_length=1, choices=cod_calendario_habiles_CHOICES, null=True, blank=True, db_column='T295codCalendarioHabiles')
    item_ya_usado = models.BooleanField(null=True, blank=True, db_column='T295itemYaUsado')

    def __str__(self):
        return str(self.id_tipo_acto_administrativo)

    class Meta:
        db_table = 'T295TiposActosAdministrativos'
        verbose_name = 'Tipo Acto Administrativo'
        verbose_name_plural = 'Tipos Actos Administrativos'