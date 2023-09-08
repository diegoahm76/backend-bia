from django.db import models
from django.forms import ValidationError
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad, CuadrosClasificacionDocumental
from gestion_documental.choices.disposicion_final_series_choices import disposicion_final_series_CHOICES
from gestion_documental.choices.tipos_medios_doc_choices import tipos_medios_doc_CHOICES
from gestion_documental.choices.tipos_medios_formato_choices import tipos_medios_formato_CHOICES
from transversal.models.personas_models import Personas


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

    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T210Formatos_TipoMedio'
        verbose_name = 'Formato Tipo Medio'
        verbose_name_plural = 'Formatos Tipos Medios'
        unique_together = ['nombre', 'cod_tipo_medio_doc']

class TipologiasDoc(models.Model):
    id_tipologia_documental = models.AutoField(editable=False, primary_key=True, db_column='T208IdTipologiaDoc')
    nombre = models.CharField(max_length=50, unique=True, db_column='T208nombre')
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
    justificacion_cambio = models.CharField(max_length=255, null=True, blank=True, db_column='T218JustificacionCambio')
    ruta_archivo_cambio = models.FileField(max_length=255, upload_to='gestion_documental/catalogo_trd/', null=True, blank=True, db_column='T218RutaArchivoCambio')
    
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
    ruta_archivo = models.CharField(max_length=255, null=True, blank =True, db_column='T219rutaArchivoCambio')
    id_persona_cambia = models.ForeignKey(Personas, null=True, blank=True, on_delete=models.SET_NULL, db_column='T219Id_PersonaCambia')

    def __str__(self):
        return str(self.id_historico_catserie_unidadorg_ccd_trd)

    class Meta:
        db_table = 'T219Historicos_CatSeries_UndOrg_CCD_TRD'
        verbose_name= 'Historicos Categoria Series UnidadOrg CCD TRD'
        verbose_name_plural = 'Historicos Categorias Series UnidadOrg CCD TRD'
