from django.db import models

from transversal.models.organigrama_models import UnidadesOrganizacionales
from transversal.choices.tipos_alertas import CATEGORIA_ALERTA_CHOICES

class ConfiguracionClaseAlerta(models.Model):
    cod_clase_alerta = models.CharField(primary_key=True, max_length=10, db_column='T040CodClaseAlerta')
    nombre_clase_alerta = models.CharField(max_length=50, unique=True, db_column='T040nombreClaseAlerta')
    descripcion_clase_alerta = models.CharField(max_length=255, db_column='T040descripcionClaseAlerta')
    COD_TIPOALERTAS_CHOICES = [
        ('FF','Alerta en Fecha Fija'),('EP','Alerta en Evento Programado'), ('EI','Alerta en Evento Inmediato')
    ]
    cod_tipo_clase_alerta = models.CharField(max_length=2, choices=COD_TIPOALERTAS_CHOICES, db_column='T040codTipoClaseAlerta')
    cod_categoria_clase_alerta = models.CharField(max_length=3, choices=[('Ale', 'Alerta'), ('Com', 'Comunicación')], db_column='T040codCategoriaClaseAlerta')
    cant_dias_previas = models.SmallIntegerField(null=True, blank=True, db_column='T040ctdadDiasAlertasPrevias')
    frecuencia_previas = models.SmallIntegerField(null=True, blank=True, db_column='T040frecuenciaAlertasPrevias')
    cant_dias_post = models.SmallIntegerField(null=True, blank=True, db_column='T040ctdadRepeticionesPost')
    frecuencia_post = models.SmallIntegerField(null=True, blank=True, db_column='T040frecuenciaRepeticionesPost')
    envios_email = models.BooleanField(default=False, db_column='T040envioSimultaneoEmail')	
    NIVEL_PRIORIDAD_CHOICES = [
        ('1', 'Máxima'),
        ('2', 'Media'),
        ('3', 'Baja'),
    ]
    nivel_prioridad = models.CharField(max_length=1, choices=NIVEL_PRIORIDAD_CHOICES, db_column='T040nivelPrioridad')#T040nivelPrioridad
    activa = models.BooleanField(default=True, db_column='T040activa')
    mensaje_base_dia = models.CharField(max_length=255, db_column='T040mensajeBaseDelDia')
    mensaje_base_previo = models.CharField(null=True, blank=True, max_length=255, db_column='T040mensajeBasePrevio')
    mensaje_base_vencido = models.CharField(null=True, blank=True, max_length=255, db_column='T040mensajeBaseVencido')
    asignar_responsable = models.BooleanField(default=False, db_column='T040asignarResponsableDirEnConfig')
    id_modulo_destino = models.ForeignKey('seguridad.Modulos', db_column='T040Id_ModuloDestino', on_delete=models.SET_NULL, null=True, blank=True, related_name='configuraciones_destino')
    id_modulo_generador = models.ForeignKey('seguridad.Modulos', db_column='T040Id_ModuloGenerador', on_delete=models.SET_NULL, null=True, blank=True, related_name='configuraciones_generador')
    nombre_funcion_comple_mensaje = models.CharField(max_length=255, null=True, blank=True, db_column='T040nombreFuncionParaCompleAMensaje')
    
    def __str__(self):
        return str(self.nombre_clase_alerta)

    class Meta:
        db_table = 'T040ConfiguracionClasesAlerta'
        verbose_name = 'Configuracion de Clase de Alerta'
        verbose_name_plural = 'Configuraciones de Clases de Alertas'


class FechaClaseAlerta(models.Model):
    id_fecha = models.AutoField(primary_key=True, db_column='T041IdFecha_ClaseAlerta')
    cod_clase_alerta = models.ForeignKey(ConfiguracionClaseAlerta, on_delete=models.CASCADE, db_column='T041Cod_ClaseAlerta')
    dia_cumplimiento = models.SmallIntegerField(db_column='T041diaCumplimiento')
    mes_cumplimiento = models.SmallIntegerField(db_column='T041mesCumplimiento')
    age_cumplimiento = models.SmallIntegerField(null=True, blank=True, db_column='T041agnoCumplimiento')

    def __str__(self):
        return str(self.id_fecha)

    class Meta:
        db_table = 'T041Fechas_ClaseAlerta'
        verbose_name = 'Fecha de Clase de Alerta'
        verbose_name_plural = 'Fechas de Clases de Alertas'
        unique_together = ['cod_clase_alerta', 'dia_cumplimiento','mes_cumplimiento','age_cumplimiento']


class PersonasAAlertar(models.Model):
    id_persona_alertar = models.AutoField(primary_key=True, db_column='T042IdPersonaAAlertar_ClaseAlerta')
    cod_clase_alerta = models.ForeignKey(ConfiguracionClaseAlerta, on_delete=models.CASCADE, db_column='T042Cod_ClaseAlerta')
    id_persona = models.ForeignKey('seguridad.Personas', null=True, blank=True, on_delete=models.SET_NULL, db_column='T042Id_Persona')
    id_unidad_org_lider = models.ForeignKey(UnidadesOrganizacionales, null=True, blank=True, on_delete=models.SET_NULL, db_column='T042Id_UndOrgDelLider')
    perfil_sistema = models.CharField(null=True, blank=True, max_length=4, db_column='T042codPerfilDelSistema')
    es_responsable_directo = models.BooleanField(null=True, blank=True, db_column='T042esResponsableDirecto')
    registro_editable = models.BooleanField(default=True, db_column='T042registroEditable')
    
    def __str__(self):
        return str(self.id_persona_alertar)

    class Meta:
        db_table = 'T042PersonasAAlertar_ClaseAlerta'
        verbose_name = 'Persona a Alertar'
        verbose_name_plural = 'Personas a Alertar'
        unique_together = ['cod_clase_alerta', 'id_persona','id_unidad_org_lider','perfil_sistema']


# Choices para T043codCategoriaAlerta


# Choices para T043nivelPrioridad
NIVEL_PRIORIDAD_CHOICES = [
    ('1', 'Máxima'),
    ('2', 'Media'),
    ('3', 'Baja'),
]
PERFIL_SISTEMA_IMPLICADO_CHOICES = [
    ('Dire', 'Director'),
    ('CViv', 'Coordinador de Viveros'),
    ('RTra', 'Responsable de Transporte'),
    ('CAlm', 'Coordinador de Almacén'),
    ('Alma', 'Almacenista'),
]

class AlertasProgramadas(models.Model):
    id_alerta_programada = models.AutoField(primary_key=True, db_column='T043IdAlertaProgramada')
    cod_clase_alerta = models.ForeignKey(ConfiguracionClaseAlerta, on_delete=models.CASCADE, db_column='T043Cod_ClaseAlerta')
    nombre_clase_alerta = models.CharField(max_length=50, db_column='T043nombreClaseAlerta')
    dia_cumplimiento = models.SmallIntegerField(db_column='T043diaCumplimiento')
    mes_cumplimiento = models.SmallIntegerField(db_column='T043mesCumplimiento')
    agno_cumplimiento = models.SmallIntegerField(null=True, blank=True, db_column='T043agnoCumplimiento')
    ctdad_dias_alertas_previas = models.SmallIntegerField(db_column='T043ctdadDiasAlertasPrevias')
    frecuencia_alertas_previas = models.SmallIntegerField(db_column='T043frecuenciaAlertasPrevias')
    ctdad_repeticiones_post = models.SmallIntegerField(db_column='T043ctdadRepeticionesPost')
    frecuencia_repeticiones_post = models.SmallIntegerField(db_column='T043frecuenciaRepeticionesPost')
    mensaje_base_del_dia = models.CharField(max_length=255, db_column='T043mensajeBaseDelDia')
    mensaje_base_previo = models.CharField(max_length=255, null=True,blank=True,db_column='T043mensajeBasePrevio')
    mensaje_base_vencido = models.CharField(max_length=255,null=True,blank=True, db_column='T043mensajeBaseVencido')
    complemento_mensaje = models.CharField(max_length=255, null=True, blank=True, db_column='T043complementoMensaje')
    nombre_funcion_comple_mensaje = models.CharField(max_length=255, null=True, blank=True, db_column='T043nombreFuncionParaCompleAMensaje')
    id_modulo_destino = models.ForeignKey('seguridad.Modulos', related_name='modulo_destino_alertas_programadas', null=True, blank=True, on_delete=models.SET_NULL, db_column='T043Id_ModuloDestino')
    id_elemento_implicado = models.IntegerField(null=True, blank=True, db_column='T043idElementoImplicado')
    valor_adicional = models.CharField(max_length=50, null=True, blank=True, db_column='T043valorAdicionalParaIdOrigenAlerta')
    id_modulo_generador = models.ForeignKey('seguridad.Modulos', related_name='modulo_generador_alertas_programadas', on_delete=models.CASCADE, db_column='T043Id_ModuloGenerador')
    tiene_implicado = models.BooleanField(default=False, db_column='T043tienePersonaImplicada')
    id_persona_implicada = models.ForeignKey('seguridad.Personas', null=True, blank=True, on_delete=models.SET_NULL, db_column='T043Id_PersonaImplicada')
    id_und_org_lider_implicada = models.ForeignKey(UnidadesOrganizacionales, null=True, blank=True, on_delete=models.SET_NULL, db_column='T043IdUndOrgLider_Implicada')
    perfil_sistema_implicado = models.CharField(
        max_length=4,
        choices=PERFIL_SISTEMA_IMPLICADO_CHOICES,
        null=True,
        blank=True,
        db_column='T043codPerfilSistema_Implicado',
    )
    id_personas_alertar = models.CharField(max_length=255, null=True, blank=True, db_column='T043idPersonasAAlertar')
    id_und_org_lider_alertar = models.CharField(max_length=255, null=True, blank=True, db_column='T043idUndOrgLideresAAlertar')
    id_perfiles_sistema_alertar = models.CharField(max_length=255, null=True, blank=True, db_column='T043codPerfilesSistemaAAlertar')
    id_personas_suspen_alertar_sin_agno = models.CharField(max_length=255, null=True, blank=True, db_column='T043idPersonasSuspendEnAlerSinAgno')
    cod_categoria_alerta = models.CharField(max_length=3, choices=CATEGORIA_ALERTA_CHOICES, db_column='T043codCategoriaAlerta')
    requiere_envio_email = models.BooleanField(default=False, db_column='T043requiereEnvioEmail')
    nivel_prioridad = models.CharField(max_length=1, choices=NIVEL_PRIORIDAD_CHOICES, db_column='T043nivelPrioridad')
    existe_alertado_previo = models.BooleanField(default=False, db_column='T043existeAlertadoPrevioAEstaProgr')
    activa = models.BooleanField(default=False, db_column='T043activa')

    def __str__(self):
        return str(self.id_alerta_programada)

    class Meta:
        db_table = 'T043AlertasProgramadas'
        verbose_name = 'Alerta Programada'
        verbose_name_plural = 'Alertas Programadas'


class AlertasGeneradas(models.Model):
    id_alerta_generada = models.AutoField(primary_key=True, db_column='T044IdAlertaGenerada')
    nombre_clase_alerta = models.CharField(max_length=50, db_column='T044nombreClaseAlerta')
    mensaje = models.CharField(max_length=2000, db_column='T044mensaje')
    fecha_generada = models.DateTimeField(auto_now=True,db_column='T044fechaGenerada')
    cod_categoria_alerta = models.CharField(max_length=3, db_column='T044codCategoriaAlerta')
    nivel_prioridad = models.SmallIntegerField(db_column='T044nivelPrioridad')
    id_modulo_destino = models.ForeignKey('seguridad.Modulos', related_name='modulo_destino_alertas_generadas', null=True, blank=True, on_delete=models.SET_NULL, db_column='T044Id_ModuloDestino')
    id_modulo_generador = models.ForeignKey('seguridad.Modulos', related_name='modulo_generador_alertas_generadas', on_delete=models.CASCADE, db_column='T044Id_ModuloGenerador')
    id_elemento_implicado = models.IntegerField(null=True, blank=True, db_column='T044idElementoImplicado')
    id_alerta_programada_origen = models.IntegerField(null=True, blank=True, db_column='T044idAlertaProgramada_Origen')
    envio_email = models.BooleanField(default=False, db_column='T044envioEmail')
    es_ultima_repeticion = models.BooleanField(default=False, db_column='T044esLaUltimaRepeticion')

    def __str__(self):
        return str(self.id_alerta_generada)

    class Meta:
        db_table = 'T044AlertasGeneradas'
        verbose_name = 'Alerta Generada'
        verbose_name_plural = 'Alertas Generadas'


class BandejaAlertaPersona(models.Model):
    id_bandeja_alerta = models.AutoField(primary_key=True, db_column='T045IdBandejaAlertas_Persona')
    id_persona = models.OneToOneField('seguridad.Personas', on_delete=models.CASCADE, db_column='T045Id_Persona')
    pendientes_leer = models.BooleanField(default=False, db_column='T045pendientesLeer')
    pendientes_archivar = models.BooleanField(default=False, db_column='T045pendientesArchivar')
    
    def __str__(self):
        return str(self.id_bandeja_alerta)

    class Meta:
        db_table = 'T045BandejasAlertas_Persona'
        verbose_name = 'Bandeja Alerta Persona'
        verbose_name_plural = 'Bandeja Alertas Personas'


class AlertasBandejaAlertaPersona(models.Model):
    id_alerta_bandeja_alerta_persona = models.AutoField(primary_key=True, db_column='T046IdAlertaGen_BandejaAlertas_Pna')
    id_bandeja_alerta_persona = models.ForeignKey(BandejaAlertaPersona, on_delete=models.CASCADE, db_column='T046Id_BandejaAlertas_Persona')
    id_alerta_generada = models.ForeignKey(AlertasGeneradas, on_delete=models.CASCADE, db_column='T046Id_AlertaGenerada')
    leido = models.BooleanField(default=False, db_column='T046leido')
    fecha_leido = models.DateTimeField(null=True, blank=True, db_column='T046fechaLeido')
    archivado = models.BooleanField(default=False, db_column='T046archivado')
    fecha_archivado = models.DateTimeField(null=True, blank=True, db_column='T046fechaArchivado')
    repeticiones_suspendidas = models.BooleanField(default=False, db_column='T046repeticionesSuspendidas')
    fecha_suspencion_repeticion = models.DateTimeField(null=True, blank=True, db_column='T046fechaSuspencionRepeticiones')
    fecha_envio_email = models.DateTimeField(null=True, blank=True, db_column='T046fechaEnvioEmail')
    email_usado = models.CharField(max_length=100, db_column='T046dirEmailUtilizado')
    responsable_directo = models.BooleanField(default=False, db_column='T046responsableDirecto')

    def __str__(self):
        return str(self.id_alerta_bandeja_alerta_persona)

    class Meta:
        db_table = 'T046AlertasGen_BandejaAlertas_Pna'
        verbose_name = 'Alerta Generada Bandeja Alerta Persona'
        verbose_name_plural = 'Alertas Generadas Bandeja Alertas Personas'
        unique_together = ['id_bandeja_alerta_persona', 'id_alerta_generada']


