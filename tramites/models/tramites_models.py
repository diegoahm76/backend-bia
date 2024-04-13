from django.db import models
from gestion_documental.models.expedientes_models import ArchivosDigitales, ExpedientesDocumentales
from gestion_documental.models.radicados_models import Anexos, EstadosSolicitudes, MediosSolicitud, T262Radicados
from gestion_documental.models.trd_models import ConsecPorNivelesTipologiasDocAgno
from transversal.models.base_models import Municipio, TipoDocumento
from transversal.models.entidades_models import SucursalesEmpresas
from tramites.choices.cod_tipo_operacion_tramite_choices import cod_tipo_operacion_tramite_CHOICES
from gestion_documental.choices.codigo_relacion_titular_choices import cod_relacion_persona_titular_CHOICES
from tramites.choices.cod_calendario_habiles_choices import cod_calendario_habiles_CHOICES
from tramites.choices.cod_tipo_permiso_ambiental_choices import cod_tipo_permiso_ambiental_CHOICES
from tramites.choices.cod_tipo_predio_choices import cod_tipo_predio_CHOICES
from tramites.choices.cod_clasificacion_territorial_choices import cod_clasificacion_territorial_CHOICES
from tramites.choices.cod_tipo_calidad_persona_choices import cod_tipo_calidad_persona_CHOICES
from tramites.choices.cod_tipo_desistimiento_choices import cod_tipo_desistimiento_CHOICES
from tramites.choices.cod_tipo_solicitud_al_requerimiento_choices import cod_tipo_solicitud_al_requerimiento_CHOICES
from tramites.choices.cod_tipo_solicitud_juridica_choices import cod_tipo_solicitud_juridica_CHOICES
from tramites.choices.cod_estado_solicitud_juridica_choices import cod_estado_solicitud_juridica_CHOICES

from transversal.models.personas_models import Personas

class SolicitudesTramites(models.Model):
    id_solicitud_tramite = models.AutoField(primary_key=True, db_column='T273IdSolicitudTramite')
    id_persona_titular = models.ForeignKey(Personas, on_delete=models.CASCADE, related_name='id_persona_titular_tramite', db_column='T273Id_PersonaTitular')
    id_persona_interpone = models.ForeignKey(Personas, on_delete=models.CASCADE, related_name='id_persona_interpone_tramite', db_column='T273Id_PersonaInterpone')
    cod_relacion_con_el_titular = models.CharField(max_length=2, choices=cod_relacion_persona_titular_CHOICES, db_column='T273codRelacionConElTitular')
    cod_tipo_operacion_tramite = models.CharField(max_length=2, choices=cod_tipo_operacion_tramite_CHOICES, db_column='T273codTipoOperacionTramite')
    nombre_proyecto = models.CharField(max_length=255, db_column='T273nombreProyecto')
    costo_proyecto = models.DecimalField(max_digits=12, decimal_places=2, db_column='T273costoProyecto')
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

class ExpedientesAsociados(models.Model):
    id_expediente_asociado = models.AutoField(primary_key=True, db_column='T274IdExpedienteAsociado')
    id_solicitud_tramite = models.OneToOneField(SolicitudesTramites, on_delete=models.CASCADE, db_column='T274Id_SolicitudTramite')
    existe_expediente = models.BooleanField(null=True, blank=True, db_column='T274existeExpediente')
    id_expediente = models.OneToOneField(ExpedientesDocumentales, on_delete=models.SET_NULL, null=True, blank=True, db_column='T274Id_Expediente')
    expediente_asociado = models.CharField(max_length=50, null=True, blank=True, db_column='T274expedienteAsociado')
    expediente_aportado_usuario = models.BooleanField(null=True, blank=True, db_column='T274expedienteAportadoUsuario')
    id_acto_administrativo = models.OneToOneField('ActosAdministrativos', on_delete=models.SET_NULL, null=True, blank=True, db_column='T274Id_ActoAdministrativo')
    acto_administrativo_asociado = models.CharField(max_length=50, null=True, blank=True, db_column='T274actoAdministrativoAsociado')
    acto_administrativo_aportado_usuario = models.BooleanField(null=True, blank=True, db_column='T274actoAdministrativoAportadoUsuario')

    def __str__(self):
        return str(self.id_expediente_asociado)
    
    class Meta:
        db_table = 'T274ExpedientesAsociados'
        verbose_name = 'Expediente Asociado'
        verbose_name_plural = 'Expedientes Asociados'

class Predios(models.Model):
    id_predio = models.AutoField(primary_key=True, db_column='T275IdPredio')
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, on_delete=models.CASCADE, db_column='T275Id_SolicitudTramite')
    nombre = models.CharField(max_length=150, null=True, blank=True, db_column='T275nombre')
    cod_tipo_predio = models.CharField(max_length=1, choices=cod_tipo_predio_CHOICES, db_column='T275codTipoPredio')
    extension_ha = models.DecimalField(max_digits=5, decimal_places=2, db_column='T275extensionHa')
    direccion = models.CharField(max_length=255, db_column='T275direccion')
    centro_poblado_vereda = models.CharField(max_length=255, db_column='T275centroPobladoVereda')
    cod_municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE, db_column='T275Cod_Municipio')
    matricula_inmobiliaria = models.CharField(max_length=20, null=True, blank=True, db_column='T275matriculaInmobiliaria')
    cedula_catastral = models.CharField(max_length=30, null=True, blank=True, db_column='T275cedulaCatastral')
    cod_clasificacion_territorial = models.CharField(max_length=1, choices=cod_clasificacion_territorial_CHOICES, db_column='T275codClasificacionTerritorial')
    cod_tipo_calidad_persona = models.CharField(max_length=2, choices=cod_tipo_calidad_persona_CHOICES, db_column='T275codTipoCalidadPersona')
    descripcion_otro_calidad_pers = models.CharField(max_length=50, null=True, blank=True, db_column='T275descripcionOtroCalidadPers')

    def __str__(self):
        return str(self.id_predio)
    
    class Meta:
        db_table = 'T275Predios'
        verbose_name = 'Predio'
        verbose_name_plural = 'Predios'

class OtrosPropietariosPredios(models.Model):
    id_otro_propietario_predio = models.AutoField(primary_key=True, db_column='T276IdOtroPropietarioPredio')
    id_predio = models.ForeignKey(Predios, on_delete=models.CASCADE, db_column='T276Id_Predio')
    nombre = models.CharField(max_length=150, null=True, blank=True, db_column='T276nombre')
    cod_tipo_documento_id = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE, db_column='T276Cod_TipoDocumentoID')
    nro_documento_id = models.CharField(max_length=20, db_column='T276nroDocumentoID')

    def __str__(self):
        return str(self.id_otro_propietario_predio)
    
    class Meta:
        db_table = 'T276OtrosPropietariosPredios'
        verbose_name = 'Otro Propietario Predio'
        verbose_name_plural = 'Otros Propietarios Predios'

class TransicionesEstados(models.Model):
    id_transicion_estado = models.AutoField(primary_key=True, db_column='T278IdTransicionEstado')
    id_estado_inicial = models.ForeignKey(EstadosSolicitudes, on_delete=models.CASCADE, related_name='id_estado_inicial_tramite', db_column='T278Id_EstadoInicial')
    id_estado_final = models.ForeignKey(EstadosSolicitudes, on_delete=models.SET_NULL, null=True, blank=True, related_name='id_estado_final_tramite', db_column='T278Id_EstadoFinal')

    def __str__(self):
        return str(self.id_transicion_estado)
    
    class Meta:
        db_table = 'T278TransicionesEstados'
        verbose_name = 'Transicion Estado'
        verbose_name_plural = 'Transiciones Estados'

class HistoricosEstados(models.Model):
    id_historico_estado = models.AutoField(primary_key=True, db_column='T279IdHistoricoEstado')
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, on_delete=models.CASCADE, db_column='T279Id_SolicitudTramite')
    id_estado_solicitud = models.ForeignKey(EstadosSolicitudes, on_delete=models.CASCADE, db_column='T279Id_EstadoSolicitud')
    fecha_ini_estado = models.DateTimeField(db_column='T279fechaIniEstado')
    id_persona_genera_estado = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T279Id_PersonaGeneraEstado')
    id_estado_asociado = models.ForeignKey('self', on_delete=models.CASCADE, db_column='T279Id_EstadoAsociado')

    def __str__(self):
        return str(self.id_historico_estado)
    
    class Meta:
        db_table = 'T279HistoricosEstados'
        verbose_name = 'Historico Estado'
        verbose_name_plural = 'Historicos Estados'

class PermisosAmbSolicitudesTramite(models.Model):
    id_permiso_amb_solicitud_tramite = models.AutoField(primary_key=True, db_column='T280IdPermisoAmbSolicitudTramite')
    id_permiso_ambiental = models.ForeignKey('PermisosAmbientales', on_delete=models.CASCADE, db_column='T280Id_PermisoAmbiental')
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, on_delete=models.CASCADE, db_column='T280Id_SolicitudTramite')
    descripcion_direccion = models.CharField(max_length=250, null=True, blank=True, db_column='T280descripcionDireccion')
    coordenada_x = models.CharField(max_length=20, null=True, blank=True, db_column='T280coordenadaX')
    coordenada_y = models.CharField(max_length=20, null=True, blank=True, db_column='T280coordenadaY')
    cod_municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE, db_column='T280cod_Municipio')
    direccion = models.CharField(max_length=255, db_column='T280direccion')

    def __str__(self):
        return str(self.id_permiso_amb_solicitud_tramite)

    class Meta:
        db_table = 'T280PermisosAmbSolicitudesTramite'
        verbose_name = 'Permiso Ambiental Solicitud Tramite'
        verbose_name_plural = 'Permisos Ambientales Solicitudes Tramites'

class PermisosAmbientales(models.Model):
    id_permiso_ambiental = models.AutoField(primary_key=True, db_column='T281IdPermisoAmbiental')
    cod_tipo_permiso_ambiental = models.CharField(max_length=1, choices=cod_tipo_permiso_ambiental_CHOICES, db_column='T281codTipoPermisoAmbiental')
    nombre = models.CharField(max_length=250, db_column='T281nombre')
    tiene_pago = models.BooleanField(default=True, db_column='T281tienePago')

    def __str__(self):
        return str(self.id_permiso_ambiental)

    class Meta:
        db_table = 'T281PermisosAmbientales'
        verbose_name = 'Permiso Ambiental'
        verbose_name_plural = 'Permisos Ambientales'

class Requerimientos(models.Model):
    id_requerimiento = models.AutoField(primary_key=True, db_column='T284IdRequerimiento')
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, on_delete=models.CASCADE, db_column='T284Id_SolicitudTramite')
    fecha_requerimiento = models.DateTimeField(db_column='T284fechaRequerimiento')
    id_radicado = models.ForeignKey(T262Radicados, null=True, blank=True, on_delete=models.SET_NULL, db_column='T284Id_Radicado')
    fecha_radicado = models.DateTimeField(null=True, blank=True, db_column='T284fechaRadicado')
    observaciones = models.CharField(max_length=500, null=True, blank=True, db_column='T284observaciones')
    plazo_inicial_entrega = models.DateTimeField(db_column='T284plazoInicialEntrega')
    plazo_final_entrega = models.DateTimeField(db_column='T284plazoFinalEntrega',null=True)
    id_persona_crea_requerimiento = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T284Id_PersonaCreaRequerimiento')
    estado = models.IntegerField(db_column='T284estado')

    def __str__(self):
        return str(self.id_requerimiento)

    class Meta:
        db_table = 'T284Requerimientos'
        verbose_name = 'Requerimiento'
        verbose_name_plural = 'Requerimientos'

class DesistimientosTramites(models.Model):
    id_desistimiento_tramite = models.AutoField(primary_key=True, db_column='T285IdDesistimientoTramite')
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, on_delete=models.CASCADE, db_column='T285Id_SolicitudTramite')
    id_requerimiento = models.ForeignKey(Requerimientos, null=True, blank=True, on_delete=models.SET_NULL, db_column='T285Id_Requerimiento')
    id_radicado = models.ForeignKey(T262Radicados, null=True, blank=True, on_delete=models.SET_NULL, db_column='T285Id_Radicado')
    fecha_radicado = models.DateTimeField(null=True, blank=True, db_column='T285fechaRadicado')
    motivo = models.CharField(max_length=500, null=True, blank=True, db_column='T285motivo')
    cod_tipo_desistimiento = models.CharField(max_length=1, choices=cod_tipo_desistimiento_CHOICES, db_column='T285codTipoDesistimiento')
    fecha_desistimiento = models.DateTimeField(db_column='T285fechaDesistimiento')
    id_persona_crea_desistimiento = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T285Id_PersonaCreaDesistimiento')

    def __str__(self):
        return str(self.id_desistimiento_tramite)

    class Meta:
        db_table = 'T285DesistimientosTramites'
        verbose_name = 'Desistieminto Tramite'
        verbose_name_plural = 'Desistiemintos Tramites'

class RecursosReposicion(models.Model):
    id_recurso_reposicion = models.AutoField(primary_key=True, db_column='T286IdRecursoReposicion')
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, on_delete=models.CASCADE, db_column='T286Id_SolicitudTramite')
    id_acto_administrativo = models.ForeignKey('ActosAdministrativos', on_delete=models.CASCADE, db_column='T286Id_ActoAdministrativo')
    fecha_recurso_repo = models.DateTimeField(db_column='T286fechaRecursoRepo')
    id_radicado = models.ForeignKey(T262Radicados, on_delete=models.SET_NULL, null=True, blank=True, db_column='T286Id_Radicado')
    fecha_radicado = models.DateTimeField(null=True, blank=True, db_column='T286fechaRadicado')
    id_persona_crea_recurso_repo = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T286Id_PersonaCreaRecursoRepo')

    def __str__(self):
        return str(self.id_recurso_reposicion)

    class Meta:
        db_table = 'T286RecursosReposicion'
        verbose_name = 'Recurso Reposicion'
        verbose_name_plural = 'Recursos Reposicion'

class AnexosTramite(models.Model):
    id_anexo_tramite = models.AutoField(primary_key=True, db_column='T287IdAnexoTramite')
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, on_delete=models.SET_NULL, null=True, blank=True, db_column='T287Id_SolicitudTramite')
    id_permiso_amb_solicitud_tramite = models.ForeignKey(PermisosAmbSolicitudesTramite, on_delete=models.SET_NULL, null=True, blank=True, db_column='T287Id_PermisoAmbSolicitudTramite')
    id_documento_lista_chequeo = models.ForeignKey('DocumentosListasChequeo', on_delete=models.SET_NULL, null=True, blank=True, db_column='T287Id_DocumentoListaChequeo')
    id_requerimiento = models.ForeignKey(Requerimientos, on_delete=models.SET_NULL, null=True, blank=True, db_column='T287Id_Requerimiento')
    id_respuesta_requerimiento = models.ForeignKey('RespuestasRequerimientos', on_delete=models.SET_NULL, null=True, blank=True, db_column='T287Id_RespuestaRequerimiento')
    id_solicitud_al_requerimiento = models.ForeignKey('SolicitudesAlRequerimiento', on_delete=models.SET_NULL, null=True, blank=True, db_column='T287Id_SolicitudAlRequerimiento')
    id_respuesta_solicitud = models.ForeignKey('RespuestaSolicitudesAlRequerimiento', on_delete=models.SET_NULL, null=True, blank=True, db_column='T287Id_RespuestaSolicitud')
    id_acto_administrativo = models.ForeignKey('ActosAdministrativos', on_delete=models.SET_NULL, null=True, blank=True, db_column='T287Id_ActoAdministrativo')
    id_recurso_reposicion = models.ForeignKey(RecursosReposicion, on_delete=models.SET_NULL, null=True, blank=True, db_column='T287Id_RecursoReposicion')
    id_anexo = models.ForeignKey(Anexos, on_delete=models.CASCADE, db_column='T287Id_Anexo')
    id_respuesta_opa = models.ForeignKey('RespuestaOPA', on_delete=models.SET_NULL, null=True, blank=True, db_column='T287Id_Respuesta_OPA')
    def __str__(self):
        return str(self.id_anexo_tramite)

    class Meta:
        db_table = 'T287Anexos_Tramite'
        verbose_name = 'Anexo Tramite'
        verbose_name_plural = 'Anexos Tramites'

class ListasChequeoTramites(models.Model):
    id_lista_chequeo_tramite = models.AutoField(primary_key=True, db_column='T288IdListaChequeoTramite')
    id_permiso_ambiental = models.ForeignKey(PermisosAmbientales, on_delete=models.CASCADE, db_column='T288Id_PermisoAmbiental')
    nombre = models.CharField(max_length=255, db_column='T288nombre')
    codigo = models.CharField(max_length=10, db_column='T288codigo')
    version = models.CharField(max_length=10, db_column='T288version')
    fecha = models.DateTimeField(db_column='T288fecha')
    estado = models.CharField(max_length=1, db_column='T288estado')

    def __str__(self):
        return str(self.id_lista_chequeo_tramite)

    class Meta:
        db_table = 'T288ListasChequeoTramites'
        verbose_name = 'Lista Chequeo Tramite'
        verbose_name_plural = 'Listas Chequeos Tramites'

class DocumentosListasChequeoPorTramites(models.Model):
    id_documentos_por_lista_tramite = models.AutoField(primary_key=True, db_column='T289IdDocumentosPorListaTramite')
    id_lista_chequeo_tramite = models.ForeignKey(ListasChequeoTramites, on_delete=models.CASCADE, db_column='T289Id_ListaChequeoTramite')
    id_documento_lista_chequeo = models.ForeignKey('DocumentosListasChequeo', on_delete=models.CASCADE, db_column='T289Id_DocumentoListaChequeo')
    codigo = models.CharField(max_length=10, db_column='T289codigo')
    version = models.CharField(max_length=10, db_column='T289version')
    fecha = models.DateTimeField(db_column='T289fecha')
    es_obligatorio = models.BooleanField(db_column='T289esObligatorio')

    def __str__(self):
        return str(self.id_documentos_por_lista_tramite)

    class Meta:
        db_table = 'T289DocumentosListasChequeoPorTramites'
        verbose_name = 'Documento Lista Chequeo Por Tramite'
        verbose_name_plural = 'Documentos Listas Chequeos Por Tramites'

class DocumentosListasChequeo(models.Model):
    id_documento_lista_chequeo = models.AutoField(primary_key=True, db_column='T290IdDocumentoListaChequeo')
    nombre_documento = models.CharField(max_length=255, db_column='T290nombreDocumento')
    observaciones_documento = models.CharField(max_length=255, blank=True, null=True, db_column='T290observacionesDocumento')
    extensiones_permitidas = models.CharField(max_length=255, db_column='T290extensionesPermitidas')
    peso_maximo = models.DecimalField(max_digits=4, decimal_places=2, db_column='T290pesoMaximo')
    item_ya_usado = models.BooleanField(default=False, db_column='T290itemYaUsado')

    def __str__(self):
        return str(self.id_documento_lista_chequeo)

    class Meta:
        db_table = 'T290DocumentosListasChequeo'
        verbose_name = 'Documento Lista Chequeo'
        verbose_name_plural = 'Documentos Listas Chequeos'

class RespuestasRequerimientos(models.Model):
    id_respuesta_requerimiento = models.AutoField(primary_key=True, db_column='T291IdRespuestaRequerimiento')
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, on_delete=models.CASCADE, db_column='T291Id_SolicitudTramite')
    id_requerimiento = models.ForeignKey(Requerimientos, on_delete=models.CASCADE, db_column='T291Id_Requerimiento')
    fecha_respuesta = models.DateTimeField(db_column='T291fechaRespuesta')
    descripcion = models.CharField(max_length=500, blank=True, null=True, db_column='T291descripcion')
    id_persona_responde = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T291Id_PersonaResponde')
    id_radicado = models.ForeignKey(T262Radicados, on_delete=models.SET_NULL, blank=True, null=True, db_column='T291Id_Radicado')
    fecha_radicado = models.DateTimeField(blank=True, null=True, db_column='T291fechaRadicado')
    complemento_asignado_unidad = models.BooleanField(db_column='T291RequerimientoAsignadoAUndOrg',default=False)

    def __str__(self):
        return str(self.id_respuesta_requerimiento)

    class Meta:
        db_table = 'T291RespuestasRequerimientos'
        verbose_name = 'Respuesta Requerimiento'
        verbose_name_plural = 'Respuestas Requerimientos'

class SolicitudesAlRequerimiento(models.Model):
    id_solicitud_al_requerimiento = models.AutoField(primary_key=True, db_column='T292IdSolicitudAlRequerimiento')
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, on_delete=models.CASCADE, db_column='T292Id_SolicitudTramite')
    id_requerimiento = models.ForeignKey(Requerimientos, on_delete=models.CASCADE, db_column='T292Id_Requerimiento')
    cod_tipo_solicitud_al_requerimiento = models.CharField(max_length=1, choices=cod_tipo_solicitud_al_requerimiento_CHOICES, db_column='T292codTipoSolicitudAlRequerimiento')
    motivo = models.CharField(max_length=500, null=True, blank=True, db_column='T292motivo')
    dias_solicitados = models.IntegerField(null=True, blank=True, db_column='T292diasSolicitados')
    cod_calendario_habiles = models.CharField(max_length=1, choices=cod_calendario_habiles_CHOICES, null=True, blank=True, db_column='T292codCalendarioHabiles')
    id_radicado = models.ForeignKey(T262Radicados, on_delete=models.SET_NULL, null=True, blank=True, db_column='T292Id_Radicado')
    fecha_radicado = models.DateTimeField(null=True, blank=True, db_column='T292fechaRadicado')
    fecha_solicitud = models.DateTimeField(null=True, blank=True, db_column='T292fechaSolicitud')
    id_persona_crea_solicitud = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T292Id_PersonaCreaSolicitud')
    aprobado = models.BooleanField(null=True, blank=True, db_column='T292aprobado')

    def __str__(self):
        return str(self.id_solicitud_al_requerimiento)

    class Meta:
        db_table = 'T292SolicitudesAlRequerimiento'
        verbose_name = 'Solicitud Al Requerimiento'
        verbose_name_plural = 'Solicitudes Al Requerimiento'

class RespuestaSolicitudesAlRequerimiento(models.Model):
    id_respuesta_solicitud_al_requerimiento = models.AutoField(primary_key=True, db_column='T293IdRespuestaSolicitudAlRequerimiento')
    id_solicitud_al_requerimiento = models.ForeignKey(SolicitudesAlRequerimiento, on_delete=models.CASCADE, db_column='T293Id_SolicitudAlRequerimiento')
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, on_delete=models.CASCADE, db_column='T293Id_SolicitudTramite')
    fecha_respuesta = models.DateTimeField(db_column='T293fechaRespuesta')
    aprobado = models.BooleanField(null=True, blank=True, db_column='T293aprobado')
    plazo_final_entrega = models.DateTimeField(null=True, blank=True, db_column='T293plazoFinalEntrega')
    observaciones = models.CharField(max_length=500, null=True, blank=True, db_column='T293observaciones')
    id_radicado = models.ForeignKey(T262Radicados, on_delete=models.SET_NULL, null=True, blank=True, db_column='T293Id_Radicado')
    fecha_radicado = models.DateTimeField(null=True, blank=True, db_column='T293fechaRadicado')
    id_persona_crea_respuesta = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T293Id_PersonaCreaRespuesta')
    estado_actual = models.IntegerField(db_column='T293estadoActual')

    def __str__(self):
        return str(self.id_respuesta_solicitud_al_requerimiento)

    class Meta:
        db_table = 'T293RespuestaSolicitudesAlRequerimiento'
        verbose_name = 'Respuesta Solicitud Al Requerimiento'
        verbose_name_plural = 'Respuestas Solicitudes Al Requerimiento'

class ActosAdministrativos(models.Model):
    id_acto_administrativo = models.AutoField(primary_key=True, db_column='T294IdActoAdministrativo')
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, on_delete=models.CASCADE, db_column='T294Id_SolicitudTramite')
    id_tipo_acto_administrativo = models.ForeignKey('TiposActosAdministrativos', on_delete=models.CASCADE, db_column='T294Id_TipoActoAdministrativo')
    #numero_acto_administrativo = models.CharField(null=True, blank=True, max_length=50, db_column='T294numeroActoAdministrativo')
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

class SolicitudesDeJuridica(models.Model):
    id_solicitud_de_juridica = models.AutoField(primary_key=True, db_column='T296IdSolicitudDeJuridica')
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, null=True, blank=True, on_delete=models.SET_NULL, db_column='T296Id_SolicitudTramite')
    cod_tipo_solicitud_juridica = models.CharField(max_length=2, choices=cod_tipo_solicitud_juridica_CHOICES, db_column='T296codTipoSolicitudJuridica')
    fecha_solicitud = models.DateTimeField(db_column='T296fechaSolicitud')
    fecha_rta_solicitud = models.DateTimeField(null=True, blank=True, db_column='T296fechaRtaSolicitud')
    observacion = models.CharField(max_length=255, null=True, blank=True, db_column='T296observacion')
    aprueba_solicitud_tramite = models.BooleanField(null=True, blank=True, db_column='T296apruebaSolicitudTramite')
    id_requerimiento = models.ForeignKey(Requerimientos, null=True, blank=True, on_delete=models.SET_NULL, db_column='T296Id_Requerimiento')
    fecha_requerimiento = models.DateTimeField(null=True, blank=True, db_column='T296fechaRequerimiento')
    solicitud_completada = models.BooleanField(null=True, blank=True, db_column='T296solicitudCompletada')
    solicitud_sin_completar = models.BooleanField(null=True, blank=True, db_column='T296solicitudSinCompletar')
    id_persona_solicita_revision = models.ForeignKey(Personas, on_delete=models.CASCADE, related_name='id_persona_solicita_revision_juridica', db_column='T296Id_PersonaSolicitaRevision')
    id_persona_revisa = models.ForeignKey(Personas, null=True, blank=True, on_delete=models.SET_NULL, related_name='id_persona_revisa_juridica', db_column='T296Id_PersonaRevisa')
    cod_estado_tipo_solicitud_juridica = models.CharField(max_length=2, choices=cod_estado_solicitud_juridica_CHOICES, db_column='T296codEstadoTipoSolicitudJuridica')

    def __str__(self):
        return str(self.id_solicitud_de_juridica)

    class Meta:
        db_table = 'T296SolicitudesDeJuridica'
        verbose_name = 'Solicitud De Juridica'
        verbose_name_plural = 'Solicitudes De Juridica'
        
class Tramites(models.Model):
    id_tramites = models.AutoField(primary_key=True, db_column='T318IdTramites')
    procedure_id = models.IntegerField(null=True, blank=True, db_column='T318procedure_Id')
    radicate_bia = models.CharField(max_length=50, null=True, blank=True, db_column='T318radicate_Bia')
    proceeding_id = models.CharField(max_length=50, null=True, blank=True, db_column='T318proceeding_Id')
    name_key = models.CharField(max_length=100, null=True, blank=True, db_column='T318name_Key')
    type_key = models.CharField(max_length=100, null=True, blank=True, db_column='T318type_Key')
    value_key = models.TextField(null=True, blank=True, db_column='T318value_Key')

    class Meta:
        db_table = 'T318Tramites'
        verbose_name = 'Tramites'
        verbose_name_plural = 'Tramites'



class RespuestaOPA(models.Model):
    id_respuesta_opa = models.AutoField(db_column='T297IdRespuesta_OPA', primary_key=True)
    id_solicitud_tramite = models.ForeignKey(SolicitudesTramites, on_delete=models.CASCADE, db_column='T297Id_SolicitudTramite')
    fecha_respuesta = models.DateTimeField(db_column='T297fechaRespuesta', null=True, blank=True)
    asunto = models.CharField(max_length=255, db_column='T297asunto')
    descripcion = models.CharField(max_length=500, db_column='T297descripcion')
    cantidad_anexos = models.SmallIntegerField(db_column='T297cantidadAnexos')
    nro_folios_totales = models.SmallIntegerField(db_column='T297nroFoliosTotales')
    id_persona_responde = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T297Id_PersonaResponde')
    id_radicado_salida = models.ForeignKey(T262Radicados, on_delete=models.SET_NULL, null=True, blank=True, db_column='T297Id_RadicadoSalida')
    fecha_radicado_salida = models.DateTimeField(db_column='T297fechaRadicadoSalida', null=True, blank=True)
    id_doc_de_arch_exp = models.ForeignKey(ExpedientesDocumentales, on_delete=models.SET_NULL, null=True, blank=True, db_column='T297Id_DocDeArch_Exp')

    class Meta:
        verbose_name = 'Respuesta OPA'
        verbose_name_plural = 'Respuestas OPA'
        db_table = 'T297Respuestas_OPA'