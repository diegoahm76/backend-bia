from django.db.models.signals import pre_save
from django.db.models import Q
from django.dispatch import receiver
from almacen.models import CatalogoBienes, Marcas, EntradasAlmacen, ItemEntradaAlmacen, Bodegas, UnidadesMedida, PorcentajesIVA

@receiver(pre_save, sender=CatalogoBienes)
def create_update_catalogo_bienes(sender, instance, **kwargs):
    if instance.id_bien is None:
        # MODIFICA MARCA
        if instance.id_marca:
            bien = CatalogoBienes.objects.filter(id_marca=instance.id_marca.id_marca).first()
            marca = Marcas.objects.filter(id_marca=instance.id_marca.id_marca).first()
            if not bien and not marca.item_ya_usado:
                marca.item_ya_usado=True
                marca.save()
        
        # MODIFICA UNIDAD MEDIDA
        if instance.id_unidad_medida:
            bien = CatalogoBienes.objects.filter(id_unidad_medida=instance.id_unidad_medida.id_unidad_medida).first()
            unidad_medida = UnidadesMedida.objects.filter(id_unidad_medida=instance.id_unidad_medida.id_unidad_medida).first()
            if not bien and not unidad_medida.item_ya_usado:
                unidad_medida.item_ya_usado=True
                unidad_medida.save()
        
        # MODIFICA UNIDAD MEDIDA VIDA UTIL
        if instance.id_unidad_medida_vida_util:
            bien = CatalogoBienes.objects.filter(id_unidad_medida_vida_util=instance.id_unidad_medida_vida_util.id_unidad_medida).first()
            unidad_medida = UnidadesMedida.objects.filter(id_unidad_medida=instance.id_unidad_medida_vida_util.id_unidad_medida).first()
            if not bien and not unidad_medida.item_ya_usado:
                unidad_medida.item_ya_usado=True
                unidad_medida.save()
        
        # MODIFICA PORCENTAJE IVA
        if instance.id_porcentaje_iva:
            bien = CatalogoBienes.objects.filter(id_porcentaje_iva=instance.id_porcentaje_iva.id_porcentaje_iva).first()
            porcentaje_iva = PorcentajesIVA.objects.filter(id_porcentaje_iva=instance.id_porcentaje_iva.id_porcentaje_iva).first()
            if not bien and not porcentaje_iva.item_ya_usado:
                porcentaje_iva.item_ya_usado=True
                porcentaje_iva.save()
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
                        
            # MODIFICA UNIDAD MEDIDA
            if previous.id_unidad_medida:
                if not current.id_unidad_medida:
                    bien = CatalogoBienes.objects.filter(Q(id_unidad_medida=previous.id_unidad_medida.id_unidad_medida) & ~Q(id_bien=previous.id_bien)).first()
                    unidad_medida = UnidadesMedida.objects.filter(id_unidad_medida=previous.id_unidad_medida.id_unidad_medida).first()
                    if not bien:
                        unidad_medida.item_ya_usado=False
                        unidad_medida.save()
                else:
                    if previous.id_unidad_medida.id_unidad_medida != current.id_unidad_medida.id_unidad_medida:
                        bien_current = CatalogoBienes.objects.filter(id_unidad_medida=current.id_unidad_medida.id_unidad_medida).first()
                        bien_previous = CatalogoBienes.objects.filter(Q(id_unidad_medida=previous.id_unidad_medida.id_unidad_medida) & ~Q(id_bien=previous.id_bien)).first()
                        unidad_medida_current = UnidadesMedida.objects.filter(id_unidad_medida=current.id_unidad_medida.id_unidad_medida).first()
                        unidad_medida_previous = UnidadesMedida.objects.filter(id_unidad_medida=previous.id_unidad_medida.id_unidad_medida).first()
                        if not bien_current:
                            unidad_medida_current.item_ya_usado=True
                            unidad_medida_current.save()
                        if not bien_previous:
                            unidad_medida_previous.item_ya_usado=False
                            unidad_medida_previous.save()
            else:
                if current.id_unidad_medida:
                    bien = CatalogoBienes.objects.filter(id_unidad_medida=current.id_unidad_medida.id_unidad_medida).first()
                    unidad_medida = UnidadesMedida.objects.filter(id_unidad_medida=current.id_unidad_medida.id_unidad_medida).first()
                    if not bien:
                        unidad_medida.item_ya_usado=True
                        unidad_medida.save()
                        
            # MODIFICA UNIDAD MEDIDA VIDA UTIL
            if previous.id_unidad_medida_vida_util:
                if not current.id_unidad_medida_vida_util:
                    bien = CatalogoBienes.objects.filter(Q(id_unidad_medida_vida_util=previous.id_unidad_medida_vida_util.id_unidad_medida) & ~Q(id_bien=previous.id_bien)).first()
                    unidad_medida = UnidadesMedida.objects.filter(id_unidad_medida=previous.id_unidad_medida_vida_util.id_unidad_medida).first()
                    if not bien:
                        unidad_medida.item_ya_usado=False
                        unidad_medida.save()
                else:
                    if previous.id_unidad_medida_vida_util.id_unidad_medida != current.id_unidad_medida_vida_util.id_unidad_medida:
                        bien_current = CatalogoBienes.objects.filter(id_unidad_medida_vida_util=current.id_unidad_medida_vida_util.id_unidad_medida).first()
                        bien_previous = CatalogoBienes.objects.filter(Q(id_unidad_medida_vida_util=previous.id_unidad_medida_vida_util.id_unidad_medida) & ~Q(id_bien=previous.id_bien)).first()
                        unidad_medida_current = UnidadesMedida.objects.filter(id_unidad_medida=current.id_unidad_medida_vida_util.id_unidad_medida).first()
                        unidad_medida_previous = UnidadesMedida.objects.filter(id_unidad_medida=previous.id_unidad_medida_vida_util.id_unidad_medida).first()
                        if not bien_current:
                            unidad_medida_current.item_ya_usado=True
                            unidad_medida_current.save()
                        if not bien_previous:
                            unidad_medida_previous.item_ya_usado=False
                            unidad_medida_previous.save()
            else:
                if current.id_unidad_medida_vida_util:
                    bien = CatalogoBienes.objects.filter(id_unidad_medida_vida_util=current.id_unidad_medida_vida_util.id_unidad_medida).first()
                    unidad_medida = UnidadesMedida.objects.filter(id_unidad_medida=current.id_unidad_medida_vida_util.id_unidad_medida).first()
                    if not bien:
                        unidad_medida.item_ya_usado=True
                        unidad_medida.save()
                        
            # MODIFICA PORCENTAJE IVA
            if previous.id_porcentaje_iva:
                if not current.id_porcentaje_iva:
                    bien = CatalogoBienes.objects.filter(Q(id_porcentaje_iva=previous.id_porcentaje_iva.id_porcentaje_iva) & ~Q(id_bien=previous.id_bien)).first()
                    porcentaje_iva = PorcentajesIVA.objects.filter(id_porcentaje_iva=previous.id_porcentaje_iva.id_porcentaje_iva).first()
                    if not bien:
                        porcentaje_iva.item_ya_usado=False
                        porcentaje_iva.save()
                else:
                    if previous.id_porcentaje_iva.id_porcentaje_iva != current.id_porcentaje_iva.id_porcentaje_iva:
                        bien_current = CatalogoBienes.objects.filter(id_porcentaje_iva=current.id_porcentaje_iva.id_porcentaje_iva).first()
                        bien_previous = CatalogoBienes.objects.filter(Q(id_porcentaje_iva=previous.id_porcentaje_iva.id_porcentaje_iva) & ~Q(id_bien=previous.id_bien)).first()
                        unidad_medida_current = PorcentajesIVA.objects.filter(id_porcentaje_iva=current.id_porcentaje_iva.id_porcentaje_iva).first()
                        unidad_medida_previous = PorcentajesIVA.objects.filter(id_porcentaje_iva=previous.id_porcentaje_iva.id_porcentaje_iva).first()
                        if not bien_current:
                            unidad_medida_current.item_ya_usado=True
                            unidad_medida_current.save()
                        if not bien_previous:
                            unidad_medida_previous.item_ya_usado=False
                            unidad_medida_previous.save()
            else:
                if current.id_porcentaje_iva:
                    bien = CatalogoBienes.objects.filter(id_porcentaje_iva=current.id_porcentaje_iva.id_porcentaje_iva).first()
                    porcentaje_iva = PorcentajesIVA.objects.filter(id_porcentaje_iva=current.id_porcentaje_iva.id_porcentaje_iva).first()
                    if not bien:
                        porcentaje_iva.item_ya_usado=True
                        porcentaje_iva.save()

@receiver(pre_save, sender=EntradasAlmacen)
def create_update_entrada(sender, instance, **kwargs):
    if instance.id_entrada_almacen is None:
        if instance.id_bodega:
            entrada_almacen = EntradasAlmacen.objects.filter(id_bodega=instance.id_bodega.id_bodega).first()
            bodega = Bodegas.objects.filter(id_bodega=instance.id_bodega.id_bodega).first()
            if not entrada_almacen and not bodega.item_ya_usado:
                bodega.item_ya_usado=True
                bodega.save()
    else:
        current=instance
        previous=EntradasAlmacen.objects.filter(id_entrada_almacen=instance.id_entrada_almacen).first()
        
        if previous:
            # MODIFICA BODEGA
            if previous.id_bodega:
                if not current.id_bodega:
                    entrada_almacen = EntradasAlmacen.objects.filter(Q(id_bodega=previous.id_bodega.id_bodega) & ~Q(id_entrada_almacen=previous.id_entrada_almacen)).first()
                    bodega = Bodegas.objects.filter(id_bodega=previous.id_bodega.id_bodega).first()
                    if not entrada_almacen:
                        bodega.item_ya_usado=False
                        bodega.save()
                else:
                    if previous.id_bodega.id_bodega != current.id_bodega.id_bodega:
                        entrada_almacen_current = EntradasAlmacen.objects.filter(id_bodega=current.id_bodega.id_bodega).first()
                        entrada_almacen_previous = EntradasAlmacen.objects.filter(Q(id_bodega=previous.id_bodega.id_bodega) & ~Q(id_entrada_almacen=previous.id_entrada_almacen)).first()
                        bodega_current = Bodegas.objects.filter(id_bodega=current.id_bodega.id_bodega).first()
                        bodega_previous = Bodegas.objects.filter(id_bodega=previous.id_bodega.id_bodega).first()
                        if not entrada_almacen_current:
                            bodega_current.item_ya_usado=True
                            bodega_current.save()
                        if not entrada_almacen_previous:
                            bodega_previous.item_ya_usado=False
                            bodega_previous.save()
            else:
                if current.id_bodega:
                    entrada_almacen = EntradasAlmacen.objects.filter(id_bodega=current.id_bodega.id_bodega).first()
                    bodega = Bodegas.objects.filter(id_bodega=current.id_bodega.id_bodega).first()
                    if not entrada_almacen:
                        bodega.item_ya_usado=True
                        bodega.save()

@receiver(pre_save, sender=ItemEntradaAlmacen)
def create_update_items(sender, instance, **kwargs):
    if instance.id_item_entrada_almacen is None:
        # MODIFICA BODEGA
        if instance.id_bodega:
            item_entrada = ItemEntradaAlmacen.objects.filter(id_bodega=instance.id_bodega.id_bodega).first()
            bodega = Bodegas.objects.filter(id_bodega=instance.id_bodega.id_bodega).first()
            if not item_entrada and not bodega.item_ya_usado:
                bodega.item_ya_usado=True
                bodega.save()
        
        # MODIFICA UNIDAD MEDIDA
        if instance.id_unidad_medida_vida_util:
            item_entrada = ItemEntradaAlmacen.objects.filter(id_unidad_medida_vida_util=instance.id_unidad_medida_vida_util.id_unidad_medida).first()
            unidad_medida = UnidadesMedida.objects.filter(id_unidad_medida=instance.id_unidad_medida_vida_util.id_unidad_medida).first()
            if not item_entrada and not unidad_medida.item_ya_usado:
                unidad_medida.item_ya_usado=True
                unidad_medida.save()
    else:
        current=instance
        previous=ItemEntradaAlmacen.objects.filter(id_item_entrada_almacen=instance.id_item_entrada_almacen).first()
        
        if previous:
            # MODIFICA BODEGA
            if previous.id_bodega:
                if not current.id_bodega:
                    item_entrada = ItemEntradaAlmacen.objects.filter(Q(id_bodega=previous.id_bodega.id_bodega) & ~Q(id_item_entrada_almacen=previous.id_item_entrada_almacen)).first()
                    bodega = Bodegas.objects.filter(id_bodega=previous.id_bodega.id_bodega).first()
                    if not item_entrada:
                        bodega.item_ya_usado=False
                        bodega.save()
                else:
                    if previous.id_bodega.id_bodega != current.id_bodega.id_bodega:
                        item_entrada_current = ItemEntradaAlmacen.objects.filter(id_bodega=current.id_bodega.id_bodega).first()
                        item_entrada_previous = ItemEntradaAlmacen.objects.filter(Q(id_bodega=previous.id_bodega.id_bodega) & ~Q(id_item_entrada_almacen=previous.id_item_entrada_almacen)).first()
                        bodega_current = Bodegas.objects.filter(id_bodega=current.id_bodega.id_bodega).first()
                        bodega_previous = Bodegas.objects.filter(id_bodega=previous.id_bodega.id_bodega).first()
                        if not item_entrada_current:
                            bodega_current.item_ya_usado=True
                            bodega_current.save()
                        if not item_entrada_previous:
                            bodega_previous.item_ya_usado=False
                            bodega_previous.save()
            else:
                if current.id_bodega:
                    item_entrada = ItemEntradaAlmacen.objects.filter(id_bodega=current.id_bodega.id_bodega).first()
                    bodega = Bodegas.objects.filter(id_bodega=current.id_bodega.id_bodega).first()
                    if not item_entrada:
                        bodega.item_ya_usado=True
                        bodega.save()
            
            # MODIFICA UNIDAD MEDIDA
            if previous.id_unidad_medida_vida_util:
                if not current.id_unidad_medida_vida_util:
                    item_entrada = ItemEntradaAlmacen.objects.filter(Q(id_unidad_medida_vida_util=previous.id_unidad_medida_vida_util.id_unidad_medida) & ~Q(id_item_entrada_almacen=previous.id_item_entrada_almacen)).first()
                    unidad_medida = UnidadesMedida.objects.filter(id_unidad_medida=previous.id_unidad_medida_vida_util.id_unidad_medida).first()
                    if not item_entrada:
                        unidad_medida.item_ya_usado=False
                        unidad_medida.save()
                else:
                    if previous.id_unidad_medida_vida_util.id_unidad_medida != current.id_unidad_medida_vida_util.id_unidad_medida:
                        item_entrada_current = ItemEntradaAlmacen.objects.filter(id_unidad_medida_vida_util=current.id_unidad_medida_vida_util.id_unidad_medida).first()
                        item_entrada_previous = ItemEntradaAlmacen.objects.filter(Q(id_unidad_medida_vida_util=previous.id_unidad_medida_vida_util.id_unidad_medida) & ~Q(id_item_entrada_almacen=previous.id_item_entrada_almacen)).first()
                        unidad_medida_current = UnidadesMedida.objects.filter(id_unidad_medida=current.id_unidad_medida_vida_util.id_unidad_medida).first()
                        unidad_medida_previous = UnidadesMedida.objects.filter(id_unidad_medida=previous.id_unidad_medida_vida_util.id_unidad_medida).first()
                        if not item_entrada_current:
                            unidad_medida_current.item_ya_usado=True
                            unidad_medida_current.save()
                        if not item_entrada_previous:
                            unidad_medida_previous.item_ya_usado=False
                            unidad_medida_previous.save()
            else:
                if current.id_unidad_medida_vida_util:
                    item_entrada = ItemEntradaAlmacen.objects.filter(id_unidad_medida_vida_util=current.id_unidad_medida_vida_util.id_unidad_medida).first()
                    unidad_medida = UnidadesMedida.objects.filter(id_unidad_medida=current.id_unidad_medida_vida_util.id_unidad_medida).first()
                    if not item_entrada:
                        unidad_medida.item_ya_usado=True
                        unidad_medida.save()