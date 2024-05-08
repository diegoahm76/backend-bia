from django.db import models
from gestion_documental.models.expedientes_models import ArchivosDigitales


class ConfigReferenciaPagoAgno(models.Model):

    id_config_ref_agno = models.SmallAutoField(primary_key=True, db_column='T469IdConfRefPagocAgno')
    agno_ref = models.SmallIntegerField(db_column='T469agnoReferencia')
    #cod_tipo_consec = models.CharField(max_length=3, choices=PROCESO_CHOICES, db_column='T469codTipoConsecutivo')
    #prefijo_consecutivo = models.CharField(null=True,max_length=10, db_column='T469prefijoConsecutivo')
    consecutivo_inicial = models.IntegerField(null=True,db_column='T469consecutivoInicial')
    cantidad_digitos = models.SmallIntegerField(null=True,db_column='T469cantidadDigitos')
    implementar = models.BooleanField(db_column='T469implementar')
    id_persona_config_implementacion = models.ForeignKey('transversal.Personas',null=True, on_delete=models.SET_NULL, db_column='T469Id_PersonaConfigImplementacion',related_name='T469Id_PersonaConfigImplementacion')
    fecha_inicial_config_implementacion = models.DateTimeField(null=True,db_column='T469fechaInicialConfigImplementacion')
    referencia_actual = models.IntegerField(null=True,db_column='T469consecutivoActual')
    fecha_consecutivo_actual = models.DateTimeField(null=True,db_column='T469fechaConsecutivoActual')
    id_persona_referencia_actual = models.ForeignKey('transversal.Personas',null=True, on_delete=models.SET_NULL, db_column='T469Id_PersonaConsecutivoActual',related_name='FK2_T469ConfigTiposRadicadoAgno')
    id_catalogo_serie_unidad = models.ForeignKey('gestion_documental.CatalogosSeriesUnidad', null=True, on_delete=models.SET_NULL, blank = True, db_column='T469Id_CatalogoSerieUnidad',related_name='T469IdCatalogoSerieUnidad')
    id_unidad = models.ForeignKey('transversal.UnidadesOrganizacionales', on_delete=models.CASCADE, db_column='T469Id_Unidad',related_name='T469IdUnidad')
    class Meta:
        db_table = 'T469ConfigReferenciaPagoAgno'
        unique_together = [('agno_ref','id_unidad', 'id_catalogo_serie_unidad'),]



class Referencia(models.Model):
    id_referencia = models.AutoField(primary_key=True, db_column='T470IdReferencia.')
    #cod_tipo_proceso = models.CharField(max_length=3, choices=PROCESO_CHOICES, db_column='T470codTipoProceso')
    id_unidad = models.ForeignKey('transversal.UnidadesOrganizacionales', on_delete=models.CASCADE, db_column='T470Id_Unidad',related_name='T470Id_Unidad')
    id_catalogo = models.ForeignKey('gestion_documental.CatalogosSeriesUnidad',blank=True,null=True ,on_delete=models.SET_NULL, db_column='T470Id_Catalogo',related_name='T470Id_Catalogo')
    agno_referencia = models.SmallIntegerField(db_column='T470agnoConsecutivo')
    nro_consecutivo = models.CharField(max_length=20, db_column='T470nroConsecutivo')
    fecha_consecutivo = models.DateTimeField(db_column='T470fechaReferencia')
    id_persona_solicita = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,db_column='T470Id_Persona')
    id_archivo = models.ForeignKey(ArchivosDigitales,on_delete=models.SET_NULL,db_column='T470Id_ArchivoDigital',blank=True,null=True)
    id_solicitud_tramite = models.ForeignKey('tramites.SolicitudesTramites',on_delete=models.CASCADE,db_column='T470Id_SolicitudTramite')
    class Meta:
        db_table = 'T470ReferenciasPago'
        #unique_together = [('agno_consecutivo','nro_consecutivo'),]