from django.db import models
from django.contrib.auth.models import User

from transversal.models.base_models import Departamento, Municipio, Paises, Sexo, TipoDocumento

class EncabezadoEncuesta(models.Model):
    id_encabezado_encuesta = models.SmallAutoField(primary_key=True, db_column='T247IdEncabezadoEncuesta')
    nombre_encuesta = models.CharField(max_length=100,unique=True, db_column='T247nombreEncuesta')
    descripcion = models.CharField(max_length=255, null=True, blank=True, db_column='T247descripcion')
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column='T247fechaCreacion')
    activo = models.BooleanField(default=True, db_column='T247activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T247itemYaUsado')
    id_persona_ult_config_implement = models.ForeignKey('transversal.Personas',null=True, on_delete=models.CASCADE, db_column='T247Id_PersonaUltConfigImplemen')
    fecha_ult_config_implement = models.DateTimeField(null=True, blank=True, db_column='T247fechaUltConfigImplemen')

    def __str__(self):
        return self.nombre_encuesta
    class Meta:
        db_table='T247EncabezadoEncuesta'
        verbose_name='Encabezado Encuesta'
        verbose_name_plural='Encabezados Encuestae'

class PreguntasEncuesta(models.Model):
    id_pregunta_encuesta = models.SmallAutoField(primary_key=True, db_column='T248idPreguntaEncuesta')
    id_encabezado_encuesta = models.ForeignKey(EncabezadoEncuesta, on_delete=models.CASCADE, db_column='T248Id_EncabezadoEncuesta')
    redaccion_pregunta = models.CharField(max_length=255, db_column='T248redaccionPregunta', verbose_name='Redacción de la Pregunta')
    ordenamiento = models.SmallIntegerField(db_column='T248ordenamiento', verbose_name='Ordenamiento')
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column='T248fechaCreacion', verbose_name='Fecha de Creación')

    class Meta:
        unique_together = ['id_encabezado_encuesta', 'redaccion_pregunta']
        verbose_name = 'Pregunta de Encuesta'
        verbose_name_plural = 'Preguntas de Encuesta'
        db_table = "T248PreguntasEncuesta"
    def __str__(self):
        return self.redaccion_pregunta
    
class OpcionesRta(models.Model):
    id_opcion_rta = models.SmallAutoField(primary_key=True, db_column='T249IdOpcionRta')
    id_pregunta = models.ForeignKey(PreguntasEncuesta, on_delete=models.CASCADE, db_column='T249Id_Pregunta')
    opcion_rta = models.CharField(max_length=10, db_column='T249opcionRta', verbose_name='Opción de Respuesta')
    ordenamiento = models.SmallIntegerField(db_column='T249ordenamiento', verbose_name='Ordenamiento')

    class Meta:
        verbose_name = 'Opción de Respuesta'
        verbose_name_plural = 'Opciones de Respuesta'
        db_table = "T249OpcionesRta"
    def __str__(self):
        return self.opcion_rta
    

class EncEncuestasResueltas(models.Model):
    id_enc_encuesta_resuelta = models.AutoField(primary_key=True, db_column='T250Id_EncEncuestaResuelta')
    id_encuesta = models.ForeignKey(EncabezadoEncuesta, on_delete=models.CASCADE, db_column='T250Id_Encuesta', verbose_name='ID de la Encuesta a Resolver')
    tipo_usuario = models.CharField(max_length=10, db_column='T250tipoUsuario', verbose_name='Tipo de Usuario')
    id_persona = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, db_column='T250Id_Persona', null=True, blank=True, verbose_name='ID de la Persona')
    id_tipo_documento_usuario = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE, db_column='T250Id_TipoDocumentoUsuario', null=True, blank=True, verbose_name='Tipo de Documento de Identidad')
    nro_documento_id = models.CharField(max_length=20, db_column='T250nroDocumentoID', null=True, blank=True, verbose_name='Número de Documento de Identidad')
    nombre_completo = models.CharField(max_length=100, db_column='T250nombreCompleto', null=True, blank=True, verbose_name='Nombre Completo')
    id_sexo = models.ForeignKey(Sexo, on_delete=models.CASCADE, db_column='T250Id_Sexo', null=True, blank=True, verbose_name='ID del Sexo')
    rango_edad = models.CharField(max_length=1, db_column='T250rangoEdad', verbose_name='Rango de Edades')
    email = models.CharField(max_length=100, db_column='T250email', null=True, blank=True, verbose_name='Correo Electrónico')
    telefono = models.CharField(max_length=20, db_column='T250telefono', null=True, blank=True, verbose_name='Teléfono')
    id_pais = models.ForeignKey(Paises, on_delete=models.CASCADE, db_column='T250Id_Pais', null=True, blank=True, verbose_name='ID del País')
    id_departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, db_column='T250Id_Departamento', null=True, blank=True, verbose_name='ID del Departamento')
    id_ciudad = models.ForeignKey(Municipio, on_delete=models.CASCADE, db_column='T250Id_Ciudad', null=True, blank=True, verbose_name='ID de la Ciudad')
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column='T250fechaCreacion', verbose_name='Fecha de Creación')

    class Meta:
        verbose_name = 'Encuesta Resuelta'
        verbose_name_plural = 'Encuestas Resueltas'
        db_table = "T250EncEncuestasResueltas"
    def __str__(self):
        return f"Encuesta {self.id_encuesta} - {self.nombre_completo}"