
#T264
#T265 YA CREADAS

from django.db import models
from gestion_documental.choices.estado_asignacion_choices import ESTADO_ASIGNACION_CHOICES
from gestion_documental.choices.estado_reasignacion_choices import ESTADO_REASIGNACION_CHOICES
from gestion_documental.choices.estado_solicitud_choices import ESTADO_SOLICITUD_TAREA_CHOICES
from gestion_documental.choices.tipos_tareas_choices import TIPOS_TAREA_CHOICES

from gestion_documental.models.radicados_models import ComplementosUsu_PQR
from tramites.models.tramites_models import RespuestasRequerimientos






class TareasAsignadas(models.Model):


    id_tarea_asignada = models.AutoField(primary_key=True, db_column='T315IdTareaAsignada')
    cod_tipo_tarea = models.CharField(max_length=5, choices=TIPOS_TAREA_CHOICES, db_column='T315codTipoTarea')
    id_asignacion = models.IntegerField(null=True,db_column='T315idAsignacion')
    fecha_asignacion = models.DateTimeField(db_column='T315fechaAsignacion')
    comentario_asignacion = models.CharField(max_length=255, null=True, db_column='T315comentarioAsignacion')
    cod_estado_asignacion = models.CharField(max_length=2, null= True,choices=ESTADO_ASIGNACION_CHOICES, db_column='T315codEstadoAsignacion')
    justificacion_rechazo = models.CharField(max_length=255, null=True, db_column='T315justificacionRechazo')
    cod_estado_solicitud = models.CharField(max_length=2, choices=ESTADO_SOLICITUD_TAREA_CHOICES, db_column='T315codEstadoSolicitud')
    fecha_respondido = models.DateTimeField(null=True, db_column='T315fechaRespondido')
    nombre_persona_que_responde = models.CharField(max_length=255, null=True, db_column='T315nombrePersonaQueResponde')
    ya_respondido_por_un_delegado = models.BooleanField(default=False, db_column='T315yaRespondidoPorUnDelegado')
    requerimientos_pendientes_respuesta = models.BooleanField(default=False, db_column='T315requerimientosPendientesRespuesta')
    id_tarea_asignada_padre_inmediata = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.CASCADE,
        db_column='T315IdTareaAsignadaPadreInmediata'
    )

    class Meta:

        db_table = 'T315TareasAsignadas'  
        verbose_name = 'Tarea Asignada'  
        verbose_name_plural = 'Tareas Asignadas'
        unique_together = ['id_asignacion', 'cod_tipo_tarea'] 
        # constraints = [
        #     models.UniqueConstraint(fields=['id_asignacion'], name='unique_asignacion_constraint')
        # ]

class ReasignacionesTareas(models.Model):


    id_reasignacion_tarea = models.AutoField(primary_key=True, db_column='T316IdReasignacionTarea')
    id_tarea_asignada = models.ForeignKey(
        TareasAsignadas,
        on_delete=models.CASCADE,
        db_column='T316IdTareaAsignada',
        related_name='reasignaciones'
    )
    id_persona_a_quien_se_reasigna = models.ForeignKey(
        'transversal.Personas',
        on_delete=models.CASCADE,
        db_column='T316IdPersonaAQuienSeReasigna'
    )
    comentario_reasignacion = models.CharField(max_length=255, null=True, db_column='T316comentarioReasignacion')
    fecha_reasignacion = models.DateTimeField(db_column='T316fechaReasignacion',null=True)
    cod_estado_reasignacion = models.CharField(max_length=2, choices=ESTADO_REASIGNACION_CHOICES, db_column='T316codEstadoReasignacion')
    justificacion_reasignacion_rechazada = models.CharField(max_length=255, null=True, db_column='T316justificacionReasignacionRechazada')

    class Meta:
        db_table = 'T316Reasignaciones_Tareas'
        verbose_name = 'Reasignación de Tarea'
        verbose_name_plural = 'Reasignaciones de Tareas'



class AdicionalesDeTareas(models.Model):
    id_adicional_de_tarea = models.AutoField(primary_key=True, db_column='T317IdAdicionalDeTarea')
    id_complemento_usu_pqr = models.ForeignKey(
        ComplementosUsu_PQR,
        null=True,
        on_delete=models.SET_NULL,
        db_column='T317IdComplementoUsuPQR',
        related_name='adicionales_tareas'
    )
    id_tarea_asignada = models.ForeignKey(
        TareasAsignadas,
        on_delete=models.CASCADE,
        db_column='T317IdTareaAsignada',
        related_name='adicionales_tareas'
    )
    fecha_de_adicion = models.DateTimeField(db_column='T317fechaDeAdicion')

    id_respuesta_requerimiento = models.ForeignKey(RespuestasRequerimientos,
    null = True,
    on_delete=models.SET_NULL,
    db_column='T317IdRespuestasRequerimientos',
    default = None
    ,
    )
    class Meta:
        db_table = 'T317AdicionalesDeTareas'
        verbose_name = 'Adicional de Tarea'
        verbose_name_plural = 'Adicionales de Tareas'
        unique_together = ['id_complemento_usu_pqr', 'id_tarea_asignada']


