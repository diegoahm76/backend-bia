from django.db import models
from recaudo.models.base_models import NaturalezaJuridica, Ubicaciones


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
    class Meta:
        db_table = 'T407Expedientes'
        verbose_name = 'Expediente'
        verbose_name_plural = 'Expedientes'


class OpcionesLiquidacionBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='T402IdOpcionLiquidacionBase')
    nombre = models.CharField(max_length=255, db_column='T402nombre')
    estado = models.IntegerField(default=1, db_column='T402estado')
    version = models.IntegerField(default=1, db_column='T402version')
    funcion = models.TextField(db_column='T402funcion')
    variables = models.JSONField(db_column='T402variables')
    bloques = models.TextField(db_column='T402bloques')

    class Meta:
        db_table = "T402OpcionesLiquidacionBase"
        verbose_name = 'Opcion liquidación base'
        verbose_name_plural = 'Opciones liquidación base'


class LiquidacionesBase(models.Model):
    id = models.AutoField(primary_key=True, db_column="T403IdLiquidacionBase")
    id_deudor = models.ForeignKey(Deudores, on_delete=models.CASCADE, db_column="T403Id_Deudor")
    id_expediente = models.ForeignKey(Expedientes, on_delete=models.CASCADE, db_column="T403Id_Expediente")
    fecha_liquidacion = models.DateTimeField(db_column="T403fechaLiquidacion")
    vencimiento = models.DateTimeField(db_column="T403vencimiento")
    periodo_liquidacion = models.CharField(max_length=255, db_column="T403periodoLiquidacion")
    valor = models.IntegerField(default=0, db_column="T403valor")
    estado = models.CharField(max_length=1, default='G', db_column="T403estado")

    class Meta:
        db_table = "T403LiquidacionesBase"
        verbose_name = 'Liquidación base'
        verbose_name_plural = 'Liquidaciones base'


class DetalleLiquidacionBase(models.Model):
    id = models.AutoField(primary_key=True, db_column="T404IdDetalle_LiquidacionBase")
    id_opcion_liq = models.ForeignKey(OpcionesLiquidacionBase, db_column="T404Id_OpcionLiquidacionBase", on_delete=models.CASCADE)
    id_liquidacion = models.ForeignKey(LiquidacionesBase, on_delete=models.CASCADE, db_column="T404Id_LiquidacionBase", related_name='detalles')
    variables = models.JSONField(db_column="T404variables")
    valor = models.IntegerField(default=0, db_column="T404valor")
    estado = models.IntegerField(default=1, db_column="T404estado")
    concepto = models.TextField(db_column="T404concepto")

    class Meta:
        db_table = "T404Detalles_LiquidacionesBase"
        verbose_name = 'Detalle liquidación base'
        verbose_name_plural = 'Detalles liquidación base'