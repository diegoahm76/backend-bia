from django.db import models
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