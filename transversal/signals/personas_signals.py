from django.db.models.signals import pre_save
from django.db.models import Q
from django.dispatch import receiver
from seguridad.models import Personas
        
@receiver(pre_save, sender=Personas)
def create_update_personas(sender, instance, **kwargs):
    if instance.id_persona is None:
        # USA UNIDAD ORGANIZACIONAL
        if instance.id_unidad_organizacional_actual:
            if not instance.id_unidad_organizacional_actual.item_usado:
                instance.id_unidad_organizacional_actual.item_usado = True
                instance.id_unidad_organizacional_actual.save()
    else:
        current=instance
        previous=Personas.objects.filter(id_persona=instance.id_persona).first()
        
        if previous:
            # MODIFICA/USA UNIDAD ORGANIZACIONAL
            if previous.id_unidad_organizacional_actual:
                if current.id_unidad_organizacional_actual:
                    if previous.id_unidad_organizacional_actual.id_unidad_organizacional != current.id_unidad_organizacional_actual.id_unidad_organizacional:
                        if not current.id_unidad_organizacional_actual.item_usado:
                            current.id_unidad_organizacional_actual.item_usado = True
                            current.id_unidad_organizacional_actual.save()
            else:
                if current.id_unidad_organizacional_actual:
                    if not current.id_unidad_organizacional_actual.item_usado:
                        current.id_unidad_organizacional_actual.item_usado = True
                        current.id_unidad_organizacional_actual.save()