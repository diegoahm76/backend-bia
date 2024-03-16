from django.db import models

from gestion_documental.choices.cod_tipo_proceso_conseg_choices import PROCESO_CHOICES
from gestion_documental.models.expedientes_models import ArchivosDigitales


class ConfigTipoConsecAgno(models.Model):

    id_config_tipo_consec_agno = models.SmallAutoField(primary_key=True, db_column='T306IdConfigTipoConsecAgno')
    agno_consecutivo = models.SmallIntegerField(db_column='T306agnoConsecutivo')
    #cod_tipo_consec = models.CharField(max_length=3, choices=PROCESO_CHOICES, db_column='T306codTipoConsecutivo')
    #prefijo_consecutivo = models.CharField(null=True,max_length=10, db_column='T306prefijoConsecutivo')
    consecutivo_inicial = models.IntegerField(null=True,db_column='T306consecutivoInicial')
    cantidad_digitos = models.SmallIntegerField(null=True,db_column='T306cantidadDigitos')
    implementar = models.BooleanField(db_column='T306implementar')
    id_persona_config_implementacion = models.ForeignKey('transversal.Personas',null=True, on_delete=models.SET_NULL, db_column='T306Id_PersonaConfigImplementacion',related_name='T306Id_PersonaConfigImplementacion')
    fecha_inicial_config_implementacion = models.DateTimeField(null=True,db_column='T306fechaInicialConfigImplementacion')
    consecutivo_actual = models.IntegerField(null=True,db_column='T306consecutivoActual')
    fecha_consecutivo_actual = models.DateTimeField(null=True,db_column='T306fechaConsecutivoActual')
    id_persona_consecutivo_actual = models.ForeignKey('transversal.Personas',null=True, on_delete=models.SET_NULL, db_column='T306Id_PersonaConsecutivoActual',related_name='FK2_T306ConfigTiposRadicadoAgno')
    id_catalogo_serie_unidad = models.ForeignKey('gestion_documental.CatalogosSeriesUnidad', null=True, on_delete=models.CASCADE, db_column='T306Id_CatalogoSerieUnidad',related_name='T306IdCatalogoSerieUnidad')
    id_unidad = models.ForeignKey('transversal.UnidadesOrganizacionales', null=True, on_delete=models.CASCADE, db_column='T306Id_Unidad',related_name='T306IdUnidad')
    class Meta:
        db_table = 'T306ConfigTiposConsecAgno'
        unique_together = [('agno_consecutivo','id_unidad', 'id_catalogo_serie_unidad'),]



class Consecutivo(models.Model):
    id_consecutivo = models.AutoField(primary_key=True, db_column='T308IdConsecutivo')
    #cod_tipo_proceso = models.CharField(max_length=3, choices=PROCESO_CHOICES, db_column='T308codTipoProceso')
    id_unidad = models.ForeignKey('transversal.UnidadesOrganizacionales', on_delete=models.CASCADE, db_column='T308Id_Unidad',related_name='T308Id_Unidad')
    id_catalogo = models.ForeignKey('gestion_documental.CatalogosSeriesUnidad',blank=True,null=True ,on_delete=models.SET_NULL, db_column='T308Id_Catalogo',related_name='T308Id_Catalogo')
    agno_consecutivo = models.SmallIntegerField(db_column='T308agnoConsecutivo')
    nro_consecutivo = models.CharField(max_length=20, db_column='T308nroConsecutivo')
    fecha_consecutivo = models.DateTimeField(db_column='T308fechaConsecutivo')
    id_persona_solicita = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,db_column='T308Id_PersonaRadica')
    id_archivo = models.ForeignKey(ArchivosDigitales,on_delete=models.SET_NULL,db_column='T308Id_ArchivoDigital',blank=True,null=True)
    class Meta:
        db_table = 'T308Consecutivo'
        #unique_together = [('agno_consecutivo','nro_consecutivo'),]