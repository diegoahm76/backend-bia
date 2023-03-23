from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from gestion_documental.models.trd_models import FormatosTiposMedioTipoDoc, FormatosTiposMedio
        
@receiver(post_save, sender=FormatosTiposMedioTipoDoc)
def create_item_usado_formatos(sender, instance, **kwargs):
    formatos_tipologias = FormatosTiposMedioTipoDoc.objects.filter(id_formato_tipo_medio=instance.id_formato_tipo_medio.id_formato_tipo_medio)
    formato_tipo_medio = FormatosTiposMedio.objects.filter(id_formato_tipo_medio=instance.id_formato_tipo_medio.id_formato_tipo_medio).first()
    if formatos_tipologias:
        formato_tipo_medio.item_ya_usado=True
        formato_tipo_medio.save()