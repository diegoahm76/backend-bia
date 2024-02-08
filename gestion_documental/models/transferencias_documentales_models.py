from django.db import models
from gestion_documental.choices.tipos_transferencia_choices import TIPOS_TRANSFERENCIA
from gestion_documental.models.ccd_models import SeriesDoc, SubseriesDoc

from gestion_documental.models.expedientes_models import DocumentosDeArchivoExpediente, EliminacionDocumental, ExpedientesDocumentales
from transversal.models.organigrama_models import UnidadesOrganizacionales

class TransferenciasDocumentales(models.Model):
    id_transferencia_documental = models.AutoField(primary_key=True, db_column='T302IdTransferenciaDocumental')
    id_expedienteDoc = models.ForeignKey(ExpedientesDocumentales, models.CASCADE, db_column='T302Id_ExpedienteDoc')
    id_persona_transfirio = models.ForeignKey('transversal.Personas', models.CASCADE, db_column='T302Id_PersonaTransfirio')
    cod_tipo_transferencia =  models.CharField(max_length=1,choices=TIPOS_TRANSFERENCIA, db_column='T302codTipoTransferencia')
    fecha_transferenciaExp = models.DateTimeField(db_column='T302fechaTransferenciaExp')
    id_serie_origen = models.ForeignKey(SeriesDoc, models.CASCADE, db_column='T302Id_SerieOrigen')
    id_subserie_origen = models.ForeignKey(SubseriesDoc, models.CASCADE, db_column='T302Id_SubSerieOrigen', blank=True, null=True)
    id_unidad_org_propietaria = models.ForeignKey(UnidadesOrganizacionales, models.CASCADE, db_column='T302Id_UnidadOrgPropietaria')
    
    class Meta:
        db_table = 'T302TransferenciasDocumentales'
        
class AnexosEliminacionTransferencia(models.Model):
    id_anexos_elim_trans = models.AutoField(primary_key=True, db_column='T309IdAnexos_Elimi_Trans')
    id_transferencia_documental = models.ForeignKey(TransferenciasDocumentales, null=True, blank=True, on_delete=models.SET_NULL, db_column='T309Id_TransferenciaDocumental')
    id_eliminacion_documental = models.ForeignKey(EliminacionDocumental, null=True, blank=True, on_delete=models.SET_NULL, db_column='T309Id_EliminacionDocumental')
    id_documento_archivo_exp = models.ForeignKey(DocumentosDeArchivoExpediente, on_delete=models.CASCADE, db_column='T301Id_DocDeArch_Exp')

    class Meta:
        db_table = 'T309Anexos_Elimi_Trans'
        verbose_name = 'Anexos Eliminacion Transferencia'
        verbose_name_plural = 'Anexos Eliminacion Transferencia'
        
class TransferenciaExpediente(models.Model):
    id_transferencia_exp = models.AutoField(primary_key=True, db_column='T310IdTransferenciaExp')
    id_transferencia_documental = models.ForeignKey(TransferenciasDocumentales, on_delete=models.CASCADE, db_column='T310Id_TransferenciaDocumental')
    id_expediente_documental = models.ForeignKey(ExpedientesDocumentales, on_delete=models.CASCADE, db_column='T310Id_ExpedienteDocumental')

    class Meta:
        db_table = 'T310TransferenciaExp'
        verbose_name = 'Transferencia de Expediente'
        verbose_name_plural = 'Transferencias de Expedientes'