from django.db import models

# Create your models here.
class PlanGestionAmbientalRegional(models.Model):
    id_plan = models.AutoField(
        primary_key=True, editable=False, db_column='T500IdPlanGestionAmbiental')
    nombre_plan = models.CharField(
        max_length=30, db_column='T500nombrePlan')
    agno_inicio = models.IntegerField(
        null=True, blank=True, db_column='T500agnoInicio')
    agno_fin = models.IntegerField(
        null=True, blank=True, db_column='T500agnoFin')

    def __str__(self):
        return str(self.nombre_plan)

    class Meta:
        db_table = 'T500PlanGestionAmbientalRegional'
        verbose_name = 'Plan Gestion Ambiental Regional'
        verbose_name_plural = 'Planes Gestiones Ambientales Regionales'

class Objetivo(models.Model):
    id_objetivo = models.AutoField(
        primary_key=True, editable=False, db_column='T501IdObjetivo')
    descripcion_objetivo = models.CharField(
        max_length=255, db_column='T501descripcionObjetivo')
    id_plan = models.ForeignKey(
        PlanGestionAmbientalRegional, on_delete=models.CASCADE, db_column='T501IdPlanGestionAmbiental')

    def __str__(self):
        return str(self.id_objetivo)

    class Meta:
        db_table = 'T501Objetivo'
        verbose_name = 'Objetivo'
        verbose_name_plural = 'Objetivos'

class LineaEstrategica(models.Model):
    id_linea_estrategica = models.AutoField(
        primary_key=True, editable=False, db_column='T502IdLineaEstrategica')
    descripcion_linea_estrategica = models.CharField(
        max_length=255, db_column='T502descripcionLineaEstrategica')
    id_obejtivo = models.ForeignKey(
        Objetivo, on_delete=models.CASCADE, db_column='T502IdObjetivo')

    def __str__(self):
        return str(self.id_linea_estrategica)

    class Meta:
        db_table = 'T502LineaEstrategica'
        verbose_name = 'Linea Estrategica'
        verbose_name_plural = 'Lineas Estrategicas'

class MetaEstrategica(models.Model):
    id_meta_estrategica = models.AutoField(
        primary_key=True, editable=False, db_column='T502IdMetaEstrategica')
    descripcion_meta_estrategica = models.CharField(
        max_length=255, db_column='T502descripcionMetaEstrategica')
    id_linea_estrategica = models.ForeignKey(
        LineaEstrategica, on_delete=models.CASCADE, db_column='T502IdLineaEstrategica')

    def __str__(self):
        return str(self.id_meta_estrategica)

    class Meta:
        db_table = 'T502MetaEstrategica'
        verbose_name = 'Meta Estrategica'
        verbose_name_plural = 'Metas Estrategicas'

class Entidades(models.Model):
    id_entidad = models.AutoField(primary_key=True, db_column='T505IdEntidad')
    nombre_entidad = models.CharField(max_length=255, db_column='T505nombreEntidad')
    descripcion_entidad = models.CharField(max_length=255, db_column='T505descripcionEntidad')
    item_ya_usado = models.BooleanField(default=False, db_column='T505itemYaUsado')
    activo = models.BooleanField(default=True, db_column='T505activo')
    
    class Meta:
        db_table = 'T505Entidades'
        verbose_name = 'Entidad'
        verbose_name_plural = 'Entidades'

class PgarIndicador(models.Model):
    id_indicador = models.AutoField(
        primary_key=True, editable=False, db_column='T503IdIndicador')
    descripcion_indicador = models.CharField(
        max_length=255, db_column='T503descripcionIndicador')
    cod_unidad_medida = models.CharField(max_length=3, choices=[
        ('NUM', 'Numero'),
        ('POR', 'Porcentaje'),
    ], db_column='T503codUnidadMedida')
    cod_tipo_indicador = models.CharField(max_length=3, choices=[
        ('IMP', 'Impacto'),
        ('RES', 'Resultado'),
        ('PRO', 'Producto'),
        ('GST', 'Gestion'),
    ], db_column='T503codTipoIndicador')
    
    responsable = models.CharField(
        max_length=200, db_column='T503responsable')
    id_entidad = models.ForeignKey(
        Entidades, on_delete=models.CASCADE, db_column='T503IdEntidad')

    
    def __str__(self):
        return str(self.id_indicador)

    class Meta:
        db_table = 'T503Indicador'
        verbose_name = 'Indicador'
        verbose_name_plural = 'Indicadores'
    
class Actividad(models.Model):
    id_actividad = models.AutoField(
        primary_key=True, editable=False, db_column='T504IdActividad')
    descripcion_linea_base = models.CharField(
        max_length=255, db_column='T504descripcionLineaBase')
    id_indicador = models.ForeignKey(
        PgarIndicador, on_delete=models.CASCADE, db_column='T504IdIndicador')
    id_meta_estrategica = models.ForeignKey(
        MetaEstrategica, on_delete=models.CASCADE, db_column='T504IdMetaEstrategica')

    def __str__(self):
        return str(self.id_actividad)

    class Meta:
        db_table = 'T504Actividad'
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'