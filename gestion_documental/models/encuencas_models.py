from django.db import models
from django.contrib.auth.models import User
from gestion_documental.choices.rango_edad_choices import RANGO_EDAD_CHOICES
from transversal.models.alertas_models import AlertasGeneradas

from transversal.models.base_models import Departamento, Municipio, Paises, Sexo, TipoDocumento

class EncabezadoEncuesta(models.Model):
    id_encabezado_encuesta = models.SmallAutoField(primary_key=True, db_column='T248IdEncuesta')
    nombre_encuesta = models.CharField(max_length=100,unique=True, db_column='T248nombreEncuesta')
    descripcion = models.CharField(max_length=255, null=True, blank=True, db_column='T248descripcion')
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column='T248fechaCreacion')
    activo = models.BooleanField(default=True, db_column='T248activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T248itemYaUsado')
    id_persona_ult_config_implement = models.ForeignKey('transversal.Personas',null=True, on_delete=models.CASCADE, db_column='T248Id_PersonaUltConfig')
    fecha_ult_config_implement = models.DateTimeField(null=True, blank=True, db_column='T248fechaUltConfig')

    def __str__(self):
        return self.nombre_encuesta
    class Meta:
        db_table='T248Encuestas'
        verbose_name='Encuesta'
        verbose_name_plural='Encuestas'

class PreguntasEncuesta(models.Model):
    id_pregunta_encuesta = models.SmallAutoField(primary_key=True, db_column='T249IdPregunta_Encuesta')
    id_encabezado_encuesta = models.ForeignKey(EncabezadoEncuesta, on_delete=models.CASCADE, db_column='T249Id_Encuesta')
    redaccion_pregunta = models.CharField(max_length=255, db_column='T249redaccionPregunta', verbose_name='Redacción de la Pregunta')
    ordenamiento = models.SmallIntegerField(db_column='T249ordenamiento', verbose_name='Ordenamiento')
    #fecha_creacion = models.DateTimeField(auto_now_add=True, db_column='T248fechaCreacion', verbose_name='Fecha de Creación')

    class Meta:
        unique_together = ['id_encabezado_encuesta', 'redaccion_pregunta']
        verbose_name = 'Pregunta de Encuesta'
        verbose_name_plural = 'Preguntas de Encuesta'
        db_table = "T249Preguntas_Encuesta"
    def __str__(self):
        return self.redaccion_pregunta
    
class OpcionesRta(models.Model):
    id_opcion_rta = models.SmallAutoField(primary_key=True, db_column='T250IdOpcion_PreguntaEncuesta')
    id_pregunta = models.ForeignKey(PreguntasEncuesta, on_delete=models.CASCADE, db_column='T250Id_Pregunta_Encuesta')
    opcion_rta = models.CharField(max_length=100, db_column='T250opcionRta', verbose_name='Opción de Respuesta')
    ordenamiento = models.SmallIntegerField(db_column='T250ordenamiento', verbose_name='Ordenamiento')

    class Meta:
        verbose_name = 'Opción de Respuesta'
        verbose_name_plural = 'Opciones de Respuesta'
        db_table = "T250Opciones_PreguntaEncuesta"
    def __str__(self):
        return self.opcion_rta
    

# class T251DatosEncuestasResueltas(models.Model):
#     id_enc_encuesta_resuelta = models.AutoField(primary_key=True, db_column='T251IdDatosEncuestaResuelta')
#     id_encuesta = models.ForeignKey(EncabezadoEncuesta, on_delete=models.CASCADE, db_column='T250Id_Encuesta', verbose_name='ID de la Encuesta a Resolver')
#     tipo_usuario = models.CharField(max_length=10, db_column='T250tipoUsuario', verbose_name='Tipo de Usuario')
#     id_persona = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, db_column='T250Id_Persona', null=True, blank=True, verbose_name='ID de la Persona')
#     id_tipo_documento_usuario = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE, db_column='T250Id_TipoDocumentoUsuario', null=True, blank=True, verbose_name='Tipo de Documento de Identidad')
#     nro_documento_id = models.CharField(max_length=20, db_column='T250nroDocumentoID', null=True, blank=True, verbose_name='Número de Documento de Identidad')
#     nombre_completo = models.CharField(max_length=100, db_column='T250nombreCompleto', null=True, blank=True, verbose_name='Nombre Completo')
#     id_sexo = models.ForeignKey(Sexo, on_delete=models.CASCADE, db_column='T250Id_Sexo', null=True, blank=True, verbose_name='ID del Sexo')
#     rango_edad = models.CharField(max_length=1, db_column='T250rangoEdad', verbose_name='Rango de Edades')
#     email = models.CharField(max_length=100, db_column='T250email', null=True, blank=True, verbose_name='Correo Electrónico')
#     telefono = models.CharField(max_length=20, db_column='T250telefono', null=True, blank=True, verbose_name='Teléfono')
#     id_pais = models.ForeignKey(Paises, on_delete=models.CASCADE, db_column='T250Id_Pais', null=True, blank=True, verbose_name='ID del País')
#     id_departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, db_column='T250Id_Departamento', null=True, blank=True, verbose_name='ID del Departamento')
#     id_ciudad = models.ForeignKey(Municipio, on_delete=models.CASCADE, db_column='T250Id_Ciudad', null=True, blank=True, verbose_name='ID de la Ciudad')
#     fecha_creacion = models.DateTimeField(auto_now_add=True, db_column='T250fechaCreacion', verbose_name='Fecha de Creación')

#     class Meta:
#         verbose_name = 'Encuesta Resuelta'
#         verbose_name_plural = 'Encuestas Resueltas'
#         db_table = "T250EncEncuestasResueltas"
#     def __str__(self):
#         return f"Encuesta {self.id_encuesta} - {self.nombre_completo}"
    

# Choices para tipo_usuario
TIPO_USUARIO_CHOICES = [
    ('A', 'Anonimo'),
    ('I', 'Identificado'),
    ('R', 'Registrado')
]

# Choices para rango_edad


class DatosEncuestasResueltas(models.Model):
    id_datos_encuesta_resuelta = models.BigAutoField(primary_key=True, db_column='T251IdDatosEncuestaResuelta')
    id_encuesta = models.ForeignKey(EncabezadoEncuesta, on_delete=models.CASCADE, db_column='T251Id_Encuesta')
    tipo_usuario = models.CharField(max_length=1, choices=TIPO_USUARIO_CHOICES, db_column='T251tipoUsuario')
    id_persona = models.ForeignKey('transversal.Personas', null=True, blank=True, on_delete=models.CASCADE, db_column='T251Id_Persona')
    id_tipo_documento_usuario = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE, db_column='T251Id_TipoDocumentoUsuario', null=True, blank=True, verbose_name='Tipo de Documento de Identidad')
    #id_tipo_documento_usuario = models.CharField(max_length=2, null=True, db_column='T251Id_TipoDocumentoUsuario')
    nro_documento_id = models.CharField(max_length=20, null=True,blank=True, db_column='T251nroDocumentoID')
    nombre_completo = models.CharField(max_length=200, null=True,blank=True, db_column='T251nombreCompleto')
    #cod_sexo = models.CharField(max_length=1, null=True,blank=True, db_column='T251Cod_Sexo')
    cod_sexo = models.ForeignKey(Sexo, on_delete=models.CASCADE, db_column='T251Cod_Sexo', null=True, blank=True, verbose_name='ID del Sexo')
    rango_edad = models.CharField(max_length=1, null=True,blank=True,choices=RANGO_EDAD_CHOICES, db_column='T251rangoEdad')
    email = models.CharField(max_length=100, null=True,blank=True, db_column='T251email')
    telefono = models.CharField(max_length=20, null=True,blank=True, db_column='T251telefono')
    #id_pais_para_extranjero = models.CharField(max_length=2, null=True, db_column='T251Id_PaisParaExtranjero')
    id_pais_para_extranjero = models.ForeignKey(Paises, on_delete=models.CASCADE, db_column='T251Id_PaisParaExtranjero', null=True, blank=True, verbose_name='ID del País')
    #id_municipio_para_nacional = models.CharField(max_length=5, null=True, db_column='T251Id_MunicipioParaNacional')
    id_municipio_para_nacional = models.ForeignKey(Municipio, on_delete=models.CASCADE, db_column='T251Id_MunicipioParaNacional', null=True, blank=True, verbose_name='ID de la Ciudad')
    fecha_creacion = models.DateTimeField(db_column='T251fechaCreacion')

    def __str__(self):
        return f'Datos de Encuesta Resuelta {self.id_datos_encuesta_resuelta}'

    class Meta:
        db_table = 'T251DatosEncuestasResueltas'
        verbose_name = 'Datos de Encuesta Resuelta'
        verbose_name_plural = 'Datos de Encuestas Resueltas'

class RespuestaEncuesta(models.Model):
    id_respuesta_encuesta = models.BigAutoField(primary_key=True, db_column='T252IdRespuesta_Encuesta')
    id_encuesta_resuelta = models.ForeignKey(DatosEncuestasResueltas, on_delete=models.CASCADE, db_column='T252Id_DatosEncuestaResuelta')
    id_opcion_pregunta_encuesta = models.ForeignKey(OpcionesRta, on_delete=models.CASCADE, db_column='T252Id_Opcion_PreguntaEncuesta')

    def __str__(self):
        return f'Respuesta de Encuesta {self.id_encuesta_resuelta} - Opción {self.id_opcion_pregunta_encuesta}'

    class Meta:
        db_table = 'T252Respuestas_Encuesta'
        verbose_name = 'Respuesta de Encuesta'
        verbose_name_plural = 'Respuestas de Encuesta'


class AsignarEncuesta(models.Model):
    id_asignar_encuesta = models.BigAutoField(primary_key=True, db_column='T311IdAsignar_Encuesta')
    id_encuesta = models.ForeignKey(EncabezadoEncuesta, on_delete=models.CASCADE, db_column='T311Id_Encuesta')
    id_persona = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, db_column='T311Id_Persona')
    id_alerta_generada = models.ForeignKey(AlertasGeneradas, on_delete=models.CASCADE, db_column='T311Id_Alerta_Generada', null=True, blank=True)
    
    def __str__(self):
        return f'Respuesta de Encuesta {self.id_asignar_encuesta}'

    class Meta:
        db_table = 'T311Asignar_Encuesta'
        verbose_name = 'Respuesta de Encuesta'
        verbose_name_plural = 'Respuestas de Encuesta'
        unique_together = (('id_encuesta', 'id_persona'),)