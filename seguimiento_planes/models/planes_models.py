from django.db import models

# Create your models here.
class ObjetivoDesarrolloSostenible(models.Model):
    id_objetivo = models.AutoField(
        primary_key=True, editable=False, db_column='T500IdObjetivo')
    nombre_objetivo = models.CharField(
        max_length=30, db_column='T500nombreObjetivo')
    activo = models.BooleanField(default=True, db_column='T500activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T500itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T500registroPrecargado')

    def __str__(self):
        return str(self.id_objetivo)

    class Meta:
        db_table = 'T500ObjetivoDesarrolloSostenible'
        verbose_name = 'Objetivo Desarrollo Sostenible'
        verbose_name_plural = 'Objetivos Desarrollo Sostenible'

class Planes(models.Model):
    id_plan = models.AutoField(
        primary_key=True, editable=False, db_column='T501IdPlanes')
    nombre_plan = models.CharField(
        max_length=30, db_column='T501nombrePlan')
    sigla_plan = models.CharField(
        max_length=30, db_column='T501siglaPlan')
    tipo_plan = models.CharField(
        max_length=3, choices=[
            ('PND', 'Plan Nacional Desarrollo'),
            ('PAI', 'Plan Accion Institucional'),
            ('PGR', 'Plan Gestion Ambiental Regional'),
        ], db_column='T501tipoPlan')
    agno_inicio = models.IntegerField(
        null=True, blank=True, db_column='T501agnoInicio')
    agno_fin = models.IntegerField(
        null=True, blank=True, db_column='T501agnoFin')
    estado_vigencia = models.BooleanField(default=True, db_column='T501estadoVigencia')

    def __str__(self):
        return str(self.nombre_plan)

    class Meta:
        db_table = 'T501PlanesNacional'
        verbose_name = 'Plan Nacional Desarrollo'
        verbose_name_plural = 'Planes Nacionales Desarrollos'

class EjeEstractegico(models.Model):
    id_eje_estrategico = models.AutoField(
        primary_key=True, editable=False, db_column='T502IdEjeEstrategico')
    nombre = models.CharField(
        max_length=255, db_column='T502nombreEjeEstrategico')
    tipo_eje = models.CharField(
        max_length=30, db_column='T502tipoEje')
    id_plan = models.ForeignKey(
        Planes, on_delete=models.CASCADE, db_column='T502IdPlanes')

    def __str__(self):
        return str(self.id_eje_estrategico)

    class Meta:
        db_table = 'T502EjeEstrategico'
        verbose_name = 'Eje Estrategico'
        verbose_name_plural = 'Ejes Estrategicos'

class Objetivo(models.Model):
    id_objetivo = models.AutoField(
        primary_key=True, editable=False, db_column='T503IdObjetivo')
    nombre_objetivo = models.CharField(
        max_length=255, db_column='T503descripcionObjetivo')
    id_plan = models.ForeignKey(
        Planes, on_delete=models.CASCADE, db_column='T503IdPlanes')    
    
    def __str__(self):
        return str(self.id_objetivo)

    class Meta:
        db_table = 'T503Objetivo'
        verbose_name = 'Objetivo'
        verbose_name_plural = 'Objetivos'

class Programa(models.Model):
    id_programa = models.AutoField(
        primary_key=True, editable=False, db_column='T504IdPrograma')
    nombre_programa = models.CharField(
        max_length=255, db_column='T504nombrePrograma')
    porcentaje_1 = models.IntegerField(
        null=True, blank=True, db_column='T504porcentaje1')
    porcentaje_2 = models.IntegerField(
        null=True, blank=True, db_column='T504porcentaje2')
    porcentaje_3 = models.IntegerField(
        null=True, blank=True, db_column='T504porcentaje3')
    porcentaje_4 = models.IntegerField(
        null=True, blank=True, db_column='T504porcentaje4')
    id_plan = models.ForeignKey(
        Planes, on_delete=models.CASCADE, db_column='T504IdPlanes')

    def __str__(self):
        return str(self.id_programa)

    class Meta:
        db_table = 'T504Programa'
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'

class Proyecto(models.Model):
    id_proyecto = models.AutoField(
        primary_key=True, editable=False, db_column='T505IdProyecto')
    nombre_proyecto = models.CharField(
        max_length=255, db_column='T505nombreProyecto')
    pondera_1 = models.IntegerField(
        null=True, blank=True, db_column='T505pondera1')
    pondera_2 = models.IntegerField(
        null=True, blank=True, db_column='T505pondera2')
    pondera_3 = models.IntegerField(
        null=True, blank=True, db_column='T505pondera3')
    pondera_4 = models.IntegerField(
        null=True, blank=True, db_column='T505pondera4')
    id_programa = models.ForeignKey(
        Programa, on_delete=models.CASCADE, db_column='T505IdPrograma')

    def __str__(self):
        return str(self.id_proyecto)

    class Meta:
        db_table = 'T505Proyecto'
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

class Productos(models.Model):
    id_producto = models.AutoField(
        primary_key=True, editable=False, db_column='T506IdProducto')
    nombre_producto = models.CharField(
        max_length=255, db_column='T506nombreProducto')
    id_proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, db_column='T506IdProyecto')

    def __str__(self):
        return str(self.id_producto)

    class Meta:
        db_table = 'T506Producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

class Actividad(models.Model):
    id_actividad = models.AutoField(
        primary_key=True, editable=False, db_column='T507IdActividad')
    nombre_actividad = models.CharField(
        max_length=255, db_column='T507nombreActividad')
    id_producto = models.ForeignKey(
        Productos, on_delete=models.CASCADE, db_column='T507IdProducto')
    id_plan = models.ForeignKey(
        Planes, on_delete=models.CASCADE, db_column='T507IdPlanes')

    def __str__(self):
        return str(self.id_actividad)

    class Meta:
        db_table = 'T507Actividad'
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

class Entidad(models.Model):
    id_entidad = models.AutoField(
        primary_key=True, editable=False, db_column='T508IdEntidad')
    nombre_entidad = models.CharField(
        max_length=255, db_column='T508nombreEntidad')
    activo = models.BooleanField(default=True, db_column='T508activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T508itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T508registroPrecargado')

    def __str__(self):
        return str(self.id_entidad)
    
    class Meta:
        db_table = 'T508Entidad'
        verbose_name = 'Entidad'
        verbose_name_plural = 'Entidades'

class Medicion(models.Model):
    id_medicion = models.AutoField(
        primary_key=True, editable=False, db_column='T509IdMedicion')
    nombre_medicion = models.CharField(
        max_length=255, db_column='T509nombreMedicion')
    activo = models.BooleanField(default=True, db_column='T509activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T509itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T509registroPrecargado')
    

    def __str__(self):
        return str(self.id_medicion)

    class Meta:
        db_table = 'T509Medicion'
        verbose_name = 'Medicion'
        verbose_name_plural = 'Mediciones'

class Tipo(models.Model):
    id_tipo = models.AutoField(
        primary_key=True, editable=False, db_column='T510IdTipo')
    nombre_tipo = models.CharField(
        max_length=255, db_column='T510nombreTipo')
    activo = models.BooleanField(default=True, db_column='T510activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T510itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T510registroPrecargado')
    

    def __str__(self):
        return str(self.id_tipo)

    class Meta:
        db_table = 'T510Tipo'
        verbose_name = 'Tipo'
        verbose_name_plural = 'Tipos'

class Rublo(models.Model):
    id_rublo = models.AutoField(
        primary_key=True, editable=False, db_column='T511IdRublo')
    cod_pre = models.CharField(
        max_length=255, db_column='T511codPre')
    cuenta = models.CharField(
        max_length=255, db_column='T511cuenta')
    valcuenta = models.CharField(
        max_length=255, db_column='T511valcuenta')        

    def __str__(self):
        return str(self.id_rublo)

    class Meta:
        db_table = 'T511Rublo'
        verbose_name = 'Rublo'
        verbose_name_plural = 'Rublos'

class Indicador(models.Model):
    id_indicador = models.AutoField(
        primary_key=True, editable=False, db_column='T512IdIndicador')
    nombre_indicador = models.CharField(
        max_length=255, db_column='T512nombreIndicador')
    linea_base = models.CharField(
        max_length=255, db_column='T512lineaBase')
    medida = models.CharField(
        max_length=3, choices=[
            ('NUM', 'Numero'),
            ('POR', 'Porcentaje'),
        ], db_column='T512medida')
    id_medicion = models.ForeignKey(
        Medicion, on_delete=models.CASCADE, db_column='T512IdMedicion')
    id_tipo = models.ForeignKey(
        Tipo, on_delete=models.CASCADE, db_column='T512IdTipo')
    id_rublo = models.ForeignKey(
        Rublo, on_delete=models.CASCADE, db_column='T512IdRublo')
    id_actividad = models.ForeignKey(
        Actividad, on_delete=models.CASCADE, db_column='T512IdActividad')
    id_plan = models.ForeignKey(
        Planes, on_delete=models.CASCADE, db_column='T512IdPlanes')

    def __str__(self):
        return str(self.id_indicador)

    class Meta:
        db_table = 'T512Indicador'
        verbose_name = 'Indicador'
        verbose_name_plural = 'Indicadores'

class Metas(models.Model):
    id_meta = models.AutoField(
        primary_key=True, editable=False, db_column='T513IdMeta')
    nombre_meta = models.CharField(
        max_length=255, db_column='T513nombreMeta')
    unidad_meta = models.CharField(
        max_length=3, choices=[
            ('NUM', 'Numero'),
            ('POR', 'Porcentaje'),
        ], db_column='T513unidadMeta')
    porcentaje_meta = models.IntegerField(
        null=True, blank=True, db_column='T513porcentajeMeta')
    valor_meta = models.CharField(
        max_length=255, db_column='T513valorMeta')
    id_indicador = models.ForeignKey(
        Indicador, on_delete=models.CASCADE, db_column='T513IdIndicador')

    def __str__(self):
        return str(self.id_meta)

    class Meta:
        db_table = 'T513Meta'
        verbose_name = 'Meta'
        verbose_name_plural = 'Metas'