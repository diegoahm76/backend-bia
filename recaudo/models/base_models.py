from django.db import models
from enum import Enum


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




class TipoRenta(models.Model):
    id_tipo_renta = models.AutoField(primary_key=True, db_column='T442IdTipoRenta')  
    nombre_tipo_renta = models.CharField(max_length=255, db_column='T442NombreTipoRenta',unique=True)

    # valor_tipo_renta = models.DecimalField(max_digits=10, decimal_places=2, db_column='T442valor_tipo_renta')
    class Meta:
        db_table = 'T442TipoRenta'
        verbose_name = 'Tipo Renta'
        verbose_name_plural = 'Tipos de Renta'

class TipoCobro(models.Model):
    id_tipo_cobro = models.AutoField(primary_key=True, db_column='T441IdTipoCobro')  
    nombre_tipo_cobro = models.CharField(max_length=255, db_column='T441NombreTipoCobro',unique=True)
    tipo_renta_asociado = models.ForeignKey(TipoRenta, on_delete=models.CASCADE, db_column='T442IdTipoAsociado', related_name='tiporenta_tipo_cobro')



    class Meta:
        db_table = 'T441TipoCobro'
        verbose_name = 'Tipo Cobro'
        verbose_name_plural = 'Tipo Cobro'

class Variables(models.Model):
    id_variables = models.AutoField(primary_key=True, db_column='T443IdVariables')
    nombre = models.CharField(max_length=255, db_column='T443Nombre',unique=True)
    tipo_cobro = models.ForeignKey(TipoCobro, on_delete=models.CASCADE, db_column='T443IdTipoCobro', related_name='variables_tipo_cobro')
    tipo_renta = models.ForeignKey(TipoRenta, on_delete=models.CASCADE, db_column='T443IdTipoRenta', related_name='variables_tipo_renta')
    numero_dias_variable = models.IntegerField(db_column='T443numero_dias_variable', null=True, default=None)
    class Meta:
        db_table = 'T443Variables'
        verbose_name = 'Variables'
        verbose_name_plural = 'Variables'


class ValoresVariables(models.Model):
    id_valores_variables = models.AutoField(primary_key=True, db_column='T444IdValoresVariables')
    variables = models.ForeignKey(Variables, on_delete=models.CASCADE, db_column='T444IdVariables', related_name='valores_variables_variables')
    fecha_inicio  =models.DateField(db_column='T444FechaInicio')
    fecha_fin = models.DateField(db_column='T444FechaFin')
    valor = models.DecimalField(max_digits=10, decimal_places=2, db_column='T444Valor')
    descripccion = models.CharField(max_length=255, db_column='T444Descripcion',unique=True)  # Corregir el nombre de la columna
    estado=models.BooleanField(default=False,db_column='T444Estado',null=True)  # Cambiado a campo booleano
    usada=models.BooleanField(default=False, db_column='T444Usada', null=True)  # Cambiado a campo booleano
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




class AdministraciondePersonal(models.Model):
    id = models.AutoField(primary_key=True, db_column='T43IdV')
    nivel = models.IntegerField(db_column='T464Nivel')
    valor=models.DecimalField(max_digits=10, decimal_places=0, db_column='T464Valor')
    nombre = models.CharField(max_length=255, db_column='T464Nombre')
    codigo_profesional = models.CharField(max_length=20, db_column='T464CodigoProfesional')
    descripcion = models.CharField(max_length=255, db_column='T464Descripcion')
    año = models.IntegerField(null=True,default=True,db_column='T464Año')  # Nuevo campo para el año

    class Meta:
        db_table = 'T464AdministraciondePersonal'
        verbose_name = 'Administracion de Personal'
        verbose_name_plural = 'Administracion de Personal'
        unique_together = [['nivel', 'nombre','año']]



MONTH_CHOICES = [
    (1, 'Enero'),
    (2, 'Febrero'),
    (3, 'Marzo'),
    (4, 'Abril'),
    (5, 'Mayo'),
    (6, 'Junio'),
    (7, 'Julio'),
    (8, 'Agosto'),
    (9, 'Septiembre'),
    (10, 'Octubre'),
    (11, 'Noviembre'),
    (12, 'Diciembre')
]

class ConfigaraicionInteres(models.Model):
    id = models.AutoField(primary_key=True, db_column='T466configuracionInteres')
    año = models.IntegerField(db_column='T466Nivel')
    mes = models.IntegerField(choices=MONTH_CHOICES, db_column='T466mes')
    valor_interes = models.DecimalField(max_digits=10, decimal_places=0, db_column='T466ValorInteres')
    estado_editable = models.BooleanField(default=False, db_column='T466EstadoEditable')

    class Meta:
        db_table = 'T466ConfigaraicionInteres'
        verbose_name = 'Configaraicion Interes'
        verbose_name_plural = 'Configaraicion Interes'
        unique_together = ('año', 'mes')  # Restricción única para año y mes



# Choices para la frecuencia de medición
FRECUENCIA_CHOICES = [
    ('mensual', 'Mensual'),
    ('semestral', 'Semestral'),
    ('trimestral', 'Trimestral'),
    ('anual', 'Anual'),
]


class Formulario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)

    class Meta:
        db_table = 'T469formularionombre'

class IndicadoresSemestral(models.Model):
    id_indicador = models.AutoField(primary_key=True, db_column='T465IdIndicador')  # Campo autoincremental
    proceso = models.CharField(max_length=255, db_column='T465Proceso')
    nombre_indicador = models.CharField(max_length=255, db_column='T465Nombre_del_indicador')
    frecuencia_medicion = models.CharField(max_length=50, choices=FRECUENCIA_CHOICES, db_column='T465Frecuencia_de_medicion')
    formula_indicador = models.CharField(max_length=255, db_column='T465Formula_del_indicador')
    vigencia_reporta = models.IntegerField( db_column='T465Vigencia_que_reporta')
    dependencia_grupo_regional = models.CharField(max_length=255, db_column='T465Dependencia_grupo_regional')
    objetivo_indicador = models.CharField(max_length=255, db_column='T465Objetivo_del_indicador')
    unidad_medicion_reporte = models.CharField(max_length=255, db_column='T465Unidad_de_medicion_y_reporte')
    descripcion_variable_1 = models.TextField(db_column='T465Descipccion_variable_1')
    descripcion_variable_2 = models.TextField(db_column='T465Descripccion_variable_2')
    origen_datos = models.CharField(max_length=255, db_column='T465Origen_de_datos')
    fecha_creacion = models.DateField(auto_now_add=True, db_column='T465Fecha_creacion')
    responsable_creacion = models.CharField(max_length=255, db_column='T465Responsable_creacion')
    tipo_indicador = models.CharField(max_length=255, db_column='T465Tipo_indicador')
    # formulario = models.CharField(max_length=1, choices=FORMULARIO_CHOICES, db_column='T465Formulario')
    formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE, db_column='T465Formulario')
    interpretacion=models.CharField(max_length=500,db_column='T465Interpretacion',null=True,default=True)  # Cambiado a campo booleano
    formula=models.CharField(max_length=255,db_column='T465Formula',null=True,default=True)  # Cambiado a campo booleano


    class Meta:
        db_table = 'T465IndicadoresSemestral'
        verbose_name = 'Configuracion Interes'
        verbose_name_plural = 'Configuracion Interes'
        unique_together = ('vigencia_reporta', 'formulario')


    def __str__(self):
        return self.nombre_indicador

class IndicadorValor(models.Model):
    indicador = models.ForeignKey(IndicadoresSemestral, on_delete=models.CASCADE)
    mes_id = models.IntegerField(choices=MONTH_CHOICES, db_column='T467mes')
    valor = models.DecimalField(max_digits=10, decimal_places=0, db_column='T467Valor')
    variable_1 = models.DecimalField(max_digits=15, decimal_places=0, db_column='T467Variable_1')
    variable_2 = models.DecimalField(max_digits=15, decimal_places=0, db_column='T467Variable_2')

    class Meta:
        db_table = 'T467IndicadorValor'

    def __str__(self):
        return f"{self.indicador} - {self.mes_id}: {self.valor}"
    


class ModeloBaseSueldoMinimo(models.Model):
    id = models.AutoField(primary_key=True)
    capacidad=models.CharField(max_length=255,db_column='T470Capacidad')
    valor=models.DecimalField(max_digits=15, decimal_places=0, db_column='T470Valor')
    editable=models.BooleanField(default=False, db_column='T470Editable')
    formula=models.CharField(max_length=255, db_column='T470Formula', null=True, default="")  # Cambiado a campo booleano

    class Meta:
        db_table = 'T470ModeloBaseSueldoMinimo'
        verbose_name = 'ModeloBase Sueldo Minimo'
        verbose_name_plural = 'ModeloBase Sueldo Minimo'
     

