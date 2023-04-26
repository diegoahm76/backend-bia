from django.db import models


class FacilidadesPago(models.Model):
    id = models.AutoField(db_column='T426id', primary_key=True)
    id_deudor_actuacion = models.IntegerField(db_column='T426id_deudor_actuacion')
    id_tipo_actuacion = models.IntegerField(db_column='T426id_tipo_actuacion')
    fecha_generacion = models.DateTimeField(db_column='T426fecha_generacion')
    observaciones = models.TextField(db_column='T426observaciones')
    periodicidad = models.IntegerField(db_column='T426periodicidad')
    cuotas = models.IntegerField(db_column='T426cuotas')
    documento_soporte = models.TextField(db_column='_T426documento_soporte')
    id_funcionario = models.IntegerField(db_column='T426id_funcionario')

    class Meta:
        db_table = 'T426facilidades_pago'
        verbose_name = 'Facilidad pago'
        verbose_name_plural = 'Facilidades pago'


class RequisitosActuacion(models.Model):
    id = models.AutoField(db_column='T428id', primary_key=True)
    descripcion = models.CharField(db_column='T428descripcion', max_length=255)
    id_tipo_actuacion = models.IntegerField(db_column='T428id_tipo_actuacion')
    tipo = models.CharField(db_column='T428tipo', max_length=255)

    class Meta:
        db_table = 'T428requisitos_actuacion'
        verbose_name = 'Requisito actuación'
        verbose_name_plural = 'Requisitos actuación'


class CumplimientoRequisitos(models.Model):
    id = models.AutoField(primary_key=True, db_column='T429id')
    id_facilidad_pago = models.IntegerField(db_column='T429id_facilidad_pago')
    id_requisito_actuacion = models.IntegerField(db_column='T429id_requisito_actuacion')
    valor = models.TextField(db_column='T429valor')

    class Meta:
        db_table = 'T429cumplimiento_requisitos'
        verbose_name = 'Cumplimiento Requisito'
        verbose_name_plural = 'Cumplimiento Requisitos'


class DetallesFacilidadPago(models.Model):
    id = models.AutoField(primary_key=True, db_column='T430id')
    id_cartera = models.IntegerField(db_column='T430id_cartera')

    class Meta:
        db_table = 'T430detalles_facilidad_pago'
        verbose_name = 'Detalle facilidad pago'
        verbose_name_plural = 'Detalles facilidad pago'


class GarantiasFacilidad(models.Model):
    id = models.AutoField(primary_key=True, db_column='T431id')
    id_bien = models.IntegerField(db_column='T431id_bien')
    id_facilidad_pago = models.IntegerField(db_column='T431id_facilidad_pago')

    class Meta:
        db_table = 'T431garantias_facilidad'
        verbose_name = 'Garantia facilidad'
        verbose_name_plural = 'Garantias facilidad'


class PlanPagos(models.Model):
    id = models.BigAutoField(db_column='T432id', primary_key=True)
    facilidad_pago = models.IntegerField(db_column='T432id_facilidad_pago')
    fecha_proyectada = models.DateTimeField(db_column='T432fecha_proyectada')
    fecha_pago = models.DateTimeField(db_column='T432fecha_pago')
    valor = models.DecimalField(db_column='T432valor', max_digits=30, decimal_places=2)
    id_tipo_pago = models.IntegerField(db_column='T432id_tipo_pago')
    verificado = models.IntegerField(db_column='T432verificado')
    soporte = models.TextField(db_column='_T432soporte')
    id_funcionario = models.IntegerField(db_column='_T4322id_funcionario')
    id_tasa_interes = models.IntegerField(db_column='T432id_tasa_interes')

    class Meta:
        db_table = 'T432plan_pagos'
        verbose_name = 'Plan pago'
        verbose_name_plural = 'Plan pagos'


class TasasInteres(models.Model):
    id = models.BigAutoField(db_column='T433id', primary_key=True)
    valor = models.DecimalField(db_column='T433valor', max_digits=30, decimal_places=2)
    vigencia_desde = models.DateTimeField(db_column='T433vigencia_desde')
    vigencia_hasta = models.DateTimeField(db_column='T433vigencia_hasta')

    class Meta:
        db_table = 'T433tasas_interes'
        verbose_name = 'Tasa interes'
        verbose_name_plural = 'Tasas interes'