from django.db import models
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad, CuadrosClasificacionDocumental
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, TablaRetencionDocumental
from gestion_documental.choices.tipo_clasificacion_choices import tipo_clasificacion_CHOICES
from transversal.models.personas_models import Personas
from transversal.models.organigrama_models import (
    UnidadesOrganizacionales
)
from transversal.models.base_models import (
    Cargos
)
from rest_framework.exceptions import ValidationError

class TablasControlAcceso(models.Model):
    id_tca=models.SmallAutoField(primary_key=True, editable=False, db_column='T216IdTCA')
    id_trd=models.OneToOneField(TablaRetencionDocumental, on_delete=models.CASCADE, db_column='T216Id_TRD')
    version=models.CharField(max_length=10, unique=True, db_column='T216version')
    nombre=models.CharField(max_length=50, unique=True, db_column='T216nombre')
    fecha_terminado=models.DateTimeField(blank=True, null=True, db_column='T216fechaTerminado')
    fecha_puesta_produccion=models.DateTimeField(blank=True, null=True, db_column='T216fechaPuestaEnProduccion')
    fecha_retiro_produccion=models.DateTimeField(blank=True, null=True, db_column='T216fechaRetiroDeProduccion')
    actual=models.BooleanField(default=False, db_column='T216actual')
    
    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table='T216TablasControlAcceso'
        verbose_name='Tabla de control de acceso'
        verbose_name_plural='Tablas de control de acceso'
        
class ClasificacionExpedientes(models.Model):
    cod_clas_expediente=models.CharField(max_length=1, primary_key=True, db_column='T214CodClasificacionExp')
    nombre=models.CharField(max_length=20, unique=True, db_column='T214nombre')
    
    def __str__(self):
        return str(self.cod_clas_expediente)
    
    class Meta:
        db_table='T214ClasificacionExpedientes'
        verbose_name='Clasificacion expediente'
        verbose_name_plural='Clasificaciones expedientes'

# class PermisosGD(models.Model):
#     cod_permiso_gd=models.CharField(primary_key=True, max_length=2, editable=False,db_column='T213CodPermisoGD')
#     tipo_permiso=models.CharField(max_length=20,db_column='T213tipoPermiso')
    
#     def __str__(self):
#         return str(self.cod_permiso_gd)
    
#     class Meta:
#         db_table='T213PermisosGD'
#         verbose_name='Permiso GD'
#         verbose_name_plural='Permisos GD'
        
class CatSeriesUnidadOrgCCD_TRD_TCA(models.Model):
    id_cat_serie_unidad_org_ccd_trd_tca=models.AutoField(primary_key=True, db_column='T215IdCatSerie_UndOrg_CCD_TRD_TCA')
    id_tca=models.ForeignKey(TablasControlAcceso, on_delete=models.CASCADE, db_column='T215Id_TCA')
    id_cat_serie_und_ccd_trd=models.OneToOneField(CatSeriesUnidadOrgCCDTRD, on_delete=models.CASCADE, db_column='T215Id_CatSerie_UndOrg_CCD_TRD')
    cod_clas_expediente=models.ForeignKey(ClasificacionExpedientes, on_delete=models.CASCADE, db_column='T215Cod_ClasificacionExp')
    fecha_registro=models.DateTimeField(auto_now_add=True, db_column='T215fechaRegistro')
    justificacion_cambio=models.CharField(max_length=255, db_column='T215justificacionDelCambio', blank=True, null=True)
    ruta_archivo_cambio = models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.SET_NULL, blank=True, null=True, db_column='T215rutaArchivoCambio')
    
    def __str__(self):
        return str(self.id_cat_serie_unidad_org_ccd_trd_tca)
    
    class Meta:
        db_table='T215CatSeries_UndOrg_CCD_TRD_TCA'
        verbose_name='Catalogo Serie Unidad CCD TRD TCA'
        verbose_name_plural='Catalogo Series Unidades CCD TRD TCA'


class HistoricoCatSeriesUnidadOrgCCD_TRD_TCA(models.Model):
    id_historico_catserie_unidad=models.AutoField(primary_key=True, editable=False, db_column='T220IdHistorico_CatSerie_UndOrg_CCD_TRD_TCA')
    id_catserie_unidad_org=models.ForeignKey(CatSeriesUnidadOrgCCD_TRD_TCA, on_delete=models.CASCADE, db_column='T220Id_CatSerie_UndOrg_CCD_TRD_TCA')
    cod_clasificacion_exp=models.ForeignKey(ClasificacionExpedientes, on_delete=models.CASCADE, db_column='T220Cod_ClasificacionExp')
    fecha_inicio=models.DateTimeField(auto_now_add=True, db_column='T220fechaInicioClasificacion')
    justificacion_del_cambio=models.CharField(max_length=255, blank=True, null=True, db_column='T220justificacionDelCambio')
    ruta_archivo_cambio = models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.SET_NULL, blank=True, null=True, db_column='T220rutaArchivoCambio')
    id_persona_cambia=models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T220Id_personaCambia')

    def __str__(self):
        return str(self.id_historico_catserie_unidad)
    
    class Meta:
        db_table='T220Historico_CatSeries_UndOrg_CCD_TRD_TCA'
        verbose_name='Historico catalogo serie unidad org CCD TRD TCA'
        verbose_name_plural='Historico catalogo series unidad org CCD TRD TCA'

# class HistoricoPermisosCatSeriesUndOrgTCA(models.Model):
#     id_historico_permisos_catseries_unidad_tca = models.AutoField(primary_key=True, editable=False, db_column='T223IdHistorico_Permisos_CatSeries_UndOrg_TCA')
#     id_permisos_catserie_unidad_tca = models.ForeignKey(PermisosCatSeriesUnidadOrgTCA, on_delete=models.CASCADE, db_column='T223Id_Permisos_CatSerie_UndOrg_TCA')
#     fecha_inicio = models.DateTimeField(auto_now_add=True, db_column='T223fechaIncioConfiguracion')
#     nombre_permisos = models.CharField(max_length=255, db_column='T223nombrePermisos')
#     justificacion = models.CharField(max_length=255, blank=True, null=True, db_column='T223justificacion')
#     ruta_archivo = models.FileField(max_length=255 ,blank=True, null=True, db_column='T223rutaArchivo')
#     id_persona_cambia = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T223Id_PersonaCambia')

#     def __str__(self):
#         return str(self.id_historico_permisos_catseries_unidad_tca)
    
#     class Meta:
#         db_table='T223Historico_Permisos_CatSeries_UndOrg_TCA'
#         verbose_name='Historico Permiso CatSerie Unidad TCA'
#         verbose_name_plural='Historicos Permisos CatSeries Unidades TCA'