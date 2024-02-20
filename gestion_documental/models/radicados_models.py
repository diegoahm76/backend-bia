from django.db import models
from gestion_documental.choices.pqrsdf_choices import (
    TIPOS_PQR,
    COD_TIPO_TAREA_CHOICES,
    COD_ESTADO_ASIGNACION_CHOICES,
    COD_ESTADO_SOLICITUD_CHOICES,
    RELACION_TITULAR,
    FORMA_PRESENTACION,
    TIPOS_OFICIO_CHOICES
    
)
from gestion_documental.choices.tipo_zonas_choices import TIPO_ZONAS_CHOICES



from gestion_documental.models.expedientes_models import ArchivosDigitales, DocumentosDeArchivoExpediente, ExpedientesDocumentales
from gestion_documental.models.trd_models import TipologiasDoc
from seguridad.models import Personas
from gestion_documental.choices.tipo_radicado_choices import TIPOS_RADICADO_CHOICES
# from tramites.models.tramites_models import SolicitudesTramites
from transversal.models.base_models import Municipio
from transversal.models.entidades_models import SucursalesEmpresas
from transversal.models.organigrama_models import UnidadesOrganizacionales
from gestion_documental.choices.medio_almacenamiento_choices import medio_almacenamiento_CHOICES
from gestion_documental.choices.tipo_archivo_choices import tipo_archivo_CHOICES
from gestion_documental.choices.origen_archivo_choices import origen_archivo_CHOICES
from gestion_documental.choices.codigo_relacion_titular_choices import cod_relacion_persona_titular_CHOICES
from gestion_documental.choices.codigo_forma_presentacion_choices import cod_forma_presentacion_CHOICES

class ConfigTiposRadicadoAgno(models.Model):

    id_config_tipo_radicado_agno = models.SmallAutoField(primary_key=True, db_column='T235IdConfigTipoRadicadoAgno')
    agno_radicado = models.SmallIntegerField(db_column='T235agnoRadicado')
    cod_tipo_radicado = models.CharField(max_length=1, choices=TIPOS_RADICADO_CHOICES, db_column='T235codTipoRadicado')
    prefijo_consecutivo = models.CharField(null=True,max_length=10, db_column='T235prefijoConsecutivo')
    consecutivo_inicial = models.IntegerField(null=True,db_column='T235consecutivoInicial')
    cantidad_digitos = models.SmallIntegerField(null=True,db_column='T235cantidadDigitos')
    implementar = models.BooleanField(db_column='T235implementar')
    id_persona_config_implementacion = models.ForeignKey('transversal.Personas',null=True, on_delete=models.CASCADE, db_column='T235Id_PersonaConfigImplementacion',related_name='T235Id_PersonaConfigImplementacion')
    fecha_inicial_config_implementacion = models.DateTimeField(null=True,db_column='T235fechaInicialConfigImplementacion')
    consecutivo_actual = models.IntegerField(null=True,db_column='T235consecutivoActual')
    fecha_consecutivo_actual = models.DateTimeField(null=True,db_column='T235fechaConsecutivoActual')
    id_persona_consecutivo_actual = models.ForeignKey('transversal.Personas',null=True, on_delete=models.CASCADE, db_column='T235Id_PersonaConsecutivoActual',related_name='FK2_T235ConfigTiposRadicadoAgno')

    class Meta:
        db_table = 'T235ConfigTiposRadicadoAgno'
        unique_together = ['agno_radicado', 'cod_tipo_radicado']


class TiposPQR(models.Model):

    cod_tipo_pqr = models.CharField( primary_key=True,max_length=2,choices=TIPOS_PQR,db_column='T252CodTipoPQR')
    nombre = models.CharField(max_length=36,unique=True,db_column='T252nombre', verbose_name='Nombre del Tipo de PQR' )
    tiempo_respuesta_en_dias = models.SmallIntegerField(null=True,blank=True,db_column='T252tiempoRtaEnDias')
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'T252TiposPQR'  
        verbose_name = 'Tipo de PQR'  
        verbose_name_plural = 'Tipos de PQR' 


class MediosSolicitud(models.Model):
    id_medio_solicitud = models.SmallAutoField(primary_key=True, db_column='T253IdMedioSolicitud')
    nombre = models.CharField(max_length=50, db_column='T253nombre',unique=True)
    aplica_para_pqrsdf = models.BooleanField(default=False, db_column='T253aplicaParaPQRSDF')
    aplica_para_tramites = models.BooleanField(default=False, db_column='T253aplicaParaTramites')
    aplica_para_otros = models.BooleanField(default=False, db_column='T253aplicaParaOtros')
    registro_precargado = models.BooleanField(default=False, db_column='T253registroPrecargado')
    activo = models.BooleanField(default=False, db_column='T253activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T253itemYaUsado')

    class Meta:
        db_table = 'T253MediosSolicitud'  
        verbose_name = 'Medio de Solicitud'  
        verbose_name_plural = 'Medios de Solictud' 


class EstadosSolicitudes(models.Model):
    id_estado_solicitud = models.SmallAutoField(primary_key=True, db_column='T254IdEstadoSolicitud')
    nombre = models.CharField(max_length=50, db_column='T254nombre')
    aplica_para_pqrsdf = models.BooleanField(db_column='T254aplicaParaPQRSDF')
    aplica_para_tramites = models.BooleanField(db_column='T254aplicaParaTramites')
    aplica_para_otros = models.BooleanField(db_column='T254aplicaParaOtros')

    class Meta:
       
        db_table = 'T254EstadosSolicitudes'
        verbose_name = 'Estado de Solicitud'  
        verbose_name_plural = 'Estados de Solictud' 


class T262Radicados(models.Model):
    id_radicado = models.AutoField(primary_key=True, db_column='T262IdRadicado')
    id_modulo_que_radica = models.ForeignKey('modulos_radican',on_delete=models.CASCADE,db_column='T262Id_ModuloQueRadica')
    cod_tipo_radicado = models.CharField(max_length=1, choices=TIPOS_RADICADO_CHOICES, db_column='T262codTipoRadicado')
    prefijo_radicado = models.CharField(max_length=10, db_column='T262prefijoRadicado')
    agno_radicado = models.SmallIntegerField(db_column='T262agnoRadicado')
    nro_radicado = models.CharField(max_length=20, db_column='T262nroRadicado')
    fecha_radicado = models.DateTimeField(db_column='T262fechaRadicado')
    id_persona_radica = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,db_column='T262Id_PersonaRadica')
    id_radicado_asociado = models.ForeignKey('self',on_delete=models.CASCADE,null=True, db_column='T262Id_RadicadoAsociado')

    class Meta:
        unique_together = [
            ("cod_tipo_radicado", "prefijo_radicado", "agno_radicado", "nro_radicado")
        ]
        db_table = 'T262Radicados'  # Nombre de la tabla personalizado

class PQRSDF(models.Model):
    id_PQRSDF = models.AutoField(primary_key=True, db_column='T257IdPQRSDF')
    cod_tipo_PQRSDF = models.CharField(max_length=2,choices=TIPOS_PQR,db_column='T257codTipoPQRSDF')#,max_length=2,choices=TIPOS_PQR
    id_persona_titular = models.ForeignKey('transversal.Personas',null=True,on_delete=models.CASCADE,db_column='T257Id_PersonaTitular', related_name='persona_titular_relacion')# models.ForeignKey('transversal.Personas',null=True, on_delete=models.CASCADE,
    id_persona_interpone = models.ForeignKey('transversal.Personas',null=True,on_delete=models.CASCADE,db_column='T257Id_PersonaInterpone',related_name='persona_interpone_relacion')
    cod_relacion_con_el_titular = models.CharField(max_length=2, null=True, choices=RELACION_TITULAR, db_column='T257codRelacionConElTitular')
    es_anonima = models.BooleanField(default=False, db_column='T257esAnonima')
    fecha_registro = models.DateTimeField(db_column='T257fechaRegistro')
    id_medio_solicitud = models.ForeignKey(MediosSolicitud,on_delete=models.CASCADE,db_column='T257Id_MedioSolicitud')
    cod_forma_presentacion = models.CharField(max_length=1, choices=FORMA_PRESENTACION, db_column='T257codFormaPresentacion')
    asunto = models.CharField(max_length=100, db_column='T257asunto')
    descripcion = models.CharField(max_length=500, db_column='T257descripcion')
    cantidad_anexos = models.SmallIntegerField(db_column='T257cantidadAnexos')
    nro_folios_totales = models.SmallIntegerField(db_column='T257nroFoliosTotales')
    requiere_rta = models.BooleanField(default=False, db_column='T257requiereRta')
    dias_para_respuesta = models.SmallIntegerField(db_column='T257diasParaRespuesta', null=True)
    id_sucursal_especifica_implicada = models.ForeignKey(SucursalesEmpresas,on_delete=models.CASCADE,db_column='T257Id_SucursalEspecificaImplicada', null=True)
    id_persona_recibe = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,db_column='T257Id_PersonaRecibe', null=True,related_name='persona_recibe_ralacion')
    id_sucursal_recepcion_fisica = models.ForeignKey(SucursalesEmpresas,on_delete=models.CASCADE,db_column='T257Id_Sucursal_RecepcionFisica', null=True,related_name='sucursal_recepciona_ralacion')
    id_radicado = models.ForeignKey(T262Radicados,on_delete=models.CASCADE,db_column='T257Id_Radicado', null=True)
    fecha_radicado = models.DateTimeField(db_column='T257fechaRadicado', null=True)
    requiere_digitalizacion = models.BooleanField(default=False, db_column='T257requiereDigitalizacion')
    fecha_envio_definitivo_a_digitalizacion = models.DateTimeField(db_column='T257fechaEnvioDefinitivoADigitalizacion', null=True)
    fecha_digitalizacion_completada = models.DateTimeField(db_column='T257fechaDigitalizacionCompletada', null=True)
    fecha_rta_final_gestion = models.DateTimeField(db_column='T257fechaRtaFinalGestion', null=True)
    id_persona_rta_final_gestion = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,db_column='T257Id_PersonaRtaFinalGestion', null=True,related_name='persona_rta_final_gestion_ralacion')
    id_estado_actual_solicitud = models.ForeignKey(EstadosSolicitudes,on_delete=models.CASCADE,db_column='T257Id_EstadoActualSolicitud')
    fecha_ini_estado_actual = models.DateTimeField(db_column='T257fechaIniEstadoActual')
    id_doc_dearch_exp = models.ForeignKey(DocumentosDeArchivoExpediente,on_delete=models.CASCADE,db_column='T257Id_DocDeArch_Exp', null=True)
    id_expediente_doc = models.ForeignKey(ExpedientesDocumentales,on_delete=models.CASCADE,db_column='T257Id_ExpedienteDoc', null=True)

    class Meta:
       
        db_table = 'T257PQRSDF'

class Otros(models.Model):
    id_otros = models.AutoField(primary_key=True, db_column='T301IdOtros')
    id_persona_titular = models.ForeignKey(Personas, on_delete=models.CASCADE, related_name='id_persona_titular_otros', db_column='T301Id_PersonaTitular')
    id_persona_interpone = models.ForeignKey(Personas, on_delete=models.CASCADE, related_name='id_persona_interpone_otros', db_column='T301Id_PersonaInterpone')
    cod_relacion_titular = models.CharField(max_length=2,null=True,blank=True, choices=cod_relacion_persona_titular_CHOICES, db_column='T301codRelacionConElTitular')
    fecha_registro = models.DateTimeField(db_column='T301fechaRegistro')
    id_medio_solicitud = models.ForeignKey (MediosSolicitud, on_delete=models.CASCADE, db_column='T301Id_MedioSolicitud')
    cod_forma_presentacion = models.CharField(max_length=1, choices=cod_forma_presentacion_CHOICES, db_column='T301codFormaPresentacion')
    asunto = models.CharField(max_length=100, db_column='T301asunto')
    descripcion = models.CharField(max_length=150, db_column='T301descripcion')
    cantidad_anexos = models.SmallIntegerField(db_column='T301cantidadAnexos')
    nro_folios_totales = models.SmallIntegerField(db_column='T301nroFoliosTotales')
    id_persona_recibe = models.ForeignKey(Personas, on_delete=models.SET_NULL, related_name='id_persona_recibe_otros', blank=True, null=True, db_column='T301Id_PersonaRecibe')
    id_sucursal_recepciona_fisica = models.ForeignKey(SucursalesEmpresas, on_delete=models.SET_NULL, blank=True, null=True, db_column='T301Id_Sucursal_RecepcionFisica')
    id_radicados = models.ForeignKey(T262Radicados, on_delete=models.SET_NULL, blank=True, null=True, db_column='T301Id_Radicado')
    fecha_radicado = models.DateTimeField(blank=True, null=True,db_column='T301fechaRadicado')
    requiere_digitalizacion = models.BooleanField(db_column='T301requiereDigitalizacion')
    fecha_envio_definitivo_digitalizacion = models.DateTimeField(blank=True, null=True,db_column='T301fechaEnvioDefinitivoADigitalizacion')
    fecha_digitalizacion_completada = models.DateTimeField(blank=True, null=True,db_column='T301fechaDigitalizacionCompletada')
    id_estado_actual_solicitud = models.ForeignKey (EstadosSolicitudes, on_delete=models.CASCADE, db_column='T301Id_EstadoActualSolicitud')
    fecha_inicial_estado_actual = models.DateTimeField(db_column='T301fechaIniEstadoActual')
    id_documento_archivo_expediente = models.ForeignKey(DocumentosDeArchivoExpediente, on_delete=models.SET_NULL, blank=True, null=True, db_column='T301Id_DocDeArch_Exp')
    id_expediente_documental = models.ForeignKey(ExpedientesDocumentales, on_delete=models.SET_NULL, blank=True, null=True, db_column='T301Id_ExpedienteDoc')

    class Meta:
        db_table = 'T301Otros'
        verbose_name = 'Otro'
        verbose_name_plural = 'Otros'
    
class Estados_PQR(models.Model):
    id_estado_PQR = models.AutoField(primary_key=True, db_column='T255IdEstado_PQR_Otros')
    PQRSDF = models.ForeignKey(PQRSDF,on_delete=models.CASCADE,db_column='T255Id_PQRSDF', null=True)
    solicitud_usu_sobre_PQR = models.ForeignKey('SolicitudAlUsuarioSobrePQRSDF',on_delete=models.CASCADE,db_column='T255Id_SolicitudAlUsuSobrePQR', null=True)#PENDIENTE MODELO T266
    id_otros = models.ForeignKey(Otros,on_delete=models.SET_NULL, blank=True, null=True,db_column='T255Id_Otros')
    id_tramite = models.ForeignKey('tramites.SolicitudesTramites', models.SET_NULL, db_column='T255Id_SolicitudTramite', blank=True, null=True)
    estado_solicitud = models.ForeignKey(EstadosSolicitudes,on_delete=models.CASCADE,db_column='T255Id_EstadoSolicitud')
    fecha_iniEstado = models.DateTimeField(db_column='T255fechaIniEstado')
    persona_genera_estado = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,db_column='T255Id_PersonaGeneraEstado', null=True)
    estado_PQR_asociado = models.ForeignKey('self',on_delete=models.CASCADE,db_column='T255Id_Estado_PQR_Asociado', null=True)#PENDIENTE MODELO T255

    class Meta:
       # managed = False  # Evita que Django gestione esta tabla en la base de datos.
        db_table = 'T255Estados_PQR_Otros'


class InfoDenuncias_PQRSDF(models.Model):
    id_info_denuncia_PQRSDF = models.AutoField(primary_key=True, db_column='T256IdInfoDenuncia_PQRSDF')
    id_PQRSDF = models.ForeignKey(PQRSDF,on_delete=models.CASCADE,db_column='T256Id_PQRSDF', null=True)
    cod_municipio_cocalizacion_hecho = models.ForeignKey(Municipio,on_delete=models.CASCADE,max_length=5, db_column='T256Cod_MunicipioLocalizacionHecho')
    Cod_zona_localizacion = models.CharField(max_length=1, choices=TIPO_ZONAS_CHOICES, db_column='T256codZonaLocalizacion')
    barrio_vereda_localizacion = models.CharField(max_length=100, db_column='T256barrioOVeredaLocalizacion', null=True)
    direccion_localizacion = models.CharField(max_length=255, db_column='T256direccionLocalizacion', null=True)
    cod_recursos_fectados_presuntos = models.CharField(max_length=30, db_column='T256codRecursosAfectadosPresuntos')
    otro_recurso_Afectado_cual = models.CharField(max_length=50, db_column='T256otroRecursoAfectado_Cual', null=True)
    evidencias_soportan_hecho = models.CharField(max_length=1000, db_column='T256evidenciasSoportanHecho', null=True)
    nombre_completo_presunto_infractor = models.CharField(max_length=130, db_column='T256nombreCompleto_PresuntoInfractor', null=True)
    telefono_presunto_infractor = models.CharField(max_length=15, db_column='T256telefono_PresuntoInfractor', null=True)
    direccion_presunto_infractor = models.CharField(max_length=255, db_column='T256direccion_PresuntoInfractor', null=True)
    ya_habia_puesto_en_conocimiento = models.BooleanField(db_column='T256yaHabiaPuestoEnConocimiento')
    ante_que_autoridad_había_interpuesto = models.CharField(max_length=200, db_column='T256anteQueAutoridadHabíaInterpuesto', null=True)

    class Meta:
        #managed = False  # Evita que Django gestione esta tabla en la base de datos.
        db_table = 'T256InfoDenuncias_PQRSDF'


class Anexos(models.Model):
    id_anexo = models.AutoField(primary_key=True, db_column='T258IdAnexo')
    nombre_anexo = models.CharField(max_length=50, db_column='T258nombreAnexo')
    orden_anexo_doc = models.SmallIntegerField(db_column='T258ordenAnexoEnElDoc')
    cod_medio_almacenamiento = models.CharField(max_length=2, choices=medio_almacenamiento_CHOICES, db_column='T258codMedioAlmacenamiento')
    medio_almacenamiento_otros_Cual = models.CharField(max_length=30, db_column='T258medioAlmacenamientoOtros_Cual', null=True)
    numero_folios = models.SmallIntegerField(db_column='T258numeroFolios')
    ya_digitalizado = models.BooleanField(db_column='T258yaDigitalizado')
    observacion_digitalizacion = models.CharField(max_length=100, db_column='T258observacionDigitalizacion', null=True)
    id_docu_arch_exp = models.ForeignKey(DocumentosDeArchivoExpediente, blank=True, null=True, on_delete=models.SET_NULL, db_column='T258Id_DocuDeArch_Exp')

    class Meta:
        #managed = False  # Evita que Django gestione esta tabla en la base de datos.
        db_table = 'T258Anexos'


class MetadatosAnexosTmp(models.Model):
    id_metadatos_anexo_tmp = models.AutoField(primary_key=True, db_column='T260IdMetadatos_Anexo_Tmp')
    id_anexo = models.ForeignKey(Anexos, on_delete=models.CASCADE, db_column='T260Id_Anexo')
    nombre_original_archivo = models.CharField(max_length=50, db_column='T260nombreOriginalDelArchivo', null=True)
    fecha_creacion_doc = models.DateField(db_column='T260fechaCreacionDoc', null=True)
    descripcion = models.CharField(max_length=500, db_column='T260descripcion', null=True)
    asunto = models.CharField(max_length=150, db_column='T260asunto', null=True)
    cod_categoria_archivo = models.CharField(max_length=2, choices=tipo_archivo_CHOICES, db_column='T260codCategoriaArchivo', null=True)
    es_version_original = models.BooleanField(db_column='T260esVersionOriginal',null=True)
    tiene_replica_fisica = models.BooleanField(db_column='T260tieneReplicaFisica',null=True)
    nro_folios_documento = models.SmallIntegerField(db_column='T260nroFoliosDocumento',null=True)
    cod_origen_archivo = models.CharField(max_length=1, choices=origen_archivo_CHOICES, db_column='T260codOrigenArchivo',null=True)
    id_tipologia_doc = models.ForeignKey(TipologiasDoc, on_delete=models.SET_NULL, blank=True, null=True, db_column='T260Id_TipologiaDoc')
    cod_tipologia_doc_Prefijo = models.CharField(max_length=10, db_column='T260codTipologiaDoc_Prefijo', null=True)
    cod_tipologia_doc_agno = models.SmallIntegerField(db_column='T260codTipologiaDoc_Agno', null=True)
    cod_tipologia_doc_Consecutivo = models.CharField(max_length=20, db_column='T260codTipologiaDoc_Consecutivo', null=True)
    tipologia_no_creada_TRD = models.CharField(max_length=50, db_column='T260tipologiaNoCreadaEnTRD', null=True)
    palabras_clave_doc = models.CharField(max_length=255, db_column='T260palabrasClaveDoc', null=True)
    id_archivo_sistema = models.ForeignKey(ArchivosDigitales, on_delete=models.CASCADE, db_column='T260Id_ArchivoEnSistema')

    class Meta:
        #managed = False  # Evita que Django gestione esta tabla en la base de datos.
        db_table = 'T260Metadatos_Anexos_Tmp'
        unique_together = ('id_anexo',)  # Restricción para que Id_Anexo sea único


class modulos_radican(models.Model):
    id_ModuloQueRadica = models.AutoField(primary_key=True,db_column='T261Id_ModuloQueRadica')
    nombre = models.CharField(max_length=100,unique=True,db_column='T261nombre')

    class Meta:
        db_table = 'T261ModulosQueRadican'

class SolicitudAlUsuarioSobrePQRSDF(models.Model):
    id_solicitud_al_usuario_sobre_pqrsdf = models.AutoField(primary_key=True, db_column='T266IdSolicitudAlUsuarioSobrePQR')
    id_pqrsdf = models.ForeignKey(PQRSDF, on_delete =models.SET_NULL, db_column='T266Id_PQRSDF',null=True,blank=True)
    id_solicitud_tramite = models.ForeignKey('tramites.SolicitudesTramites',on_delete= models.SET_NULL, db_column='T266Id_SolicitudTramite',null=True,blank=True)
    id_persona_solicita = models.ForeignKey('transversal.Personas', models.CASCADE, db_column='T266Id_PersonaSolicita')
    id_und_org_oficina_solicita = models.ForeignKey(UnidadesOrganizacionales, models.CASCADE, db_column='T266Id_UndOrgOficina_Solicita')
    cod_tipo_oficio = models.CharField(max_length=1,choices=TIPOS_OFICIO_CHOICES,db_column='T266codTipoOficio')
    fecha_solicitud = models.DateTimeField(db_column='T66fechaSolicitud')
    asunto = models.CharField(max_length=100, db_column='T266asunto')
    descripcion = models.CharField(max_length=500, db_column='T266descripcion')
    cantidad_anexos = models.SmallIntegerField(null=True, db_column='T266cantidadAnexos')
    nro_folios_totales = models.SmallIntegerField(null=True, db_column='T266nroFoliosTotales')
    dias_para_respuesta = models.SmallIntegerField(null=True, db_column='T266diasParaRespuesta')
    id_radicado_salida = models.ForeignKey(T262Radicados, models.SET_NULL, db_column='T266Id_RadicadoSalida', blank=True, null=True)
    fecha_radicado_salida = models.DateTimeField(db_column='T266fechaRadicadoSalida', blank=True, null=True)
    id_estado_actual_solicitud = models.ForeignKey(EstadosSolicitudes, models.CASCADE, db_column='T266Id_EstadoActualSolicitud')
    fecha_ini_estado_actual = models.DateTimeField(db_column='T266fechaIniEstadoActual')
    id_doc_de_archivo_exp = models.ForeignKey(DocumentosDeArchivoExpediente, models.SET_NULL, db_column='T266Id_DocDeArch_Exp', blank=True, null=True)
    
    class Meta:
        db_table = 'T266SolicitudAlUsuarioSobrePQRSDF'


class ComplementosUsu_PQR(models.Model):
    idComplementoUsu_PQR = models.AutoField(primary_key=True, db_column='T267IdComplementoUsu_PQR')
    id_PQRSDF = models.ForeignKey(PQRSDF,on_delete=models.CASCADE,null=True, db_column='T267Id_PQRSDF')
    id_solicitud_usu_PQR = models.ForeignKey(SolicitudAlUsuarioSobrePQRSDF,on_delete=models.CASCADE,null=True, db_column='T267Id_SolicitudAlUsuSobrePQR')#T266
    id_persona_interpone = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,db_column='T267Id_PersonaInterpone',related_name='persona_interpone')
    cod_relacion_titular = models.CharField(max_length=2, choices=RELACION_TITULAR, db_column='T267codRelacionConElTitular')
    fecha_complemento = models.DateTimeField(db_column='T267fechaComplemento')
    id_medio_solicitud_comple = models.ForeignKey(MediosSolicitud,on_delete=models.CASCADE,db_column='T267Id_MedioSolicitudComple')
    asunto = models.CharField(max_length=100, db_column='T267asunto')
    descripcion = models.CharField(max_length=500, db_column='T267descripcion')
    cantidad_anexos = models.SmallIntegerField(db_column='T267cantidadAnexos')
    nro_folios_totales = models.SmallIntegerField(db_column='T267nroFoliosTotales')
    id_persona_recibe = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,null=True, db_column='T267Id_PersonaRecibe',related_name='persona_recibe')
    id_radicado = models.ForeignKey(T262Radicados,on_delete=models.CASCADE,null=True, db_column='T267Id_Radicado')
    fecha_radicado = models.DateTimeField(null=True, db_column='T267fechaRadicado')
    requiere_digitalizacion = models.BooleanField(db_column='T267requiereDigitalizacion')
    fecha_envio_definitivo_digitalizacion = models.DateTimeField(null=True, db_column='T267fechaEnvioDefinitivoADigitalizacion')
    fecha_digitalizacion_completada = models.DateTimeField(null=True, db_column='T267fechaDigitalizacionCompletada')
    fecha_integracion_solic_origen = models.DateTimeField(null=True, db_column='T267fechaIntegracionASolicOrigen')
    complemento_asignado_unidad = models.BooleanField(db_column='T267complementoAsignadoAUndOrg',default=False)
    id_doc_arch_exp = models.ForeignKey(DocumentosDeArchivoExpediente,on_delete=models.CASCADE,null=True, db_column='T267Id_DocDeArch_Exp')

    class Meta:
        db_table = 'T267ComplementosUsu_PQR'


class SolicitudDeDigitalizacion(models.Model):
    id_solicitud_de_digitalizacion = models.AutoField(primary_key=True, db_column='T263IdSolicitudDeDigitalizacion')
    id_pqrsdf = models.ForeignKey('Pqrsdf', models.SET_NULL, db_column='T263Id_PQRSDF', blank=True, null=True)
    id_complemento_usu_pqr = models.ForeignKey(ComplementosUsu_PQR, models.SET_NULL, db_column='T263Id_ComplementoUsu_PQR', blank=True, null=True)
    id_otro = models.ForeignKey(Otros, models.SET_NULL, db_column='T263Id_Otro', blank=True, null=True)
    id_tramite = models.ForeignKey('tramites.SolicitudesTramites', models.SET_NULL, db_column='T263Id_SolicitudTramite', blank=True, null=True)
    fecha_solicitud = models.DateTimeField(db_column='T263fechaSolicitud')
    fecha_rta_solicitud = models.DateTimeField(db_column='T263fechaRtaSolicitud', blank=True, null=True)
    observacion_digitalizacion = models.CharField(max_length=255, db_column='T263observacionDigitalizacion',null=True, blank=True)
    digitalizacion_completada = models.BooleanField(db_column='T263digitalizacionCompletada')
    devuelta_sin_completar = models.BooleanField(db_column='T263devueltaSinCompletar')
    id_persona_digitalizo = models.ForeignKey('transversal.Personas', models.SET_NULL, db_column='T263Id_PersonaDigitalizo', blank=True, null=True)

    class Meta:
        db_table = 'T263SolicitudesDeDigitalizacion'


class BandejaTareasPersona(models.Model):
    id_bandeja_tareas_persona = models.AutoField(primary_key=True, db_column='T264IdBandejaTareas_Persona')
    id_persona = models.ForeignKey('transversal.Personas', models.CASCADE, db_column='T264Id_Persona')
    pendientes_leer = models.BooleanField(db_column='T264pendientesLeer')
    class Meta:
        db_table = 'T264BandejasTareas_Persona'
        unique_together = ('id_persona',)


class TareaBandejaTareasPersona(models.Model):
    id_tarea_bandeja_tareas_persona = models.AutoField(primary_key=True, db_column='T265IdTarea_BandejaTareas_Persona')
    id_bandeja_tareas_persona = models.ForeignKey(BandejaTareasPersona,on_delete=models.CASCADE, db_column='T265Id_BandejaTareas_Persona')
    id_tarea_asignada = models.ForeignKey('TareasAsignadas',on_delete=models.CASCADE, db_column='T265Id_TareaAsignada')
    es_responsable_ppal = models.BooleanField(db_column='T265esResponsablePpal')
    fecha_leida = models.DateTimeField(db_column='T265fechaLeida', null=True)
    leida = models.BooleanField(db_column='T265leida',default=False)   

    class Meta:
        db_table = 'T265Tareas_BandejaTareas_Persona'
        unique_together = ('id_bandeja_tareas_persona', 'id_tarea_asignada')


class AsignacionPQR(models.Model):
    id_asignacion_pqr = models.AutoField(primary_key=True,db_column='T268IdAsignacion_PQR')
    id_pqrsdf = models.ForeignKey('PQRSDF',on_delete=models.CASCADE,db_column='T268Id_PQRSDF')
    consecutivo_asign_x_pqrsdf = models.SmallIntegerField(db_column='T268consecutivoAsignXPQRSDF')
    fecha_asignacion = models.DateTimeField(db_column='T268fechaAsignacion')
    id_persona_asigna = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,db_column='T268Id_PersonaAsigna',related_name='persona_asigna_pqrs')
    id_persona_asignada = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,db_column='T268Id_PersonaAsignada',related_name='persona_asignada_pqrs')
    cod_estado_asignacion = models.CharField(max_length=2,
                                             choices=[('Ac', 'Aceptado'),('Re', 'Rechazado')],
                                             db_column='T268codEstadoAsignacion',null=True,blank=True)
    fecha_eleccion_estado = models.DateTimeField(db_column='T268fechaEleccionEstado',null=True,blank=True)
    justificacion_rechazo = models.CharField(max_length=250,null=True,blank=True,db_column='T268justificacionRechazo')
    asignacion_de_ventanilla = models.BooleanField(db_column='T268asignacionDeVentanilla')
    id_und_org_seccion_asignada = models.ForeignKey(UnidadesOrganizacionales,on_delete=models.CASCADE,null=True,blank=True,db_column='T268Id_UndOrgSeccion_Asignada',related_name='unidad_asignada_pqrs')
    id_und_org_oficina_asignada = models.ForeignKey(UnidadesOrganizacionales,on_delete=models.CASCADE,null=True,blank=True,db_column='T268Id_UndOrgOficina_Asignada')

    class Meta:
        db_table = 'T268Asignacion_PQR'
        unique_together = (('id_pqrsdf', 'consecutivo_asign_x_pqrsdf'), )


class AsignacionTramites(models.Model):
    id_asignacion_tramite = models.AutoField(db_column='T279IdAsignacion_Tramite', primary_key=True)
    id_solicitud_tramite = models.ForeignKey('tramites.SolicitudesTramites',on_delete=models.CASCADE,db_column='T279Id_SolicitudTramite')
    consecutivo_asign_x_tramite = models.SmallIntegerField(db_column='T279consecutivoAsignXTramite', null=True, blank=True)
    fecha_asignacion = models.DateTimeField(db_column='T279fechaAsignacion', null=True, blank=True)
    id_persona_asigna = models.ForeignKey('transversal.Personas',on_delete = models.CASCADE,db_column='T279Id_PersonaAsigna',related_name='persona_asigna_tramite')
    id_persona_asignada =  models.ForeignKey('transversal.Personas',on_delete = models.CASCADE,db_column='T279Id_PersonaAsignada',related_name='persona_asignada_tramites')
    cod_estado_asignacion = models.CharField(max_length=2,
                                             choices=[('Ac', 'Aceptado'),('Re', 'Rechazado')], db_column='T279codEstadoAsignacion',null=True,blank=True)
    fecha_eleccion_estado = models.DateTimeField(db_column='T279fechaEleccionEstado',null=True,blank=True)
    justificacion_rechazo = models.CharField(db_column='T279justificacionRechazo', max_length=250, null=True, blank=True)
    asignacion_de_ventanilla = models.BooleanField(db_column='T279asignacionDeVentanilla')
    id_und_org_seccion_asignada = models.ForeignKey(UnidadesOrganizacionales,on_delete=models.SET_NULL,null=True,blank=True,db_column='T279Id_UndOrgSeccion_Asignada',related_name='unidad_asignada_tramites')
    id_und_org_oficina_asignada = models.ForeignKey(UnidadesOrganizacionales,on_delete=models.SET_NULL,null=True,blank=True,db_column='T279Id_UndOrgOficina_Asignada')
    class Meta:
        db_table = 'T279Asignacion_Tramites'
        unique_together = (('id_solicitud_tramite', 'consecutivo_asign_x_tramite'),)



class AsignacionOtros(models.Model):
    id_asignacion_otros = models.AutoField(primary_key=True,db_column='T303IdAsignacion_Otros')
    id_otros = models.ForeignKey(Otros,on_delete=models.CASCADE,db_column='T303Id_Otros')
    consecutivo_asign_x_otros = models.SmallIntegerField(db_column='T303consecutivoAsignXOtros')
    fecha_asignacion = models.DateTimeField(db_column='T303fechaAsignacion')
    id_persona_asigna = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,db_column='T303Id_PersonaAsigna',related_name='persona_asigna_otros')
    id_persona_asignada = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,db_column='T303Id_PersonaAsignada',related_name='persona_asignada_otros')
    cod_estado_asignacion = models.CharField(max_length=2,
                                             choices=[('Ac', 'Aceptado'),('Re', 'Rechazado')],
                                             db_column='T303codEstadoAsignacion',null=True,blank=True)
    fecha_eleccion_estado = models.DateTimeField(db_column='T303fechaEleccionEstado',null=True,blank=True)
    justificacion_rechazo = models.CharField(max_length=250,null=True,blank=True,db_column='T303justificacionRechazo')
    asignacion_de_ventanilla = models.BooleanField(db_column='T303asignacionDeVentanilla')
    id_und_org_seccion_asignada = models.ForeignKey(UnidadesOrganizacionales,on_delete=models.CASCADE,null=True,blank=True,db_column='T303Id_UndOrgSeccion_Asignada',related_name='unidad_asignada_otros')
    id_und_org_oficina_asignada = models.ForeignKey(UnidadesOrganizacionales,on_delete=models.CASCADE,null=True,blank=True,db_column='T303Id_UndOrgOficina_Asignada')

    class Meta:
        db_table = 'T303Asignacion_Otros'
        unique_together = (('id_otros', 'consecutivo_asign_x_otros'), )


class RespuestaPQR(models.Model):
    id_respuesta_pqr = models.AutoField(primary_key=True,db_column='T269IdRespuesta_PQR')
    id_pqrsdf = models.ForeignKey(PQRSDF,on_delete=models.CASCADE,db_column='T269Id_PQRSDF')
    fecha_respuesta = models.DateTimeField(db_column='T269fechaRespuesta')
    asunto = models.CharField(max_length=100,db_column='T269asunto')
    descripcion = models.CharField(max_length=500,db_column='T269descripcion')
    cantidad_anexos = models.SmallIntegerField(db_column='T269cantidadAnexos')
    nro_folios_totales = models.SmallIntegerField(db_column='T269nroFoliosTotales')
    id_persona_responde = models.ForeignKey('transversal.personas',on_delete=models.CASCADE,db_column='T269Id_PersonaResponde')
    id_radicado_salida = models.ForeignKey(T262Radicados,on_delete=models.CASCADE,null=True,db_column='T269Id_RadicadoSalida')
    fecha_radicado_salida = models.DateTimeField(null=True,db_column='T269fechaRadicadoSalida')
    id_doc_archivo_exp = models.ForeignKey(DocumentosDeArchivoExpediente,on_delete=models.CASCADE,null=True,db_column='T269Id_DocDeArch_Exp')

    class Meta:
        db_table = 'T269Respuestas_PQR'
        unique_together = (('id_pqrsdf', 'id_persona_responde', 'fecha_respuesta'), )


class Anexos_PQR(models.Model):
    id_anexo_PQR = models.AutoField(primary_key=True,db_column='T259IdAnexos_PQR_Otros')
    id_PQRSDF = models.ForeignKey(PQRSDF,on_delete=models.CASCADE,null=True,db_column='T259Id_PQRSDF')
    id_solicitud_usu_sobre_PQR = models.ForeignKey(SolicitudAlUsuarioSobrePQRSDF,on_delete=models.CASCADE,db_column='T259Id_SolicitudAlUsuSobrePQR',null=True)#T266
    id_otros =  models.ForeignKey(Otros, on_delete=models.SET_NULL, blank=True, null=True, db_column='T259Id_Otros')
    id_complemento_usu_PQR = models.ForeignKey(ComplementosUsu_PQR,on_delete=models.CASCADE,db_column='T259Id_ComplementoUsuAPQR', null=True)#T267
    id_respuesta_PQR = models.ForeignKey(RespuestaPQR,on_delete=models.CASCADE,db_column='T259Id_Respuesta_PQR', null=True)
    id_anexo = models.ForeignKey(Anexos,on_delete=models.CASCADE,db_column='T259Id_Anexo')

    class Meta:
        unique_together = [("id_anexo",)]
        db_table = 'T259Anexos_PQR_Otros'

