from django.db import models
from recaudo.models.base_models import TiposPago
from recaudo.models.facilidades_pagos_models import FacilidadesPago
from recaudo.models.liquidaciones_models import Deudores
from recaudo.models.procesos_models import Bienes
from recaudo.models.garantias_models import RolesGarantias


class TasasInteres(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='T433IdTasaInteres')
    valor = models.DecimalField(max_digits=30, decimal_places=2, db_column='T433valor')
    vigencia_desde = models.DateField(db_column='T433vigenciaDesde')
    vigencia_hasta = models.DateField(db_column='T433vigenciaHasta')

    class Meta:
        db_table = 'T433TasasInteres'
        verbose_name = 'Tasa interes'
        verbose_name_plural = 'Tasas interes'


class PlanPagos(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='T435IdPlanPago')
    id_facilidad_pago = models.ForeignKey(FacilidadesPago, on_delete=models.CASCADE, db_column='T435Id_FacilidadPago')
    id_funcionario = models.IntegerField(db_column='T435Id_Funcionario')
    agno_tasa = models.SmallIntegerField(db_column='T435agnoTasa')
    mes_tasa = models.SmallIntegerField(db_column='T435mesTasa')
    tasa_usura = models.DecimalField(max_digits=10, decimal_places=2, db_column='T435tasaUsura')
    tasa_diaria_aplicada = models.DecimalField(max_digits=10, decimal_places=2, db_column='T435tasaDiariaAplicada')
    abono_aplicado = models.DecimalField(max_digits=30, decimal_places=2, db_column='T435abonoAplicado')
    porcentaje_abono = models.DecimalField(max_digits=5, decimal_places=2, db_column='T435porcentajeAbono')
    fecha_pago_abono = models.DateField(db_column='T435fechaPagoAbono')
    nro_cuotas = models.IntegerField(db_column='T435nroCuotas')
    periodicidad = models.IntegerField(db_column='T435periodicidad')
    fecha_creacion_registro = models.DateTimeField(db_column='T435fechaCreacionRegistro')
    # fecha_proyectada = models.DateField(db_column='T435fechaProyectada')
    # fecha_pago = models.DateField(db_column='T435fechaPago')
    # valor = models.DecimalField(max_digits=30, decimal_places=2, db_column='T435valor')
    # id_tipo_pago = models.ForeignKey(TiposPago, on_delete=models.CASCADE, db_column='T435Id_TipoPago')
    # verificado = models.IntegerField(db_column='T435verificado')
    # soporte = models.TextField(db_column='T435soporte')
    # id_tasa_interes = models.ForeignKey(TasasInteres, on_delete=models.CASCADE, db_column='T435Id_TasaInteres')

    class Meta:
        db_table = 'T435PlanesPago'
        verbose_name = 'Plan de pagos'
        verbose_name_plural = 'Planes de pago'


# class PlanPagosCuotas(models.Model):
#     id = models.BigAutoField(primary_key=True, db_column='T435IdPlanPagoCuota')
#     id_plan_pago = models.ForeignKey(PlanPagos, on_delete=models.CASCADE, db_column='T435Id_PlanPago')
#     nro_cuota = models.IntegerField(db_column='T435nroCuota')


#     id_funcionario = models.IntegerField(db_column='T435Id_Funcionario')
#     anio_tasa = models.SmallIntegerField(db_column='T435anioTasa')
#     mes_tasa = models.SmallIntegerField(db_column='T435mesTasa')
#     tasa_usura = models.DecimalField(max_digits=10, decimal_places=2, db_column='T435tasaUsura')
#     tasa_diaria_aplicada = models.DecimalField(max_digits=10, decimal_places=2, db_column='T435tasaDiariaAplicada')
#     abono_aplicado = models.DecimalField(max_digits=30, decimal_places=2, db_column='T435abonoAplicado')
#     porcentaje_abono = models.DecimalField(max_digits=5, decimal_places=2, db_column='T435porcentajeAbono')
#     fecha_pago_abono = models.DateField(db_column='T435fechaPagoAbono')
#     nro_cuotas = models.IntegerField(db_column='T435nroCuotas')
#     periodicidad = models.IntegerField(db_column='T435periodicidad')
#     fecha_creacion_registro = models.DateTimeField(db_column='T435fechaCreacionRegistro')
#     # fecha_proyectada = models.DateField(db_column='T435fechaProyectada')
#     # fecha_pago = models.DateField(db_column='T435fechaPago')
#     # valor = models.DecimalField(max_digits=30, decimal_places=2, db_column='T435valor')
#     # id_tipo_pago = models.ForeignKey(TiposPago, on_delete=models.CASCADE, db_column='T435Id_TipoPago')
#     # verificado = models.IntegerField(db_column='T435verificado')
#     # soporte = models.TextField(db_column='T435soporte')
#     # id_tasa_interes = models.ForeignKey(TasasInteres, on_delete=models.CASCADE, db_column='T435Id_TasaInteres')

#     class Meta:
#         db_table = 'T435PlanesPagoCuotas'
#         verbose_name = 'Plan de pagos'
#         verbose_name_plural = 'Planes de pago'
