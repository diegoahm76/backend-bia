from django.db import models
from recaudo.models.liquidaciones_models import LiquidacionesBase, Deudores, Expedientes
from recaudo.models.pagos_models import TasasInteres
from recaudo.models.base_models import RangosEdad


class DocumentosCobro(models.Model):
    id = models.AutoField(primary_key=True, db_column='T405id')
    cod_deudor = models.ForeignKey(Deudores, on_delete=models.CASCADE, db_column='T405cod_deudor')
    fecha_cobro = models.DateTimeField(db_column='T405fecha_cobro')
    vencimiento = models.DateTimeField(db_column='T405vencimiento')
    valor_deuda = models.IntegerField(default=0, db_column='T405valor_deuda')
    tasa_interes = models.ForeignKey(TasasInteres, on_delete=models.CASCADE, default=0, db_column='T405tasa_interes')
    valor_mora = models.IntegerField(default=0, db_column='T405valor_mora')
    porcentaje_descuento = models.IntegerField(default=0, db_column='T405porcentaje_descuento')
    valor_descuento = models.IntegerField(default=0, db_column='T405valor_descuento')
    valor_total = models.IntegerField(default=0, db_column='T405valor_total')
    estado = models.CharField(max_length=1, default='G', db_column='T405estado')

    class Meta:
        db_table = 'T405documentos_cobro'
        verbose_name = 'Documentos cobro'
        verbose_name_plural = 'Documento cobro'


class DetalleDocumentosCobro(models.Model):
    id = models.AutoField(primary_key=True, db_column='T406id')
    id_documento_cobro = models.ForeignKey(DocumentosCobro, on_delete=models.CASCADE, db_column='T406id_documento_cobro')
    id_liquidacion_base = models.ForeignKey(LiquidacionesBase, on_delete=models.CASCADE, db_column='T406id_liquidacion_base')
    valor = models.IntegerField(default=0, db_column='T406valor')
    estado = models.CharField(max_length=1, default='G', db_column='T406estado')

    class Meta:
        db_table = 'T406detalles_documentos_cobro'
        verbose_name = 'Detalle documentos cobro'
        verbose_name_plural = 'Detalles documentos cobro'


class Obligaciones(models.Model):
    id = models.AutoField(primary_key=True, db_column='T416id')
    nombre = models.CharField(max_length=255, db_column='T416nombre')
    cod_factura = models.CharField(max_length=255, db_column='T416cod_factura')
    fecha_inicio = models.DateField(db_column='T416fecha_inicio')
    monto_inicial = models.DecimalField(max_digits=30, decimal_places=2, db_column='T416monto_inicial')
    naturaleza = models.CharField(max_length=255, db_column='T416naturaleza')
    id_documento_cobro = models.ForeignKey(DocumentosCobro, on_delete=models.CASCADE, db_column='T416id_documento_cobro')
    id_expediente = models.ForeignKey(Expedientes, on_delete=models.CASCADE, db_column='T416id_expediente')

    class Meta:
        db_table = 'T416obligaciones'
        verbose_name = 'Obligación'
        verbose_name_plural = 'Obligaciones'


class Cartera(models.Model):
    id = models.AutoField(primary_key=True, db_column='T417id')
    id_obligacion = models.ForeignKey(Obligaciones, on_delete=models.CASCADE, db_column='T417id_obligacion')
    dias_mora = models.IntegerField(db_column='T417dias_mora')
    valor_intereses = models.DecimalField(max_digits=30, decimal_places=2, db_column='T417valor_intereses')
    valor_sancion = models.DecimalField(max_digits=30, decimal_places=2, db_column='T417valor_sancion')
    inicio = models.DateField(db_column='T417inicio')
    fin = models.DateField(null=True, blank=True,db_column='T417fin')
    id_rango = models.ForeignKey(RangosEdad, on_delete=models.CASCADE, db_column='T417id_rango')
    codigo_contable = models.CharField(max_length=255, db_column='T417codigo_contable')
    fecha_facturacion = models.DateField(db_column='T417fecha_facturacion')
    numero_factura = models.CharField(max_length=255, db_column='T417numero_factura')

    class Meta:
        db_table = 'T417cartera'
        verbose_name = 'Cartera'
        verbose_name_plural = 'Cartera'