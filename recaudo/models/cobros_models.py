from django.db import models
from recaudo.models.liquidaciones_models import LiquidacionesBase, Deudores, Expedientes
from recaudo.models.planes_pagos_models import TasasInteres
from recaudo.models.base_models import RangosEdad, TipoRenta


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


class ConceptoContable(models.Model):
    id = models.AutoField(primary_key=True, db_column='T412IdConceptoContable')
    codigo_contable = models.CharField(max_length=255, db_column='T412codigoContable')
    descripcion = models.CharField(max_length=255, null=True, blank=True, db_column='T412descripcion')

    class Meta: 
        db_table = 'T412ConceptosContable'
        verbose_name = 'Concepto contable'
        verbose_name_plural = 'Conceptos contables'


class Cartera(models.Model):
    id = models.AutoField(primary_key=True, db_column='T413IdCartera')
    nombre = models.CharField(max_length=255, db_column='T413nombre')
    dias_mora = models.IntegerField(db_column='T413diasMora')
    valor_intereses = models.DecimalField(max_digits=30, decimal_places=4, null=True, blank=True, db_column='T413valorIntereses')
    valor_sancion = models.DecimalField(max_digits=30, decimal_places=4, null=True, blank=True, db_column='T413valorSancion')
    inicio = models.DateTimeField(db_column='T413inicio', null=True, blank=True)
    fin = models.DateTimeField(null=True, blank=True,db_column='T413fin')
    id_rango = models.ForeignKey(RangosEdad, on_delete=models.CASCADE, db_column='T413Id_RangoEdad')
    codigo_contable = models.ForeignKey(ConceptoContable, on_delete=models.CASCADE, db_column='T413Id_ConceptoContable')
    fecha_facturacion = models.DateTimeField(null=True, blank=True, db_column='T413fechaFacturacion')
    fecha_notificacion = models.DateTimeField(null=True, blank=True, db_column='T413fechaNotificacion')
    fecha_ejecutoriado = models.DateTimeField(null=True, blank=True, db_column='T413fechaEjecutoriado')
    numero_factura = models.CharField(max_length=255, null=True, blank=True, db_column='T413numeroFactura')
    monto_inicial = models.DecimalField(max_digits=30, decimal_places=4, db_column='T413montoInicial')
    tipo_cobro = models.CharField(max_length=255, db_column='T413tipoCobro')
    id_deudor = models.ForeignKey(Deudores, on_delete=models.CASCADE, db_column='T413Id_Deudor')
    id_documento_cobro = models.ForeignKey(DocumentosCobro, on_delete=models.SET_NULL, null=True, blank=True, db_column='T413Id_DocumentoCobro')
    id_expediente = models.ForeignKey(Expedientes, on_delete=models.CASCADE, db_column='T413Id_Expediente')
    tipo_renta = models.CharField(max_length=255, db_column='T413tipoRenta', null=True, blank=True)

    def calcular_valor_total(self):
        return self.valor_sancion + self.valor_intereses

    class Meta:
        db_table = 'T413Carteras'
        verbose_name = 'Cartera'
        verbose_name_plural = 'Cartera'


class VistaCarteraTua(models.Model):
    fecha = models.DateTimeField()
    cod_cia = models.CharField(max_length=5)
    tipo_renta = models.CharField(max_length=100)
    cuenta_contable = models.CharField(max_length=100)
    nit = models.CharField(max_length=15)
    nombre_deudor = models.CharField(max_length=255)
    fecha_fac = models.DateTimeField()
    fecha_notificacion = models.DateTimeField()
    fecha_en_firme = models.DateTimeField()
    corte_desde = models.CharField(max_length=100)
    corte_hasta = models.CharField(max_length=100)
    num_factura = models.CharField(max_length=255)
    num_liquidacion = models.IntegerField(primary_key=True)
    periodo = models.CharField(max_length=100)
    agno = models.IntegerField()
    expediente = models.CharField(max_length=100)
    num_resolucion = models.CharField(max_length=100)
    recurso = models.CharField(max_length=100)
    doc_auto = models.CharField(max_length=100)
    saldo_capital = models.DecimalField(max_digits=30, decimal_places=2)
    saldo_intereses = models.DecimalField(max_digits=30, decimal_places=2)
    dias_mora = models.IntegerField()

    class Meta:
        managed = False  # No permite a Django crear, modificar o borrar esta tabla
        db_table = 'vcarterabiatua'  # El nombre de la vista en la base de datos