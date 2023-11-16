from django.db import models

from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD,TablaRetencionDocumental,TipologiasDoc
from transversal.models.organigrama_models import UnidadesOrganizacionales
from gestion_documental.models.ccd_models import SeriesDoc,SubseriesDoc
from seguridad.models import Personas
from gestion_documental.choices.tipo_expediente_choices import tipo_expediente_CHOICES
from gestion_documental.choices.estado_expediente_choices import estado_expediente_CHOICES
from gestion_documental.choices.etapa_actual_expediente_choices import etapa_actual_expediente_CHOICES
from gestion_documental.choices.categoria_archivo_choices import categoria_archivo_CHOICES
from gestion_documental.choices.tipo_origen_doc_choices import tipo_origen_doc_CHOICES
from gestion_documental.choices.tipo_subsistema_creado_choices import tipo_subsistema_creado_CHOICES
from gestion_documental.choices.tipo_radicado_choices import TIPOS_RADICADO_CHOICES
from gestion_documental.choices.operacion_realizada_choices import operacion_realizada_CHOICES


#EXPEDIENTES_DOCUMENTALES
#Almacena la información de los diferentes expedientes de las Series Documentales de las Unidades Organizacionales de la corporación.	

class ExpedientesDocumentales(models.Model):

    id_expediente_documental = models.AutoField(primary_key=True, db_column='T236IdExpedienteDocumental')
    codigo_exp_und_serie_subserie = models.CharField(max_length=50, db_column='T236codigoExp_UndSerieSubserie')
    codigo_exp_Agno = models.SmallIntegerField(db_column='T236codigoExp_Agno')
    codigo_exp_consec_por_agno	= models.SmallIntegerField(db_column='T236codigoExp_ConsecPorAgno', null=True, blank=True)
    id_cat_serie_und_org_ccd_trd_prop = models.ForeignKey(CatSeriesUnidadOrgCCDTRD, on_delete=models.CASCADE, db_column='T236Id_CatSerie_UndOrg_CCD_TRD_Prop')
    id_trd_origen= models.ForeignKey(TablaRetencionDocumental, on_delete=models.CASCADE, db_column='T236Id_TRDOrigen')
    id_und_seccion_propietaria_serie= models.ForeignKey(UnidadesOrganizacionales, related_name='id_und_seccion_propietaria_serie',on_delete=models.CASCADE, db_column='T236Id_UndSeccionPropietariaSerie')
    id_serie_origen= models.ForeignKey(SeriesDoc, on_delete=models.CASCADE, db_column='T236Id_SerieOrigen')
    id_subserie_origen= models.ForeignKey(SubseriesDoc, on_delete=models.SET_NULL, db_column='T236Id_SubserieOrigen',null=True, blank=True)
    titulo_expediente= models.CharField(max_length=255, db_column='T236tituloExpediente')
    descripcion_expediente	= models.CharField(max_length=500, db_column='T236descripcionExpediente',null=True,blank=True)
    fecha_apertura_expediente = models.DateTimeField(db_column='T236fechaAperturaExpediente')
    id_persona_titular_exp_complejo= models.ForeignKey(Personas, related_name='id_persona_titular_exp_complejo',blank=True,null=True, on_delete=models.SET_NULL, db_column='T236Id_PersonaTitular_ExpComplejo')
    cod_tipo_expediente = models.CharField(max_length=1, choices=tipo_expediente_CHOICES, db_column='T236codTipoExpediente')
    estado = models.CharField(max_length=1, choices=estado_expediente_CHOICES, db_column='T236estado')
    fecha_folio_inicial	 = models.DateTimeField(db_column='T236fechaFolioInicial')
    fecha_folio_final= models.DateTimeField(blank=True,null=True,db_column='T236fechaFolioFinal')
    fecha_cierre_reapertura_actual = models.DateTimeField(blank=True,null=True,db_column='T236fechaCierreReaperturaActual')
    fecha_firma_cierre_indice_elec = models.DateTimeField(blank=True,null=True,db_column='T236fechaFirmaCierreIndiceElec')
    palabras_clave_expediente = models.CharField(max_length=255, blank=True,null=True, db_column='T236palabrasClaveExpediente')
    cod_etapa_de_archivo_actual_exped = models.CharField(max_length=1, choices=etapa_actual_expediente_CHOICES, db_column='T236codEtapaDeArchivoActual_Exped')
    fecha_paso_a_archivo_central = models.DateTimeField(blank=True,null=True,db_column='T236fechaPasoAArchivoCentral')
    fecha_paso_a_archivo_historico = models.DateTimeField(blank=True,null=True,db_column='T236fechaPasoAArchivoHistorico')
    fecha_eliminacion_x_dispo_final	= models.DateTimeField(blank=True,null=True,db_column='T236fechaEliminacionXDispoFinal')
    tiene_carpeta_fisica = models.BooleanField(default=False, db_column='T236tieneCarpetaFisica')
    ubicacion_fisica_esta_actualizada = models.BooleanField(default=False, db_column='T236ubicacionFisicaEstaActualizada')
    anulado = models.BooleanField(blank=True, null=True, db_column='T236anulado')
    observacion_anulacion = models.CharField(max_length=255, blank=True, null=True, db_column='T236observacionAnulacion')
    fecha_anulacion	= models.DateTimeField(blank=True, null=True, db_column='T236fechaAnulacion')
    id_persona_anula = models.ForeignKey(Personas, related_name='id_persona_anula_expediente', blank=True, null=True, on_delete=models.SET_NULL, db_column='T236Id_PersonaAnula')
    creado_automaticamente = models.BooleanField(blank=True, null=True, db_column='T236creadoAutomaticamente')
    fecha_creacion_manual = models.DateTimeField(blank=True, null=True, db_column='T236fechaDeCreacionManual')
    id_persona_crea_manual = models.ForeignKey(Personas, related_name='id_persona_crea_manual_expediente', blank=True, null=True, on_delete=models.SET_NULL, db_column='T236Id_PersonaCreaManual')
    id_unidad_org_oficina_respon_original = models.ForeignKey(UnidadesOrganizacionales, related_name='id_unidad_org_oficina_respon_original',on_delete=models.CASCADE, db_column='T236Id_UnidadOrgOficinaRespon_Original')
    id_und_org_oficina_respon_actual = models.ForeignKey(UnidadesOrganizacionales,related_name='expedientes_respon_actual', on_delete=models.CASCADE, db_column='T236Id_UndOrgOficinaRespon_Actual')
    id_persona_responsable_actual	= models.ForeignKey(Personas, related_name='id_persona_responsable_actual',blank=True,null=True,on_delete=models.SET_NULL, db_column='T236Id_PersonaResponsableActual')

    class Meta:
        db_table = 'T236ExpedientesDocumentales'
        verbose_name = 'Expediente Docuemental'
        verbose_name_plural = 'Expedientes Documentales'
        unique_together = ('codigo_exp_und_serie_subserie', 'codigo_exp_Agno', 'codigo_exp_consec_por_agno')



class ArchivosDigitales(models.Model):

    id_archivo_digital = models.AutoField(primary_key=True, db_column='T238IdArchivoDigital')
    nombre_de_Guardado = models.CharField(max_length=20, db_column='T238nombreDeGuardado', unique=True)
    formato = models.CharField(max_length=20, db_column='T238formato')
    tamagno_kb = models.IntegerField(db_column='T238tamagnoEnKB')
    ruta_archivo = models.FileField(max_length=255, db_column='T238rutaArchivo')
    #ruta_archivo = models.CharField(max_length=500, db_column='T238rutaArchivo')
    fecha_creacion_doc = models.DateTimeField(auto_now=True,db_column='T238fechaCreacionDoc')
    es_Doc_elec_archivo = models.BooleanField(db_column='T238EsDocElecDeArchivo')

    def __str__(self):
            return self.nombre_de_Guardado
    
    class Meta:
            db_table = 'T238ArchivosDigitales'
            verbose_name = 'Archivo Digital'
            verbose_name_plural = 'Archivos Digitales'
        

        
class DocumentosDeArchivoExpediente(models.Model):

    id_documento_de_archivo_exped = models.AutoField(primary_key=True, db_column='T237IdDocumentoDeArchivo_Exped')
    id_expediente_documental = models.ForeignKey(ExpedientesDocumentales, on_delete=models.CASCADE, db_column='T237Id_ExpedienteDocumental')
    identificacion_doc_en_expediente = models.CharField(max_length=15, db_column='T237IdentificacionDoc_EnExpediente')
    nombre_asignado_documento = models.CharField(max_length=100, db_column='T237nombreAsignado_Documento')
    nombre_original_del_archivo = models.CharField(max_length=100,blank=True,null=True ,db_column='T237nombreOriginalDelArchivo')
    fecha_creacion_doc	= models.DateTimeField(db_column='T237fechaCreacionDoc')
    fecha_incorporacion_doc_a_Exp = models.DateTimeField(db_column='T237fechaIncorporacionDocAExp')
    descripcion	= models.CharField(max_length=200,blank=True,null=True , db_column='T237descripcion')
    asunto	= models.CharField(max_length=50, db_column='T237asunto')
    id_persona_titular	= models.ForeignKey(Personas, related_name='id_persona_titular',blank=True,null=True, on_delete=models.SET_NULL, db_column='T237Id_PersonaTitular')
    cod_categoria_archivo	= models.CharField(max_length=2, choices=categoria_archivo_CHOICES, db_column='T237codCategoríaArchivo')
    es_version_original	 = models.BooleanField(default=True, db_column='T237esVersionOriginal')
    tiene_replica_fisica = models.BooleanField(default=False, db_column='T237tieneReplicaFisica')
    nro_folios_del_doc	 = models.SmallIntegerField(db_column='T237nroFoliosDelDoc')
    cod_origen_archivo	= models.CharField(max_length=1, choices=tipo_origen_doc_CHOICES, db_column='T237codOrigenArchivo')
    orden_en_expediente	 = models.SmallIntegerField(db_column='T237ordenEnExpediente')
    id_tipologia_documental	= models.ForeignKey(TipologiasDoc,blank=True, null=True , on_delete=models.SET_NULL, db_column='T237Id_TipologiaDocumental')
    codigo_tipologia_doc_prefijo = models.CharField(max_length=20, blank=True, null=True, db_column='T237codigoTipologiaDoc_Prefijo')
    codigo_tipologia_doc_agno = models.SmallIntegerField(blank=True, null=True,db_column='T237codigoTipologiaDoc_Agno')
    codigo_tipologia_doc_consecutivo = models.CharField(max_length=50, blank=True, null=True, db_column='T237codigoTipologiaDoc_Consecutivo')
    es_un_archivo_anexo = models.BooleanField(default=False, db_column='T237esUnArchivoAnexo')
    id_doc_de_arch_del_cual_es_anexo =  models.ForeignKey('self', related_name='arch_anexo', on_delete=models.SET_NULL, null=True, blank=True, db_column='T237Id_DocDeArch_DelCualEsAnexo')
    tipologia_no_creada_trd	 = models.CharField(max_length=50, blank=True, null=True, db_column='T237tipologiaNoCreadaEnTRD')
    anexo_corresp_a_lista_chequeo	 = models.BooleanField(default=False, db_column='T237anexoCorrespAListaDeChequeo')
    cantidad_anexos	= models.SmallIntegerField(blank=True, null=True,db_column='T237cantidadDeAnexos')
    id_archivo_sistema	= models.ForeignKey(ArchivosDigitales, on_delete=models.SET_NULL, null=True, blank=True, db_column='T237Id_ArchivoEnSistema')#falta clase (oskitar)
    palabras_clave_documento = models.CharField(max_length=255,blank=True,null=True , db_column='T237palabrasClaveDocumento')
    sub_sistema_incorporacion = models.CharField(max_length=4, choices=tipo_subsistema_creado_CHOICES, db_column='T237subSistemaDeIncorporacion')
    cod_tipo_radicado = models.CharField(max_length=1, choices=TIPOS_RADICADO_CHOICES,blank=True, null=True, db_column='T237codTipoRadicado')
    codigo_radicado_prefijo	 = models.CharField(max_length=10,blank=True,null=True ,db_column='T237codigoRadicado_Prefijo')
    codigo_radicado_agno = models.SmallIntegerField(blank=True,null=True ,db_column='T237codigoRadicado_Agno')
    codigo_radicado_consecutivo = models.IntegerField(blank=True,null=True, db_column='T237codigoRadicado_Consecutivo')
    es_radicado_inicial_de_solicitud	= models.BooleanField(blank=True,null=True, db_column='T237esRadicadoInicialDeLaSolicitud')
    documento_requiere_rta = models.BooleanField(default=False, db_column='T237documentoRequiereRta')
    creado_automaticamente = models.BooleanField(blank=True, null=True, db_column='T237creadoAutomaticamente')
    fecha_indexacion_manual_sistema = models.DateTimeField(blank=True, null=True, db_column='T237fechaDeIndexacionManualEnElSistema')
    anulado = models.BooleanField(blank=True, null=True, db_column='T237anulado')
    observacion_anulacion = models.CharField(max_length=255, blank=True, null=True, db_column='T237observacionAnulacion')
    fecha_anulacion = models.DateTimeField(blank=True, null=True, db_column='T237fechaAnulacion')
    id_persona_anula = models.ForeignKey(Personas, blank=True, null=True, related_name='id_persona_anula_doc_exp', on_delete=models.SET_NULL, db_column='T237Id_PersonaAnula')
    id_doc_arch_respondido	 =  models.ForeignKey('self', related_name='arch_respondido', on_delete=models.SET_NULL, null=True, blank=True, db_column='T237Id_DocDeArch_Respondido')
    id_doc_arch_rad_ini_exp_simple =  models.ForeignKey('self', related_name='id_doc_arch_rad_exp_simple', on_delete=models.SET_NULL, null=True, blank=True, db_column='T237Id_DocDeArch_RadIni_EnExpSimple')
    id_und_org_oficina_creadora= models.ForeignKey(UnidadesOrganizacionales, related_name='id_und_org_oficina_creadora',on_delete=models.CASCADE, db_column='T237Id_UndOrgOficina_Creadora')
    id_persona_que_crea	= models.ForeignKey(Personas, related_name='id_persona_que_crea',on_delete=models.CASCADE, db_column='T237Id_PersonaQueCrea')
    id_und_org_oficina_respon_actual = models.ForeignKey(UnidadesOrganizacionales,related_name='id_und_org_oficina_respon_actual', on_delete=models.CASCADE, db_column='T237Id_UndOrgOficinaRespon_Actual')

    def __str__(self):
        return str(self.id_documento_de_archivo_exped)
    
    class Meta:
            db_table = 'T237DocumentosDeArchivo_Expediente'
            verbose_name = 'Documento De Archivo'
            verbose_name_plural = 'Documentos De Archivos'
            unique_together = [('id_expediente_documental', 'identificacion_doc_en_expediente')]




class IndicesElectronicosExp(models.Model):
    id_indice_electronico_exp	 = models.AutoField(primary_key=True, db_column='T239IdIndiceElectronicoExp')
    id_expediente_doc	 = models.ForeignKey(ExpedientesDocumentales, on_delete=models.CASCADE, db_column='T239Id_ExpedienteDoc')
    fecha_indice_electronico = models.DateTimeField(db_column='T239fechaIndiceElectronico')
    abierto = models.BooleanField(default=False, db_column='T239abierto')
    fecha_cierre = models.DateTimeField(null=True, blank=True,db_column='T239fechaCierre')
    id_persona_firma_cierre	= models.ForeignKey(Personas,  on_delete=models.SET_NULL, null=True, blank=True, db_column='T239Id_PersonaFirmaCierre')
    fecha_envio_cod_verificacion = models.DateTimeField(null=True, blank=True,db_column='T239fechaEnvioCodVerificacion')
    email_envio_cod_verificacion = models.CharField(max_length=100,blank=True,null=True , db_column='T239emailEnvioCodVerificacion')
    nro_cel_envio_cod_verificacion	 = models.CharField(max_length=15,blank=True,null=True , db_column='T239nroCelEnvioCodVerificacion')
    fecha_intro_cod_verificacion_ok	 = models.DateTimeField(null=True, blank=True,db_column='T239fechaIntroCodVerificacionOK')
    observacion_firme_cierre = models.CharField(max_length=255,blank=True,null=True , db_column='T239observacionFirmaCierre')

    class Meta:
            db_table = 'T239IndicesElectronicosExp'
            verbose_name = 'Indice electronico exp'
            verbose_name_plural = 'Indices Electronicos Exp'
         




class Docs_IndiceElectronicoExp (models.Model):
    id_doc_indice_electronico_exp	= models.AutoField(primary_key=True, db_column='T240IdDoc_IndiceElectronicoExp')
    id_indice_electronico_exp = models.ForeignKey(IndicesElectronicosExp, on_delete=models.CASCADE, db_column='T240Id_IndiceElectronicoExp')
    id_doc_archivo_exp = models.ForeignKey(DocumentosDeArchivoExpediente, on_delete=models.CASCADE, db_column='T240Id_DocDeArchivo_Exp')
    identificación_doc_exped = models.CharField(max_length=15, db_column='T240IdentificaciónDoc_EnExped')
    nombre_documento = models.CharField(max_length=100, db_column='T240nombreDocumento')
    id_tipologia_documental = models.ForeignKey(TipologiasDoc, on_delete=models.SET_NULL, null=True, blank=True,  db_column='T240Id_TipologiaDocumental')
    fecha_creacion_doc = models.DateTimeField(db_column='T240fechaCreacionDoc')
    fecha_incorporacion_exp	 = models.DateTimeField(db_column='T240fechaIncorporacionAExp')
    valor_huella = models.CharField(max_length=150, db_column='T240valorHuella')
    funcion_resumen	= models.CharField(max_length=5, db_column='T240funcionResumen')        
    orden_doc_expediente = models.SmallIntegerField(db_column='T240ordenDocEnExpediente')
    pagina_inicio = models.IntegerField(db_column='T240paginaInicio')
    pagina_fin = models.IntegerField(db_column='T240paginaFin')
    formato	= models.CharField(max_length=20, db_column='T240formato')        
    tamagno_kb = models.IntegerField(db_column='T240tamagnoEnKB')
    anulado = models.BooleanField(blank=True, null=True, db_column='T240anulado')
    cod_origen_archivo = models.CharField(max_length=1, choices=tipo_origen_doc_CHOICES, db_column='T240codOrigenArchivo')
    id_doc_indice_Anexo	=  models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, db_column='T240Id_DocIndice_DelCualEsAnexo')
    tipologia_no_creada_trd	 = models.CharField(max_length=50,blank=True,null=True , db_column='T240tipologiaNoCreadaEnTRD')
    es_un_archivo_anexo = models.BooleanField(default=False, db_column='T240esUnArchivoAnexo')

    def __str__(self):
        return str(self.id_doc_indice_electronico_exp)
    
    class Meta:
        db_table = 'T240Docs_IndiceElectronicoExp'
        verbose_name = 'Documento Indice Electronico'
        verbose_name_plural = 'Documentos Indices Electronicos'
        unique_together = [('id_indice_electronico_exp', 'id_doc_archivo_exp'),('id_indice_electronico_exp', 'identificación_doc_exped')]
    


class CierresReaperturasExpediente(models.Model):
    id_cierre_reapertura_exp = models.AutoField(primary_key=True, db_column='T241IdCierreReapertura_Exp')
    id_expediente_doc = models.ForeignKey(ExpedientesDocumentales, on_delete=models.CASCADE, db_column='T241Id_ExpedienteDoc')
    cod_operacion	 = models.CharField(max_length=1, choices=operacion_realizada_CHOICES, db_column='T241codOperacion')
    fecha_cierre_reapertura = models.DateTimeField(db_column='T241fechaCierreReapertura')
    justificacion_cierre_reapertura = models.CharField(max_length=255, db_column='T241justificacionCierreReapertura')
    id_persona_cierra_reabre = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T241Id_PersonaCierraReabre')
    cod_etapa_archivo_pre_reapertura= models.CharField(null=True, blank=True,max_length=1, choices=etapa_actual_expediente_CHOICES, db_column='T241codEtapaEnArchivo_PreReApertura')
    class Meta:
        db_table = 'T241CierresReaperturas_Expediente'
        verbose_name = 'Cierre De reapertura '
        verbose_name_plural = 'Cierres De Reaperturas'
      


class ArchivosSoporte_CierreReapertura(models.Model):
    id_archivo_soporte_cierre_reaper = models.AutoField(primary_key=True, db_column='T242IdArchivoSoporte_CierreReaper')
    id_cierre_reapertura_exp = models.ForeignKey(CierresReaperturasExpediente, on_delete=models.CASCADE, db_column='T242Id_CierreReapertura_Exp')
    id_doc_archivo_exp_soporte = models.ForeignKey(DocumentosDeArchivoExpediente, on_delete=models.CASCADE, db_column='T242Id_DocDeArchivo_Exp_Soporte')

    class Meta:
        db_table = 'T242ArchivosSoporte_CierreReapertura'
        verbose_name = 'Archivo De Soporte De Cierre Reapertura'
        verbose_name_plural = 'Archivos De Soportes De Cierres Reapertura'
        unique_together = ('id_cierre_reapertura_exp', 'id_doc_archivo_exp_soporte')
        
class DobleVerificacionTmp(models.Model):
    id_doble_verificacion = models.AutoField(primary_key=True, db_column='T270IdDobleVerificacion')
    id_expediente = models.ForeignKey(ExpedientesDocumentales, on_delete=models.CASCADE, db_column='T270Id_Expediente')
    id_persona_firma = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T270Id_PersonaFirma')
    codigo_generado = models.CharField(max_length=6, db_column='T270codigoGenerado')
    fecha_hora_codigo = models.DateTimeField(auto_now_add=True, db_column="T270fechaHoraCodigo")

    class Meta:
        db_table = 'T270DobleVerificacion_Tmp'
        verbose_name = 'Doble Verificacion Tmp'
        verbose_name_plural = 'Doble Verificacion Tmp'
        unique_together = ('id_expediente', 'id_persona_firma')
        
class ConcesionesAccesoAExpsYDocs(models.Model):
    id_concesion_acc = models.AutoField(primary_key=True, db_column='T272IdConcesionAcc')
    id_persona_concede_acceso = models.ForeignKey(Personas, on_delete=models.CASCADE, related_name='id_persona_concede_acceso_exp', db_column='T272Id_PersonaQueConcedeAcceso')
    id_persona_recibe_acceso = models.ForeignKey(Personas, on_delete=models.CASCADE, related_name='id_persona_recibe_acceso_exp', db_column='T272Id_PersonaALaQueSeConcedeAcceso')
    id_unidad_org_destinatario_conceder = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, related_name='id_unidad_org_destinatario_conceder_exp', db_column='T272Id_UndOrgDestinatarioAlConceder')
    id_expediente = models.ForeignKey(ExpedientesDocumentales, on_delete=models.SET_NULL, blank=True, null=True, db_column='T272Id_Expediente')
    con_acceso_tipologias_reservadas = models.BooleanField(blank=True, null=True, db_column='T272conAccesoATipologiasReservadas')
    id_documento_exp = models.ForeignKey(DocumentosDeArchivoExpediente, on_delete=models.SET_NULL, blank=True, null=True, db_column='T272Id_DocumentoExp')
    fecha_registro = models.DateTimeField(auto_now_add=True, db_column="T272fechaRegistro")
    fecha_acceso_inicia = models.DateField(db_column="T272fechaAccesoInicia")
    fecha_acceso_termina = models.DateField(db_column="T272fechaAccesoTermina")
    observacion = models.CharField(max_length=150, db_column='T272observacion')

    class Meta:
        db_table = 'T272ConcesionesAccesoAExpsYDocs'
        verbose_name = 'Concesion Acceso a Exps y Docs'
        verbose_name_plural = 'Concesiones Acceso a Exps y Docs'