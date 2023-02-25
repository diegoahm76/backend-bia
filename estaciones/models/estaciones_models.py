from django.db import models
from estaciones.choices.estaciones_choices import (
    cod_tipo_estacion_choices
)
from seguridad.choices.municipios_choices import municipios_CHOICES
from seguridad.choices.tipo_documento_choices import tipo_documento_CHOICES

class Estaciones(models.Model):
    id_estacion = models.AutoField(primary_key=True, editable=False, db_column='T900IdEstacion')
    fecha_modificacion = models.DateTimeField(null=True, blank=True, db_column='T900fechaModificacion')
    nombre_estacion = models.CharField(max_length=30, db_column='T900nombreEstacion')
    cod_tipo_estacion = models.CharField(max_length=2, choices=cod_tipo_estacion_choices, null=True, blank=True, db_column='T900codTipoEstacion')
    latitud = models.DecimalField(max_digits=18, decimal_places=13, db_column='T900latitud')
    longitud = models.DecimalField(max_digits=18, decimal_places=13, db_column='T900longitud')
    cod_municipio = models.CharField(max_length=5, choices=municipios_CHOICES, null=True, blank=True, db_column='T900Cod_Municipio')
    indicaciones_ubicacion = models.CharField(max_length=255, null=True, blank=True, db_column='T900indicacionesUbicacion')
    fecha_modificacion_coordenadas = models.DateTimeField(null=True, blank=True, db_column='T900fechaModificacionCoord')
    id_persona_modifica = models.IntegerField(null=True, blank=True, db_column='T900id_PersonaModifica')

    def __str__(self):
        return str(self.nombre_estacion)
    
    class Meta:
        db_table = 'T900Estaciones'
        verbose_name = 'Estacion'
        verbose_name_plural = 'Estaciones'


class Datos(models.Model):
    id_data = models.AutoField(primary_key=True, editable=False, db_column='T901IdData')
    fecha_registro = models.DateTimeField(db_column='T901fechaRegistro')
    id_estacion = models.ForeignKey(Estaciones, on_delete=models.CASCADE, db_column='T901Id_Estacion')
    temperatura_ambiente = models.DecimalField(max_digits=18, decimal_places=4, db_column='T901temperaturaAmbiente')
    humedad_ambiente = models.DecimalField(max_digits=18, decimal_places=4, db_column='T901humedadAmbiente')
    presion_barometrica = models.DecimalField(max_digits=18, decimal_places=4, db_column='T901presionBarometrica')
    velocidad_viento = models.DecimalField(max_digits=18, decimal_places=4, db_column='T901velocidadViento')
    direccion_viento = models.DecimalField(max_digits=18, decimal_places=4, db_column='T901direccionViento')
    precipitacion = models.DecimalField(max_digits=18, decimal_places=4, db_column='T901precipitacion')
    luminosidad = models.DecimalField(max_digits=18, decimal_places=4, db_column='T901luminosidad')
    nivel_agua = models.DecimalField(max_digits=18, decimal_places=4, db_column='T901nivelAgua')
    velocidad_agua = models.DecimalField(max_digits=18, decimal_places=4, db_column='T901velocidadAgua')

    def __str__(self):
        return str(self.id_data)
    
    class Meta:
        db_table = 'T901Datos'
        verbose_name = 'Dato'
        verbose_name_plural = 'Datos'

class ParametrosReferencia(models.Model):
    id_parametro_referencia = models.AutoField(primary_key=True, editable=False, db_column='T902IdParametroReferencia')
    fecha_modificacion = models.DateTimeField(db_column='T902fechaModificacion')
    id_estacion = models.ForeignKey(Estaciones, on_delete=models.CASCADE, db_column='T902Id_Estacion')
    frecuencia_solicitud_datos = models.PositiveIntegerField(db_column='T902frecuenciaSolicitudDatos')
    temperatura_ambiente_max = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902temperaturaAmbienteMax')
    temperatura_ambiente_min = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902temperaturaAmbienteMin')
    humedad_ambiente_max = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902humedadAmbienteMax')
    humedad_ambiente_min = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902humedadAmbienteMin')
    presion_barometrica_max = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902presionBarometricaMax')
    presion_barometrica_min = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902presionBarometricaMin')
    velocidad_viento_max = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902velocidadVientoMax')
    velocidad_viento_min = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902velocidadVientoMin')
    direccion_viento_max = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902direccionVientoMax')
    direccion_viento_min = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902direccionVientoMin')
    precipitacion_max = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902precipitacionMax')
    precipitacion_min = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902precipitacionMin')
    luminosidad_max = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902luminosidadMax')
    luminosidad_min = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902luminosidadMin')
    nivel_agua_max = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902nivelAguaMax')
    nivel_agua_min = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902nivelAguaMin')
    velocidad_agua_max = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902velocidadAguaMax')
    velocidad_agua_min = models.DecimalField(max_digits=18, decimal_places=4, db_column='T902velocidadAguaMin')
    id_persona_modifica = models.PositiveIntegerField(null=True, blank=True, db_column='T902Id_PersonaModifica')

    def __str__(self):
        return str(self.id_parametro_referencia)
    
    class Meta:
        db_table = 'T902ParametrosReferencia'
        verbose_name = 'Parametro Referencia'
        verbose_name_plural = 'Parametros Referencias'


class AlertasEquipoEstacion(models.Model):
    id_alerta_equipo_estacion = models.AutoField(primary_key=True, editable=False, db_column='T903IdAlertaEquipoEstacion')
    id_estacion = models.ForeignKey(Estaciones, on_delete=models.CASCADE, db_column='T903Id_Estacion')
    descripcion = models.CharField(max_length=255, db_column='T903descripcion')
    fecha_generacion = models.DateTimeField(db_column='T903fechaGeneracion')
    nombre_variable = models.CharField(max_length=30, null=True, blank=True, db_column='T903nombreVariable')

    def __str__(self):
        return str(self.id_alerta_equipo_estacion)
    
    class Meta:
        db_table = 'T903AlertasEquipoEstacion'
        verbose_name = 'Alerta Equipo Estacion'
        verbose_name_plural = 'Alertas Equipos Estaciones'


class PersonasEstaciones(models.Model):
    id_persona = models.AutoField(primary_key=True, editable=False, db_column='T904IdPersonaEstaciones')
    cod_tipo_documento_id = models.CharField(max_length=2, choices=tipo_documento_CHOICES, db_column='T904Cod_TipoDocumentoID')
    numero_documento_id = models.CharField(max_length=20, db_column='T904nrodocumentoID')
    primer_nombre = models.CharField(max_length=30, db_column='T904primerNombre')
    segundo_nombre = models.CharField(max_length=30, null=True, blank=True, db_column='T904segundoNombre')
    primer_apellido = models.CharField(max_length=30, db_column='T904PrimerApellido')
    segundo_apellido = models.CharField(max_length=30, null=True, blank=True, db_column='T904segundoApellido')
    entidad = models.CharField(max_length=30, db_column='T904entidad')
    cargo = models.CharField(max_length=30, null=True, blank=True, db_column='T904cargo')
    email_notificacion = models.EmailField(db_column='T904emailNotificacion')
    nro_celular_notificacion = models.CharField(max_length=15, db_column='T904nroCelularNotificacion')
    observacion = models.CharField(max_length=255, null=True, blank=True, db_column='T904observacion')

    def __str__(self):
        return str(self.id_persona)

    class Meta:
        db_table = 'T904PersonasEstaciones'
        verbose_name = 'Persona Estacion'
        verbose_name_plural = 'Personas Estaciones'


class PersonasEstacionesEstacion(models.Model):
    id_persona_estaciones_estacion = models.AutoField(primary_key=True, editable=False, db_column='T905IdPersonaEstaciones_Estacion')
    id_estacion = models.ForeignKey(Estaciones, on_delete=models.CASCADE, db_column='T905Id_Estacion')
    id_persona_estaciones = models.ForeignKey(PersonasEstaciones, on_delete=models.CASCADE, db_column='T905Id_PersonaEstaciones')

    def __str__(self):
        return str(self.id_persona_estaciones_estacion)
    
    class Meta:
        db_table = 'T905PersonasEstaciones_Estacion'
        verbose_name = 'Persona Estaciones Estacion'
        verbose_name_plural  = 'Personas Estaciones Estacion'


class ConfiguracionAlertaPersonas(models.Model):
    id_confi_alerta_persona = models.AutoField(primary_key=True, editable=False, db_column='T906IdConfiAlertaPersona')
    nombre_variable_alarma = models.CharField(max_length=30, db_column='T906nombreVariableAlarma')
    mensaje_alarma_maximo = models.CharField(max_length=255, db_column='T906mensajeAlarmaMaximo')
    mensaje_alarma_minimo = models.CharField(max_length=255, db_column='T906mensajeAlarmaMinimo')
    mensaje_no_alarma = models.CharField(max_length=255, db_column='T906mensajeNoAlarma')
    frecuencia_alarma = models.PositiveIntegerField(db_column='T906frecuenciaAlarma')

    def __str__(self):
        return str(self.nombre_variable_alarma)
    
    class Meta:
        db_table = 'T906ConfiguracionAlertasPersonas'
        verbose_name = 'Configuracion Alerta Persona'
        verbose_name_plural = 'Configuracion Alertas Personas'


class HistorialAlarmasEnviadasEstacion(models.Model):
    id_historial_alarma_enviada_estacion = models.AutoField(primary_key=True, editable=False, db_column='T907IdHistorialAlarmaEnviada_Estacion')
    id_estacion = models.ForeignKey(Estaciones, on_delete=models.CASCADE, db_column='T907Id_Estacion')
    id_persona_estacion = models.ForeignKey(PersonasEstaciones, on_delete=models.CASCADE, db_column='T907Id_PersonaEstaciones')
    fecha_hora_envio = models.DateTimeField(db_column='T907fechaHoraEnvio')
    mensaje_enviado = models.CharField(max_length=255, db_column='T907mensajeEnviado')
    dir_email_enviado = models.EmailField(db_column='T907dirEmailEnviado')
    nro_celular_enviado = models.CharField(max_length=15, db_column='T907nroCelularEnviado')

    def __str__(self):
        return str(self.id_historial_alarma_enviada_estacion)
    
    class Meta:
        db_table = 'T907HistorialAlarmasEnviadas_PorEstacion'
        verbose_name = 'Historial Alarma Enviada Por Estacion'
        verbose_name_plural = 'Historial Alarmas Enviadas por Estacion'


