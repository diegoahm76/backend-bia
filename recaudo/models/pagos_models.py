from django.db import models
from recaudo.models.base_models import TipoActuacion, TiposPago
from recaudo.models.liquidaciones_models import Deudores
# from recaudo.models.cobros_models import Cartera
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


class FacilidadesPago(models.Model):
    id = models.AutoField(primary_key=True, db_column='T426IdFacilidadPago')
    id_deudor = models.ForeignKey(Deudores, on_delete=models.CASCADE, db_column='T426Id_Deudor')
    id_tipo_actuacion = models.ForeignKey(TipoActuacion, on_delete=models.CASCADE, db_column='T426Id_TipoActuacion')
    fecha_generacion = models.DateTimeField(auto_now_add=True, db_column='T426fechaGeneracion')
    observaciones = models.TextField(db_column='T426observaciones')
    periodicidad = models.IntegerField(db_column='T426periodicidad')
    cuotas = models.IntegerField(db_column='T426cuotas')
    documento_soporte = models.FileField(db_column='T426documentoSoporte')
    consignacion_soporte = models.FileField(db_column='T426consignacionSoporte')
    documento_garantia = models.FileField(db_column='T426documentoGarantia')
    documento_no_enajenacion = models.FileField(db_column='T426documentoNoEnajenacion')
    id_funcionario = models.IntegerField(db_column='T426Id_Funcionario')
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
    documento = models.FileField(db_column='T429documento')

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
    id_bien = models.ForeignKey(Bienes, on_delete=models.CASCADE, db_column='T431Id_Bien')
    id_facilidad_pago = models.ForeignKey(FacilidadesPago, on_delete=models.CASCADE, db_column='T431Id_FacilidadPago')
    id_rol = models.ForeignKey(RolesGarantias, on_delete=models.CASCADE, db_column='T431Id_RolGarantia')
    
    class Meta:
        db_table = 'T431GarantiasFacilidad'
        verbose_name = 'Garantia facilidad'
        verbose_name_plural = 'Garantias facilidad'


class PlanPagos(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='T432IdPlanPago')
    id_facilidad_pago = models.ForeignKey(FacilidadesPago, on_delete=models.CASCADE, db_column='T432Id_FacilidadPago')
    fecha_proyectada = models.DateField(db_column='T432fechaProyectada')
    fecha_pago = models.DateField(db_column='T432fechaPago')
    valor = models.DecimalField(max_digits=30, decimal_places=2, db_column='T432valor')
    id_tipo_pago = models.ForeignKey(TiposPago, on_delete=models.CASCADE, db_column='T432Id_TipoPago')
    verificado = models.IntegerField(db_column='T432verificado')
    soporte = models.TextField(db_column='T432soporte')
    id_funcionario = models.IntegerField(db_column='T432Id_Funcionario')
    id_tasa_interes = models.ForeignKey(TasasInteres, on_delete=models.CASCADE, db_column='T432Id_TasaInteres')

    class Meta:
        db_table = 'T432PlanesPago'
        verbose_name = 'Plan de pagos'
        verbose_name_plural = 'Planes de pago'


class RespuestaSolicitud(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='T435idRespuestaSolicitud')
    id_funcionario = models.IntegerField(db_column='T435Id_Funcionario')
    id_facilidades_pago = models.ForeignKey(FacilidadesPago, on_delete=models.CASCADE, db_column='T435Id_FacilidadesPago')
    estado = models.CharField(max_length=255, db_column='T435estado')
    aprobacion = models.BooleanField(db_column='T435aprobacion')
    observacion = models.CharField(max_length=255, db_column='T435observacion')
    informe_dbme = models.FileField(db_column='T435informeDbme')
    reportado_dbme = models.BooleanField(db_column='T435reportadoDbme')

    class Meta:
        db_table = 'T435RespuestasSolicitud'
        verbose_name = 'Respuesta Solicitud'
        verbose_name_plural = 'Respuestas Solicitud'