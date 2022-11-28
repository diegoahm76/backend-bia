from django.db import models
from gestion_documental.models.ccd_models import SeriesSubseriesUnidadOrg, CuadrosClasificacionDocumental
from gestion_documental.choices.tipo_clasificacion_choices import tipo_clasificacion_CHOICES

class TablasControlAcceso(models.Model):
    id_TCA=models.AutoField(primary_key=True, editable=False, db_column='T216IdTCA')
    id_CCD=models.ForeignKey(CuadrosClasificacionDocumental,on_delete=models.CASCADE,db_column='T216Id_CCD')
    version=models.CharField(max_length=30,unique=True,db_column='T216version')
    nombre=models.CharField(max_length=200,unique=True,db_column='T216nombre')
    fecha_terminado=models.DateTimeField(blank=True,null=True,db_column='T216fechaTerminado')
    fecha_puesta_produccion=models.DateTimeField(blank=True,null=True,db_column='T216fechaPuestaEnProduccion')
    fecha_retiro_produccion=models.DateTimeField(blank=True,null=True,db_column='T216fechaRetiroDeProduccion')
    justificacion_nueva_version=models.CharField(max_length=500,blank=True,null=True,db_column='T216justificacionNuevaVersion')
    ruta_soporte=models.CharField(max_length=200,blank=True,null=True,db_column='T216rutaSoporte')
    actual=models.BooleanField(default=False,db_column='T216actual')
    
    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table='T216TablasControlAcceso'
        verbose_name='Tabla de control de acceso'
        verbose_name_plural='Tablas de control de acceso'
        
class ClasificacionSeriesSubDoc(models.Model):
    cod_clas_serie_doc=models.IntegerField(db_column='T214CodClasSerieDoc')
    tipo_clasificacion=models.CharField(max_length=20,choices=tipo_clasificacion_CHOICES,db_column='T214tipoClasificacion')
    
    def __str__(self):
        return str(self.cod_clas_serie_doc)
    
    class Meta:
        db_table='T214ClasificacionSeriesSubDoc'
        verbose_name='Clasificacion serie sub Doc '
        verbose_name_plural='Clasificaciones serie sub Doc'

class PermisosGD(models.Model):
    permisos_GD=models.AutoField(primary_key=True, editable=False,db_column='T213IdPermisosGD')
    tipo_permiso=models.CharField(max_length=20,db_column='T213tipoPermiso')
    
    def __str__(self):
        return str(self.permisos_GD)
    
    class Meta:
        db_table='T213PermisosGD'
        verbose_name='Permiso GD'
        verbose_name_plural='Permisos GD'
        
class CCD_Clasif_Serie_Subserie_TCA(models.Model):
    id_serie_subserie_caro_permiso_GDTCA=models.AutoField(primary_key=True, db_column='T215IdSerieSubserieCargoPermisoGDTCA')
    id_TCA=models.ForeignKey(TablasControlAcceso,on_delete=models.CASCADE,db_column='T215Id_TCA')
    id_serie_subserie_doc=models.ForeignKey(SeriesSubseriesUnidadOrg,on_delete=models.CASCADE,db_column='T215Id_SerieSubserieDoc')
    id_permiso_GD=models.ForeignKey(PermisosGD,on_delete=models.CASCADE,db_column='T215Id_PermisoGd')
    fecha_registro=models.DateTimeField(db_column='T215fechaRegistro')
    ruta_archivo=models.TextField(db_column='T215rutaArchivo',blank=True,null=True)
    justificacion=models.CharField(max_length=255,db_column='T215justificacion',blank=True,null=True)
    
    def __str__(self):
        return str(self.id_serie_subserie_caro_permiso_GDTCA)
    
    class Meta:
        db_table='T215CCD_Clasif_Serie_Subserie_TCA'
        verbose_name='clasificacion serie subserie TCA'
        verbose_name_plural='clasificacion serie subseri TCA'
        unique_together = ['id_TCA', 'id_serie_subserie_doc','id_permiso_GD']
