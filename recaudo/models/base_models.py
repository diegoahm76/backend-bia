from django.db import models


class VariablesBase(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='T400IdVariable')
    nombre = models.CharField(max_length=255, db_column='T400nombre')
    tipo = models.CharField(max_length=1, db_column='T400tipo')
    valor_defecto = models.DecimalField(max_digits=30, decimal_places=2, default=0, db_column='T400valorDefecto')
    estado = models.IntegerField(default=1, db_column='T400estado')

    class Meta:
        db_table = "T400VariablesBase"
        verbose_name = 'Variable base'
        verbose_name_plural = 'Variables base'


class NaturalezaJuridica(models.Model):
    id = models.AutoField(primary_key=True, db_column='T408IdNaturaleza')
    descripcion = models.CharField(max_length=255, db_column='T408descripcion')

    class Meta:
        db_table = 'T408NaturalezasJuridica'
        verbose_name = 'Naturaleza juridica'
        verbose_name_plural = 'Naturaleza juridica'


class Ubicaciones(models.Model):
    id = models.AutoField(primary_key=True, db_column='T409IdUbicaciones')
    nombre = models.CharField(max_length=255, db_column='T409nombre')
    id_ubicacion_padre = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, db_column='T409Id_UbicacionPadre')

    class Meta:
        db_table = 'T409Ubicaciones'
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'


class RangosEdad(models.Model):
    id = models.AutoField(primary_key=True, db_column='T411IdRangosEdad')
    descripcion = models.CharField(max_length=255, db_column='T411descripcion')
    inicial = models.IntegerField(db_column='T411inicial')
    final = models.IntegerField(db_column='T411final')

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
    id = models.AutoField(primary_key=True, db_column='T412IdTipoPago')
    descripcion = models.CharField(max_length=255, db_column='T412descripcion')

    class Meta:
        db_table = 'T412TiposPago'
        verbose_name = 'Tipos pago'
        verbose_name_plural = 'Tipos pagos'


class TipoActuacion(models.Model):
    id = models.AutoField(primary_key=True, db_column='T427IdTipoActuacion')
    descripcion = models.CharField(max_length=255, db_column='T427descripcion')

    class Meta:
        db_table = 'T427TiposActuacion'
        verbose_name = 'Tipo actuación'
        verbose_name_plural = 'Tipos actuación'