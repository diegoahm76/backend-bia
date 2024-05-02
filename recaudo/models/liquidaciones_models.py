from django.db import models
from recaudo.models.base_models import NaturalezaJuridica, TipoRenta, Ubicaciones
from recaudo.choices.estados_liquidacion_choices import estados_liquidacion_CHOICES


class Deudores(models.Model):
    id = models.AutoField(primary_key=True, db_column='T410IdDeudor')
    identificacion = models.CharField(max_length=255, db_column='T410identificacion')
    nombres = models.CharField(max_length=255, db_column='T410nombres')
    apellidos = models.CharField(null=True, blank=True, max_length=255, db_column='T410apellidos')
    telefono = models.CharField(max_length=255, db_column='T410telefono')
    email = models.CharField(max_length=255, db_column='T410email')
    ubicacion_id = models.ForeignKey(Ubicaciones, on_delete=models.CASCADE, db_column='T410Id_Ubicacion')
    naturaleza_juridica_id = models.ForeignKey(NaturalezaJuridica, on_delete=models.CASCADE, db_column='T410Id_NaturalezaJuridica')

    class Meta:
        db_table = 'T410Deudores'
        verbose_name = 'Deudor'
        verbose_name_plural = 'Deudores'


class Expedientes(models.Model):
    id = models.AutoField(primary_key=True, db_column='T407IdExpediente')
    cod_expediente = models.CharField(max_length=255, db_column='T407codigoExpediente')
    id_deudor = models.ForeignKey(Deudores, on_delete=models.CASCADE, db_column='T407Id_Deudor')
    numero_resolucion = models.CharField(max_length=255, db_column='T407codigoResolucion')
    cod_auto = models.CharField(max_length=255, db_column='T407codigoAuto')
    cod_recurso = models.CharField(max_length=255, db_column='T407codigoRecurso')
    liquidado = models.BooleanField(default=False, db_column='T407liquidado')
    id_expediente_doc = models.ForeignKey('gestion_documental.ExpedientesDocumentales', on_delete=models.SET_NULL, blank=True, null=True, db_column='T407Id_ExpedienteDoc') # Definir. Según modelado debe ser obligatorio

    class Meta:
        db_table = 'T407Expedientes'
        verbose_name = 'Expediente'
        verbose_name_plural = 'Expedientes'


class OpcionesLiquidacionBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='T402IdOpcionLiquidacionBase')
    nombre = models.CharField(max_length=255, unique=True, db_column='T402nombre')
    estado = models.IntegerField(default=1, db_column='T402estado')
    version = models.IntegerField(default=1, db_column='T402version')
    funcion = models.TextField(db_column='T402funcion')
    variables = models.JSONField(db_column='T402variables')
    bloques = models.TextField(db_column='T402bloques')
    tipo_renta=models.CharField(max_length=255, db_column='T402tipoRenta',null=True,default=True)
    tipo_cobro=models.CharField(max_length=255, db_column='T402tipoCobro', null=True, default=True)

    class Meta:
        db_table = "T402OpcionesLiquidacionBase"
        verbose_name = 'Opcion liquidación base'
        verbose_name_plural = 'Opciones liquidación base'


class LiquidacionesBase(models.Model):
    id = models.AutoField(primary_key=True, db_column="T403IdLiquidacionBase")
    fecha_liquidacion = models.DateTimeField(db_column="T403fechaLiquidacion")
    vencimiento = models.DateTimeField(db_column="T403vencimiento")
    periodo_liquidacion = models.CharField(max_length=255, db_column="T403periodoLiquidacion")
    valor = models.DecimalField(max_digits=20, decimal_places=4, default=0, db_column="T403Valor")
    estado = models.CharField(choices=estados_liquidacion_CHOICES, max_length=10, db_column="T403estado")
    id_deudor = models.ForeignKey(Deudores, blank=True, null=True, on_delete=models.SET_NULL, db_column="T403Id_Deudor")
    id_expediente = models.ForeignKey(Expedientes, blank=True, null=True, on_delete=models.SET_NULL, db_column="T403Id_Expediente")
    ciclo_liquidacion = models.CharField(max_length=255, blank=True, null=True, db_column="T403cicloliquidacion")
    id_solicitud_tramite = models.ForeignKey('tramites.SolicitudesTramites', blank=True, null=True, on_delete=models.SET_NULL, db_column="T403Id_SolicitudTramite")
    id_archivo = models.ForeignKey('gestion_documental.ArchivosDigitales', blank=True, null=True, on_delete=models.SET_NULL, db_column="T403Id_Archivo")
    id_tipo_renta=models.ForeignKey(TipoRenta, on_delete=models.SET_NULL, db_column='T403Id_TipoRenta',null=True, default=True)
    num_liquidacion = models.IntegerField(null=True, default=True, db_column='T403numLiquidacion')
    agno = models.SmallIntegerField(null=True, default=True, db_column='T403Agno')
    periodo = models.SmallIntegerField(null=True, default=True, db_column='T403Periodo')
    nit = models.CharField(max_length=15, blank=True, null=True, db_column="T403Nit")
    fecha = models.DateTimeField(null=True, default=True, db_column="t403Fecha")
    valor_liq = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=True, db_column='T403ValorLiq')
    valor_pagado = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=True, db_column='T403ValorPagado')
    valor_prescripcion = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=True, db_column='T403valorPrescripcion')
    anulado = models.CharField(max_length=1, blank=True, null=True, db_column="T403Anulado")
    num_resolucion = models.IntegerField(blank=True, null=True, db_column="T403numResolucion")
    agno_resolucion = models.SmallIntegerField(null=True, default=True, db_column='T403AgnoResolucion')
    cod_origen_liq = models.CharField(max_length=1, blank=True, null=True, db_column="T403codOrigenLiq")
    observacion = models.CharField(max_length=255, blank=True, null=True, db_column="T403Observacion")
    cod_tipo_beneficio = models.CharField(max_length=5, blank=True, null=True, db_column="T403codTipoBeneficio")
    fecha_contab = models.DateTimeField(null=True, default=True, db_column="T403fechaContab")
    se_cobra = models.CharField(max_length=1, blank=True, null=True, db_column="T403seCobra")
    fecha_en_firme = models.DateTimeField(null=True, default=True, db_column="T403fechaEnFirme")
    nnum_origen_liq = models.IntegerField(blank=True, null=True, db_column="T403NnumOrigenLiq")

    class Meta:
        db_table = "T403LiquidacionesBase"
        verbose_name = 'Liquidación base'
        verbose_name_plural = 'Liquidaciones base'


class DetalleLiquidacionBase(models.Model):
    id = models.AutoField(primary_key=True, db_column="T404IdDetalle_LiquidacionBase")
    id_opcion_liq = models.ForeignKey(OpcionesLiquidacionBase, db_column="T404Id_OpcionLiquidacionBase", on_delete=models.CASCADE)
    id_liquidacion = models.ForeignKey(LiquidacionesBase, on_delete=models.CASCADE, db_column="T404Id_LiquidacionBase", related_name='detalles')
    variables = models.JSONField(db_column="T404variables")
    valor = models.DecimalField(max_digits=20, decimal_places=4, default=0, db_column="T404valor")
    estado = models.IntegerField(default=1, db_column="T404estado")
    concepto = models.TextField(db_column="T404concepto")

    class Meta:
        db_table = "T404Detalles_LiquidacionesBase"
        verbose_name = 'Detalle liquidación base'
        verbose_name_plural = 'Detalles liquidación base'


class CalculosLiquidacionBase(models.Model):
    id = models.AutoField(primary_key=True, db_column="T450IdCalculos_LiquidacionBase")
    id_liquidacion = models.ForeignKey(LiquidacionesBase, on_delete=models.CASCADE, db_column="T450Id_LiquidacionBase")
    calculos = models.JSONField(db_column="T450calculos")

    class Meta:
        db_table = "T450Calculos_LiquidacionesBase"
        verbose_name = 'Calculo liquidación base'
        verbose_name_plural = 'Calculos liquidación base'

class HistEstadosLiq(models.Model):
    id_hist_estado_liq = models.AutoField(primary_key=True, db_column='T470IdHistEstadoLiq')
    liquidacion_base = models.ForeignKey(LiquidacionesBase, on_delete=models.CASCADE, db_column='T470Id_LiquidacionBase')
    estado_liq = models.CharField(choices=estados_liquidacion_CHOICES, max_length=10, db_column='T470EstadoLiq')
    fecha_estado = models.DateTimeField(blank=True, null=True, db_column='T470fechaEstado')

    class Meta:
        db_table = "T470HistEstadosLiq"
        verbose_name = 'Historial estado liquidación'
        verbose_name_plural = 'Historial estados liquidación'