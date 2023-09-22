from django.db import models
from gestion_documental.choices.tipos_pqr_choices import TIPOS_PQR
from seguridad.models import Personas
from gestion_documental.choices.tipo_radicado_choices import TIPOS_RADICADO_CHOICES
class ConfigTiposRadicadoAgno(models.Model):

    
    id_config_tipo_radicado_agno = models.SmallAutoField(primary_key=True, db_column='T235IdConfigTipoRadicadoAgno')
    agno_radicado = models.SmallIntegerField(db_column='T235agnoRadicado')
    cod_tipo_radicado = models.CharField(max_length=1, choices=TIPOS_RADICADO_CHOICES, db_column='T235codTipoRadicado')
    prefijo_consecutivo = models.CharField(null=True,max_length=10, db_column='T235prefijoConsecutivo')
    consecutivo_inicial = models.IntegerField(null=True,db_column='T235consecutivoInicial')
    cantidad_digitos = models.SmallIntegerField(null=True,db_column='T235cantidadDigitos')
    implementar = models.BooleanField(db_column='T235implementar')
    id_persona_config_implementacion = models.ForeignKey('transversal.Personas',null=True, on_delete=models.CASCADE, db_column='T235Id_PersonaConfigImplementacion',related_name='T235Id_PersonaConfigImplementacion')
    fecha_inicial_config_implementacion = models.DateTimeField(null=True,db_column='T235fechaInicialConfigImplementacion')
    consecutivo_actual = models.IntegerField(null=True,db_column='T235consecutivoActual')
    fecha_consecutivo_actual = models.DateTimeField(null=True,db_column='T235fechaConsecutivoActual')
    id_persona_consecutivo_actual = models.ForeignKey('transversal.Personas',null=True, on_delete=models.CASCADE, db_column='T235Id_PersonaConsecutivoActual',related_name='FK2_T235ConfigTiposRadicadoAgno')

    class Meta:
        db_table = 'T235ConfigTiposRadicadoAgno'
        unique_together = ['agno_radicado', 'cod_tipo_radicado']

class TiposPQR(models.Model):


    cod_tipo_pqr = models.CharField( primary_key=True,max_length=1,choices=TIPOS_PQR,db_column='T252CodTipoPQR')
    nombre = models.CharField(max_length=15,unique=True,db_column='T252nombre', verbose_name='Nombre del Tipo de PQR' )
    tiempo_respuesta_en_dias = models.SmallIntegerField(null=True,blank=True,db_column='T252tiempoRtaEnDias')
    
    def __str__(self):
        return self.nombre
    class Meta:
        db_table = 'T252TiposPQR'  
        verbose_name = 'Tipo de PQR'  
        verbose_name_plural = 'Tipos de PQR' 

class MediosSolicitud(models.Model):
    id_medio_solicitud = models.SmallAutoField(primary_key=True, db_column='T253IdMedioSolicitud')
    nombre = models.CharField(max_length=50, db_column='T253nombre',unique=True)
    aplica_para_pqrsdf = models.BooleanField(default=False, db_column='T253aplicaParaPQRSDF')
    aplica_para_tramites = models.BooleanField(default=False, db_column='T253aplicaParaTramites')
    aplica_para_otros = models.BooleanField(default=False, db_column='T253aplicaParaOtros')
    registro_precargado = models.BooleanField(default=False, db_column='T253registroPrecargado')
    activo = models.BooleanField(default=False, db_column='T253activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T253itemYaUsado')

    class Meta:
        db_table = 'T253MediosSolicitud'  
        verbose_name = 'Medio de Solicitud'  
        verbose_name_plural = 'Medios de Solictud' 


