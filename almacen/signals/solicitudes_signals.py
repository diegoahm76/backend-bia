from django.db.models.signals import pre_save
from django.db.models import Q
from django.dispatch import receiver
from almacen.models.solicitudes_models import ItemsSolicitudConsumible
from almacen.models import UnidadesMedida

@receiver(pre_save, sender=ItemsSolicitudConsumible)
def create_update_solicitudes(sender, instance, **kwargs):
    if instance.id_item_solicitud_consumible is None:
        if instance.id_unidad_medida:
            item_solicitud = ItemsSolicitudConsumible.objects.filter(id_unidad_medida=instance.id_unidad_medida.id_unidad_medida).first()
            unidad_medida = UnidadesMedida.objects.filter(id_unidad_medida=instance.id_unidad_medida.id_unidad_medida).first()
            if not item_solicitud and not unidad_medida.item_ya_usado:
                unidad_medida.item_ya_usado=True
                unidad_medida.save()
    else:
        current=instance
        previous=ItemsSolicitudConsumible.objects.filter(id_item_solicitud_consumible=instance.id_item_solicitud_consumible).first()
        
        if previous:
            # MODIFICA UNIDAD MEDIDA
            if previous.id_unidad_medida:
                if not current.id_unidad_medida:
                    item_solicitud = ItemsSolicitudConsumible.objects.filter(Q(id_unidad_medida=previous.id_unidad_medida.id_unidad_medida) & ~Q(id_item_solicitud_consumible=previous.id_item_solicitud_consumible)).first()
                    unidad_medida = UnidadesMedida.objects.filter(id_unidad_medida=previous.id_unidad_medida.id_unidad_medida).first()
                    if not item_solicitud:
                        unidad_medida.item_ya_usado=False
                        unidad_medida.save()
                else:
                    if previous.id_unidad_medida.id_unidad_medida != current.id_unidad_medida.id_unidad_medida:
                        item_solicitud_current = ItemsSolicitudConsumible.objects.filter(id_unidad_medida=current.id_unidad_medida.id_unidad_medida).first()
                        item_solicitud_previous = ItemsSolicitudConsumible.objects.filter(Q(id_unidad_medida=previous.id_unidad_medida.id_unidad_medida) & ~Q(id_item_solicitud_consumible=previous.id_item_solicitud_consumible)).first()
                        unidad_medida_current = UnidadesMedida.objects.filter(id_unidad_medida=current.id_unidad_medida.id_unidad_medida).first()
                        unidad_medida_previous = UnidadesMedida.objects.filter(id_unidad_medida=previous.id_unidad_medida.id_unidad_medida).first()
                        if not item_solicitud_current:
                            unidad_medida_current.item_ya_usado=True
                            unidad_medida_current.save()
                        if not item_solicitud_previous:
                            unidad_medida_previous.item_ya_usado=False
                            unidad_medida_previous.save()
            else:
                if current.id_unidad_medida:
                    item_solicitud = ItemsSolicitudConsumible.objects.filter(id_unidad_medida=current.id_unidad_medida.id_unidad_medida).first()
                    unidad_medida = UnidadesMedida.objects.filter(id_unidad_medida=current.id_unidad_medida.id_unidad_medida).first()
                    if not item_solicitud:
                        unidad_medida.item_ya_usado=True
                        unidad_medida.save()