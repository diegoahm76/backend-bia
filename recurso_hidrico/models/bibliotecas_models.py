from django.db import models
#from django.contrib.gis.db import models
from seguridad.models import Personas

class Secciones(models.Model):
    id_seccion = models.AutoField(primary_key=True,editable=False,db_column="T605IdSeccion")
    nombre = models.CharField(max_length=255,db_column="T605nombre")
    descripcion = models.CharField(max_length=255,db_column="T605descripcion")
    fecha_creacion = models.DateField(auto_now_add=True,db_column="T605fechaCreacion")
    id_persona_creada = models.ForeignKey(Personas,on_delete=models.CASCADE,db_column="T605Id_PersonaCrea")
    registroPrecargado = models.BooleanField(db_column="T605registroPrecargado")
    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table = 'T605Seccion'
        verbose_name = 'Seccion'
        verbose_name_plural = 'Secciones'
        unique_together = ['nombre']

class Subsecciones(models.Model):
    id_subseccion = models.AutoField(primary_key=True,db_column="T606IdSubseccion_Seccion")
    id_seccion = models.ForeignKey(Secciones, on_delete=models.CASCADE,db_column="T606Id_Seccion")
    nombre = models.CharField(max_length=255,db_column="T606nombre")
    descripcion = models.CharField(max_length=255,db_column="T606descripcion")
    fechaCreacion = models.DateTimeField(auto_now_add=True,db_column="T606fechaCreacion")
    id_persona_creada = models.ForeignKey(Personas, on_delete=models.CASCADE,db_column="T606Id_PersonaCrea")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'T606Subsecciones_Seccion'
        verbose_name = 'subseccion'
        verbose_name_plural = 'subsecciones'
        unique_together = ['id_seccion', 'nombre']

#Consulta biblioteca
class Instrumentos(models.Model):
    id_instrumento = models.AutoField(primary_key=True, db_column='T607IdInstrumento')
    nombre = models.CharField(max_length=255, db_column='T607nombre')
    id_seccion = models.ForeignKey(Secciones, on_delete=models.CASCADE, db_column='T607Id_Seccion')
    id_subseccion = models.ForeignKey(Subsecciones, on_delete=models.CASCADE, db_column='T607Id_Subseccion', related_name='instrumentos')
    id_resolucion = models.IntegerField(blank=True, null=True, db_column='T607Id_Resolucion')#falta la tabla resolucion
    id_persona_registra = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T607Id_PersonaRegistra')
    fecha_registro = models.DateTimeField(auto_now=True,db_column='T607fechaRegistro')
    fecha_creacion_instrumento = models.DateTimeField(db_column='T607fechaCreacionInstrumento')
    fecha_fin_vigencia = models.DateField(blank=True, null=True, db_column='T607fechaFinVigencia')
    id_pozo = models.ForeignKey('Pozos', null=True,on_delete=models.CASCADE, db_column='T607Id_Pozo')
    cod_tipo_agua = models.CharField(max_length=3, choices=[
        ('SUP', 'Superficial'),
        ('SUB', 'Subterránea'),
        ('OTR', 'Otros')
    ], db_column='T607codTipoAgua')
    
    class Meta:
        db_table = 'T607Instrumentos'
        verbose_name = 'instrumento'
        verbose_name_plural='instrumentos'
        unique_together = ('nombre', 'id_subseccion',)

#'Administración de Instrumentos de Biblioteca'

class Cuencas(models.Model):
    id_cuenca = models.AutoField(primary_key=True, db_column='T608IdCuenca')
    nombre = models.CharField(max_length=255, db_column='T608nombre')
    activo = models.BooleanField(db_column='T608activo')
    item_ya_usado = models.BooleanField(db_column='T608itemYaUsado')
    registro_precargado=models.BooleanField(default=False, db_column='T608registroPrecargado')
    class Meta:
        db_table = 'T608Cuencas'
        verbose_name = 'cuenca'
        verbose_name_plural = 'cuencas'
        unique_together = ['nombre']


class Pozos(models.Model):
    id_pozo = models.AutoField(primary_key=True, db_column='T609IdPozo')
    cod_pozo = models.CharField(max_length=10, db_column='T609codPozo')
    nombre = models.CharField(max_length=255, db_column='T609nombre')
    descripcion = models.CharField(max_length=255, db_column='T609descripcion')
    activo = models.BooleanField(db_column='T609activo')
    item_ya_usado = models.BooleanField(db_column='T609itemYaUsado')
    registro_precargado=models.BooleanField(default=False, db_column='T609registroPrecargado')
    class Meta:
        db_table = 'T609Pozos'
        verbose_name = 'pozo'
        verbose_name_plural = 'pozos'
        unique_together = ( 'cod_pozo',)

class CuencasInstrumento(models.Model):
    id_cuenca_instrumento = models.AutoField(primary_key=True, db_column='T610IdCuenca_Instrumento')
    id_instrumento = models.ForeignKey(Instrumentos, on_delete=models.CASCADE, db_column='T610Id_Instrumento')
    id_cuenca = models.ForeignKey(Cuencas, on_delete=models.CASCADE, db_column='T610Id_Cuenca')

    class Meta:
        db_table = 'T610Cuencas_Instrumento'
        verbose_name = 'cuencas instrumento'
        verbose_name_plural = 'cuencas instrumento'
        unique_together = ('id_instrumento', 'id_cuenca',)





class CarteraAforos(models.Model):
    id_cartera_aforos = models.AutoField(primary_key=True, db_column='T612IdCarteraAforos')
    id_instrumento = models.ForeignKey(Instrumentos, on_delete=models.CASCADE, db_column='T612Id_Instrumento')
    id_cuenca = models.ForeignKey(Cuencas, on_delete=models.CASCADE, db_column='T612Id_Cuenca')
    fecha_registro = models.DateField(auto_now=True,db_column='T612fechaRegistro')
    ubicacion_aforo = models.CharField(max_length=255, db_column='T612ubicacionAforo')
    descripcion = models.CharField(max_length=255, blank=True, db_column='T612descripcion')
    #coordenadas = models.CharField(db_column='T612coordenadas')
    
    latitud = models.DecimalField(
        max_digits=18, decimal_places=13, db_column='T612latitud')
    longitud = models.DecimalField(
        max_digits=18, decimal_places=13, db_column='T612longitud')

    fecha_aforo = models.DateTimeField(db_column='T612fechaAforo')
    cod_tipo_aforo = models.CharField(max_length=2, choices=[
        ('VD', 'Vadea'),
        ('SP', 'Suspensión'),
        ('AG', 'Angular')
    ], db_column='T612codTipoAforo')
    molinete=models.CharField(max_length=30,db_column='T612molinete',default='')
    numero_serie = models.CharField(max_length=30, db_column='T612numeroSerie')
    numero_helice = models.CharField(max_length=30, db_column='T612numeroHelice')

    class Meta:
        db_table = 'T612CarteraAforos'
        verbose_name = 'cartera de aforos'
        verbose_name_plural = 'carteras de aforos'


class DatosCarteraAforos(models.Model):
    id_dato_cartera_aforos = models.AutoField(primary_key=True, db_column='T613IdDato_CarteraAforos')
    id_cartera_aforos = models.ForeignKey(CarteraAforos, on_delete=models.CASCADE, db_column='T613Id_CarteraAforos')
    distancia_a_la_orilla = models.DecimalField(max_digits=10, decimal_places=2, db_column='T613distanciaALaOrilla')
    profundidad = models.DecimalField(max_digits=10, decimal_places=2, db_column='T613profundidad')
    velocidad_superficial = models.DecimalField(max_digits=10, decimal_places=2, db_column='T613velocidadSuperficial')
    velocidad_profunda = models.DecimalField(max_digits=10, decimal_places=2, db_column='T613velocidadProfunda')
    transecto = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_column='T613transecto')
    profundidad_promedio = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_column='T613profundidadPromedio')
    velocidad_promedio = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_column='T613velocidadPromedio')
    velocidad_transecto = models.DecimalField(max_digits=10, decimal_places=2, db_column='T613velocidadTransecto')
    caudal = models.DecimalField(max_digits=10, decimal_places=2, db_column='T613caudal')

    class Meta:
        db_table = 'T613Datos_CarteraAforos'
        verbose_name = 'datos cartera de aforos'
        verbose_name_plural = 'datos cartera de aforos'


class PruebasBombeo(models.Model):
    id_prueba_bombeo = models.AutoField(primary_key=True, db_column='T614IdPruebaBombeo')
    id_instrumento = models.ForeignKey(Instrumentos, on_delete=models.CASCADE, db_column='T614Id_Instrumento')
    id_pozo = models.ForeignKey(Pozos, on_delete=models.CASCADE, db_column='T614Id_Pozo')
    descripcion = models.CharField(max_length=255, blank=True, db_column='T614descripcion')
    fecha_registro = models.DateTimeField(auto_now_add=True,db_column='T614fechaRegistro')
    fecha_prueba_bombeo = models.DateField(db_column='T614fechaPruebaBombeo')
    #coordenadas = models.PointField(db_column='T614coordenadas')
    
    latitud = models.DecimalField(
        max_digits=18, decimal_places=13, db_column='T614latitud')
    longitud = models.DecimalField(
        max_digits=18, decimal_places=13, db_column='T614longitud')

    ubicacion_prueba = models.CharField(max_length=255, db_column='T614ubicacionPrueba')

    class Meta:
        db_table = 'T614PruebasBombeo'
        verbose_name = 'prueba de bombeo'
        verbose_name_plural = 'pruebas de bombeo'


class SesionesPruebaBombeo(models.Model):
    id_sesion_prueba_bombeo = models.AutoField(primary_key=True, db_column='T615IdSesion_PruebaBombeo')
    id_prueba_bombeo = models.ForeignKey(PruebasBombeo, on_delete=models.CASCADE, db_column='T615Id_PruebaBombeo')
    consecutivo_sesion = models.SmallIntegerField(db_column='T615consecutivoSesion')
    fecha_inicio = models.DateTimeField(db_column='T615fechaInicio')
    cod_tipo_sesion = models.CharField(max_length=5, choices=[
        ('ACC', 'Abatimiento a Caudal Constante'),
        ('ACE', 'Abatimiento a Caudal Escalonado'),
        ('RCE', 'Recuperación a Caudal Escalonado'),
        ('RCC', 'Recuperación a Caudal Constante'),
    ], db_column='T615codTipoSesion')

    class Meta:
        db_table = 'T615Sesiones_PruebaBombeo'
        verbose_name = 'sesión de prueba de bombeo'
        verbose_name_plural = 'sesiones de prueba de bombeo'
        unique_together = ('id_prueba_bombeo','consecutivo_sesion', 'cod_tipo_sesion',)


class DatosSesionPruebaBombeo(models.Model):
    id_dato_sesion_prueba_bombeo = models.AutoField(primary_key=True, db_column='T616IdDato_Sesion_PruebaBombeo')
    id_sesion_prueba_bombeo = models.ForeignKey(SesionesPruebaBombeo, on_delete=models.CASCADE, db_column='T616Id_Sesion_PruebaBombeo')
    tiempo_transcurrido = models.DecimalField(max_digits=10, decimal_places=2, db_column='T616tiempoTranscurrido')
    hora = models.TimeField(db_column='T616hora')
    nivel = models.DecimalField(max_digits=10, decimal_places=2, db_column='T616nivel')
    resultado = models.DecimalField(max_digits=10, decimal_places=2, db_column='T616resultado')
    caudal = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_column='T616caudal')

    class Meta:
        db_table = 'T616Datos_Sesion_PruebaBombeo'
        verbose_name = 'datos de sesión de prueba de bombeo'
        verbose_name_plural = 'datos de sesiones de prueba de bombeo'


class ResultadosLaboratorio(models.Model):
    id_resultado_laboratorio = models.AutoField(primary_key=True, db_column='T617IdResultadoLaboratorio')
    id_instrumento = models.ForeignKey(Instrumentos, on_delete=models.CASCADE, db_column='T617Id_Instrumento')
    id_cuenca = models.ForeignKey(Cuencas, null=True, blank=True, on_delete=models.CASCADE, db_column='T617Id_Cuenca')
    id_pozo = models.ForeignKey(Pozos, null=True, blank=True, on_delete=models.CASCADE, db_column='T617Id_Pozo')
    descripcion = models.CharField(max_length=255, blank=True, db_column='T617descripcion')
    lugar_muestra = models.CharField(max_length=255, db_column='T617lugarMuestra')
    cod_clase_muestra = models.CharField(max_length=3, choices=[
        ('SUB', 'Subterránea'),
        ('SUP', 'Superficial'),
    ], db_column='T617codClaseDeMuestra')
    fecha_registro = models.DateTimeField(auto_now=True,db_column='T617fechaRegistro')
    fecha_toma_muestra = models.DateField(db_column='T617fechaTomaMuestra')
    fecha_resultados_lab = models.DateField(db_column='T617fechaResultadosLab')
    fecha_envio_lab = models.DateField(db_column='T617fechaEnvioALab')
    #coordenadas = models.PointField(db_column='T617coordenadas')

    latitud = models.DecimalField(
        max_digits=18, decimal_places=13, db_column='T617latitud')
    longitud = models.DecimalField(
        max_digits=18, decimal_places=13, db_column='T617longitud')

    class Meta:
        db_table = 'T617ResultadosLaboratorio'
        verbose_name = 'resultado de laboratorio'
        verbose_name_plural = 'resultados de laboratorio'


class ParametrosLaboratorio(models.Model):
    id_parametro = models.AutoField(primary_key=True, db_column='T619IdParametro')
    cod_tipo_parametro = models.CharField(max_length=2, choices=[
        ('FQ', 'Fisicoquímico'),
        ('MB', 'Microbiológico'),
    ], db_column='T619codTipoParametro')
    nombre = models.CharField(max_length=255, db_column='T619nombre')
    unidad_de_medida = models.CharField(max_length=100, db_column='T619unidadDeMedida')
    item_ya_usado = models.BooleanField(db_column='T619itemYaUsado')
    activo = models.BooleanField(db_column='T619activo')
    registro_precargado=models.BooleanField(default=False, db_column='T619registroPrecargado')
    class Meta:
        db_table = 'T619Parametros_Laboratorio'
        verbose_name = 'parámetro de laboratorio'
        verbose_name_plural = 'parámetros de laboratorio'

class DatosRegistroLaboratorio(models.Model):
    id_dato_registro_laboratorio = models.AutoField(primary_key=True, db_column='T618IdDato_RegistroLaboratorio')
    id_registro_laboratorio = models.ForeignKey(ResultadosLaboratorio, on_delete=models.CASCADE, db_column='T618Id_RegistroLaboratorio')
    id_parametro = models.ForeignKey(ParametrosLaboratorio, on_delete=models.CASCADE, db_column='T618Id_Parametro')
    metodo = models.CharField(max_length=50, db_column='T618metodo')
    resultado = models.CharField(max_length=30, db_column='T618resultado')
    fecha_analisis = models.DateField(db_column='T618fechaAnalisis')

    class Meta:
        db_table = 'T618Datos_RegistroLaboratorio'
        verbose_name = 'datos de registro de laboratorio'
        verbose_name_plural = 'datos de registros de laboratorio'

class ArchivosInstrumento(models.Model):
    id_archivo_instrumento = models.AutoField(primary_key=True, db_column='T611IdArchivo_Instrumento')
    id_instrumento = models.ForeignKey(Instrumentos, on_delete=models.CASCADE, db_column='T611Id_Instrumento')
    cod_tipo_de_archivo = models.CharField(max_length=3, choices=[
        ('CDA', 'Cartera de Aforo'),
        ('LAB', 'Registro de Laboratorio'),
        ('PDB', 'Prueba de Bombeo'),
        ('INS', 'Instrumento')
    ], db_column='T611codTipoDeArchivo')
    nombre_archivo = models.CharField(max_length=255, db_column='T611nombreArchivo')
    ruta_archivo = models.FileField( db_column='T611rutaArchivo')
    fecha_cargado = models.DateField(auto_now=True,db_column='T611fechaCargado')
    id_cartera_aforo = models.ForeignKey(CarteraAforos, null=True, blank=True, on_delete=models.CASCADE, db_column='T611Id_CarteraAforo')
    id_prueba_bombeo = models.ForeignKey(PruebasBombeo, null=True, blank=True, on_delete=models.CASCADE, db_column='T611Id_PruebaBombeo')
    id_resultado_laboratorio = models.ForeignKey(ResultadosLaboratorio, null=True, blank=True, on_delete=models.CASCADE, db_column='T611Id_ResultadoLaboratorio')
    class Meta:
        db_table = 'T611Archivos_Instrumento'
        verbose_name = 'archivo instrumento'
        verbose_name_plural = 'archivos instrumento'
        unique_together = ('id_instrumento', 'nombre_archivo',)