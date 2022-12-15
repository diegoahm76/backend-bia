from django.db.models.signals import pre_save
from django.db.models import Q
from django.dispatch import receiver
from almacen.models import CatalogoBienes, Marcas

@receiver(pre_save, sender=CatalogoBienes)
def create_update_marcas(sender, instance, **kwargs):
    if instance.id_bien is None:
        bien = CatalogoBienes.objects.filter(id_marca=instance.id_marca.id_marca).first()
        marca = Marcas.objects.filter(id_marca=instance.id_marca.id_marca).first()
        if not bien and not marca.item_ya_usado:
            marca.item_ya_usado=True
            marca.save()
    else:
        current=instance
        previous=CatalogoBienes.objects.filter(id_bien=instance.id_bien).first()
        
        if previous:
            # MODIFICA MARCA
            if previous.id_marca:
                if not current.id_marca:
                    bien = CatalogoBienes.objects.filter(Q(id_marca=previous.id_marca.id_marca) & ~Q(id_bien=previous.id_bien)).first()
                    marca = Marcas.objects.filter(id_marca=previous.id_marca.id_marca).first()
                    if not bien:
                        marca.item_ya_usado=False
                        marca.save()
                else:
                    if previous.id_marca.id_marca != current.id_marca.id_marca:
                        bien_current = CatalogoBienes.objects.filter(id_marca=current.id_marca.id_marca).first()
                        bien_previous = CatalogoBienes.objects.filter(Q(id_marca=previous.id_marca.id_marca) & ~Q(id_bien=previous.id_bien)).first()
                        marca_current = Marcas.objects.filter(id_marca=current.id_marca.id_marca).first()
                        marca_previous = Marcas.objects.filter(id_marca=previous.id_marca.id_marca).first()
                        if not bien_current:
                            marca_current.item_ya_usado=True
                            marca_current.save()
                        if not bien_previous:
                            marca_previous.item_ya_usado=False
                            marca_previous.save()
            else:
                if current.id_marca:
                    bien = CatalogoBienes.objects.filter(id_marca=current.id_marca.id_marca).first()
                    marca = Marcas.objects.filter(id_marca=current.id_marca.id_marca).first()
                    if not bien:
                        marca.item_ya_usado=True
                        marca.save()