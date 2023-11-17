from django.db import models
from seguimiento_planes.models.planes_models import ObjetivoDesarrolloSostenible, Planes, EjeEstractegico, Objetivo, Programa, Proyecto, Productos, Actividad, Entidad, Medicion, Tipo, Rubro, Indicador, Metas, TipoEje, Subprograma
from recurso_hidrico.models.bibliotecas_models import Cuencas

class FuenteFinanciacionIndicadores(models.Model):
    id_fuente = models.AutoField(primary_key=True, editable=False, db_column='T516IdFuente')
    nombre_fuente = models.CharField(max_length=100, db_column='T516nombreFuente')
    vano_1 = models.BigIntegerField(null=True, blank=True, db_column='T516vano1')
    vano_2 = models.BigIntegerField(null=True, blank=True, db_column='T516vano2')
    vano_3 = models.BigIntegerField(null=True, blank=True, db_column='T516vano3')
    vano_4 = models.BigIntegerField(null=True, blank=True, db_column='T516vano4')
    valor_total = models.BigIntegerField(null=True, blank=True, db_column='T516valorTotal')
    id_indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, db_column='T516IdIndicador')
    id_cuenca = models.ForeignKey(Cuencas, on_delete=models.CASCADE, db_column='T516IdCuenca')

    def __str__(self):
        return str(self.nombre_fuente)
    
    class Meta: 
        db_table = 'T516FuentesFinanciacionIndicadores'
        verbose_name = 'Fuentes de Financiación Indicadores'
        verbose_name_plural = 'Fuentes de Financiación Indicadores'

class Sector(models.Model):
    id_sector = models.AutoField(primary_key=True, editable=False, db_column='T517IdSector')
    nombre_sector = models.CharField(max_length=100, db_column='T517nombreSector')
    aplicacion = models.CharField(max_length=100, db_column='T517aplicacion')
    activo = models.BooleanField(default=True, db_column='T517activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T517itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T517registroPrecargado')

    def __str__(self):
        return str(self.id_sector)

    class Meta:
        db_table = 'T517Sector'
        verbose_name = 'Sector'
        verbose_name_plural = 'Sectores'

class DetalleInversionCuentas(models.Model):
    id_detalle_inversion = models.AutoField(primary_key=True, editable=False, db_column='T518IdDetalleInversion')
    cuenta = models.CharField(max_length=100, db_column='T518cuenta')
    valor_cuenta = models.IntegerField(null=True, blank=True, db_column='T518valorCuenta')
    id_sector = models.ForeignKey(Sector, on_delete=models.CASCADE, db_column='T518IdSector')
    id_rubro = models.ForeignKey(Rubro, on_delete=models.CASCADE, db_column='T518IdRubro')
    id_programa = models.ForeignKey(Programa, on_delete=models.CASCADE, db_column='T518IdPrograma')
    id_subprograma = models.ForeignKey(Subprograma, on_delete=models.CASCADE, db_column='T518IdSubprograma')
    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, db_column='T518IdProyecto')
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE, db_column='T518IdProducto')
    id_actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, db_column='T518IdActividad')

    def __str__(self):
        return str(self.cuenta)

    class Meta:
        db_table = 'T518DetalleInversionCuentas'
        verbose_name = 'Detalle de Inversión Cuentas'
        verbose_name_plural = 'Detalle de Inversión Cuentas'

class Modalidad(models.Model): # Tabla básica
    id_modalidad = models.AutoField(primary_key=True, editable=False, db_column='T519IdModalidad')
    nombre_modalidad = models.CharField(max_length=100, db_column='T519nombreModalidad')
    codigo_modalidad = models.CharField(max_length=100, db_column='T519codigoModalidad')
    activo = models.BooleanField(default=True, db_column='T519activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T519itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T519registroPrecargado')

    def __str__(self):
        return str(self.nombre_modalidad)

    class Meta:
        db_table = 'T519Modalidad'
        verbose_name = 'Modalidad'
        verbose_name_plural = 'Modalidades'

class Ubicaciones(models.Model):
    id_ubicacion = models.AutoField(primary_key=True, editable=False, db_column='T520IdUbicacion')
    nombre_ubicacion = models.CharField(max_length=100, db_column='T520nombreUbicacion')
    codigo_ubicacion = models.CharField(max_length=100, db_column='T520codigoUbicacion')
    activo = models.BooleanField(default=True, db_column='T520activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T520itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T520registroPrecargado')

    def __str__(self):
        return str(self.nombre_ubicacion)

    class Meta:
        db_table = 'T520Ubicaciones'
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'

class FuenteRecursosPaa(models.Model):
    id_fuente = models.AutoField(primary_key=True, editable=False, db_column='T521IdFuente')
    nombre_fuente = models.CharField(max_length=100, db_column='T521nombreFuente')
    activo = models.BooleanField(default=True, db_column='T521activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T521itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T521registroPrecargado')

    def __str__(self):
        return str(self.nombre_fuente)

    class Meta:
        db_table = 'T521FuenteRecursosPaa'
        verbose_name = 'Fuente de Recursos PAA'
        verbose_name_plural = 'Fuentes de Recursos PAA'

class Intervalo(models.Model):
    id_intervalo = models.AutoField(primary_key=True, editable=False, db_column='T522IdIntervalo')
    nombre_intervalo = models.CharField(max_length=100, db_column='T522nombreIntervalo')
    activo = models.BooleanField(default=True, db_column='T522activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T522itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T522registroPrecargado')

    def __str__(self):
        return str(self.nombre_intervalo)

    class Meta:
        db_table = 'T522Intervalo'
        verbose_name = 'Intervalo'
        verbose_name_plural = 'Intervalos'
    
class EstadoVF(models.Model):
    id_estado = models.AutoField(primary_key=True, editable=False, db_column='T523IdEstado')
    nombre_estado = models.CharField(max_length=100, db_column='T523nombreEstado')
    activo = models.BooleanField(default=True, db_column='T523activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T523itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T523registroPrecargado')

    def __str__(self):
        return str(self.nombre_estado)

    class Meta:
        db_table = 'T523EstadoVF'
        verbose_name = 'Estado VF'
        verbose_name_plural = 'Estados VF'

class CodigosUNSP(models.Model):
    id_codigo = models.AutoField(primary_key=True, editable=False, db_column='T524IdCodigo')
    codigo_unsp = models.CharField(max_length=100, db_column='T524codigoUNSP')
    nombre_producto_unsp = models.CharField(max_length=255, db_column='T524nombreProductoUNSP')
    activo = models.BooleanField(default=True, db_column='T524activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T524itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T524registroPrecargado')

    def __str__(self):
        return str(self.id_codigo)

    class Meta:
        db_table = 'T524CodigosUNSP'
        verbose_name = 'Código UNSP'
        verbose_name_plural = 'Códigos UNSP'