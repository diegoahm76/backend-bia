from django.db.models.signals import post_save, pre_delete,pre_save
from django.dispatch import receiver
from seguridad.models import Personas, HistoricoEmails, HistoricoDireccion

@receiver(pre_save, sender=Personas)
def create_historico_personas(sender, instance, **kwargs):
    if instance.id_persona is None:
        pass
    else:
        current=instance
        previous=Personas.objects.filter(id_persona=instance.id_persona).first()
        
        if previous:
            # MODIFICA EMAIL PRINCIPAL
            if previous.email!= current.email:
                historico_email = HistoricoEmails.objects.create(
                    id_persona = current,
                    email_notificacion = current.email
                )
                historico_email.save()
            
            # MODIFICA DIRECCION
            if previous.direccion_laboral!= current.direccion_laboral:
                if current.direccion_laboral:
                    direccion = current.direccion_laboral
                else:
                    direccion = ''
                cod_municipio = current.cod_municipio_laboral_nal if previous.cod_municipio_laboral_nal!= current.cod_municipio_laboral_nal else None
                cod_pais_exterior = current.pais_residencia if previous.pais_residencia!= current.pais_residencia else None
                
                historico_direccion = HistoricoDireccion.objects.create(
                    direccion = direccion,
                    tipo_direccion = 'LAB',
                    id_persona = current,
                    cod_municipio = cod_municipio,
                    cod_pais_exterior = cod_pais_exterior
                )
                historico_direccion.save()
                
            if previous.direccion_residencia!= current.direccion_residencia:
                if current.direccion_residencia:
                    direccion = current.direccion_residencia
                else:
                    direccion = ''
                cod_municipio = current.municipio_residencia if previous.municipio_residencia!= current.municipio_residencia else None
                cod_pais_exterior = current.pais_residencia if previous.pais_residencia!= current.pais_residencia else None
                
                historico_direccion = HistoricoDireccion.objects.create(
                    direccion = direccion,
                    tipo_direccion = 'RES',
                    id_persona = current,
                    cod_municipio = cod_municipio,
                    cod_pais_exterior = cod_pais_exterior
                )
                historico_direccion.save()
                
            if previous.direccion_notificaciones!= current.direccion_notificaciones:
                if current.direccion_notificaciones:
                    direccion = current.direccion_notificaciones
                else:
                    direccion = ''
                if current.tipo_persona == 'J':
                    cod_pais_exterior = current.cod_pais_nacionalidad_empresa if previous.cod_pais_nacionalidad_empresa!= current.cod_pais_nacionalidad_empresa else None
                else:
                    cod_pais_exterior = current.pais_residencia if previous.pais_residencia!= current.pais_residencia else None
                cod_municipio = current.cod_municipio_notificacion_nal if previous.cod_municipio_notificacion_nal!= current.cod_municipio_notificacion_nal else None
                
                historico_direccion = HistoricoDireccion.objects.create(
                    direccion = direccion,
                    tipo_direccion = 'NOT',
                    id_persona = current,
                    cod_municipio = cod_municipio,
                    cod_pais_exterior = cod_pais_exterior
                )
                historico_direccion.save()
                