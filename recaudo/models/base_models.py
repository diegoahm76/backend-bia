from django.db import models


class NaturalezaJuridica(models.Model):
    id = models.AutoField(primary_key=True, db_column='T448IdNaturaleza')
    descripcion = models.CharField(max_length=255, db_column='T448descripcion')

    class Meta:
        db_table = 'T448NaturalezasJuridica'
        verbose_name = 'Naturaleza juridica'
        verbose_name_plural = 'Naturaleza juridica'


class Ubicaciones(models.Model):
    id = models.AutoField(primary_key=True, db_column='T449IdUbicaciones')
    nombre = models.CharField(max_length=255, db_column='T449nombre')
    id_ubicacion_padre = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, db_column='T449Id_UbicacionPadre')

    class Meta:
        db_table = 'T449Ubicaciones'
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'


class RangosEdad(models.Model):
    id = models.AutoField(primary_key=True, db_column='T411IdRangosEdad')
    descripcion = models.CharField(max_length=255, db_column='T411descripcion')
    inicial = models.IntegerField(db_column='T411inicial')
    final = models.IntegerField(db_column='T411final')
    color = models.CharField(max_length=16, db_column='T411color')

    class Meta:
        db_table = 'T411RangosEdad'
        verbose_name = 'Rango edad'
        verbose_name_plural = 'Rangos edad'


class TiposBien(models.Model):
    id = models.AutoField(primary_key=True, db_column='T415IdTipoBien')
    descripcion = models.CharField(max_length=255, db_column='T415descripcion')
    vigencia_avaluo = models.IntegerField(db_column='T415vigenciaAvaluo')

    class Meta:
        db_table = 'T415TiposBien'
        verbose_name = 'Tipo bien'
        verbose_name_plural = 'Tipos bien'


class TiposPago(models.Model):
    id = models.AutoField(primary_key=True, db_column='T434IdTipoPago')
    descripcion = models.CharField(max_length=255, db_column='T434descripcion')

    class Meta:
        db_table = 'T434TiposPago'
        verbose_name = 'Tipos pago'
        verbose_name_plural = 'Tipos pagos'


class TipoActuacion(models.Model):
    id = models.AutoField(primary_key=True, db_column='T427IdTipoActuacion')
    descripcion = models.CharField(max_length=255, db_column='T427descripcion')

    class Meta:
        db_table = 'T427TiposActuacion'
        verbose_name = 'Tipo actuación'
        verbose_name_plural = 'Tipos actuación'


#PARTE DE STIVEN PRACTICANTE 

class RegistrosConfiguracion(models.Model):
    id = models.AutoField(primary_key=True, db_column='T440IdRegistroConfiguracion')
    Estado = models.BooleanField(db_column='T440Estado')  # Cambiado a campo booleano
    TipoRenta = models.CharField(max_length=255, db_column='T440TipoRenta')
    TipoCobro = models.CharField(max_length=255, db_column='T440TipoCobro')
    Descripcion = models.CharField(max_length=255, db_column='T440Descripcion')

    class Meta:
        db_table = 'T440RegistrosConfiguración'
        verbose_name = 'Registro configuración'
        verbose_name_plural = 'Registros configuración'


class TipoCobro(models.Model):
    id_tipo_cobro = models.AutoField(primary_key=True, db_column='T441IdTipoCobro')  
    nombre_tipo_cobro = models.CharField(max_length=255, db_column='T441NombreTipoCobro')
    # valor_tipo_cobro = models.DecimalField(max_digits=10, decimal_places=2, db_column='T441valor_tipo_cobro')


    class Meta:
        db_table = 'T441TipoCobro'
        verbose_name = 'Tipo Cobro'
        verbose_name_plural = 'Tipo Cobro'


class TipoRenta(models.Model):
    id_tipo_renta = models.AutoField(primary_key=True, db_column='T442IdTipoRenta')  
    nombre_tipo_renta = models.CharField(max_length=255, db_column='T442NombreTipoRenta')
    tipo_cobro_asociado = models.ForeignKey(TipoCobro, on_delete=models.CASCADE, db_column='T442IdTipoCobroAsociado', related_name='tiporenta_tipo_cobro')

    # valor_tipo_renta = models.DecimalField(max_digits=10, decimal_places=2, db_column='T442valor_tipo_renta')
    class Meta:
        db_table = 'T442TipoRenta'
        verbose_name = 'Tipo Renta'
        verbose_name_plural = 'Tipos de Renta'


class Variables(models.Model):
    id_variables = models.AutoField(primary_key=True, db_column='T443IdVariables')
    nombre = models.CharField(max_length=255, db_column='T443Nombre')
    tipo_cobro = models.ForeignKey('TipoCobro', on_delete=models.CASCADE, db_column='T443IdTipoCobro', related_name='variables_tipo_cobro')
    tipo_renta = models.ForeignKey(TipoRenta, on_delete=models.CASCADE, db_column='T443IdTipoRenta', related_name='variables_tipo_renta')
    valor_varaible = models.DecimalField(max_digits=10, decimal_places=2, db_column='T443valor_varaible')
    
    numero_dias_variable = models.IntegerField(db_column='T443numero_dias_variable', null=True, default=None)
    class Meta:
        db_table = 'T443Variables'
        verbose_name = 'Variables'
        verbose_name_plural = 'Variables'


class ValoresVariables(models.Model):
    id_valores_variables = models.AutoField(primary_key=True, db_column='T444IdValoresVariables')
    variables = models.ForeignKey(Variables, on_delete=models.CASCADE, db_column='T444IdVariables', related_name='valores_variables_variables')
    fecha_inicio = models.DateTimeField(auto_now_add=True, db_column='T444FechaInicio')  
    fecha_fin = models.DateField(db_column='T444FechaFin')
    valor = models.DecimalField(max_digits=10, decimal_places=2, db_column='T444Valor')
    descripccion = models.CharField(max_length=255, db_column='T444Descripcion')  # Corregir el nombre de la columna
    estado=models.BooleanField(db_column='T444Estado',null=True,default=True)  # Cambiado a campo booleano
    class Meta:
        db_table = 'T444ValoresVariables'
        verbose_name = 'Valores Variables'
        verbose_name_plural = 'Valores Variables'


class LeyesLiquidacion(models.Model):
    id_ley = models.AutoField(primary_key=True, db_column='T451IdLey')
    ley = models.TextField(db_column='T451Ley')

    class Meta:
        db_table = 'T451Leyes'
        verbose_name = 'Ley'
        verbose_name_plural = 'Leyes'


class Twwwprincipal(models.Model):
    Twwwfecha = models.DateTimeField(db_column='Twwwfecha')
    Twwwt908codcia = models.FloatField(db_column='Twwwt908codcia', null=True)
    Twwwtiporenta = models.TextField(db_column='Twwwtiporenta', null=True)
    Twwwcuentacontable = models.TextField(db_column='Twwwcuentacontable', null=True)
    Twwwnombredeudor = models.TextField(db_column='Twwwnombredeudor', null=True)
    Twwwfechafact = models.DateTimeField(db_column='Twwwfechafact', null=True)
    Twwwfechanotificacion = models.DateTimeField(db_column='Twwwfechanotificacion', null=True)
    Twwwfechaenfirme = models.DateTimeField(db_column='Twwwfechaenfirme', null=True)
    Twwwcortedesde = models.TextField(db_column='Twwwcortedesde', null=True)
    Twwwcortehasta = models.TextField(db_column='Twwwcortehasta', null=True)
    Twwwnumfactura = models.TextField(db_column='Twwwnumfactura', null=True)
    Twwwnumliquidacion = models.FloatField(db_column='Twwwnumliquidacion', null=True)
    Twwwperiodo = models.TextField(db_column='Twwwperiodo', null=True)
    Twwwaño = models.FloatField(db_column='Twwwaño', null=True)
    Twwwexpediente = models.TextField(db_column='Twwwexpediente', null=True)
    Twwwnumresolucion = models.TextField(db_column='Twwwnumresolucion', null=True)
    Twwwrecurso = models.TextField(db_column='Twwwrecurso', null=True)
    Twwwdocauto = models.TextField(db_column='Twwwdocauto', null=True)
    Twwwsaldocapital = models.FloatField(db_column='Twwwsaldocapital', null=True)
    Twwwsaldointeres = models.FloatField(db_column='Twwwsaldointeres', null=True)
    Twwwdiasmora = models.FloatField(db_column='Twwwdiasmora', null=True)
    Twwwnit = models.TextField(db_column='Twwwnit', null=True)

    class Meta:
        db_table = 'TwwwPrincipal'
        verbose_name = 'Principal'
        verbose_name_plural = 'Principal'

