from django.db.models.signals import post_save, pre_delete,pre_save
from django.dispatch import receiver
from seguridad.models import User, HistoricoActivacion

@receiver(pre_save, sender=User)
def create_historico_users(sender, instance, **kwargs):
    if instance.id_usuario is None:
        pass
    else:
        current=instance
        previous=User.objects.filter(id_usuario=instance.id_usuario).first()
        
        if previous:
            # MODIFICA IS_ACTIVE
            if (previous.is_active != current.is_active) and (current.is_active):
                historico_activacion = HistoricoActivacion.objects.create(
                    id_usuario_afectado = current,
                    cod_operacion = 'A',
                    justificacion = 'Verificación de usuario'
                )
                historico_activacion.save()
            elif (previous.is_active != current.is_active) and (current.is_active == False):
                historico_activacion = HistoricoActivacion.objects.create(
                    id_usuario_afectado = current,
                    cod_operacion = 'D',
                    justificacion = 'Desactivación de usuario',
                )
                historico_activacion.save()
            
            # MODIFICA IS_BLOCKED
            if (previous.is_blocked != current.is_blocked) and (current.is_blocked):
                historico_activacion = HistoricoActivacion.objects.create(
                    id_usuario_afectado = current,
                    cod_operacion = 'B',
                    justificacion = 'Bloqueo de usuario',
                )
                historico_activacion.save()
            elif (previous.is_blocked != current.is_blocked) and (current.is_blocked == False):
                historico_activacion = HistoricoActivacion.objects.create(
                    id_usuario_afectado = current,
                    cod_operacion = 'U',
                    justificacion = 'Desbloqueo de usuario',
                )
                historico_activacion.save()
                