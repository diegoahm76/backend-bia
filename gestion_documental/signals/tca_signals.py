from django.db.models.signals import pre_save
from django.db.models import Q
from django.dispatch import receiver
# from gestion_documental.models.tca_models import PermisosCatSeriesUnidadOrgTCA
from transversal.models.base_models import Cargos

# @receiver(pre_save, sender=PermisosCatSeriesUnidadOrgTCA)
# def create_update_cargos_unidad(sender, instance, **kwargs):
#     if instance.id_cargo_unidad_s_subserie_unidad_org_tca is None:
#         cargo_unidad = PermisosCatSeriesUnidadOrgTCA.objects.filter(id_cargo_persona=instance.id_cargo_persona.id_cargo).first()
#         cargo = Cargos.objects.filter(id_cargo=instance.id_cargo_persona.id_cargo).first()
#         if not cargo_unidad and not cargo.item_usado:
#             cargo.item_usado=True
#             cargo.save()
#     else:
#         current=instance
#         previous=PermisosCatSeriesUnidadOrgTCA.objects.filter(id_cargo_unidad_s_subserie_unidad_org_tca=instance.id_cargo_unidad_s_subserie_unidad_org_tca).first()
        
#         if previous:
#             # MODIFICA CARGO
#             if previous.id_cargo_persona:
#                 if current.id_cargo_persona:
#                     if previous.id_cargo_persona.id_cargo != current.id_cargo_persona.id_cargo:
#                         cargo_unidad_current = PermisosCatSeriesUnidadOrgTCA.objects.filter(id_cargo_persona=current.id_cargo_persona.id_cargo).first()
#                         cargo_current = Cargos.objects.filter(id_cargo=current.id_cargo_persona.id_cargo).first()
#                         if not cargo_unidad_current:
#                             cargo_current.item_usado=True
#                             cargo_current.save()
#             else:
#                 if current.id_cargo_persona:
#                     cargo_unidad = PermisosCatSeriesUnidadOrgTCA.objects.filter(id_cargo_persona=current.id_cargo_persona.id_cargo).first()
#                     cargo = Cargos.objects.filter(id_cargo=current.id_cargo_persona.id_cargo).first()
#                     if not cargo_unidad:
#                         cargo.item_usado=True
#                         cargo.save()