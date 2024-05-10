from django.db import models
from recaudo.models.base_models import TiposPago
from recaudo.models.facilidades_pagos_models import FacilidadesPago
#from seguridad.models import Personas


class TasasInteres(models.Model):
    id = models.AutoField(primary_key=True, db_column='T433IdTasaInteres')
    valor = models.DecimalField(max_digits=30, decimal_places=2, db_column='T433valor')
    vigencia_desde = models.DateField(db_column='T433vigenciaDesde')
    vigencia_hasta = models.DateField(db_column='T433vigenciaHasta')

    class Meta:
        db_table = 'T433TasasInteres'
        verbose_name = 'Tasa interes'
        verbose_name_plural = 'Tasas interes'


class PlanPagos(models.Model):
    id = models.AutoField(primary_key=True, db_column='T435IdPlanPago')
    id_facilidad_pago = models.ForeignKey(FacilidadesPago, on_delete=models.CASCADE, db_column='T435Id_FacilidadPago')
    id_funcionario = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, db_column='T435Id_Funcionario')
    id_tasa_interes = models.ForeignKey(TasasInteres, on_delete=models.CASCADE, db_column='T435Id_TasaInteres')
    tasa_diaria_aplicada = models.DecimalField(max_digits=30, decimal_places=2, db_column='T435tasaDiariaAplicada')
    abono_aplicado = models.DecimalField(max_digits=30, decimal_places=2, db_column='T435abonoAplicado')
    porcentaje_abono = models.DecimalField(max_digits=5, decimal_places=2, db_column='T435porcentajeAbono')
    fecha_pago_abono = models.DateField(db_column='T435fechaPagoAbono')
    nro_cuotas = models.IntegerField(db_column='T435nroCuotas')
    periodicidad = models.IntegerField(db_column='T435periodicidad')
    fecha_creacion_registro = models.DateTimeField(auto_now_add=True, db_column='T435fechaCreacionRegistro')

    class Meta:
        db_table = 'T435PlanesPago'
        verbose_name = 'Plan de pagos'
        verbose_name_plural = 'Planes de pago'


class PlanPagosCuotas(models.Model):
    id = models.AutoField(primary_key=True, db_column='T436IdPlanPagoCuota')
    id_plan_pago = models.ForeignKey(PlanPagos, on_delete=models.CASCADE, db_column='T436Id_PlanPago')
    id_tipo_pago = models.ForeignKey(TiposPago, on_delete=models.CASCADE, db_column='T436Id_TipoPago')
    nro_cuota = models.SmallIntegerField(db_column='T436nroCuota')
    valor_capital = models.DecimalField(max_digits=30, decimal_places=2, db_column='T436valorCapital')
    valor_interes = models.DecimalField(max_digits=30, decimal_places=2, db_column='T436valorInteres')
    monto_cuota = models.DecimalField(max_digits=30, decimal_places=2, db_column='T436montoCuota')
    fecha_vencimiento = models.DateField(db_column='T436fechaVencimiento')
    saldo_pendiente = models.DecimalField(max_digits=30, decimal_places=2, db_column='T436saldoPendiente')
    id_cuota_anterior = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, db_column='T436Id_CuotaAnterior')
    fecha_pago = models.DateField(blank=True, null=True, db_column='T436fechaPago')
    monto_pagado = models.DecimalField(blank=True, null=True, max_digits=30, decimal_places=2, db_column='T436montoPagado')

    class Meta:
        db_table = 'T436PlanesPagoCuotas'
        verbose_name = 'Plan de pagos cuota'
        verbose_name_plural = 'Planes de pago cuotas'


class ResolucionesPlanPago(models.Model):
    id = models.AutoField(primary_key=True, db_column='T437IdResolucionPlanPago')
    id_plan_pago = models.ForeignKey(PlanPagos, on_delete=models.CASCADE, db_column='T437Id_PlanPago')
    doc_asociado = models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.CASCADE, db_column='T437docAsociado')
    observacion = models.CharField(max_length=255, db_column='T437observacion')
    fecha_creacion_registro = models.DateTimeField(auto_now_add=True, db_column='T437fechaCreacionRegistro')

    class Meta:
        db_table = 'T437ResolucionesPlanPago'
        verbose_name = 'Resolucion Plan de Pago'
        verbose_name_plural = 'Resoluciones Plan de Pagos'


class FacPagoLiquidacion(models.Model):
    id = models.AutoField(primary_key=True, db_column='T438IdFacPagoLiquidacion')
    id_plan_pago = models.ForeignKey(PlanPagos, on_delete=models.CASCADE, db_column='T438Id_PlanPago')
    item_consecutivo = models.SmallIntegerField(db_column='T438consecutivoItem')
    id_obligacion = models.IntegerField(db_column='T438Id_Obligacion')
    resolucion = models.CharField(max_length=100, db_column='T438resolucion')
    valor_capital = models.DecimalField(max_digits=30, decimal_places=2, db_column='T438valorCapital')
    fecha_mora = models.DateField(db_column='T438fechaConsMora')
    dias_mora = models.SmallIntegerField(db_column='T438diasMora')
    valor_intereses = models.DecimalField(max_digits=30, decimal_places=2, db_column='T438valorIntereses')
    monto_total = models.DecimalField(max_digits=30, decimal_places=2, db_column='T438montoTotal')
    valor_abonado = models.DecimalField(max_digits=30, decimal_places=2, db_column='T438valorAbonado')
    porcentaje_abono = models.DecimalField(max_digits=5, decimal_places=2, db_column='T438porcentajeAbono')
    valor_abono_capital = models.DecimalField(max_digits=30, decimal_places=2, db_column='T438valorAbonoCapital')
    valor_abono_interes = models.DecimalField(max_digits=30, decimal_places=2, db_column='T438valorAbonoIntereses')
    saldo_capital = models.DecimalField(max_digits=30, decimal_places=2, db_column='T438saldoCapital')
    fecha_creacion_registro = models.DateTimeField(auto_now_add=True, db_column='T438fechaCreacionRegistro')

    class Meta:
        db_table = 'T438FacPagoLiquidacion'
        verbose_name = 'Fac Pago liquidacion'
        verbose_name_plural = 'Fac Pagos liquidacion'


class FacPagoProyeccion(models.Model):
    id = models.AutoField(primary_key=True, db_column='T439IdFacPagoProyeccion')
    id_plan_pago = models.ForeignKey(PlanPagos, on_delete=models.CASCADE, db_column='T439Id_PlanPago')
    item_consecutivo = models.SmallIntegerField(db_column='T439consecutivoItem')
    id_obligacion = models.IntegerField(db_column='T439Id_Obligacion')
    resolucion = models.CharField(max_length=100, db_column='T439resolucion')
    valor_capital = models.DecimalField(max_digits=30, decimal_places=2, db_column='T439valorCapital')
    fecha_mora = models.DateField(db_column='T439fechaConsMora')
    dias_mora = models.SmallIntegerField(db_column='T439diasMora')
    valor_intereses = models.DecimalField(max_digits=30, decimal_places=2, db_column='T439valorInteresesMoratorio')
    monto_total = models.DecimalField(max_digits=30, decimal_places=2, db_column='T439montoTotal')
    fecha_creacion_registro = models.DateTimeField(auto_now_add=True, db_column='T439fechaCreacionRegistro')

    class Meta:
        db_table = 'T439FacPagoProyeccion'
        verbose_name = 'Fac Pago Proyeccion'
        verbose_name_plural = 'Fac Pagos Proyeccion'
