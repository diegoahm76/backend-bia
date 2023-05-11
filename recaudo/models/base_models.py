from django.db import models


class VariablesBase(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='T400id')
    nombre = models.CharField(max_length=255, db_column='T400nombre')
    tipo = models.CharField(max_length=1, db_column='T400tipo')
    valor_defecto = models.DecimalField(max_digits=30, decimal_places=2, default=0, db_column='T400valor_defecto')
    estado = models.IntegerField(default=1, db_column='T400estado')

    class Meta:
        db_table = "T400variables_base"
        verbose_name = 'Variable base'
        verbose_name_plural = 'Variables base'


class NaturalezaJuridica(models.Model):
    id = models.AutoField(primary_key=True, db_column='T408id')
    descripcion = models.CharField(max_length=255, db_column='T408descripcion')

    class Meta:
        db_table = 'T408naturalezas_juridica'
        verbose_name = 'Naturaleza juridica'
        verbose_name_plural = 'Naturaleza juridica'


class Ubicaciones(models.Model):
    id = models.AutoField(primary_key=True, db_column='T409id')
    nombre = models.CharField(max_length=255, db_column='T409nombre')
    id_ubicacion_padre = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, db_column='T409id_ubicacion_padre')

    class Meta:
        db_table = 'T409ubicaciones'
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'


class RangosEdad(models.Model):
    id = models.AutoField(primary_key=True, db_column='T411id')
    descripcion = models.CharField(max_length=255, db_column='T411descripcion')
    inicial = models.DateTimeField(db_column='T411inicial')
    final = models.DateTimeField(db_column='T411final')

    class Meta:
        db_table = 'T411rangos_edad'
        verbose_name = 'Rango edad'
        verbose_name_plural = 'Rangos edad'


class TiposBien(models.Model):
    id = models.AutoField(primary_key=True, db_column='T415id')
    descripcion = models.CharField(max_length=255, db_column='T415descripcion')

    class Meta:
        db_table = 'T415tipos_bien'
        verbose_name = 'Tipo bien'
        verbose_name_plural = 'Tipos bien'


class TiposPago(models.Model):
    id = models.AutoField(primary_key=True, db_column='T412id')
    descripcion = models.CharField(max_length=255, db_column='T412descripcion')

    class Meta:
        db_table = 'T412tipos_pago'
        verbose_name = 'Tipos pago'
        verbose_name_plural = 'Tipos pagos'


class TipoActuacion(models.Model):
    id = models.AutoField(primary_key=True, db_column='T427id')
    descripcion = models.CharField(max_length=255, db_column='T427descripcion')

    class Meta:
        db_table = 'T427tipo_actuacion'
        verbose_name = 'Tipo actuación'
        verbose_name_plural = 'Tipo actuación'