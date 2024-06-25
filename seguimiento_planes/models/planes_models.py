from django.db import models

from transversal.models.organigrama_models import UnidadesOrganizacionales
# from seguimiento_planes.models.seguimiento_models import FuenteFinanciacionIndicadores 

# Create your models here.

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

class ObjetivoDesarrolloSostenible(models.Model):
    id_objetivo = models.AutoField(primary_key=True, editable=False, db_column='T500IdObjetivo')
    nombre_objetivo = models.CharField(max_length=400, db_column='T500nombreObjetivo')
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
    id_plan = models.AutoField(primary_key=True, editable=False, db_column='T501IdPlan')
    nombre_plan = models.CharField(max_length=255, db_column='T501nombrePlan')
    sigla_plan = models.CharField(max_length=30, db_column='T501siglaPlan')
    tipo_plan = models.CharField(max_length=3, choices=[
            ('PND', 'Plan Nacional Desarrollo'),
            ('PAI', 'Plan Accion Institucional'),
            ('PGR', 'Plan Gestion Ambiental Regional'),
            ('PES', 'Plan de desarrollo economico y social'),
            ('POA', 'Plan Operativo Anual de Inversiones'),
        ], db_column='T501tipoPlan')
    agno_inicio = models.IntegerField(null=True, blank=True, db_column='T501agnoInicio')
    agno_fin = models.IntegerField(null=True, blank=True, db_column='T501agnoFin')
    estado_vigencia = models.BooleanField(default=True, db_column='T501estadoVigencia')

    def __str__(self):
        return str(self.nombre_plan)

    class Meta:
        db_table = 'T501PlanesNacional'
        verbose_name = 'Plan Nacional Desarrollo'
        verbose_name_plural = 'Planes Nacionales Desarrollos'

class TipoEje(models.Model):
    id_tipo_eje = models.AutoField(primary_key=True, editable=False, db_column='T514IdTipoEje')
    nombre_tipo_eje = models.CharField(max_length=255, db_column='T514nombreTipoEje')
    activo = models.BooleanField(default=True, db_column='T514activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T514itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T514registroPrecargado')
    

    def __str__(self):
        return str(self.id_tipo_eje)

    class Meta:
        db_table = 'T514TipoEje'
        verbose_name = 'Tipo Eje'
        verbose_name_plural = 'Tipos Ejes'

class Objetivo(models.Model):
    id_objetivo = models.AutoField(
        primary_key=True, editable=False, db_column='T503IdObjetivo')
    nombre_objetivo = models.CharField(
        max_length=255, db_column='T503nombreObjetivo')
    id_plan = models.ForeignKey(
        Planes, on_delete=models.CASCADE, db_column='T503IdPlan')    
    
    def __str__(self):
        return str(self.id_objetivo)

    class Meta:
        db_table = 'T503Objetivo'
        verbose_name = 'Objetivo'
        verbose_name_plural = 'Objetivos'


class EjeEstractegico(models.Model):
    id_eje_estrategico = models.AutoField(
        primary_key=True, editable=False, db_column='T502IdEjeEstrategico')
    nombre = models.CharField(
        max_length=400, db_column='T502nombreEjeEstrategico')
    id_tipo_eje = models.ForeignKey(
        TipoEje, on_delete=models.CASCADE, db_column='T502IdTipoEje')
    id_plan = models.ForeignKey(
        Planes, on_delete=models.SET_NULL, null=True, blank=True, db_column='T502IdPlan')
    id_objetivo = models.ForeignKey(
        Objetivo, on_delete=models.SET_NULL, null=True, blank=True, db_column='T502IdObjetivo')

    def __str__(self):
        return str(self.id_eje_estrategico)

    class Meta:
        db_table = 'T502EjeEstrategico'
        verbose_name = 'Eje Estrategico'
        verbose_name_plural = 'Ejes Estrategicos'


class Programa(models.Model):
    id_programa = models.AutoField(
        primary_key=True, editable=False, db_column='T504IdPrograma')
    nombre_programa = models.CharField(
        max_length=255, db_column='T504nombrePrograma')
    numero_programa = models.CharField(
        max_length=255, db_column='T504numeroPrograma')
    porcentaje_1 = models.IntegerField(
        null=True, blank=True, db_column='T504porcentaje1')
    porcentaje_2 = models.IntegerField(
        null=True, blank=True, db_column='T504porcentaje2')
    porcentaje_3 = models.IntegerField(
        null=True, blank=True, db_column='T504porcentaje3')
    porcentaje_4 = models.IntegerField(
        null=True, blank=True, db_column='T504porcentaje4')
    id_eje_estrategico = models.ForeignKey(
        EjeEstractegico, on_delete=models.CASCADE, db_column='T504IdEjeEstrategico')
    cumplio = models.BooleanField(default=False, db_column='T504cumplio')
    fecha_creacion = models.DateField(
        null=True, blank=True, db_column='T504fechaCreacion')
    id_sector = models.ForeignKey(
        Sector, on_delete=models.CASCADE, db_column='T504IdSector')

    def __str__(self):
        return str(self.id_programa)

    class Meta:
        db_table = 'T504Programa'
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'



class Proyecto(models.Model):
    id_proyecto = models.AutoField(
        primary_key=True, editable=False, db_column='T505IdProyecto')
    numero_proyecto = models.CharField(
        max_length=255, db_column='T505numeroProyecto')
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
    id_plan = models.ForeignKey(
        Planes, on_delete=models.CASCADE, db_column='T505IdPlan')
    cumplio = models.BooleanField(default=False, db_column='T505cumplio')
    fecha_creacion = models.DateField(
        null=True, blank=True, db_column='T505fechaCreacion')

    def __str__(self):
        return str(self.id_proyecto)

    class Meta:
        db_table = 'T505Proyecto'
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

class Productos(models.Model):
    id_producto = models.AutoField(
        primary_key=True, editable=False, db_column='T506IdProducto')
    numero_producto = models.CharField(
        max_length=255, db_column='T506numeroProducto')
    nombre_producto = models.CharField(
        max_length=255, db_column='T506nombreProducto')
    id_proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, db_column='T506IdProyecto')
    id_plan = models.ForeignKey(
        Planes, on_delete=models.CASCADE, db_column='T506IdPlan')
    id_programa = models.ForeignKey(
        Programa, on_delete=models.CASCADE, db_column='T506IdPrograma')
    fecha_creacion = models.DateField(null=True, blank=True, db_column='T506fechaCreacion')    
    cumplio = models.BooleanField(default=False, db_column='T506cumplio')

    def __str__(self):
        return str(self.id_producto)

    class Meta:
        db_table = 'T506Producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'


class MetasEjePGAR(models.Model):
    id_meta_eje = models.AutoField(primary_key=True, editable=False, db_column='T534IdMetaEje')
    numero_meta_eje = models.CharField(max_length=255, db_column='T534numeroMetaEje')
    nombre_meta_eje = models.CharField(max_length=255, db_column='T534nombreMetaEje')
    id_eje_estrategico = models.ForeignKey(EjeEstractegico, on_delete=models.CASCADE, db_column='T534IdEjeEstrategico')
    id_objetivo = models.ForeignKey(Objetivo, on_delete=models.SET_NULL, null=True, blank=True, db_column='T534IdObjetivo')
    id_plan = models.ForeignKey(Planes, on_delete=models.SET_NULL, null=True, blank=True, db_column='T534IdPlan')
    cumplio = models.BooleanField(default=False, db_column='T534cumplio')
    fecha_creacion = models.DateField(db_column='T534fechaCreacion')

    class Meta:
        db_table = 'T534MetasEjePGAR'
        verbose_name = 'Meta Eje'
        verbose_name_plural = 'Metas Ejes'

class LineasBasePGAR(models.Model):
    id_linea_base = models.AutoField(primary_key=True, editable=False, db_column='T533IdLineaBase')
    nombre_linea_base = models.CharField(max_length=255, db_column='T533nombreLineaBase')
    id_meta_eje = models.ForeignKey(MetasEjePGAR, on_delete=models.CASCADE, db_column='T533IdMetaEje')
    id_eje_estrategico = models.ForeignKey(EjeEstractegico, on_delete=models.CASCADE, db_column='T533IdEjeEstrategico')
    id_objetivo = models.ForeignKey(Objetivo, on_delete=models.SET_NULL, null=True, blank=True, db_column='T533IdObjetivo')
    id_plan = models.ForeignKey(Planes, on_delete=models.SET_NULL, null=True, blank=True, db_column='T533IdPlan')
    cumplio = models.BooleanField(default=False, db_column='T533cumplio')
    fecha_creacion = models.DateField(null=True, blank=True, db_column='T533fechaCreacion')

    class Meta:
        db_table = 'T533LineaBasePGAR'
        verbose_name = 'Linea Base'
        verbose_name_plural = 'Lineas Base'


class Actividad(models.Model):
    id_actividad = models.AutoField(
        primary_key=True, editable=False, db_column='T507IdActividad')
    numero_actividad = models.CharField(
        max_length=255, db_column='T507numeroActividad')
    nombre_actividad = models.CharField(
        max_length=255, db_column='T507nombreActividad')
    id_producto = models.ForeignKey(
        Productos, on_delete=models.SET_NULL, null=True, blank=True, db_column='T507IdProducto')
    id_plan = models.ForeignKey(
        Planes, on_delete=models.SET_NULL, null=True, blank=True, db_column='T507IdPlan')
    id_proyecto = models.ForeignKey(
        Proyecto, on_delete=models.SET_NULL, null=True, blank=True, db_column='T507IdProyecto')
    id_programa = models.ForeignKey(
        Programa, on_delete=models.SET_NULL, null=True, blank=True, db_column='T507IdPrograma')
    fecha_creacion = models.DateField(null=True, blank=True, db_column='T507fechaCreacion')
    cumplio = models.BooleanField(default=False, db_column='T507cumplio')
    id_linea_base = models.ForeignKey(LineasBasePGAR, on_delete=models.SET_NULL, null=True, blank=True, db_column='T507IdLineaBase')
    id_meta_eje = models.ForeignKey(MetasEjePGAR, on_delete=models.SET_NULL, null=True, blank=True, db_column='T507IdMetaEje')
    id_objetivo = models.ForeignKey(Objetivo, on_delete=models.SET_NULL, null=True, blank=True, db_column='T507IdObjetivo')
    id_eje_estrategico = models.ForeignKey(EjeEstractegico, on_delete=models.SET_NULL, null=True, blank=True, db_column='T507IdEjeEstrategico')

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

class Indicador(models.Model):
    id_indicador = models.AutoField(
        primary_key=True, editable=False, db_column='T512IdIndicador')
    nombre_indicador = models.CharField(
        max_length=255, db_column='T512nombreIndicador')
    numero_indicador = models.CharField(
        max_length=255, db_column='T512numeroIndicador')
    linea_base = models.CharField(
        max_length=255, null=True, blank=True, db_column='T512lineaBase')
    medida = models.CharField(
        max_length=3, choices=[
            ('NUM', 'Numero'),
            ('POR', 'Porcentaje'),
            ("TMP", "Tiempo"),
        ], db_column='T512medida')
    tipo_indicador = models.CharField(
        max_length=3, choices=[
            ('MAN', 'Mantenimiento'),
            ('INC', 'Incremento'),
        ], db_column='T512tipoIndicador')
    id_medicion = models.ForeignKey(
        Medicion, on_delete=models.CASCADE, db_column='T512IdMedicion')
    id_tipo = models.ForeignKey(
        Tipo, on_delete=models.SET_NULL, null=True, blank=True, db_column='T512IdTipo')
    id_producto = models.ForeignKey(
        Productos, on_delete=models.SET_NULL, null=True, blank=True, db_column='T512IdProducto')
    id_actividad = models.ForeignKey(
        Actividad, on_delete=models.SET_NULL, null=True, blank=True, db_column='T512IdActividad')
    id_plan = models.ForeignKey(
        Planes, on_delete=models.SET_NULL, null=True, blank=True, db_column='T512IdPlan')
    id_proyecto = models.ForeignKey(
        Proyecto, on_delete=models.SET_NULL, null=True, blank=True, db_column='T512IdProyecto')
    id_programa = models.ForeignKey(
        Programa, on_delete=models.SET_NULL, null=True, blank=True, db_column='T512IdPrograma')
    fecha_creacion = models.DateField(null=True, blank=True, db_column='T512fechaCreacion')
    cumplio = models.BooleanField(default=False, db_column='T512cumplio')
    id_linea_base = models.ForeignKey(LineasBasePGAR, on_delete=models.SET_NULL, null=True, blank=True, db_column='T512IdLineaBase')
    id_meta_eje = models.ForeignKey(MetasEjePGAR, on_delete=models.SET_NULL, null=True, blank=True, db_column='T512IdMetaEje')
    id_eje_estrategico = models.ForeignKey(EjeEstractegico, on_delete=models.SET_NULL, null=True, blank=True, db_column='T512IdEjeEstrategico')
    id_unidad_organizacional = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.SET_NULL, null=True, blank=True, db_column='T512IdUnidadOrganizacional')
    entidad_responsable = models.CharField(max_length=255, null=True, blank=True, db_column='T512entidadResponsable')

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
    # numero_meta = models.CharField(
    #     max_length=255, db_column='T513numeroMeta')
    unidad_meta = models.CharField(
        max_length=3, choices=[
            ('NUM', 'Numero'),
            ('POR', 'Porcentaje'),
        ], db_column='T513unidadMeta')
    porcentaje_meta = models.IntegerField(
        null=True, blank=True, db_column='T513porcentajeMeta')
    valor_meta = models.CharField(
        max_length=255, db_column='T513valorMeta')
    cumplio = models.BooleanField(default=False, db_column='T513cumplio')
    fecha_creacion_meta = models.DateField(
        null=True, blank=True, db_column='T513fechaCreacionMeta')
    # agno_1 = models.IntegerField(
    #     null=True, blank=True, db_column='T513agno1')
    # agno_2 = models.IntegerField(
    #     null=True, blank=True, db_column='T513agno2')
    # agno_3 = models.IntegerField(
    #     null=True, blank=True, db_column='T513agno3')
    # agno_4 = models.IntegerField(
    #     null=True, blank=True, db_column='T513agno4')
    # valor_ejecutado_compromiso = models.BigIntegerField(
    #     null=True, blank=True, db_column='T513valorEjecutadoCompromiso')
    # valor_ejecutado_obligado = models.BigIntegerField(
    #     null=True, blank=True, db_column='T513valorEjecutadoObligado')
    # avance_fisico = models.IntegerField(
    #     null=True, blank=True, db_column='T513avanceFisico')
    id_indicador = models.ForeignKey(
        Indicador, on_delete=models.CASCADE, db_column='T513IdIndicador')
    id_plan = models.ForeignKey(
        Planes, on_delete=models.CASCADE, db_column='T513IdPlan')
    id_programa = models.ForeignKey(
        Programa, on_delete=models.CASCADE, db_column='T513IdPrograma')
    id_proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, db_column='T513IdProyecto')
    id_producto = models.ForeignKey(
        Productos, on_delete=models.CASCADE, db_column='T513IdProducto')
    id_actividad = models.ForeignKey(
        Actividad, on_delete=models.CASCADE, db_column='T513IdActividad')

    def __str__(self):
        return str(self.id_meta)

    class Meta:
        db_table = 'T513Meta'
        verbose_name = 'Meta'
        verbose_name_plural = 'Metas'


class ParametricaRubro(models.Model):
    id_rubro = models.AutoField(primary_key=True, editable=False, db_column='T541IdRubro')
    id_plan = models.ForeignKey(Planes, on_delete=models.CASCADE, db_column='T541IdPlan')
    cod_pre = models.CharField(max_length=255, db_column='T541codPre')
    cuenta = models.CharField(max_length=255, db_column='T541cuenta')

    class Meta:
        db_table = 'T541ParametricaRubro'
        verbose_name = 'Parametrica Rubro'
        verbose_name_plural = 'Parametricas Rubros'


class Rubro(models.Model):
    id_rubro = models.AutoField(primary_key=True, editable=False, db_column='T511IdRubro')
    id_rubro_pa = models.ForeignKey(ParametricaRubro, on_delete=models.CASCADE, db_column='T511IdRubro')
    id_plan = models.ForeignKey(Planes, on_delete=models.CASCADE, db_column='T511IdPlan')
    id_meta = models.ForeignKey(Metas, on_delete=models.CASCADE, db_column='T511IdMeta')
    id_fuente = models.ForeignKey("FuenteFinanciacionIndicadores", on_delete=models.CASCADE, db_column='T511IdFuente')
    valor_fuentes = models.BigIntegerField(db_column='T511valorFuentes')
    agno = models.IntegerField(db_column='T511agno')
    adicion = models.BooleanField(db_column='T511adicion')

    def __str__(self):
        return str(self.id_rubro)

    class Meta:
        db_table = 'T511Rubro'
        verbose_name = 'Rubro'
        verbose_name_plural = 'Rubros'
        unique_together = ('id_rubro', 'id_plan', 'id_meta', 'id_fuente')


class Subprograma(models.Model):
    id_subprograma = models.AutoField(
        primary_key=True, editable=False, db_column='T515IdSubprograma')
    nombre_subprograma = models.CharField(
        max_length=255, db_column='T515nombreSubprograma')
    numero_subprograma = models.CharField(
        max_length=255, db_column='T515numeroSubprograma')
    id_programa = models.ForeignKey(
        Programa, on_delete=models.CASCADE, db_column='T515IdPrograma')

    def __str__(self):
        return str(self.id_subprograma)

    class Meta:
        db_table = 'T515Subprograma'
        verbose_name = 'Subprograma'
        verbose_name_plural = 'Subprogramas'

    
class ArmonizarPAIPGAR(models.Model):
    id_armonizar = models.AutoField(primary_key=True, editable=False, db_column='T535IdArmonizar')
    nombre_relacion = models.CharField(max_length=255, db_column='T535nombreRelacion')
    id_planPGAR = models.ForeignKey(Planes, on_delete=models.CASCADE, db_column='T535IdPlanPGAR', related_name='T535Id_PlanPGAR')
    id_planPAI = models.ForeignKey(Planes, on_delete=models.CASCADE, db_column='T535IdPlanPAI', related_name='T535Id_PlanPAI')
    estado = models.BooleanField(db_column='T535estado')
    fecha_creacion = models.DateField(null=True, blank=True, db_column='T535fechaCreacion')

    class Meta:
        db_table = 'T535ArmonizarPAIPGAR'
        verbose_name = 'Armonizar PAI PGAR'
        verbose_name_plural = 'Armonizar PAI PGAR'


class SeguimientoPGAR(models.Model):
    id_PGAR = models.AutoField(primary_key=True, editable=False, db_column='T536IdPGAR')
    ano_PGAR = models.IntegerField(db_column='T536anoPGAR')
    id_armonizar = models.ForeignKey(ArmonizarPAIPGAR, on_delete=models.CASCADE, db_column='T536IdArmonizar')
    id_indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, db_column='T536IdIndicador', related_name='T536Id_Indicador')
    id_actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, db_column='T536IdActividad')
    id_linea_base = models.ForeignKey(LineasBasePGAR, on_delete=models.CASCADE, db_column='T536IdLineaBase')
    id_meta_eje = models.ForeignKey(MetasEjePGAR, on_delete=models.CASCADE, db_column='T536IdMetaEje')
    id_eje_estrategico = models.ForeignKey(EjeEstractegico, on_delete=models.CASCADE, db_column='T536IdEjeEstrategico')
    id_programa = models.ForeignKey(Programa, on_delete=models.CASCADE, db_column='T536IdPrograma')
    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, db_column='T536IdProyecto')
    id_indicador_seg = models.ForeignKey(Indicador, on_delete=models.CASCADE, db_column='T536IdIndicadorSeg', related_name='T536Id_Indicador_seg')
    meta_fisica_anual = models.IntegerField(db_column='T536metaFisicaAnual')
    avance_fisico_anual = models.IntegerField(db_column='T536avanceFisicoAnual')
    pavance_fisico = models.IntegerField(db_column='T536pavanceFisico')
    pavance_fisico_acumulado = models.IntegerField(db_column='T536pavanceFisicoAcumulado')
    descripcion_avance = models.CharField(max_length=255, db_column='T536descripcionAvance')
    meta_finaciera_anual = models.BigIntegerField(db_column='T536metaFinacieraAnual')
    avance_financiero_anual = models.BigIntegerField(db_column='T536avanceFinancieroAnual')
    pavance_financiero = models.IntegerField(db_column='T536pavanceFinanciero')
    avance_recurso_obligado = models.BigIntegerField(db_column='T536avanceRecursoObligado')
    pavance_recurso_obligado = models.IntegerField(db_column='T536pavanceRecursoObligado')

    class Meta:
        db_table = 'T536SeguimientoPGAR'
        verbose_name = 'Seguimiento PGAR'
        verbose_name_plural = 'Seguimiento PGAR'




# class ActividadesEjePGAR(models.Model):
#     id_actividad_eje = models.AutoField(primary_key=True, editable=False, db_column='T535IdActividadEje')
#     nombre_actividad_eje = models.CharField(max_length=255, db_column='T535nombreActividadEje')
#     id_linea_base = models.ForeignKey(LineasBasePGAR, on_delete=models.CASCADE, db_column='T535IdLineaBase')
#     id_meta_eje = models.ForeignKey(MetasEjePGAR, on_delete=models.CASCADE, db_column='T535IdMetaEje')
#     id_plan = models.ForeignKey(Planes, on_delete=models.CASCADE, db_column='T535IdPlan')
#     id_objetivo = models.ForeignKey(Objetivo, on_delete=models.CASCADE, db_column='T535IdObjetivo')
#     id_eje_estrategico = models.ForeignKey(EjeEstractegico, on_delete=models.CASCADE, db_column='T535IdEjeEstrategico')
#     cumplio = models.BooleanField(default=False, db_column='T535cumplio')
#     fecha_creacion = models.DateField(null=True, blank=True, db_column='T535fechaCreacion')

#     class Meta:
#         db_table = 'T535ActividadesEjePGAR'
#         verbose_name = 'Actividad Eje'
#         verbose_name_plural = 'Actividades Ejes'


