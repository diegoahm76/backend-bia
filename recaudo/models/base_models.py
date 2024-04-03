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




class TipoRenta(models.Model):
    id_tipo_renta = models.AutoField(primary_key=True, db_column='T442IdTipoRenta')  
    nombre_tipo_renta = models.CharField(max_length=255, db_column='T442NombreTipoRenta')

    # valor_tipo_renta = models.DecimalField(max_digits=10, decimal_places=2, db_column='T442valor_tipo_renta')
    class Meta:
        db_table = 'T442TipoRenta'
        verbose_name = 'Tipo Renta'
        verbose_name_plural = 'Tipos de Renta'

class TipoCobro(models.Model):
    id_tipo_cobro = models.AutoField(primary_key=True, db_column='T441IdTipoCobro')  
    nombre_tipo_cobro = models.CharField(max_length=255, db_column='T441NombreTipoCobro')
    tipo_renta_asociado = models.ForeignKey(TipoRenta, on_delete=models.CASCADE, db_column='T442IdTipoAsociado', related_name='tiporenta_tipo_cobro')

    # valor_tipo_cobro = models.DecimalField(max_digits=10, decimal_places=2, db_column='T441valor_tipo_cobro')


    class Meta:
        db_table = 'T441TipoCobro'
        verbose_name = 'Tipo Cobro'
        verbose_name_plural = 'Tipo Cobro'

class Variables(models.Model):
    id_variables = models.AutoField(primary_key=True, db_column='T443IdVariables')
    nombre = models.CharField(max_length=255, db_column='T443Nombre')
    tipo_cobro = models.ForeignKey('TipoCobro', on_delete=models.CASCADE, db_column='T443IdTipoCobro', related_name='variables_tipo_cobro')
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




class AdministraciondePersonal(models.Model):
    id = models.AutoField(primary_key=True, db_column='T43IdV')
    nivel = models.IntegerField(db_column='T464Nivel')
    valor=models.DecimalField(max_digits=10, decimal_places=0, db_column='T464Valor')
    nombre = models.CharField(max_length=255, db_column='T464Nombre')
    codigo_profesional = models.CharField(max_length=20, db_column='T464CodigoProfesional')
    descripcion = models.CharField(max_length=255, db_column='T464Descripcion')

    class Meta:
        db_table = 'T464AdministraciondePersonal'
        verbose_name = 'Administracion de Personal'
        verbose_name_plural = 'Administracion de Personal'
        unique_together = [['nivel', 'nombre']]



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

# Choices para el formulario
FORMULARIO_CHOICES = [
    ('1', 'RECAUDO TUA'),
    ('2', 'RECAUDO TR'),
    ('3', 'COSTO RECAUDO TUA'),
    ('4', 'COSTO RECAUDO TR'),
]


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
    formulario = models.CharField(max_length=1, choices=FORMULARIO_CHOICES, db_column='T465Formulario')

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
    variable_1 = models.DecimalField(max_digits=10, decimal_places=0, db_column='T467Variable_1')
    variable_2 = models.DecimalField(max_digits=10, decimal_places=0, db_column='T467Variable_2')

    class Meta:
        db_table = 'T467IndicadorValor'

    def __str__(self):
        return f"{self.indicador} - {self.mes_id}: {self.valor}"
    
#_____modelosPimisis___________________________________________
    
class Rt970Tramite(models.Model):
    t970codcia = models.CharField(max_length=5, null=True, default=None, db_column='t970codcia')
    t970idtramite = models.CharField(max_length=255, db_column='t970idtramite')
    t970agno = models.SmallIntegerField(null=True, blank=True, db_column='t970agno')
    t970codtipotramite = models.CharField(max_length=5, null=True, blank=True, db_column='t970codtipotramite')
    t970codexpediente = models.CharField(max_length=30, null=True, blank=True, db_column='t970codexpediente')
    t970coddepen = models.CharField(max_length=20, null=True, blank=True, db_column='t970coddepen')
    t970numradicadoentrada = models.CharField(max_length=30, null=True, blank=True, db_column='t970numradicadoentrada')
    t970fecharadicadoentrada = models.DateTimeField(null=True, blank=True, db_column='t970fecharadicadoentrada')
    t970descripcion = models.TextField(null=True, blank=True, db_column='t970descripcion')
    t970idtramiteref = models.CharField(max_length=30, null=True, blank=True, db_column='t970idtramiteref')
    t970observacion = models.TextField(null=True, blank=True, db_column='t970observacion')
    t970codestadotram = models.CharField(max_length=5, null=True, blank=True, db_column='t970codestadotram')
    t970tuafechainiperm = models.DateTimeField(null=True, blank=True, db_column='t970tuafechainiperm')
    t970tuamesesplazo = models.CharField(max_length=100, null=True, blank=True, db_column='t970tuamesesplazo')
    t970tuafechafinperm = models.DateTimeField(null=True, blank=True, db_column='t970tuafechafinperm')
    t970numresolperm = models.CharField(max_length=30, null=True, blank=True, db_column='t970numresolperm')
    t970fecharesperm = models.DateTimeField(null=True, blank=True, db_column='t970fecharesperm')
    t970tuacaudalconcesi = models.CharField(max_length=200, null=True, blank=True, db_column='t970tuacaudalconcesi')
    t970tuapredio = models.CharField(max_length=255, null=True, blank=True, db_column='t970tuapredio')
    t970verifico_fun = models.CharField(max_length=1, null=True, blank=True, db_column='t970verifico_fun')

    class Meta:
        db_table = 'rt970tramite'  # Nombre de la tabla en la base de datos
        unique_together = ('t970codcia', 't970idtramite')  # Clave primaria compuesta


class Rt987TrVertimiento(models.Model):
    t987codcia = models.CharField(max_length=5, db_column='t987codcia')
    t987numtr = models.IntegerField(db_column='t987numtr')
    t987consecutivo = models.SmallIntegerField(db_column='t987consecutivo')
    t987codtipofuentehid = models.CharField(max_length=5, db_column='t987codtipofuentehid')
    t987codfuentehid = models.CharField(max_length=10, db_column='t987codfuentehid')
    t987codtramo = models.CharField(max_length=5, db_column='t987codtramo')
    t987caudalcaptado = models.DecimalField(max_digits=19, decimal_places=6, db_column='t987caudalcaptado')
    t987aguaenbloque = models.DecimalField(max_digits=19, decimal_places=6, db_column='t987aguaenbloque')
    t987consumoacueducto = models.DecimalField(max_digits=19, decimal_places=6, db_column='t987consumoacueducto')
    t987codubicacion = models.CharField(max_length=20, db_column='t987codubicacion')

    class Meta:
        unique_together = ('t987codcia', 't987numtr', 't987consecutivo')
        db_table = 'rt987trvertimiento'


class Rt986trActividad(models.Model):
    t986codcia = models.CharField(max_length=5, db_column='t986codcia')
    t986numtr = models.IntegerField(db_column='t986numtr')
    t986codactividadciiu = models.CharField(max_length=10, db_column='t986codactividadciiu')
    t986descripcion = models.CharField(max_length=255, db_column='t986descripcion')

    class Meta:
        unique_together = ('t986codcia', 't986numtr', 't986codactividadciiu')
        db_table = 'rt986tractividad'


class Rt985Tr(models.Model):
    t985codcia = models.CharField(max_length=5, db_column='t985codcia')
    t985numtr = models.IntegerField(db_column='t985numtr')
    t985agno = models.SmallIntegerField(db_column='t985agno')
    t985periodo = models.SmallIntegerField(db_column='t985periodo')
    t985numformulario = models.CharField(max_length=20, db_column='t985numformulario')
    t985codtipodeclaracion = models.CharField(max_length=5, db_column='t985codtipodeclaracion')
    t985aprobada = models.CharField(max_length=1, db_column='t985aprobada')
    t985fechadiligenciamiento = models.DateTimeField(db_column='t985fechadiligenciamiento')
    t985fecha = models.DateTimeField(db_column='t985fecha')
    t985numradicadoentrada = models.CharField(max_length=30, db_column='t985numradicadoentrada')
    t985fecharadicadoentrada = models.DateTimeField(db_column='t985fecharadicadoentrada')
    t985nit = models.CharField(max_length=15, db_column='t985nit')
    t985coddpto = models.CharField(max_length=5, db_column='t985coddpto')
    t985codmpio = models.CharField(max_length=5, db_column='t985codmpio')
    t985codpostal = models.CharField(max_length=20, db_column='t985codpostal')
    t985direccion = models.CharField(max_length=100, db_column='t985direccion')
    t985telefono = models.CharField(max_length=100, db_column='t985telefono')
    t985codtipousuario = models.CharField(max_length=5, db_column='t985codtipousuario')
    t985nitreplegal = models.CharField(max_length=15, db_column='t985nitreplegal')
    t985codubicacion = models.CharField(max_length=10, db_column='t985codubicacion')
    t985idcobro = models.IntegerField(db_column='t985idcobro')
    t985anulado = models.CharField(max_length=1, db_column='t985anulado')
    t985observacion = models.CharField(max_length=255, db_column='t985observacion')
    t985nitelaboro = models.CharField(max_length=15, db_column='t985nitelaboro')
    t985cargoelaboro = models.CharField(max_length=100, db_column='t985cargoelaboro')
    t985lugarelaboro = models.CharField(max_length=100, db_column='t985lugarelaboro')
    t985numficha = models.CharField(max_length=30, db_column='t985numficha')
    t985nummatricula = models.CharField(max_length=20, db_column='t985nummatricula')
    t985geoubicacion = models.CharField(max_length=50, db_column='t985geoubicacion')
    t985idtramite = models.CharField(max_length=30, db_column='t985idtramite')

    class Meta:
        db_table = 'rt985tr'



class Rt982Tuacaptacion(models.Model):
    t982codcia = models.CharField(max_length=5, db_column='t982codcia')
    t982numtua = models.IntegerField(db_column='t982numtua')
    t982consecutivo = models.SmallIntegerField(db_column='t982consecutivo')
    t982codtipofuentehid = models.CharField(max_length=5, db_column='t982codtipofuentehid')
    t982codclaseusoagua = models.CharField(max_length=5, db_column='t982codclaseusoagua')
    t982codfuentehid = models.CharField(max_length=10, db_column='t982codfuentehid')
    t982codtramo = models.CharField(max_length=5, db_column='t982codtramo')
    t982coddpto = models.CharField(max_length=5, db_column='t982coddpto')
    t982codmpio = models.CharField(max_length=5, db_column='t982codmpio')
    t982factorregional = models.DecimalField(max_digits=19, decimal_places=4, db_column='t982factorregional')

    class Meta:
        db_table = 'rt982tuacaptacion'


class Rt981TuaActividad(models.Model):
    t981codcia = models.CharField(max_length=5, db_column='t981codcia')
    t981numtua = models.IntegerField(db_column='t981numtua')
    t981codactividadciiu = models.CharField(max_length=10, db_column='t981codactividadciiu')
    t981descripcion = models.CharField(max_length=255, db_column='t981descripcion')

    class Meta:
        db_table = 'rt981tuaactividad'



class Rt980Tua(models.Model):
    t980codcia = models.CharField(max_length=5, db_column='t980codcia')
    t980numtua = models.IntegerField(db_column='t980numtua')
    t980agno = models.SmallIntegerField(db_column='t980agno')
    t980periodo = models.SmallIntegerField(db_column='t980periodo')
    t980numformulario = models.CharField(max_length=20, db_column='t980numformulario', null=True)
    t980codtipodeclaracion = models.CharField(max_length=5, db_column='t980codtipodeclaracion', null=True)
    t980aprobada = models.CharField(max_length=1, db_column='t980aprobada', null=True)
    t980fechadiligenciamiento = models.DateTimeField(db_column='t980fechadiligenciamiento', null=True)
    t980fecha = models.DateTimeField(db_column='t980fecha', null=True)
    t980numradicadoentrada = models.CharField(max_length=30, db_column='t980numradicadoentrada', null=True)
    t980fecharadicadoentrada = models.DateTimeField(db_column='t980fecharadicadoentrada', null=True)
    t980nit = models.CharField(max_length=15, db_column='t980nit', null=True)
    t980coddpto = models.CharField(max_length=5, db_column='t980coddpto', null=True)
    t980codmpio = models.CharField(max_length=5, db_column='t980codmpio', null=True)
    t980codpostal = models.CharField(max_length=20, db_column='t980codpostal', null=True)
    t980direccion = models.CharField(max_length=100, db_column='t980direccion', null=True)
    t980telefono = models.CharField(max_length=100, db_column='t980telefono', null=True)
    t980codtipousuario = models.CharField(max_length=5, db_column='t980codtipousuario', null=True)
    t980nitreplegal = models.CharField(max_length=15, db_column='t980nitreplegal', null=True)
    t980codubicacion = models.CharField(max_length=10, db_column='t980codubicacion', null=True)
    t980idcobro = models.IntegerField(db_column='t980idcobro', null=True)
    t980anulado = models.CharField(max_length=1, db_column='t980anulado', null=True)
    t980observacion = models.CharField(max_length=255, db_column='t980observacion', null=True)
    t980idtramite = models.CharField(max_length=30, db_column='t980idtramite', null=True)

    class Meta:
        db_table = 'rt980tua'



class Rt956FuenteHid(models.Model):
    t956codcia = models.CharField(max_length=5, db_column='t956codcia')
    t956codfuentehid = models.CharField(max_length=10, db_column='t956codfuentehid')
    t956nombre = models.CharField(max_length=100, db_column='t956nombre')
    t956observacion = models.CharField(max_length=255, db_column='t956observacion')
    t956geoubicacion = models.CharField(max_length=50, db_column='t956geoubicacion')
    t956areacuenca = models.DecimalField(max_digits=19, decimal_places=4, db_column='t956areacuenca')
    t956longitudcauce = models.DecimalField(max_digits=19, decimal_places=4, db_column='t956longitudcauce')
    t956movimiento = models.CharField(max_length=1, db_column='t956movimiento')

    class Meta:
        db_table = 'rt956fuentehid'


class Rt904RentaCtaBanco(models.Model):
    t904codcia = models.CharField(max_length=5, db_column='t904codcia')
    t904codtiporenta = models.CharField(max_length=20, db_column='t904codtiporenta')
    t904codctabanco = models.CharField(max_length=20, db_column='t904codctabanco')

    class Meta:
        db_table = 'rt904rentactabanco'




class Rt914Distribucion(models.Model):
    t914codcia = models.CharField(max_length=5, db_column='t914codcia')
    t914codtiporenta = models.CharField(max_length=5, db_column='t914codtiporenta')
    t914numdistribucion = models.IntegerField(db_column='t914numdistribucion')
    t914agno = models.SmallIntegerField(db_column='t914agno')
    t914codtipodoc = models.CharField(max_length=5, db_column='t914codtipodoc')
    t914numerodoc = models.IntegerField(db_column='t914numerodoc')
    t914codctabanco = models.CharField(max_length=20, db_column='t914codctabanco')
    t914codgruporec = models.CharField(max_length=10, db_column='t914codgruporec')
    t914fecha = models.DateTimeField(db_column='t914fecha')
    t914numorigen = models.IntegerField(db_column='t914numorigen')
    t914codorigen = models.CharField(max_length=1, db_column='t914codorigen')
    t914abonarliq = models.CharField(max_length=1, db_column='t914abonarliq')
    t914anulado = models.CharField(max_length=1, db_column='t914anulado')
    t914numerodocrnt = models.IntegerField(db_column='t914numerodocrnt', null=True)

    class Meta:
        db_table = 'rt914distribucion'


class Rt913Recaudo(models.Model):
    t913codcia = models.CharField(max_length=5, db_column='t913codcia')
    t913codtiporenta = models.CharField(max_length=5, db_column='t913codtiporenta')
    t913numrecaudo = models.IntegerField(db_column='t913numrecaudo')
    t913agno = models.SmallIntegerField(db_column='t913agno')
    t913codtipodoc = models.CharField(max_length=5, db_column='t913codtipodoc')
    t913codctabanco = models.CharField(max_length=20, db_column='t913codctabanco')
    t913codgruporec = models.CharField(max_length=10, db_column='t913codgruporec')
    t913nit = models.CharField(max_length=15, db_column='t913nit')
    t913fecha = models.DateTimeField(db_column='t913fecha')
    t913fechareal = models.DateTimeField(db_column='t913fechareal')
    t913valor = models.DecimalField(max_digits=19, decimal_places=4, db_column='t913valor')
    t913tipodistribucion = models.CharField(max_length=5, db_column='t913tipodistribucion')
    t913codtipoformulario = models.CharField(max_length=5, db_column='t913codtipoformulario')
    t913numformulario = models.CharField(max_length=20, db_column='t913numformulario')
    t913numformulariopago = models.IntegerField(null=True, db_column='t913numformulariopago')
    t913anulado = models.CharField(max_length=1, db_column='t913anulado')
    t913numanulacion = models.IntegerField(db_column='t913numanulacion')
    t913codformapago = models.CharField(max_length=5, null=True, db_column='t913codformapago')
    t913numdocpago = models.CharField(max_length=20, null=True, db_column='t913numdocpago')

    class Meta:
        db_table = 'rt913recaudo'



class Rt915DistribucionLiq(models.Model):
    t915codcia = models.CharField(max_length=5, db_column='t915codcia')
    t915codtiporenta = models.CharField(max_length=5, db_column='t915codtiporenta')
    t915numdistribucion = models.IntegerField(db_column='t915numdistribucion')
    t915numliquidacion = models.IntegerField(db_column='t915numliquidacion')
    t915codconcepto = models.CharField(max_length=5, db_column='t915codconcepto')
    t915valorpagado = models.DecimalField(max_digits=19, decimal_places=4, db_column='t915valorpagado')
    t915valorprescripcion = models.DecimalField(max_digits=19, decimal_places=4, db_column='t915valorprescripcion')
    t915valorpagadodet = models.DecimalField(max_digits=19, decimal_places=4, db_column='t915valorpagadodet')

    class Meta:
        unique_together = ('t915codcia', 't915codtiporenta', 't915numdistribucion', 't915numliquidacion', 't915codconcepto')
        db_table = 'rt915distribucionliq'


class Rt916DistribucionCuot(models.Model):
    t916codcia = models.CharField(max_length=5, db_column='t916codcia')
    t916codtiporenta = models.CharField(max_length=5, db_column='t916codtiporenta')
    t916numdistribucion = models.IntegerField(db_column='t916numdistribucion')
    t916numliquidacion = models.IntegerField(db_column='t916numliquidacion')
    t916numcuota = models.SmallIntegerField(db_column='t916numcuota')
    t916valorcapital = models.DecimalField(max_digits=19, decimal_places=4, db_column='t916valorcapital')
    t916valorinteres = models.DecimalField(max_digits=19, decimal_places=4, db_column='t916valorinteres')
    t916fechainiint = models.DateTimeField(db_column='t916fechainiint')
    t916valorint1066 = models.DecimalField(max_digits=19, decimal_places=4, db_column='t916valorint1066')
    t916valorprescripcion = models.DecimalField(max_digits=19, decimal_places=4, db_column='t916valorprescripcion')

    class Meta:
        db_table = 'rt916distribucioncuot'
