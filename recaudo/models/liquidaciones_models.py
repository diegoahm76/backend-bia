from django.db import models
from recaudo.models.base_models import NaturalezaJuridica, Ubicaciones


class Deudores(models.Model):
    codigo = models.AutoField(primary_key=True, db_column='T410codigo')
    identificacion = models.CharField(max_length=255, db_column='T410identificacion')
    nombres = models.CharField(max_length=255, db_column='T410nombres')
    apellidos = models.CharField(max_length=255, db_column='T410apellidos')
    telefono = models.CharField(max_length=255, db_column='T410telefono')
    email = models.CharField(max_length=255, db_column='T410email')
    ubicacion_id = models.ForeignKey(Ubicaciones, on_delete=models.CASCADE, db_column='T410ubicacion_id')
    naturaleza_juridica_id = models.ForeignKey(NaturalezaJuridica, on_delete=models.CASCADE, db_column='T410naturaleza_juridica_id')

    class Meta:
        db_table = 'T410deudores'
        verbose_name = 'Deudor'
        verbose_name_plural = 'Deudores'


class Expedientes(models.Model):
    id = models.AutoField(primary_key=True, db_column='T407id')
    codigo_expediente = models.IntegerField(db_column='T407codigo_expediente')
    cod_deudor = models.ForeignKey(Deudores, on_delete=models.CASCADE, db_column='T407cod_deudor')
    numero_resolucion = models.CharField(max_length=255, db_column='T407resolucion')

    class Meta:
        db_table = 'T407expedientes'
        verbose_name = 'Expediente'
        verbose_name_plural = 'Expedientes'


class OpcionesLiquidacionBase(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='T402id')
    nombre = models.CharField(max_length=255, db_column='T402nombre')
    estado = models.IntegerField(default=1, db_column='T402estado')
    version = models.IntegerField(default=1, db_column='T402version')
    funcion = models.TextField(db_column='T402funcion')
    variables = models.JSONField(db_column='T402variables')
    bloques = models.TextField(db_column='T402bloques')

    class Meta:
        db_table = "T402opciones_liquidacion_base"
        verbose_name = 'Opcion liquidación base'
        verbose_name_plural = 'Opciones liquidación base'


class LiquidacionesBase(models.Model):
    id = models.AutoField(primary_key=True, db_column="T403id")
    cod_deudor = models.ForeignKey(Deudores, on_delete=models.CASCADE, db_column="T403cod_deudor")
    cod_expediente = models.ForeignKey(Expedientes, on_delete=models.CASCADE, db_column="T403cod_expediente")
    fecha_liquidacion = models.DateTimeField(db_column="T403fecha_liquidacion")
    vencimiento = models.DateTimeField(db_column="T403vencimiento")
    periodo_liquidacion = models.CharField(max_length=255, db_column="T403periodo_liquidacion")
    valor = models.IntegerField(default=0, db_column="T403valor")
    estado = models.CharField(max_length=1, default='G', db_column="T403estado")

    class Meta:
        db_table = "T403liquidaciones_base"
        verbose_name = 'Liquidación base'
        verbose_name_plural = 'Liquidaciones base'


class DetalleLiquidacionBase(models.Model):
    id = models.AutoField(primary_key=True, db_column="T404id")
    id_opcion_liq = models.ForeignKey(OpcionesLiquidacionBase, db_column="T403id_opcion_liq", on_delete=models.CASCADE)
    id_liquidacion = models.ForeignKey(LiquidacionesBase, on_delete=models.CASCADE, db_column="T404id_liquidacion", related_name='detalles')
    variables = models.JSONField(db_column="T404variables")
    valor = models.IntegerField(default=0, db_column="T404valor")
    estado = models.IntegerField(default=1, db_column="T404estado")
    concepto = models.TextField(db_column="T404concepto")

    class Meta:
        db_table = "T404detalles_liquidaciones_base"
        verbose_name = 'Detalle liquidación base'
        verbose_name_plural = 'Detalles liquidación base'