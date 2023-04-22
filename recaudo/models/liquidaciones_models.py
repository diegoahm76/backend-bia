from django.db import models
from recaudo.models.base_models import VariablesBase


class OpcionesLiquidacionBase(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='T402id')
    nombre = models.CharField(max_length=255, db_column='T402nombre')
    estado = models.IntegerField(default=1, db_column='T402estado')
    version = models.IntegerField(default=1, db_column='T402version')
    funcion = models.TextField(db_column='T402funcion')
    variables = models.JSONField(db_column='T402variables')

    class Meta:
        db_table = "T402opciones_liquidacion_base"
        verbose_name = 'Opcion liquidación base'
        verbose_name_plural = 'Opciones liquidación base'


class LiquidacionesBase(models.Model):
    id = models.AutoField(primary_key=True, db_column="T403id")
    id_opcion_liq = models.ForeignKey(OpcionesLiquidacionBase, db_column="T403id_opcion_liq", on_delete=models.CASCADE)
    cod_deudor = models.IntegerField(db_column="T403cod_deudor")
    cod_expediente = models.IntegerField(db_column="T403cod_expediente")
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
    id_liquidacion = models.ForeignKey(LiquidacionesBase, on_delete=models.CASCADE, db_column="T404id_liquidacion")
    id_variable = models.ForeignKey(VariablesBase, on_delete=models.CASCADE, db_column="T404id_variable")
    valor = models.IntegerField(default=0, db_column="T404valor")
    estado = models.IntegerField(default=1, db_column="T404estado")

    class Meta:
        db_table = "T404detalles_liquidaciones_base"
        verbose_name = 'Opcion liquidación base'
        verbose_name_plural = 'Opciones liquidación base'