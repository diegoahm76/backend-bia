from django.db import models
from gestion_documental.choices.tipo_soli_noti_choices import tipo_soli_noti_CHOICES
from gestion_documental.choices.pqrsdf_choices import RELACION_TITULAR
from gestion_documental.choices.cod_medio_solicitud_choices import cod_medio_solicitud_CHOICES
from gestion_documental.choices.cod_estado_noti_choices import cod_estado_noti_CHOICES
from gestion_documental.choices.habiles_calendario_choices import habiles_calendario_CHOICES
from gestion_documental.choices.estado_asignacion_choices import ESTADO_ASIGNACION_CHOICES
from gestion_documental.choices.doc_entrada_salida_choices import doc_entrada_salida_CHOICES
from gestion_documental.choices.uso_del_documento_choices import uso_del_documento_CHOICES
from gestion_documental.choices.doc_generado_choices import doc_generado_CHOICES

from gestion_documental.models.expedientes_models import DocumentosDeArchivoExpediente, ExpedientesDocumentales
from transversal.models.base_models import Municipio
from transversal.models.organigrama_models import UnidadesOrganizacionales
from gestion_documental.models.radicados_models import Anexos, T262Radicados
from tramites.models import ActosAdministrativos, SolicitudesTramites

 

class NotificacionesCorrespondencia(models.Model):
    id_notificacion_correspondencia = models.SmallAutoField(primary_key=True, db_column='T350IdNotificacionCorrespondencia')
    cod_tipo_solicitud = models.CharField(choices=tipo_soli_noti_CHOICES, max_length=2, db_column='T350codTipoSolicitud')
    #cod_tipo_documento = models.ForeignKey('TiposDocumentos', on_delete=models.CASCADE, db_column='T350codTipoDocumento',related_name='T350codTipoDocumento')
    id_expediente_documental = models.ForeignKey(ExpedientesDocumentales, on_delete=models.SET_NULL, null=True, blank=True, db_column='T350Id_ExpedienteDocumental', related_name='T350IdExpedienteDocumental')
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, on_delete=models.SET_NULL, null=True, blank=True, db_column='T350Id_SolicitudTramite',related_name='T350IdSolicitudTramite')
    id_acto_administrativo = models.ForeignKey(ActosAdministrativos, on_delete=models.SET_NULL, null=True, blank=True, db_column='T350Id_ActoAdministrativo',related_name='T350IdActoAdministrativo')
    procede_recurso_reposicion = models.BooleanField(null=True, db_column='T350procedeRecursoReposicion')
    id_persona_titular = models.ForeignKey('transversal.Personas', on_delete=models.SET_NULL, null=True, blank=True, db_column='T350Id_PersonaTitular',related_name='T350IdPersonaTitular')
    id_persona_interpone = models.ForeignKey('transversal.Personas', on_delete=models.SET_NULL, null=True, blank=True, db_column='T350Id_PersonaInterpone',related_name='T350IdPersonaInterpone')
    cod_relacion_con_titular = models.CharField(choices=RELACION_TITULAR, max_length=2, null=True, db_column='T350codRelacionConTitular')
    es_anonima = models.BooleanField(null=True, db_column='T350esAnonima')
    permite_notificacion_email = models.BooleanField(null=True, db_column='T350permiteNotificacionEmail')
    persona_a_quien_se_dirige = models.CharField(max_length=255, null=True, db_column='T350personaAQuienSeDirige')
    cod_tipo_documentoID = models.ForeignKey('transversal.TipoDocumento', on_delete=models.CASCADE, db_column='T350codTipoDocumentoID',related_name='T350codTipoDocumentoID')
    nro_documentoID = models.CharField(max_length=20, db_column='T350nroDocumentoID')
    cod_municipio_notificacion_nal = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True, blank=True, db_column='T350codMunicipioNotificacionNal',related_name='T350codMunicipioNotificacionNal')
    dir_notificacion_nal = models.CharField(max_length=255, null=True, db_column='T350dirNotificacionNal')
    tel_celular = models.CharField(max_length=15, null=True, db_column='T350telCelular')
    tel_fijo = models.CharField(max_length=15, null=True, db_column='T350telFijo')
    email_notificacion = models.CharField(max_length=100, null=True, db_column='T350emailNotificacion')
    asunto = models.CharField(max_length=100, db_column='T350asunto')
    descripcion = models.CharField(max_length=500, null=True, db_column='T350descripcion')
    cod_medio_solicitud = models.CharField(choices=cod_medio_solicitud_CHOICES, max_length=2, db_column='T350codMedioSolicitud')
    fecha_solicitud = models.DateTimeField(db_column='T350fechaSolicitud')
    id_persona_solicita = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, db_column='T350Id_PersonaSolicita',related_name='T350IdPersonaSolicita')
    id_und_org_oficina_solicita = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T350Id_UndOrgOficinaSolicita',related_name='T350IdUndOrgOficinaSolicita')
    allega_copia_fisica = models.BooleanField(null=True, db_column='T350allegaCopiaFisica')
    cantidad_anexos = models.SmallIntegerField(null=True, db_column='T350cantidadAnexos')
    nro_folios_totales = models.SmallIntegerField(null=True, db_column='T350nroFoliosTotales')
    id_persona_recibe_solicitud_manual = models.ForeignKey('transversal.Personas', on_delete=models.SET_NULL, null=True, blank=True, db_column='T350Id_PersonaRecibeSolicitudManual',related_name='T350IdPersonaRecibeSolicitudManual')
    requiere_digitalizacion = models.BooleanField(null=True, db_column='T350requiereDigitalizacion')
    fecha_envio_definitivo_a_digitalizacion = models.DateTimeField(null=True, db_column='T350fechaEnvioDefinitivoADigitalizacion')
    fecha_digitalizacion_completada = models.DateTimeField(null=True, db_column='T350fechaDigitalizacionCompletada')
    ya_digitizado = models.BooleanField(null=True, db_column='T350yaDigitizado')
    fecha_rta_final_gestion = models.DateTimeField(null=True, db_column='T350fechaRtaFinalGestion')
    id_persona_rta_final_gestion = models.ForeignKey('transversal.Personas', on_delete=models.SET_NULL, null=True, blank=True, db_column='T350Id_PersonaRtaFinalGestion',related_name='T350IdPersonaRtaFinalGestion')
    solicitud_aceptada_rechazada = models.BooleanField(null=True, db_column='T350solicitudAceptadaRechazada')
    fecha_devolucion = models.DateTimeField(null=True, db_column='T350fechaDevolucion')
    cod_estado = models.CharField(choices=cod_estado_noti_CHOICES, max_length=2, db_column='T350codEstado')
    id_doc_de_arch_exp = models.ForeignKey(DocumentosDeArchivoExpediente, on_delete=models.SET_NULL, null=True, blank=True, db_column='T350Id_DocDeArchExp',related_name='T350IdDocDeArchExp')

    class Meta:
        db_table = 'T350NotificacionesCorrespondencia'


class Registros_NotificacionesCorrespondecia(models.Model):
    id_registro_notificacion_correspondencia = models.SmallAutoField(primary_key=True, db_column='T352IdRegistro_NotificacionCorrespondencia')
    id_notificacion_correspondencia = models.ForeignKey('NotificacionesCorrespondencia', on_delete=models.CASCADE, db_column='T352Id_NotificacionCorrespondencia',related_name='T352Id_NotificacionCorrespondencia')
    fecha_registro = models.DateTimeField(db_column='T352fechaRegistro')
    id_tipo_notificacion_correspondencia = models.ForeignKey('TiposNotificacionesCorrespondencia', on_delete=models.CASCADE, db_column='T352Id_TipoNotificacionCorrespondencia',related_name='T352Id_TipoNotificacionCorrespondencia')
    id_persona_titular = models.ForeignKey('transversal.Personas', on_delete=models.SET_NULL, null=True, blank=True, db_column='T352Id_PersonaTitular',related_name='T352IdPersonaTitular')
    id_persona_interpone = models.ForeignKey('transversal.Personas', on_delete=models.SET_NULL, null=True, blank=True, db_column='T352Id_PersonaInterpone',related_name='T352IdPersonaInterpone')
    cod_relacion_con_titular = models.CharField(choices=RELACION_TITULAR, max_length=2, null=True, db_column='T352codRelacionConTitular')
    persona_a_quien_se_dirige = models.CharField(max_length=255, null=True, db_column='T352personaAQuienSeDirige')
    cod_tipo_documentoID = models.ForeignKey('transversal.TipoDocumento', on_delete=models.SET_NULL, null=True, blank=True, db_column='T352cod_TipoDocumentoID',related_name='T352codTipoDocumentoID')
    numero_identificacion = models.CharField(max_length=20, null=True, db_column='T352numeroIdentificacion')
    cod_municipio_notificacion_nal = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True, blank=True, db_column='T352codMunicipioNotificacionNal',related_name='T352codMunicipioNotificacionNal')
    dir_notificacion_nal = models.CharField(max_length=255, null=True, db_column='T352dirNotificacionNal')
    tel_celular = models.CharField(max_length=15, null=True, db_column='T352telCelular')
    tel_fijo = models.CharField(max_length=15, null=True, db_column='T352telFijo')
    email_notificacion = models.CharField(max_length=100, null=True, db_column='T352emailNotificacion')
    asunto = models.CharField(max_length=255, db_column='T352asunto')
    descripcion = models.CharField(max_length=500, null=True, db_column='T352descripcion')
    fecha_asignacion = models.DateTimeField(null=True, db_column='T352fechaAsignacion')
    id_persona_asigna = models.ForeignKey('transversal.Personas', on_delete=models.SET_NULL, null=True, blank=True, db_column='T352Id_PersonaAsigna',related_name='T352IdPersonaAsigna')
    id_persona_asignada = models.ForeignKey('transversal.Personas', on_delete=models.SET_NULL, null=True, blank=True, db_column='T352Id_PersonaAsignada',related_name='T352IdPersonaAsignada')
    cod_estado_asignacion = models.CharField(choices=ESTADO_ASIGNACION_CHOICES, max_length=2, null=True, db_column='T352codEstadoAsignacion')
    fecha_eleccion_estado = models.DateTimeField(null=True, db_column='T352fechaEleccionEstado')
    cantidad_anexos = models.SmallIntegerField(null=True, db_column='T352cantidadAnexos')
    nro_folios_totales = models.SmallIntegerField(null=True, db_column='T352nroFoliosTotales')
    requiere_digitalizacion = models.BooleanField(null=True, db_column='T352requiereDigitalizacion')
    fecha_envio_definitivo_a_digitalizacion = models.DateTimeField(null=True, db_column='T352fechaEnvioDefinitivoADigitalizacion')
    fecha_digitalizacion_completada = models.DateTimeField(null=True, db_column='T352fechaDigitalizacionCompletada')
    ya_digitizado = models.BooleanField(null=True, db_column='T352yaDigitizado')
    id_radicado_salida = models.ForeignKey(T262Radicados, on_delete=models.SET_NULL, null=True, blank=True, db_column='T352Id_RadicadoSalida',related_name='T352IdRadicadoSalida')
    fecha_radicado_salida = models.DateTimeField(null=True, db_column='T352fechaRadicadoSalida')
    fecha_inicial_registro = models.DateTimeField(db_column='T352fechaInicialRegistro')
    fecha_final_registro = models.DateTimeField(null=True, db_column='T352fechaFinalRegistro')
    id_persona_finaliza_registro = models.ForeignKey('transversal.Personas', on_delete=models.SET_NULL, null=True, blank=True, db_column='T352Id_PersonaFinalizaRegistro',related_name='T352IdPersonaFinalizaRegistro')
    id_estado_actual_registro = models.ForeignKey('EstadosNotificacionesCorrespondencia', on_delete=models.CASCADE, db_column='T352Id_EstadoActualRegistro',related_name='T352IdEstadoActualRegistro')
    id_doc_de_arch_exp = models.ForeignKey(DocumentosDeArchivoExpediente, on_delete=models.SET_NULL, null=True, blank=True, db_column='T352Id_DocDeArch_Exp',related_name='T352IdDocDeArchExp')

    class Meta:
        db_table = 'T352Registros_NotificacionesCorrespondencia'


class AsignacionNotificacionCorrespondencia(models.Model):
    idAsignacion_noti_corr = models.SmallAutoField(primary_key=True, db_column='T351IdAsignacion_Noti_Corr')
    id_notificacion_correspondencia = models.ForeignKey('NotificacionesCorrespondencia', on_delete=models.CASCADE, db_column='T350Id_NotificacionCorrespondencia',related_name='T351Id_NotificacionCorrespondencia')
    id_orden_notificacion = models.ForeignKey('Registros_NotificacionesCorrespondecia', on_delete=models.CASCADE, db_column='T351Id_OrdenNotificacion',related_name='T351Id_OrdenNotificacion')
    fecha_asignacion = models.DateTimeField(db_column='T351fechaAsignacion')
    id_persona_asigna = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, db_column='T351Id_PersonaAsigna',related_name='T351IdPersonaAsigna')
    id_persona_asignada = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, db_column='T351Id_PersonaAsignada',related_name='T351IdPersonaAsignada')
    cod_estado_asignacion = models.CharField(choices=ESTADO_ASIGNACION_CHOICES, null=True, max_length=2, db_column='T351codEstadoAsignacion')
    fecha_eleccion_estado = models.DateTimeField(db_column='T351fechaEleccionEstado', null=True)
    justificacion_rechazo = models.CharField(max_length=250, null=True, db_column='T351justificacionRechazo')
    id_und_org_seccion_asignada = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.SET_NULL, null=True, blank=True, db_column='T351Id_UndOrgSeccion_Asignada',related_name='T351IdUndOrgSeccionAsignada')
    id_und_org_oficina_asignada = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.SET_NULL, null=True, blank=True, db_column='T351Id_UndOrgOficina_Asignada',related_name='T351IdUndOrgOficinaAsignada')

    class Meta:
        db_table = 'T351Asignacion_Noti_Corr'


class TiposNotificacionesCorrespondencia(models.Model):
    id_tipo_notificacion_correspondencia = models.SmallAutoField(primary_key=True, db_column='T354IdTipoNotificacionCorrespondencia')
    nombre = models.CharField(max_length=50, db_column='T354nombre')
    aplica_para_notificaciones = models.BooleanField(db_column='T354aplicaParaNotificaciones')
    aplica_para_correspondencia = models.BooleanField(db_column='T354aplicaParaCorrespondencia')
    tiempo_en_dias = models.SmallIntegerField(db_column='T354tiempoEnDias')
    habiles_o_calendario = models.CharField(choices=habiles_calendario_CHOICES, max_length=1, db_column='T354habilesOCalendario')
    registro_precargado = models.BooleanField(db_column='T354registroPrecargado')
    activo = models.BooleanField(db_column='T354activo')
    item_ya_usado = models.BooleanField(db_column='T354itemYaUsado')

    class Meta:
        db_table = 'T354TiposNotificacionesCorrespondencia'


class TiposAnexosSoporte(models.Model):
    id_tipo_anexo_soporte = models.SmallAutoField(primary_key=True, db_column='T358IdTipoAnexoSoporte')
    nombre = models.CharField(max_length=255, db_column='T358nombre')
    id_tipo_notificacion_correspondencia = models.ForeignKey('TiposNotificacionesCorrespondencia', on_delete=models.CASCADE, db_column='T358Id_TipoNotificacionCorrespondencia',related_name='T358Id_TipoNotificacionCorrespondencia')
    registro_precargado = models.BooleanField(db_column='T358registroPrecargado')
    activo = models.BooleanField(db_column='T358activo')
    item_ya_usado = models.BooleanField(db_column='T358itemYaUsado')

    class Meta:
        db_table = 'T358TiposAnexosSoporte'


class Anexos_NotificacionesCorrespondencia(models.Model):
    id_anexo_notificacion_correspondencia = models.SmallAutoField(primary_key=True, db_column='T353IdAnexo_NotificacionCorrespondencia')
    id_notificacion_correspondecia = models.ForeignKey('NotificacionesCorrespondencia', on_delete=models.CASCADE, db_column='T353Id_NotificacionCorrespondencia',related_name='T353Id_NotificacionCorrespondencia')
    id_registro_notificacion = models.ForeignKey('Registros_NotificacionesCorrespondecia', on_delete=models.SET_NULL, null=True, blank=True, db_column='T353Id_RegistroNotificacion',related_name='T353Id_Registro_Notificacion')
    id_acto_administrativo = models.ForeignKey(ActosAdministrativos, on_delete=models.SET_NULL, null=True, blank=True, db_column='T353Id_ActoAdministrativo',related_name='T353Id_ActoAdministrativo')
    doc_entrada_salida = models.CharField(choices=doc_entrada_salida_CHOICES, max_length=2, db_column='T353docEntradaSalida')
    uso_del_documento = models.CharField(choices=uso_del_documento_CHOICES, max_length=2, db_column='T353usoDelDocumento')
    cod_tipo_documento = models.ForeignKey('TiposAnexosSoporte', on_delete=models.CASCADE, db_column='T353codTipoDocumento',related_name='T353codTipoDocumento')
    doc_generado = models.CharField(choices=doc_generado_CHOICES, max_length=2, db_column='T353docGenerado')
    id_persona_anexa_documento = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, db_column='T353Id_PersonaAnexaDocumento',related_name='T353Id_PersonaAnexaDocumento')
    fecha_anexo = models.DateTimeField(db_column='T353fechaAnexo')
    id_causa_o_anomalia = models.ForeignKey('CausasOAnomalias', on_delete=models.SET_NULL, null=True, blank=True, db_column='T353Id_CausaOAnomalia',related_name='T353Id_CausaOAnomalia')
    id_anexo = models.ForeignKey('gestion_documental.Anexos', on_delete=models.CASCADE, db_column='T353Id_Anexo',related_name='T353Id_Anexo')

    class Meta:
        db_table = 'T353Anexos_NotificacionesCorrespondencia'


class EstadosNotificacionesCorrespondencia(models.Model):
    id_estado_notificacion_correspondencia = models.SmallAutoField(primary_key=True, db_column='T355IdEstadoNotificacionCorrespondencia')
    nombre = models.CharField(max_length=255, db_column='T355nombre')
    cod_tipo_notificacion_correspondencia = models.ForeignKey('TiposNotificacionesCorrespondencia', on_delete=models.CASCADE, db_column='T355codTipoNotificacionCorrespondencia',related_name='T355codTipoNotificacionCorrespondencia')
    registro_precargado = models.BooleanField(db_column='T355registroPrecargado')
    activo = models.BooleanField(db_column='T355activo')
    item_ya_usado = models.BooleanField(db_column='T355itemYaUsado')

    class Meta:
        db_table = 'T355EstadosNotificacionesCorrespondencia'


class HistoricosEstados(models.Model):
    id_estado_not_corr = models.SmallAutoField(primary_key=True, db_column='T356IdEstado_Not_Corr')
    id_notificacion_correspondencia = models.ForeignKey('NotificacionesCorrespondencia', on_delete=models.CASCADE, db_column='T356IdNotificacionCorrespondencia',related_name='T356Id_NotificacionCorrespondencia')
    id_registro_notificacion = models.ForeignKey('Registros_NotificacionesCorrespondecia', on_delete=models.CASCADE, db_column='T356Id_RegistroNotificacion',related_name='T356Id_RegistroNotificacion')
    id_tipo_notificacion_correspondencia = models.ForeignKey('TiposNotificacionesCorrespondencia', on_delete=models.CASCADE, db_column='T356Id_TipoNotificacionCorrespondencia',related_name='T356Id_TipoNotificacionCorrespondencia')
    fecha_ini_estado = models.DateTimeField(db_column='T356fechaIniEstado')
    id_persona_cambia_estado = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, db_column='T356Id_PersonaCambiaEstado',related_name='T356Id_PersonaCambiaEstado')
    id_estado_asociado = models.ForeignKey('self', on_delete=models.CASCADE, db_column='T356Id_EstadoAsociado',related_name='T356Id_Estado_Asociado')

    class Meta:
        db_table = 'T356HistoricosEstados'

    
class CausasOAnomalias(models.Model):
    id_causa_o_anomalia = models.SmallAutoField(primary_key=True, db_column='T357IdCausaOAnomalia')
    nombre = models.CharField(max_length=255, db_column='T357nombre')
    id_tipo_notificacion_correspondencia = models.ForeignKey('TiposNotificacionesCorrespondencia', on_delete=models.CASCADE, db_column='T357Id_TipoNotificacionCorrespondencia',related_name='T357Id_TipoNotificacionCorrespondencia')
    registro_precargado = models.BooleanField(db_column='T357registroPrecargado')
    activo = models.BooleanField(db_column='T357activo')
    item_ya_usado = models.BooleanField(db_column='T357itemYaUsado')

    class Meta:
        db_table = 'T357CausasOAnomalias'


class TiposDocumentos(models.Model):
    id_tipo_documento = models.SmallAutoField(primary_key=True, db_column='T359IdTipoDocumento')
    nombre = models.CharField(max_length=255, db_column='T359nombre')
    aplica_para_notificaciones = models.BooleanField(db_column='T359aplicaParaNotificaciones')
    aplica_para_correspondencia = models.BooleanField(db_column='T359aplicaParaCorrespondencia')
    registro_precargado = models.BooleanField(db_column='T359registroPrecargado')
    activo = models.BooleanField(db_column='T359activo')
    item_ya_usado = models.BooleanField(db_column='T359itemYaUsado')

    class Meta:
        db_table = 'T359TiposDocumentos'

    
