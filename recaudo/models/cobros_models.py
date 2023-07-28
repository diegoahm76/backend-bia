from django.db import models
from recaudo.models.liquidaciones_models import LiquidacionesBase, Deudores, Expedientes
from recaudo.models.pagos_models import TasasInteres
from recaudo.models.base_models import RangosEdad


class DocumentosCobro(models.Model):
    id = models.AutoField(primary_key=True, db_column='T405IdDocumentoCobro')
    id_deudor = models.ForeignKey(Deudores, on_delete=models.CASCADE, db_column='T405Id_Deudor')
    fecha_cobro = models.DateField(db_column='T405fechaCobro')
    vencimiento = models.DateField(db_column='T405vencimiento')
    valor_deuda = models.FloatField(default=0, db_column='T405valorDeuda')
    tasa_interes = models.ForeignKey(TasasInteres, on_delete=models.CASCADE, default=0, db_column='T405Id_TasaInteres')
    valor_mora = models.FloatField(default=0, db_column='T405valorMora')
    porcentaje_descuento = models.FloatField(default=0, db_column='T405porcentajeDescuento')
    valor_descuento = models.FloatField(default=0, db_column='T405valorDescuento')
    valor_total = models.FloatField(default=0, db_column='T405valorTotal')
    estado = models.CharField(max_length=1, default='G', db_column='T405estado')

    class Meta:
        db_table = 'T405DocumentosCobro'
        verbose_name = 'Documento cobro'
        verbose_name_plural = 'Documentos cobro'


class DetalleDocumentosCobro(models.Model):
    id = models.AutoField(primary_key=True, db_column='T406IdDetalle_DocumentosCobro')
    id_documento_cobro = models.ForeignKey(DocumentosCobro, on_delete=models.CASCADE, db_column='T406Id_DocumentoCobro')
    id_liquidacion_base = models.ForeignKey(LiquidacionesBase, on_delete=models.CASCADE, db_column='T406Id_LiquidacionBase')
    valor = models.IntegerField(default=0, db_column='T406valor')
    estado = models.CharField(max_length=1, default='G', db_column='T406estado')

    class Meta:
        db_table = 'T406Detalles_DocumentosCobro'
        verbose_name = 'Detalle documentos cobro'
        verbose_name_plural = 'Detalles documentos cobro'


class Obligaciones(models.Model):
    id = models.AutoField(primary_key=True, db_column='T416IdObligaciones')
    nombre = models.CharField(max_length=255, db_column='T416nombre')
    cod_factura = models.CharField(max_length=255, db_column='T416codFactura')
    fecha_inicio = models.DateField(db_column='T416fechaInicio')
    monto_inicial = models.DecimalField(max_digits=30, decimal_places=2, db_column='T416montoInicial')
    naturaleza = models.CharField(max_length=255, db_column='T416naturaleza')
    id_documento_cobro = models.ForeignKey(DocumentosCobro, on_delete=models.CASCADE, db_column='T416Id_DocumentoCobro')
    id_expediente = models.ForeignKey(Expedientes, on_delete=models.CASCADE, db_column='T416Id_Expediente')

    class Meta:
        db_table = 'T416Obligaciones'
        verbose_name = 'Obligación'
        verbose_name_plural = 'Obligaciones'


class ConceptoContable(models.Model):
    id = models.AutoField(primary_key=True, db_column='T436IdConceptoContable')
    codigo_contable = models.CharField(max_length=255, db_column='T436codigoContable')
    descripcion = models.CharField(max_length=255, db_column='T436descripcion')

    class Meta: 
        db_table = 'T436ConceptosContable'
        verbose_name = 'Concepto contable'
        verbose_name_plural = 'Conceptos contables'


class Cartera(models.Model):
    id = models.AutoField(primary_key=True, db_column='T417IdCartera')
    id_obligacion = models.ForeignKey(Obligaciones, on_delete=models.CASCADE, db_column='T417Id_Obligacion')
    dias_mora = models.IntegerField(db_column='T417diasMora')
    valor_intereses = models.DecimalField(max_digits=30, decimal_places=2, db_column='T417valorIntereses')
    valor_sancion = models.DecimalField(max_digits=30, decimal_places=2, db_column='T417valorSancion')
    inicio = models.DateField(db_column='T417inicio')
    fin = models.DateField(null=True, blank=True,db_column='T417fin')
    id_rango = models.ForeignKey(RangosEdad, on_delete=models.CASCADE, db_column='T417Id_RangoEdad')
    codigo_contable = models.ForeignKey(ConceptoContable, on_delete=models.CASCADE, db_column='T417Id_ConceptoContable')
    fecha_facturacion = models.DateField(null=True, blank=True, db_column='T417fechaFacturacion')
    fecha_notificacion = models.DateField(null=True, blank=True, db_column='T417fechaNotificacion')
    fecha_ejecutoriado = models.DateField(null=True, blank=True, db_column='T417fechaEjecutoriado')
    numero_factura = models.CharField(max_length=255, db_column='T417numeroFactura')
    monto_inicial = models.DecimalField(max_digits=30, decimal_places=2, db_column='T417montoInicial')
    tipo_cobro = models.CharField(max_length=255, db_column='T417tipoCobro')
    id_deudor = models.ForeignKey(Deudores, on_delete=models.CASCADE, db_column='T417Id_Deudor')

    def calcular_valor_total(self):
        return self.valor_sancion + self.valor_intereses

    class Meta:
        db_table = 'T417Carteras'
        verbose_name = 'Cartera'
        verbose_name_plural = 'Cartera'