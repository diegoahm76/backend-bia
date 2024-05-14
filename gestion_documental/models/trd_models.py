from django.db import models
from django.forms import ValidationError
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad, CuadrosClasificacionDocumental 
from gestion_documental.choices.disposicion_final_series_choices import disposicion_final_series_CHOICES
from gestion_documental.choices.tipos_medios_doc_choices import tipos_medios_doc_CHOICES
from gestion_documental.choices.tipos_medios_formato_choices import tipos_medios_formato_CHOICES
from gestion_documental.choices.cod_nivel_consecutivo_choices import cod_nivel_consecutivo_CHOICES
#from gestion_documental.models.expedientes_models import ArchivosDigitales
from transversal.models.personas_models import Personas
from transversal.models.organigrama_models import UnidadesOrganizacionales



class TablaRetencionDocumental(models.Model):
    id_trd = models.SmallAutoField(primary_key=True, editable=False, db_column='T212IdTRD')
    id_ccd = models.OneToOneField(CuadrosClasificacionDocumental, on_delete=models.CASCADE, db_column='T212Id_CCD')
    version = models.CharField(max_length=10, unique=True, db_column='T212version')
    nombre = models.CharField(max_length=50, unique=True, db_column='T212nombre')
    fecha_terminado = models.DateTimeField(null=True, blank=True, db_column='T212fechaTerminado')
    fecha_puesta_produccion = models.DateTimeField(null=True, blank=True, db_column='T212fechaPuestaEnProduccion')
    fecha_retiro_produccion = models.DateTimeField(null=True, blank=True, db_column='T212fechaRetiroDeProduccion')
    actual = models.BooleanField(default=False, db_column='T212actual')

    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table = 'T212TablasRetencionDoc'
        verbose_name= 'Tabla de Retención Documental'
        verbose_name_plural = 'Tablas de Retención Documental'

class TiposMediosDocumentos(models.Model):
    cod_tipo_medio_doc = models.CharField(max_length=1, choices=tipos_medios_doc_CHOICES, primary_key=True, editable=False, db_column='T209CodTipoMedioDoc')
    nombre = models.CharField(max_length=20, unique=True, db_column='T209nombre')

    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T209TiposMediosDocumentos'
        verbose_name = 'Tipo Medio Documento'
        verbose_name_plural = 'Tipos Medios Documentos'


class FormatosTiposMedio(models.Model):
    id_formato_tipo_medio = models.SmallAutoField(primary_key=True, editable=False, db_column='T210IdFormato_TipoMedio')
    cod_tipo_medio_doc = models.ForeignKey(TiposMediosDocumentos, on_delete=models.CASCADE, db_column='T210Cod_TipoMedioDoc')
    nombre = models.CharField(max_length=20, db_column='T210nombre')
    registro_precargado=models.BooleanField(default=False, db_column='T210registroPrecargado')
    activo = models.BooleanField(default=True, db_column='T210activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T210itemYaUsado')
    control_tamagno_max = models.BooleanField(null=True, db_column='T210controlarTamagnoMax')
    tamagno_max_mb = models.SmallIntegerField(null=True,blank=True ,db_column='T210tamagnoMaxEnMB')
    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T210Formatos_TipoMedio'
        verbose_name = 'Formato Tipo Medio'
        verbose_name_plural = 'Formatos Tipos Medios'
        unique_together = ['nombre', 'cod_tipo_medio_doc']

class TipologiasDoc(models.Model):
    id_tipologia_documental = models.AutoField(editable=False, primary_key=True, db_column='T208IdTipologiaDoc')
    nombre = models.CharField(max_length=255, unique=True, db_column='T208nombre')
    cod_tipo_medio_doc = models.ForeignKey(TiposMediosDocumentos, on_delete=models.CASCADE, db_column='T208Cod_TipoMedioDoc')
    activo = models.BooleanField(default=True, db_column='T208activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T208ItemYaUsado')

    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T208TipologiasDoc'
        verbose_name = 'Tipologia Documental'
        verbose_name_plural = 'Tipologias Documentales'
        ordering = ['nombre']

class FormatosTiposMedioTipoDoc(models.Model):
    id_formato_tipomedio_tipo_doc = models.AutoField(primary_key=True, editable=False, db_column='T217IdFormato_TipoMedio_TipoDoc')
    id_tipologia_doc = models.ForeignKey(TipologiasDoc, on_delete=models.CASCADE, db_column='T217Id_TipologiaDoc')
    id_formato_tipo_medio = models.ForeignKey(FormatosTiposMedio, on_delete=models.CASCADE, db_column='T217Id_Formato_TipoMedio')

    def __str__(self):
        return str(self.id_formato_tipomedio_tipo_doc)

    class Meta:
        db_table = 'T217Formatos_TiposMedio_TipoDoc'
        verbose_name = 'Formatos Tipos Medio Tipologia Documental'
        verbose_name_plural = 'Formatos Tipos Medio Tipologia Documental'
        unique_together = ['id_tipologia_doc','id_formato_tipo_medio']

class DisposicionFinalSeries(models.Model):
    cod_disposicion_final = models.CharField(max_length=1, editable=False, primary_key=True, db_column='T207CodDisposicionFinal')
    nombre = models.CharField(max_length=30, unique=True, db_column='T207nombre')

    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T207DisposicionFinalSeries'
        verbose_name = 'Disposición Final Serie'
        verbose_name_plural = 'Disposición Final Series'

class CatSeriesUnidadOrgCCDTRD(models.Model):
    id_catserie_unidadorg = models.AutoField(primary_key=True, editable=False, db_column='T218IdCatSerie_UndOrg_CCD_TRD')
    id_trd = models.ForeignKey(TablaRetencionDocumental, on_delete=models.CASCADE, db_column='T218Id_TRD')
    id_cat_serie_und = models.OneToOneField(CatalogosSeriesUnidad, on_delete=models.CASCADE, db_column='T218Id_CatSerie_UndOrg_CCD')
    cod_disposicion_final = models.ForeignKey(DisposicionFinalSeries, on_delete=models.CASCADE, db_column='T218Cod_DisposicionFinal')
    digitalizacion_dis_final = models.BooleanField(null=True, blank=True, db_column='T218digitalizacionDispFinal')
    tiempo_retencion_ag = models.SmallIntegerField(null=True, blank=True, db_column='T218tiempoRetencionAG')
    tiempo_retencion_ac = models.SmallIntegerField(null=True, blank=True, db_column='T218tiempoRetencionAC')
    descripcion_procedimiento = models.CharField(max_length=1000, null=True, blank=True, db_column='T218descripcionProcedimiento')
    fecha_registro = models.DateTimeField(auto_now=True, null=True, blank=True, db_column='T218fechaRegistro')
    justificacion_cambio = models.CharField(max_length=255, null=True, blank=True, db_column='T218justificacionCambio')
    ruta_archivo_cambio = models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.SET_NULL, blank=True, null=True, db_column='T218rutaArchivoCambio')
    
    def __str__(self):
        return str(self.id_catserie_unidadorg)

    class Meta:
        db_table = 'T218CatSeries_UndOrg_CCD_TRD'
        verbose_name = 'Categoria serie Unidad Organizacional CCD TRD'
        verbose_name = 'Categorias series Unidad Organizacional CCD TRD'
        # unique_together = ['id_trd', 'id_cat_serie_und']


class SeriesSubSUnidadOrgTRDTipologias(models.Model):
    id_tipologia_catserie_unidad_ccd_trd = models.AutoField(primary_key=True, editable=False, db_column='T211IdTipologia_CatSeries_UndOrg_CCD_TRD')
    id_catserie_unidadorg_ccd_trd = models.ForeignKey(CatSeriesUnidadOrgCCDTRD, on_delete=models.CASCADE, db_column='T211Id_CatSerie_UndOrg_CCD_TRD')
    id_tipologia_doc = models.ForeignKey(TipologiasDoc, on_delete=models.CASCADE, db_column='T211Id_TipologiaDoc')
    activo = models.BooleanField(default=True, db_column='T211activo')
    reservada = models.BooleanField(default=False, db_column='T211reservada')
    
    def __str__(self):
        return str(self.id_tipologia_catserie_unidad_ccd_trd)

    class Meta:
        db_table = 'T211Tipologias_CatSeries_UndOrg_CCD_TRD'
        verbose_name= 'Categoria Series Unidad Organizacional CCD TRD'
        verbose_name_plural = 'CategoriaS Series Unidad Organizacional CCD TRD'
        unique_together = ['id_catserie_unidadorg_ccd_trd', 'id_tipologia_doc']


class HistoricosCatSeriesUnidadOrgCCDTRD(models.Model):
    id_historico_catserie_unidadorg_ccd_trd = models.AutoField(primary_key=True, editable=False, db_column='T219IdHistorico_CatSeries_UndOrg_CCD_TRD')
    id_catserie_unidadorg_ccd_trd = models.ForeignKey(CatSeriesUnidadOrgCCDTRD, on_delete=models.CASCADE, db_column='T219Id_CatSerie_UndOrg_CCD_TRD')
    cod_disposicion_final = models.ForeignKey(DisposicionFinalSeries, on_delete=models.CASCADE, db_column='T219Cod_DisposicionFinal')
    digitalizacion_disp_final = models.BooleanField(default=False, db_column='T219digitalizacionDispFinal')
    tiempo_retencion_ag = models.SmallIntegerField(db_column='T219tiempoRetencionAG')
    tiempo_retencion_ac = models.SmallIntegerField(db_column='T219tiempoRetencionAC')
    descripcion_procedimiento = models.CharField(max_length=1000, db_column='T219descripcionProcedimiento')
    fecha_registro_historico = models.DateTimeField(auto_now=True, db_column='T219fechaInicioDisposicion')
    justificacion = models.CharField(max_length=255, null=True, blank=True, db_column='T219justificacionDelCambio')
    # ruta_archivo = models.CharField(max_length=255, null=True, blank =True, db_column='T219rutaArchivoCambio')
    ruta_archivo = models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.SET_NULL, blank=True, null=True, db_column='T219rutaArchivoCambio')
    id_persona_cambia = models.ForeignKey(Personas, null=True, blank=True, on_delete=models.SET_NULL, db_column='T219Id_PersonaCambia')

    def __str__(self):
        return str(self.id_historico_catserie_unidadorg_ccd_trd)

    class Meta:
        db_table = 'T219Historicos_CatSeries_UndOrg_CCD_TRD'
        verbose_name= 'Historicos Categoria Series UnidadOrg CCD TRD'
        verbose_name_plural = 'Historicos Categorias Series UnidadOrg CCD TRD'

class ConfigTipologiasDocAgno(models.Model):
    id_config_tipologia_doc_agno = models.AutoField(primary_key=True, editable=False, db_column='T246ConfigTipologiasDocAgno')
    agno_tipologia = models.SmallIntegerField(db_column='T246agnoTipologia')
    id_tipologia_doc = models.ForeignKey(TipologiasDoc, on_delete=models.CASCADE, db_column='T246Id_TipologiaDoc')
    maneja_consecutivo = models.BooleanField(default=False, db_column='T246manejaConsecutivo')
    cod_nivel_consecutivo = models.CharField(max_length=2,null=True, blank=True, choices=cod_nivel_consecutivo_CHOICES, db_column='T246codNivelDelConsecutivo')
    item_ya_usado = models.BooleanField(default=False, db_column='T246itemYaUsado')
    class Meta:
        db_table = 'T246ConfigTipologiasDocAgno'
        verbose_name = 'Configuracion de tipologia documental'
        verbose_name_plural = 'Configuracion de tipologias documentales'
        unique_together = [('id_tipologia_doc'),( 'agno_tipologia')]


class ConsecPorNivelesTipologiasDocAgno(models.Model):
    id_consec_nivel_tipologias_doc_agno = models.AutoField(primary_key=True, editable=False, db_column='T247IdConsecPorNivel_TipologiasDocAgno')
    id_config_tipologia_doc_agno = models.ForeignKey(ConfigTipologiasDocAgno, on_delete=models.CASCADE, db_column='T247Id_ConfigTipologiaDocAgno')
    id_unidad_organizacional = models.ForeignKey(UnidadesOrganizacionales, null=True, blank=True, on_delete=models.SET_NULL, db_column='T247Id_UnidadOrganizacional')
    id_trd = models.ForeignKey(TablaRetencionDocumental, null=True, blank=True, on_delete=models.SET_NULL, db_column='T247Id_TRD')
    consecutivo_inicial = models.IntegerField(db_column='T247consecutivoInicial')
    cantidad_digitos = models.SmallIntegerField(db_column='T247cantidadDigitos')
    prefijo_consecutivo = models.CharField(max_length=10, null=True, blank =True, db_column='T247prefijoConsecutivo')
    item_ya_usado = models.BooleanField(default=False, db_column='T247itemYaUsado')
    id_persona_ult_config_implemen = models.ForeignKey(Personas, related_name='id_persona_ult_config_implemen', null=True, blank=True, on_delete=models.SET_NULL, db_column='T247Id_PersonaUltConfigImplemen')
    fecha_ult_config_implemen = models.DateTimeField(auto_now=True, null=True, blank=True, db_column='T247fechaUltConfigImplemen')
    consecutivo_actual = models.IntegerField(db_column='T247consecutivoActual')
    fecha_consecutivo_actual = models.DateTimeField(auto_now=True, null=True, blank=True, db_column='T247fechaConsecutivoActual')
    id_persona_consecutivo_actual = models.ForeignKey(Personas, null=True, blank=True,related_name='id_persona_consecutivo_actual', on_delete=models.SET_NULL, db_column='T247Id_PersonaConsecutivoActual')

    class Meta:
        db_table = 'T247ConsecPorNiveles_TipologiasDocAgno'
        verbose_name = 'Consecutivo por nivel de tipologia documental'
        verbose_name_plural = 'Consecutivos por niveles de tipologias documentales'
        unique_together = [('id_config_tipologia_doc_agno'),( 'id_unidad_organizacional')]


class ConsecutivoTipologia(models.Model):
    id_consecutivo_tipologia = models.AutoField(primary_key=True, db_column='T319IdConsecutivoTipologia')
    id_unidad_organizacional = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T319Id_UnidadOrganizacional')
    id_tipologia_doc = models.ForeignKey(TipologiasDoc, on_delete=models.CASCADE, db_column='T319Id_TipologiaDoc')
    CatalogosSeriesUnidad = models.ForeignKey('gestion_documental.CatalogosSeriesUnidad',blank=True,null=True ,on_delete=models.SET_NULL, db_column='T329Id_CatalogoSeriesUnidad',related_name='T319Id_CatalogoSeriesUnidad')
    agno_consecutivo = models.SmallIntegerField(db_column='T319agnoConsecutivo')
    nro_consecutivo = models.CharField(max_length=20, db_column='T319nroConsecutivo')
    prefijo_consecutivo = models.CharField(max_length=10, db_column='T319prefijoConsecutivo')
    fecha_consecutivo = models.DateTimeField(db_column='T319fechaConsecutivo')
    id_persona_genera = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T319Id_PersonaGenera')
    id_radicado_interno = models.ForeignKey('gestion_documental.T262Radicados', on_delete=models.SET_NULL, db_column='T319Id_RadicadoInterno', related_name='T319Id_RadicadoInterno', blank=True, null=True)
    fecha_radicado_interno = models.DateTimeField(db_column='T319fechaRadicadoInterno', blank=True, null=True)
    id_radicado_salida = models.ForeignKey('gestion_documental.T262Radicados', on_delete=models.SET_NULL, db_column='T319Id_RadicadoSalida', related_name='T319Id_RadicadoSalida', blank=True, null=True)
    fecha_radicado_salida = models.DateTimeField(db_column='T319fechaRadicadoSalida', blank=True, null=True)
    id_archivo_digital = models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.SET_NULL, db_column='T319Id_ArchivoDigital', blank=True, null=True)
    class Meta:
        db_table = 'T319ConsecutivoTipologia'
        #unique_together = [('agno_consecutivo','nro_consecutivo'),]    ble = 'T308Consecutivo'









