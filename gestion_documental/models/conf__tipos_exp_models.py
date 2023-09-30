from django.db import models

from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD

class ConfiguracionTipoExpedienteAgno(models.Model):
    id_config_tipo_expediente_agno = models.AutoField(primary_key=True, db_column='T245IdConfigTipoExpedienteAgno')
    id_cat_serie_undorg_ccd = models.ForeignKey(CatSeriesUnidadOrgCCDTRD,on_delete=models.CASCADE,db_column='T245Id_CatSerie_UndOrg_CCD')
    agno_expediente = models.SmallIntegerField(db_column='T245agnoExpediente')
    cod_tipo_expediente = models.CharField(max_length=1, choices=[('C', 'Complejo'), ('S', 'Simple')], db_column='T245codTipoExpediente')
    consecutivo_inicial = models.IntegerField(null=True, blank=True, db_column='T245consecutivoInicial')
    cantidad_digitos = models.SmallIntegerField(null=True, blank=True, db_column='T245cantidadDigitos')
    item_ya_usado = models.BooleanField(db_column='T245itemYaUsado')
    id_persona_ult_config_implement = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,null=True, blank=True, db_column='T245Id_PersonaUltConfigImplemen',related_name='config_tipo_expediente_ult_config')
    fecha_ult_config_implement = models.DateTimeField(null=True, blank=True, db_column='T245fechaUltConfigImplemen')
    consecutivo_actual = models.IntegerField(null=True, blank=True, db_column='T245consecutivoActual')
    fecha_consecutivo_actual = models.DateTimeField(null=True, blank=True, db_column='T245fechaConsecutivoActual')
    id_persona_consecutivo_actual = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,null=True, blank=True, db_column='T245Id_PersonaConsecutivoActual', related_name='config_tipo_expediente_consecutivo_actual')
#id_persona_config_implementacion = models.ForeignKey('transversal.Personas',null=True, on_delete=models.CASCADE, db_column='T235Id_PersonaConfigImplementacion',related_name='T235Id_PersonaConfigImplementacion')
    class Meta:
        unique_together = (('id_cat_serie_undorg_ccd', 'agno_expediente'),)
        db_table = 'T245ConfigTiposExpedienteAgno'  # Cambia 'NombreTabla' al nombre real de tu tabla en la base de datos

    def __str__(self):
        return f'Tipo de Expediente {self.id_config_tipo_expediente_agno} - Agno {self.agno_expediente}'