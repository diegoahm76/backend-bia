from django.db import models
from almacen.models.organigrama_models import Organigramas, UnidadesOrganizacionales

class CuadrosClasificacionDocumental(models.Model):
    id_ccd = models.AutoField(primary_key=True, editable=False, db_column='T206IdCCD')
    id_organigrama = models.ForeignKey(Organigramas, on_delete=models.CASCADE, db_column='T206Id_Organigrama')
    version = models.CharField(max_length=10, unique=True, db_column='T206version')
    nombre = models.CharField(max_length=50, unique=True, db_column='T206nombre')
    fecha_terminado = models.DateTimeField(null=True, blank=True, db_column='T206fechaTerminado')
    fecha_puesta_produccion = models.DateTimeField(null=True, blank=True, db_column='T206fechaPuestaEnProduccion')
    fecha_retiro_produccion = models.DateTimeField(null=True, blank=True, db_column='T206fechaRetiroDeProduccion')
    justificacion = models.CharField(max_length=255,null=True, blank=True, db_column='T206justificacionNuevaVersion')
    ruta_soporte = models.FileField(max_length=255,null=True, blank=True, db_column='T206rutaSoporte')
    actual = models.BooleanField(default=False, db_column='T206actual')
    valor_aumento_serie = models.SmallIntegerField(db_column='T206valorAumentoSerie')
    valor_aumento_subserie = models.SmallIntegerField(db_column='T206valorAumentoSubserie')
    
    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table = 'T206CuadrosClasificacionDoc'
        verbose_name= 'Cuadro Clasificacion Documental'
        verbose_name_plural = 'Cuadros Clasificacion Documental'
    
class SeriesDoc(models.Model):
    id_serie_doc = models.AutoField(primary_key=True, editable=False, db_column='T203IdSerieDocCCD')
    nombre = models.CharField(max_length=200,db_column='T203nombre')
    codigo = models.CharField(max_length=200,db_column='T203codigo')
    id_ccd = models.ForeignKey(CuadrosClasificacionDocumental, on_delete=models.CASCADE, db_column='T203Id_CCD')

    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table = 'T203SeriesDoc_CCD'
        verbose_name = 'Serie'
        verbose_name_plural = 'Series'
        ordering = ['nombre']
        unique_together =(('id_ccd','nombre'),('id_ccd','codigo'))       

class SubseriesDoc(models.Model):
    id_subserie_doc = models.AutoField(primary_key=True, editable=False, db_column='T204IdSubserie_Serie_CCD')
    nombre = models.CharField(max_length=200, db_column='T204nombre')
    codigo = models.CharField(max_length=200,db_column='T204codigo')
    id_serie_doc = models.ForeignKey(SeriesDoc, on_delete=models.CASCADE, db_column='T204Id_SerieDoc_CCD')

    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T204Subseries_Series_CCD'
        verbose_name = 'Subserie'
        verbose_name_plural = 'Subseries'
        unique_together = (('id_serie_doc','nombre'), ('id_serie_doc','codigo'))        
        ordering = ['nombre']

class CatalogosSeries(models.Model):
    id_catalogo_serie = models.AutoField(primary_key=True, editable=False, db_column='T205IdCatalogoSerie_CCD')
    id_serie_doc = models.ForeignKey(SeriesDoc,on_delete=models.CASCADE,db_column='T205Id_SerieDoc_CCD')
    id_subserie_doc = models.ForeignKey(SubseriesDoc, on_delete=models.SET_NULL, null=True, blank=True, db_column='T205Id_Subserie_Serie_CCD')

    def __str__(self):
        return str(self.id_catalogo_serie)

    class Meta:
        db_table = 'T205CatalogosSeries_CCD'
        verbose_name = 'Catalogo Serie'
        verbose_name_plural = 'Catalogos Series'
        unique_together= ['id_serie_doc','id_subserie_doc']

class CatalogosSeriesUnidad(models.Model):
    id_cat_serie_und = models.AutoField(primary_key=True, editable=False, db_column='T224IdCatSerie_UndOrg_CCD')
    id_unidad_organizacional = models.ForeignKey(UnidadesOrganizacionales,on_delete=models.CASCADE,db_column='T224Id_UnidadOrganizacional ')
    id_catalogo_serie = models.ForeignKey(CatalogosSeries, on_delete=models.CASCADE, db_column='T224Id_CatalogoSerie_CCD')

    def __str__(self):
        return str(self.id_cat_serie_und)

    class Meta:
        db_table = 'T224CatSeries_UndOrg_CCD'
        verbose_name = 'Catalogo Serie Unidad'
        verbose_name_plural = 'Catalogos Series Unidades'
        unique_together= ['id_unidad_organizacional','id_catalogo_serie']