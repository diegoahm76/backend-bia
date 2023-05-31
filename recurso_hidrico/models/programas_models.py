from django.db import models

from seguridad.models import Personas


class ProgramasPORH(models.Model):
    id_programa = models.AutoField(primary_key=True,editable=False,db_column="T600IdPrograma_PORH")
    id_instrumento = models.IntegerField(db_column="T600Id_Instrumento_PORH (NN)")
    nombre = models.CharField(max_length=255,db_column="T600nombre")
    fecha_creacion = models.DateField(auto_now_add=True,db_column="T600fechaCreacion")
    fecha_inicio = models.DateField(db_column="T600fechaInicio")
    fecha_fin = models.DateField(db_column="T600fechaFin")
    
    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table = 'T600Programas_PORH'
        verbose_name = 'Programas_PORH'
        verbose_name_plural = 'Programas_PORHS'
        unique_together = ['id_instrumento','nombre']
        
class ProyectosPORH(models.Model):
    id_proyecto = models.AutoField(primary_key=True,editable=False,db_column="T601IdProyecto_Pg_PORH")
    id_programa = models.ForeignKey(ProgramasPORH,on_delete=models.CASCADE,db_column="T601Id_Programa_PORH (NN)")
    nombre = models.CharField(max_length=255,db_column="T601nombre")
    vigencia_inicial = models.DateField(db_column="T601vigenciaInicial")
    vigencia_final = models.DateField(db_column="T601vigenciaFinal")
    inversion = models.PositiveIntegerField(db_column="T601inversion")
    fecha_registro = models.DateField(auto_now_add=True,db_column="T601fechaRegistro")
    
    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table = 'T601Proyectos_Pg_PORH'
        verbose_name = 'Proyectos_Pg_PORH'
        verbose_name_plural = 'Proyectos_Pg_PORHS'
        unique_together = ['id_programa','nombre']

class ActividadesProyectos(models.Model):
    id_actividades = models.AutoField(primary_key=True,editable=False,db_column="T602IdActividad_Py_Pg_PORH")
    id_proyecto = models.ForeignKey(ProyectosPORH,on_delete=models.CASCADE,db_column="T602Id_Proyecto_Pg_PORH")
    nombre = models.CharField(max_length=255,db_column="T602nombre")
    fecha_registro = models.DateField(auto_now_add=True,db_column="T602fechaRegistro")
    
    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table = 'T602Actividades_Py_Pg_PORH'
        verbose_name = 'Actividades_Py_Pg_PORH'
        verbose_name_plural = 'Actividades_Py_Pg_PORHS'
        unique_together = ['id_proyecto','nombre']
        
class AvancesProyecto(models.Model):
    id_avance = models.AutoField(primary_key=True,editable=False,db_column="T603IdAvance_Py_Pg_PORH")
    id_proyecto = models.ForeignKey(ProyectosPORH, on_delete=models.CASCADE,db_column="T603IdProyecto_Pg_PORH")
    fecha_reporte = models.DateField(db_column="T603fechaReporte")
    accion = models.CharField(max_length=255,db_column="T603accion")
    descripcion = models.CharField(max_length=255,db_column="T603descripcion")
    id_persona_registra = models.ForeignKey(Personas,on_delete=models.CASCADE,db_column="T603IdPersonaRegistra")
    fecha_registro = models.DateField(auto_now_add=True,db_column="T603fechaRegistro")
    
    def __str__(self):
        return str(self.id_avance)
    
    class Meta:
        db_table = 'T603Avances_Py_Pg_PORH'
        verbose_name = 'Avances_Py_Pg_PORH'
        verbose_name_plural = 'Avances_Py_Pg_PORHS'

class EvidenciasAvance(models.Model):
    id_evidencia_avance = models.AutoField(primary_key=True,editable=False,db_column="T604IdEvidencia_Avance_Py_Pg_PORH")
    id_avance = models.ForeignKey(ProgramasPORH,on_delete=models.CASCADE,db_column="T603Id_Avance_Py_Pg_PORH")
    nombre_archivo = models.CharField(max_length=255,db_column="T603nombreArchivo")
    id_archivo = models.IntegerField(db_column="T603Id_Archivo")
    
    def __str__(self):
        return str(self.id_evidencia_avance)
    
    class Meta:
        db_table = 'T604Evidencias_Avance_Py_Pg_PORH'
        verbose_name = 'Evidencias_Avance_Py_Pg_PORH'
        verbose_name_plural = 'Evidencias_Avance_Py_Pg_PORHS'