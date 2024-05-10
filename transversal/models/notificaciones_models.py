from django.db import models

from recaudo.models import Expedientes


class MedioNotificacion(models.Model):

    id_medio_notificacion = models.SmallAutoField(primary_key=True, db_column='T030IdMedioNotificacion')
    nombre = models.CharField(unique=True, max_length=100, db_column='T030nombreMedioNotificacion')

    class Meta:
        db_table = 'T030MedioNotificacion'
        verbose_name = 'Medio de notificacion'
        verbose_name_plural = 'Medios de notificaciones'


class Notificacion(models.Model):
        
    id_notificacion = models.AutoField(primary_key=True, db_column='T031IdNotificacion')
    id_modulo_generador = models.ForeignKey('seguridad.Modulos', on_delete=models.CASCADE, db_column='T031Id_moduloGenerador')
    id_funcionario = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, related_name='persona_funcionario', db_column='T031Id_Funcionario')
    id_destinatario = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, related_name='persona_destinatario', db_column='T031Id_Destinatario')
    id_expediente = models.ForeignKey(Expedientes, on_delete=models.SET_NULL, null=True, blank=True, db_column='T031Id_Expediente')
    id_medio_notificacion = models.ForeignKey(MedioNotificacion, on_delete=models.CASCADE, db_column='T031Id_MedioNotificacion')
    doc_asociado = models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.CASCADE, db_column='T031docAsociado')
    observaciones = models.CharField(max_length=255, db_column='T031observacion')
    fecha_creacion = models.DateTimeField(auto_now=True, db_column='T031fechaCreacionRegistro')
    email = models.CharField(max_length=100, db_column='T031Email')
    email_alterno = models.CharField(max_length=100, null=True, blank=True, db_column='T031EmailAlterno')

    class Meta:
        db_table = 'T031Notificacion'
        verbose_name = 'Notificacion'
        verbose_name_plural = 'Notificaciones'
        unique_together = ['id_modulo_generador', 'id_expediente']


class DespachoNotificacion(models.Model):
            
    id_despacho_notificacion = models.AutoField(primary_key=True, db_column='T032IdDespachoNotificacion')
    id_notificacion = models.ForeignKey(Notificacion, on_delete=models.CASCADE, db_column='T032Id_Notificacion')
    id_funcionario = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, db_column='T032Id_Funcionario')
    fecha_despacho = models.DateTimeField(db_column='T032fechaDespachoNotificacion')
    empresa_entrega = models.CharField( max_length=100, db_column='T032empresaEntrega')
    funcionario_entrega = models.CharField( max_length=100, db_column='T032funcionarioEntrega')
    observaciones = models.CharField( max_length=255, blank=True, null=True, db_column='T032observacion')
    fecha_creacion = models.DateTimeField(auto_now=True, db_column='T032fechaCreacionRegistro')

    class Meta:
        db_table = 'T032DespachoNotificacion'
        verbose_name = 'Despacho de notificacion'
        verbose_name_plural = 'Despacho de notificaciones'


class RespuestaNotificacion(models.Model):

    id_respuesta_notificacion = models.AutoField(primary_key=True, db_column='T033IdRespuestaNotificacion')
    id_despacho_notificacion = models.ForeignKey(DespachoNotificacion, on_delete=models.CASCADE, db_column='T033Id_DespachoNotificacion')
    id_notificacion = models.ForeignKey(Notificacion, on_delete=models.CASCADE, db_column='T033Id_Notificacion')
    doc_asociado = models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.CASCADE, db_column='T033docAsociado')
    numero_guia = models.CharField(max_length=100, db_column='T033nroGuia')
    fecha_prestacion = models.DateTimeField(db_column='T033fechaPresentacionCorm')
    funcionario_entrega = models.CharField(max_length=100, db_column='T033funcionarioEntrega')
    observaciones = models.CharField(max_length=255, blank=True,  null=True, db_column='T033observacion')
    fecha_creacion = models.DateTimeField(auto_now=True, db_column='T033fechaCreacionRegistro')

    class Meta:
        db_table = 'T033RespuestaNotificacion'
        verbose_name = 'Respuesta de notificacion'
        verbose_name_plural = 'Respuestas de notificaciones'
        unique_together = ['id_notificacion', 'numero_guia']