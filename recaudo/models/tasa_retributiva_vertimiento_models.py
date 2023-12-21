from django.db import models

# from gestion_documental.models.expedientes_models import ArchivosDigitales

class documento_formulario_recuado(models.Model):
    id_documento = models.AutoField(primary_key=True,db_column='TXXXIdDocumentoFormularioRecaudo')
    id_persona = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE,db_column='TXXXId_Persona')	
    radicado = models.CharField(max_length=225, db_column='TXXXRadicado')
    id_archivo_sistema	= models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.CASCADE, db_column='TXXXId_ArchivoEnSistema')
    ids_destinatarios_personas = models.CharField(max_length=225, db_column='TXXXIds_Destinatarios_Personas')
    ids_destinatarios_unidades = models.CharField(max_length=225, db_column='TXXXIds_Destinatarios_Unidades')



    class Meta:
        db_table = 'TXXXDocumentoFormularioRecuado'
        verbose_name = 'Documento de Formulario de Recuado'
        verbose_name_plural = 'Documentos de Formularios de Recuado'
        #unique_together = ('codigo_exp_und_serie_subserie', 'codigo_exp_Agno', 'codigo_exp_consec_por_agno')