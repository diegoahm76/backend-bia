from django.db import models
from recaudo.models.base_models import TipoActuacion, TiposPago
from recaudo.models.liquidaciones_models import Deudores
# from recaudo.models.cobros_models import Cartera
from recaudo.models.procesos_models import Bienes
from recaudo.models.garantias_models import RolesGarantias


class TasasInteres(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='T433id')
    valor = models.DecimalField(max_digits=30, decimal_places=2, db_column='T433valor')
    vigencia_desde = models.DateField(db_column='T433vigencia_desde')
    vigencia_hasta = models.DateField(db_column='T433vigencia_hasta')

    class Meta:
        db_table = 'T433tasas_interes'
        verbose_name = 'Tasa interes'
        verbose_name_plural = 'Tasas interes'


class FacilidadesPago(models.Model):
    id = models.AutoField(primary_key=True, db_column='T426id')
    id_deudor_actuacion = models.ForeignKey(Deudores, on_delete=models.CASCADE, db_column='T426id_deudor_actuacion')
    id_tipo_actuacion = models.ForeignKey(TipoActuacion, on_delete=models.CASCADE, db_column='T426id_tipo_actuacion')
    fecha_generacion = models.DateTimeField(auto_now_add=True, db_column='T426fecha_generacion')
    observaciones = models.TextField(db_column='T426observaciones')
    periodicidad = models.IntegerField(db_column='T426periodicidad')
    cuotas = models.IntegerField(db_column='T426cuotas')
    id_tasas_interes = models.ForeignKey(TasasInteres, on_delete=models.CASCADE, db_column='T426id_tasa_interes')
    documento_soporte = models.FileField(db_column='T426documento_soporte')
    consignacion_soporte = models.FileField(db_column='T426consignacion_soporte')
    documento_garantia = models.FileField(db_column='T426documento_garantia')
    documento_no_enajenacion = models.FileField(db_column='T426documento_no_enajenacion')
    id_funcionario = models.IntegerField(db_column='T426id_funcionario')
    notificaciones = models.BooleanField(db_column='T426id_notificaciones')

    class Meta:
        db_table = 'T426facilidades_pago'
        verbose_name = 'Facilidad pago'
        verbose_name_plural = 'Facilidades pago'


class RequisitosActuacion(models.Model):
    id = models.AutoField(primary_key=True, db_column='T428id')
    descripcion = models.CharField(max_length=255, db_column='T428descripcion')
    id_tipo_actuacion = models.ForeignKey(TipoActuacion, on_delete=models.CASCADE, db_column='T428id_tipo_actuacion')
    tipo = models.CharField(max_length=255, db_column='T428tipo')

    class Meta:
        db_table = 'T428requisitos_actuacion'
        verbose_name = 'Requisito actuación'
        verbose_name_plural = 'Requisitos actuación'


class CumplimientoRequisitos(models.Model):
    id = models.AutoField(primary_key=True, db_column='T429id')
    id_facilidad_pago = models.ForeignKey(FacilidadesPago, on_delete=models.CASCADE, db_column='T429id_facilidad_pago')
    id_requisito_actuacion = models.ForeignKey(RequisitosActuacion, on_delete=models.CASCADE, db_column='T429id_requisito_actuacion')
    documento = models.FileField(db_column='T429documento')

    class Meta:
        db_table = 'T429cumplimiento_requisitos'
        verbose_name = 'Cumplimiento Requisito'
        verbose_name_plural = 'Cumplimiento Requisitos'


class DetallesFacilidadPago(models.Model):
    id = models.AutoField(primary_key=True, db_column='T430id')
    id_cartera = models.ForeignKey('recaudo.Cartera', on_delete=models.CASCADE, db_column='T430id_cartera')
    id_facilidad_pago = models.ForeignKey(FacilidadesPago, on_delete=models.CASCADE, db_column='T430id_facilidad_pago')

    class Meta:
        db_table = 'T430detalles_facilidad_pago'
        verbose_name = 'Detalle facilidad pago'
        verbose_name_plural = 'Detalles facilidad pago'


class GarantiasFacilidad(models.Model):
    id = models.AutoField(primary_key=True, db_column='T431id')
    id_bien = models.ForeignKey(Bienes, on_delete=models.CASCADE, db_column='T431id_bien')
    id_facilidad_pago = models.ForeignKey(FacilidadesPago, on_delete=models.CASCADE, db_column='T431id_facilidad_pago')
    id_rol = models.ForeignKey(RolesGarantias, on_delete=models.CASCADE, db_column='T431id_rol')
    
    class Meta:
        db_table = 'T431garantias_facilidad'
        verbose_name = 'Garantia facilidad'
        verbose_name_plural = 'Garantias facilidad'


class PlanPagos(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='T432id')
    id_facilidad_pago = models.ForeignKey(FacilidadesPago, on_delete=models.CASCADE, db_column='T432id_facilidad_pago')
    fecha_proyectada = models.DateField(db_column='T432fecha_proyectada')
    fecha_pago = models.DateField(db_column='T432fecha_pago')
    valor = models.DecimalField(max_digits=30, decimal_places=2, db_column='T432valor')
    id_tipo_pago = models.ForeignKey(TiposPago, on_delete=models.CASCADE, db_column='T432id_tipo_pago')
    verificado = models.IntegerField(db_column='T432verificado')
    soporte = models.TextField(db_column='T432soporte')
    id_funcionario = models.IntegerField(db_column='T432id_funcionario')
    id_tasa_interes = models.ForeignKey(TasasInteres, on_delete=models.CASCADE, db_column='T432id_tasa_interes')

    class Meta:
        db_table = 'T432plan_pagos'
        verbose_name = 'Plan pago'
        verbose_name_plural = 'Plan pagos'


class RespuestaSolicitud(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='T435id')
    id_funcionario = models.IntegerField(db_column='T435id_funcionario')
    id_facilidades_pago = models.ForeignKey(FacilidadesPago, on_delete=models.CASCADE, db_column='T435id_facilidades_pago')
    estado = models.CharField(max_length=255, db_column='T435estado')
    aprobacion = models.BooleanField(db_column='T435aprobacion')
    observacion = models.CharField(max_length=255, db_column='T435observacion')
    informe_dbme = models.FileField(db_column='T435informe_dbme')
    reportado_dbme = models.BooleanField(db_column='T435reportado_dbme')

    class Meta:
        db_table = 'T435respuesta_solicitud'
        verbose_name = 'Respuesta Solicitud'
        verbose_name_plural = 'Respuestas Solicitud'