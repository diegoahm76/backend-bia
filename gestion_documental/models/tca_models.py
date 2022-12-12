from django.db import models
from gestion_documental.models.ccd_models import SeriesSubseriesUnidadOrg, CuadrosClasificacionDocumental
from gestion_documental.choices.tipo_clasificacion_choices import tipo_clasificacion_CHOICES
from seguridad.models import Personas, Cargos
from almacen.models.organigrama_models import (
    UnidadesOrganizacionales
)
class TablasControlAcceso(models.Model):
    id_tca=models.AutoField(primary_key=True, editable=False, db_column='T216IdTCA')
    id_ccd=models.ForeignKey(CuadrosClasificacionDocumental,on_delete=models.CASCADE,db_column='T216Id_CCD')
    version=models.CharField(max_length=30,unique=True,db_column='T216version')
    nombre=models.CharField(max_length=200,unique=True,db_column='T216nombre')
    fecha_terminado=models.DateTimeField(blank=True,null=True,db_column='T216fechaTerminado')
    fecha_puesta_produccion=models.DateTimeField(blank=True,null=True,db_column='T216fechaPuestaEnProduccion')
    fecha_retiro_produccion=models.DateTimeField(blank=True,null=True,db_column='T216fechaRetiroDeProduccion')
    justificacion_nueva_version=models.CharField(max_length=255,blank=True,null=True,db_column='T216justificacionNuevaVersion')
    ruta_soporte=models.FileField(blank=True,null=True,db_column='T216rutaSoporte')
    actual=models.BooleanField(default=False,db_column='T216actual')
    
    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table='T216TablasControlAcceso'
        verbose_name='Tabla de control de acceso'
        verbose_name_plural='Tablas de control de acceso'
        
class ClasificacionExpedientes(models.Model):
    cod_clas_expediente=models.CharField(max_length=1,db_column='T214CodClasificacionExp')
    tipo_clasificacion=models.CharField(max_length=20,db_column='T214tipoClasificacion')
    
    def __str__(self):
        return str(self.cod_clas_serie_doc)
    
    class Meta:
        db_table='T214ClasificacionExpedientes'
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
        
class Clasif_Serie_Subserie_Unidad_TCA(models.Model):
    id_clasif_serie_subserie_unidad_tca=models.AutoField(primary_key=True, db_column='T215IdClasif_S_Ss_UndOrg_TCA')
    id_tca=models.ForeignKey(TablasControlAcceso,on_delete=models.CASCADE,db_column='T215Id_TCA')
    id_serie_subserie_unidad=models.ForeignKey(SeriesSubseriesUnidadOrg,on_delete=models.CASCADE,db_column='T215Id_SerieSubserieUnidadOrg')
    cod_clas_expediente=models.CharField(max_length=1,choices=tipo_clasificacion_CHOICES,db_column='T215Cod_ClasificacionExp')
    fecha_registro=models.DateTimeField(auto_now_add=True, db_column='T215fechaRegistro')
    justificacion_cambio=models.CharField(max_length=255,db_column='T215justificacionDelCambio',blank=True,null=True)
    ruta_archivo_cambio=models.FileField(db_column='T215rutaArchivoCambio',blank=True,null=True)
    
    def __str__(self):
        return str(self.id_clasif_serie_subserie_unidad_tca)
    
    class Meta:
        db_table='T215Clasif_S_Ss_UndOrg_TCA'
        verbose_name='Clasificacion Serie Subserie Unidad TCA'
        verbose_name_plural='Clasificacion Serie Subserie Unidad TCA'
        unique_together = ['id_tca', 'id_serie_subserie_unidad']


class Historico_Clasif_S_Ss_UndOrg_TCA(models.Model):
    id_historico_clasif_serie_subserie_unidad_tca=models.AutoField(primary_key=True,editable=False, db_column='T220IdHistorico_Clasif_S_Ss_UndOrg_TCA')
    id_clasif_s_ss_unidad_tca=models.ForeignKey(Clasif_Serie_Subserie_Unidad_TCA,on_delete=models.CASCADE,db_column='T220Id_Clasif_S_Ss_UndOrg_TCA')
    cod_clasificacion_exp=models.CharField(max_length=1,choices=tipo_clasificacion_CHOICES,db_column='T220CodClasificacionExp')
    fecha_inicio=models.DateTimeField(auto_now_add=True,db_column='T220fechaInicio')
    justificacion_del_cambio=models.CharField(max_length=255,blank=True,null=True,db_column='T220justificacionDelCambio')
    ruta_archivo_cambio=models.FileField(blank=True,null=True,db_column='T220rutaArchivoCambio')
    id_persona_cambia=models.ForeignKey(Personas,on_delete=models.CASCADE,db_column='T220Id_personaCambia')

    def __str__(self):
        return str(self.id_historico_clasif_serie_subserie_unidad_tca)

    class Meta:
        db_table='T220Historico_Clasif_S_Ss_UndOrg_TCA'
        verbose_name='Historico_clasificacion serie subserie unidad org tca'
        verbose_name_plural='Historico_clasificacion serie subserie unidad org tca'

class Cargos_Unidad_S_Ss_UndOrg_TCA(models.Model):
    id_cargo_unidad_s_subserie_unidad_org_tca=models.AutoField(primary_key=True,editable=False,db_column='T221IdCargo_Unidad_S_Ss_UndOrg_TCA')
    id_clasif_serie_subserie_unidad_tca=models.ForeignKey(Clasif_Serie_Subserie_Unidad_TCA,on_delete=models.CASCADE,db_column='T221Id_Clasif_S_Ss_UndOrg_TCA')
    id_cargo_persona=models.ForeignKey(Cargos,on_delete=models.CASCADE,db_column='T221Id_CargoPersona')
    id_unidad_org_cargo=models.ForeignKey(UnidadesOrganizacionales,on_delete=models.CASCADE,db_column='T221Id_UnidadOrgCargo')
    fecha_configuracion=models.DateTimeField(auto_now=True,db_column='T221fechaConfiguracion')
    justificacion_del_cambio=models.CharField(max_length=255,blank=True,null=True,db_column='T221justificacionDelCambio')
    ruta_archivo_cambio=models.FileField(blank=True,null=True,db_column='T221rutaArchivoCambio')
    
    def __str__(self):
        return str(self.id_cargo_unidad_s_subserie_unidad_org_tca)    
    class Meta:
        db_table='T221Cargos_Unidad_S_Ss_UndOrg_TCA'
        verbose_name='Cargos unidad serie subserie unidad TCA'
        verbose_name_plural='Cargos unidad serie subserie unidad TCA'
        unique_together=['id_unidad_org_cargo','id_cargo_persona']

class PermisosCargoUnidadSerieSubserieUnidadTCA(models.Model):
    id_permiso_cargo_unidad_s_ss_unidad_tca = models.AutoField(primary_key=True, editable=False, db_column='T222IdPermiso_Cargo_Unidad_S_Ss_UndOrg_TCA')
    id_cargo_unidad_s_ss_unidad_tca = models.ForeignKey(Cargos_Unidad_S_Ss_UndOrg_TCA, on_delete=models.CASCADE, db_column='T222Id_Cargo_Unidad_S_Ss_UnidadOrg_TCA')
    cod_permiso = models.ForeignKey(PermisosGD, on_delete=models.CASCADE, db_column='T222_Cod_Permiso')

    def __str__(self):
        return str(self.id_permiso_cargo_unidad_s_ss_unidad_tca)
    class Meta:
        db_table='T222Permisos_Cargo_Unidad_S_Ss_UndOrg_TCA'
        verbose_name='Permiso Cargo Unidad Serie Subserie Unidad TCA'
        verbose_name_plural='Permisos Cargos Unidades Series Subseries Unidades TCA'
        unique_together = ['id_permiso_cargo_unidad_s_ss_unidad_tca', 'cod_permiso']

class HistoricoCargosUnidadSerieSubserieUnidadTCA(models.Model):
    id_historico_cargos_unidad_s_ss_unidad_tca = models.AutoField(primary_key=True, editable=False, db_column='T223IdHistorico_Cargos_Unidad_S_Ss_UndOrg_TCA')
    id_cargo_unidad_s_ss_unidad_tca = models.ForeignKey(Cargos_Unidad_S_Ss_UndOrg_TCA, on_delete=models.CASCADE, db_column='T223Id_Cargo_Unidad_S_Ss_UndOrg_TCA')
    fecha_inicio = models.DateTimeField(auto_now_add=True, db_column='T223FechaIncio')
    nombre_permisos = models.CharField(max_length=255, db_column='T223nombrePermisos')
    justificacion = models.CharField(max_length=255, blank=True, null=True, db_column='T223justificacion')
    ruta_archivo = models.FileField(blank=True, null=True, db_column='T223rutaArchivo')
    id_persona_cambia = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T223Id_PersonaCambia')

    def __str__(self):
        return str(self.id_historico_cargos_unidad_s_ss_unidad_tca)
    
    class Meta:
        db_table='T223Historico_Cargos_Unidad_S_Ss_UndOrg_TCA'
        verbose_name='Historico Cargo Unidad Serie Subserie Unidad TCA'
        verbose_name_plural='Historicos Cargos Unidades Series Subseries Unidades TCA'