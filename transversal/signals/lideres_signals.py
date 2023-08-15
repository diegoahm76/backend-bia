from django.db.models.signals import pre_save
from django.db.models import Q
from django.dispatch import receiver
from transversal.models.lideres_models import LideresUnidadesOrg
        
@receiver(pre_save, sender=LideresUnidadesOrg)
def create_update_lider_unidad_org(sender, instance, **kwargs):
    if instance.id_lider_unidad_org is None:
        # USA UNIDAD ORGANIZACIONAL
        if instance.id_unidad_organizacional:
            if not instance.id_unidad_organizacional.item_usado:
                instance.id_unidad_organizacional.item_usado = True
                instance.id_unidad_organizacional.save()
    else:
        current=instance
        previous=LideresUnidadesOrg.objects.filter(id_lider_unidad_org=instance.id_lider_unidad_org).first()
        
        if previous:
            # MODIFICA/USA UNIDAD ORGANIZACIONAL
            if previous.id_unidad_organizacional:
                if current.id_unidad_organizacional:
                    if previous.id_unidad_organizacional.id_unidad_organizacional != current.id_unidad_organizacional.id_unidad_organizacional:
                        if not current.id_unidad_organizacional.item_usado:
                            current.id_unidad_organizacional.item_usado = True
                            current.id_unidad_organizacional.save()
            else:
                if current.id_unidad_organizacional:
                    if not current.id_unidad_organizacional.item_usado:
                        current.id_unidad_organizacional.item_usado = True
                        current.id_unidad_organizacional.save()