from django.db.models.signals import pre_save
from django.db.models import Q
from django.dispatch import receiver
from almacen.models import Inventario, Bodegas

@receiver(pre_save, sender=Inventario)
def create_update_bodega_inventario(sender, instance, **kwargs):
    if instance.id_inventario is None:
        if instance.id_bodega:
            inventario = Inventario.objects.filter(id_bodega=instance.id_bodega.id_bodega).first()
            bodega = Bodegas.objects.filter(id_bodega=instance.id_bodega.id_bodega).first()
            if not inventario and not bodega.item_ya_usado:
                bodega.item_ya_usado=True
                bodega.save()
    else:
        current=instance
        previous=Inventario.objects.filter(id_inventario=instance.id_inventario).first()
        
        if previous:
            # MODIFICA BODEGA
            if previous.id_bodega:
                if current.id_bodega:
                    if previous.id_bodega.id_bodega != current.id_bodega.id_bodega:
                        inventario_current = Inventario.objects.filter(id_bodega=current.id_bodega.id_bodega).first()
                        bodega_current = Bodegas.objects.filter(id_bodega=current.id_bodega.id_bodega).first()
                        if not inventario_current:
                            bodega_current.item_ya_usado=True
                            bodega_current.save()
            else:
                if current.id_bodega:
                    inventario = Inventario.objects.filter(id_bodega=current.id_bodega.id_bodega).first()
                    bodega = Bodegas.objects.filter(id_bodega=current.id_bodega.id_bodega).first()
                    if not inventario:
                        bodega.item_ya_usado=True
                        bodega.save()