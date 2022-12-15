from django.db.models.signals import pre_save
from django.db.models import Q
from django.dispatch import receiver
from gestion_documental.models.tca_models import Cargos_Unidad_S_Ss_UndOrg_TCA
from seguridad.models import Cargos

@receiver(pre_save, sender=Cargos_Unidad_S_Ss_UndOrg_TCA)
def create_update_cargos_unidad(sender, instance, **kwargs):
    if instance.id_cargo_unidad_s_subserie_unidad_org_tca is None:
        cargo_unidad = Cargos_Unidad_S_Ss_UndOrg_TCA.objects.filter(id_cargo_persona=instance.id_cargo_persona.id_cargo).first()
        cargo = Cargos.objects.filter(id_cargo=instance.id_cargo_persona.id_cargo).first()
        if not cargo_unidad and not cargo.item_usado:
            cargo.item_usado=True
            cargo.save()
    else:
        current=instance
        previous=Cargos_Unidad_S_Ss_UndOrg_TCA.objects.filter(id_cargo_unidad_s_subserie_unidad_org_tca=instance.id_cargo_unidad_s_subserie_unidad_org_tca).first()
        
        if previous:
            # MODIFICA CARGO
            if previous.id_cargo_persona:
                if not current.id_cargo_persona:
                    cargo_unidad = Cargos_Unidad_S_Ss_UndOrg_TCA.objects.filter(Q(id_cargo_persona=previous.id_cargo_persona.id_cargo) & ~Q(id_cargo_unidad_s_subserie_unidad_org_tca=previous.id_cargo_unidad_s_subserie_unidad_org_tca)).first()
                    cargo = Cargos.objects.filter(id_cargo=previous.id_cargo_persona.id_cargo).first()
                    if not cargo_unidad:
                        cargo.item_usado=False
                        cargo.save()
                else:
                    if previous.id_cargo_persona.id_cargo != current.id_cargo_persona.id_cargo:
                        cargo_unidad_current = Cargos_Unidad_S_Ss_UndOrg_TCA.objects.filter(id_cargo_persona=current.id_cargo_persona.id_cargo).first()
                        cargo_unidad_previous = Cargos_Unidad_S_Ss_UndOrg_TCA.objects.filter(Q(id_cargo_persona=previous.id_cargo_persona.id_cargo) & ~Q(id_cargo_unidad_s_subserie_unidad_org_tca=previous.id_cargo_unidad_s_subserie_unidad_org_tca)).first()
                        cargo_current = Cargos.objects.filter(id_cargo=current.id_cargo_persona.id_cargo).first()
                        cargo_previous = Cargos.objects.filter(id_cargo=previous.id_cargo_persona.id_cargo).first()
                        if not cargo_unidad_current:
                            cargo_current.item_usado=True
                            cargo_current.save()
                        if not cargo_unidad_previous:
                            cargo_previous.item_usado=False
                            cargo_previous.save()
            else:
                if current.id_cargo_persona:
                    cargo_unidad = Cargos_Unidad_S_Ss_UndOrg_TCA.objects.filter(id_cargo_persona=current.id_cargo_persona.id_cargo).first()
                    cargo = Cargos.objects.filter(id_cargo=current.id_cargo_persona.id_cargo).first()
                    if not cargo_unidad:
                        cargo.item_usado=True
                        cargo.save()