from django.db import models

class ConfiguracionTiemposRespuesta(models.Model):
    id_configuracion_tiempo_respuesta = models.AutoField(primary_key=True, db_column='T271IdConfiguracionTiempoRespuesta')
    nombre_configuracion = models.CharField(max_length=150, db_column='T271nombreConfiguracion', verbose_name="Nombre de la acción que se configura")
    tiempo_respuesta_en_dias = models.SmallIntegerField(db_column='T271tiempoRtaEnDias', blank=True, null=True, verbose_name="Tiempo de respuesta (en días) configurado")
    observacion_ultimo_cambio = models.CharField(max_length=255, blank=True, null=True, db_column='T271observacionUltimoCambio', verbose_name="Observaciones relacionadas con la configuración realizada")

    # Función para representar el modelo como una cadena
    def __str__(self):
        return self.nombre_configuracion

    class Meta:
        verbose_name = "Configuración de Tiempos de Respuesta"
        verbose_name_plural = "Configuraciones de Tiempos de Respuesta"
        db_table = "T271ConfiguracionTiemposRespuesta"  # Nombre de la tabla personalizado