from django.db import models
from recaudo.models.base_models import TipoActuacion
from recaudo.models.liquidaciones_models import Deudores
from recaudo.models.procesos_models import Bienes
from recaudo.models.garantias_models import RolesGarantias


class FacilidadesPago(models.Model):
    id = models.AutoField(primary_key=True, db_column='T426IdFacilidadPago')
    id_deudor = models.ForeignKey(Deudores, on_delete=models.CASCADE, db_column='T426Id_Deudor')
    id_tipo_actuacion = models.ForeignKey(TipoActuacion, on_delete=models.CASCADE, db_column='T426Id_TipoActuacion')
    fecha_generacion = models.DateTimeField(auto_now_add=True, db_column='T426fechaGeneracion')
    periodicidad = models.IntegerField(db_column='T426periodicidad')
    cuotas = models.IntegerField(db_column='T426cuotas')
    documento_soporte = models.ForeignKey('gestion_documental.ArchivosDigitales', related_name='facilidad_documento_soporte', on_delete=models.CASCADE, db_column='T426documentoSoporte')
    consignacion_soporte = models.ForeignKey('gestion_documental.ArchivosDigitales', related_name='facilidad_consignacion_soporte', on_delete=models.CASCADE, db_column='T426consignacionSoporte')
    valor_abonado = models.DecimalField(max_digits=30, decimal_places=2, db_column='T426valorAbonado')
    fecha_abono = models.DateField(db_column='T426fechaAbono')
    documento_no_enajenacion = models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.CASCADE, db_column='T426documentoNoEnajenacion')
    observaciones = models.TextField(db_column='T426observaciones')
    id_funcionario = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, db_column='T426Id_Funcionario')
    notificaciones = models.BooleanField(db_column='T426notificaciones')
    numero_radicacion = models.CharField(max_length=255, db_column='T426numeroRadicacion')

    class Meta:
        db_table = 'T426FacilidadesPago'
        verbose_name = 'Facilidad pago'
        verbose_name_plural = 'Facilidades pago'


class RequisitosActuacion(models.Model):
    id = models.AutoField(primary_key=True, db_column='T428IdRequisitoActuacion')
    descripcion = models.CharField(max_length=255, db_column='T428descripcion')
    id_tipo_actuacion = models.ForeignKey(TipoActuacion, on_delete=models.CASCADE, db_column='T428Id_TipoActuacion')
    tipo = models.CharField(max_length=255, db_column='T428tipo')

    class Meta:
        db_table = 'T428RequisitosActuacion'
        verbose_name = 'Requisito actuación'
        verbose_name_plural = 'Requisitos actuación'


class CumplimientoRequisitos(models.Model):
    id = models.AutoField(primary_key=True, db_column='T429IdCumplimientoRequisito')
    id_facilidad_pago = models.ForeignKey(FacilidadesPago, on_delete=models.CASCADE, db_column='T429Id_FacilidadPago')
    id_requisito_actuacion = models.ForeignKey(RequisitosActuacion, on_delete=models.CASCADE, db_column='T429Id_RequisitoActuacion')
    documento = models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.CASCADE, db_column='T429documento')

    class Meta:
        db_table = 'T429CumplimientoRequisitos'
        verbose_name = 'Cumplimiento Requisito'
        verbose_name_plural = 'Cumplimiento Requisitos'


class DetallesFacilidadPago(models.Model):
    id = models.AutoField(primary_key=True, db_column='T430IdDetalle_FacilidadPago')
    id_cartera = models.ForeignKey('recaudo.Cartera', on_delete=models.CASCADE, db_column='T430Id_Cartera')
    id_facilidad_pago = models.ForeignKey(FacilidadesPago, on_delete=models.CASCADE, db_column='T430Id_FacilidadPago')

    class Meta:
        db_table = 'T430Detalles_FacilidadesPago'
        verbose_name = 'Detalle facilidad pago'
        verbose_name_plural = 'Detalles facilidad pago'


class GarantiasFacilidad(models.Model):
    id = models.AutoField(primary_key=True, db_column='T431IdGarantiaFacilidad')
    id_facilidad_pago = models.ForeignKey(FacilidadesPago, on_delete=models.CASCADE, db_column='T431Id_FacilidadPago')
    id_rol = models.ForeignKey(RolesGarantias, on_delete=models.CASCADE, db_column='T431Id_RolGarantia')
    documento_garantia = models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.CASCADE, db_column='T431documentoGarantia')
    
    class Meta:
        db_table = 'T431GarantiasFacilidad'
        verbose_name = 'Garantia facilidad'
        verbose_name_plural = 'Garantias facilidad'


class RespuestaSolicitud(models.Model):
    id = models.AutoField(primary_key=True, db_column='T432idRespuestaSolicitud')
    id_funcionario = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, db_column='T432Id_Funcionario')
    id_facilidad_pago = models.ForeignKey(FacilidadesPago, on_delete=models.CASCADE, db_column='T432Id_FacilidadPago')
    estado = models.CharField(max_length=255, db_column='T432estado')
    aprobacion = models.BooleanField(db_column='T432aprobacion')
    observacion = models.CharField(max_length=255, db_column='T432observacion')
    informe_dbme = models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.CASCADE, db_column='T432informeDbme')
    reportado_dbme = models.BooleanField(db_column='T432reportadoDbme')

    class Meta:
        db_table = 'T432RespuestasSolicitud'
        verbose_name = 'Respuesta Solicitud'
        verbose_name_plural = 'Respuestas Solicitud'


class DetallesBienFacilidadPago(models.Model):
    id = models.AutoField(primary_key=True, db_column='T425IdDetalle_BienFacilidadPago')
    id_bien = models.ForeignKey(Bienes, on_delete=models.CASCADE, db_column='T425Id_Bien')
    id_facilidad_pago = models.ForeignKey(FacilidadesPago, on_delete=models.CASCADE, db_column='T425Id_FacilidadPago')

    class Meta:
        db_table = 'T425Detalles_BienesFacilidadesPago'
        verbose_name = 'Detalle bien facilidad pago'
        verbose_name_plural = 'Detalles bienes facilidades pago'