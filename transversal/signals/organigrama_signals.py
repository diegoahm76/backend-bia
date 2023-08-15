from django.db.models.signals import post_save
from django.db.models import Q
from django.dispatch import receiver
from transversal.models.organigrama_models import UnidadesOrganizacionales

@receiver(post_save, sender=UnidadesOrganizacionales)
def create_unidades_org(sender, instance, created, **kwargs):
    if created:
        instance.id_unidad_org_actual_admin_series = instance
        instance.save()