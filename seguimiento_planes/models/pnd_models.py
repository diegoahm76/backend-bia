from django.db import models

# Create your models here.
class PlanNacionalDesarrollo(models.Model):
    id_plan = models.AutoField(
        primary_key=True, editable=False, db_column='T506IdPlanNacionalDesarrollo')
    nombre_plan = models.CharField(
        max_length=30, db_column='T506nombrePlan')
    agno_inicio = models.IntegerField(
        null=True, blank=True, db_column='T506agnoInicio')
    agno_fin = models.IntegerField(
        null=True, blank=True, db_column='T506agnoFin')

    def __str__(self):
        return str(self.nombre_plan)

    class Meta:
        db_table = 'T506PlanNacionalDesarrolloNacional'
        verbose_name = 'Plan Nacional Desarrollo'
        verbose_name_plural = 'Planes Nacionales Desarrollos'

class Sector(models.Model):
    id_sector = models.AutoField(
        primary_key=True, editable=False, db_column='T507IdSector')
    nombre_sector = models.CharField(
        max_length=255, db_column='T507nombreSector')
    id_plan_desarrollo = models.ForeignKey(
        PlanNacionalDesarrollo, on_delete=models.CASCADE, db_column='T507IdPlanNacionalDesarrollo')

    def __str__(self):
        return str(self.id_sector)

    class Meta:
        db_table = 'T507Sector'
        verbose_name = 'Sector'
        verbose_name_plural = 'Sectores'
        
class Programa(models.Model):
    id_programa = models.AutoField(
        primary_key=True, editable=False, db_column='T508IdPrograma')
    cod_programa = models.CharField(
        max_length=30, db_column='T508codPrograma')
    nombre_programa = models.CharField(
        max_length=255, db_column='T508nombrePrograma')
    id_sector = models.ForeignKey(
        Sector, on_delete=models.CASCADE, db_column='T508IdSector')

    def __str__(self):
        return str(self.id_programa)

    class Meta:
        db_table = 'T508Programa'
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'

class Producto(models.Model):
    id_producto = models.AutoField(
        primary_key=True, editable=False, db_column='T509IdProducto')
    cod_producto = models.CharField(
        max_length=30, db_column='T509codProducto')
    nombre_producto = models.CharField(
        max_length=255, db_column='T509nombreProducto')
    descripcion_producto = models.CharField(
        max_length=255, db_column='T509descripcionProducto')
    medida_producto = models.CharField(
        max_length=255, db_column='T509medidaProducto')
    id_sector = models.ForeignKey(
        Programa, on_delete=models.CASCADE, db_column='T509IdPrograma')

    def __str__(self):
        return str(self.id_producto)

    class Meta:
        db_table = 'T509Producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

class PndIndicador(models.Model):
    id_indicador = models.AutoField(
        primary_key=True, editable=False, db_column='T510IdIndicador')
    cod_indicador = models.CharField(
        max_length=30, db_column='T510codIndicador')
    nombre_indicador = models.CharField(
        max_length=255, db_column='T510nombreIndicador')
    descripcion_indicador = models.CharField(
        max_length=255, db_column='T510descripcionIndicador')
    cod_unidad_medida = models.CharField(max_length=3, choices=[
        ('NUM', 'Numero'),
        ('POR', 'Porcentaje'),
    ], db_column='T510codUnidadMedida')
    nacional = models.BooleanField(default=False, db_column='T510nacional')
    territorial = models.BooleanField(default=False, db_column='T510territorial')
    tipologia_general = models.BooleanField(default=False, db_column='T510tipologiaGeneral')
    tipo_a = models.BooleanField(default=False, db_column='T510tipoA')
    tipo_b = models.BooleanField(default=False, db_column='T510tipoB')
    tipo_c = models.BooleanField(default=False, db_column='T510tipoC')
    id_producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, db_column='T510IdProducto')

    def __str__(self):
        return str(self.id_indicador)

    class Meta:
        db_table = 'T510Indicador'
        verbose_name = 'Indicador'
        verbose_name_plural = 'Indicadores'