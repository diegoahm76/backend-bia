from django.db.models.signals import pre_save
from django.db.models import Q
from django.dispatch import receiver
from datetime import datetime
from transversal.models.base_models import (
    HistoricoEmails,
    HistoricoDireccion,
    HistoricoAutirzacionesNotis,
    HistoricoRepresentLegales
)
from transversal.models.personas_models import Personas
from transversal.models.base_models import Cargos
from transversal.models.base_models import EstadoCivil, TipoDocumento

@receiver(pre_save, sender=Personas)
def create_historico_personas(sender, instance, **kwargs):
    if instance.id_persona is None:
        # MODIFICA TIPO DOCUMENTO
        if instance.tipo_documento:
            persona = Personas.objects.filter(tipo_documento=instance.tipo_documento.cod_tipo_documento).first()
            tipo_documento = TipoDocumento.objects.filter(cod_tipo_documento=instance.tipo_documento.cod_tipo_documento).first()
            if not persona and not tipo_documento.item_ya_usado:
                tipo_documento.item_ya_usado=True
                tipo_documento.save()
                
        # MODIFICA ESTADO CIVIL
        if instance.estado_civil:
            persona = Personas.objects.filter(estado_civil=instance.estado_civil.cod_estado_civil).first()
            estado_civil = EstadoCivil.objects.filter(cod_estado_civil=instance.estado_civil.cod_estado_civil).first()
            if not persona and not estado_civil.item_ya_usado:
                estado_civil.item_ya_usado=True
                estado_civil.save()
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
            
            # MODIFICA NOTIFICACION SMS O EMAIL
            if previous.acepta_notificacion_sms!= current.acepta_notificacion_sms or previous.acepta_notificacion_email != current.acepta_notificacion_email:
                fecha = previous.fecha_creacion if not previous.fecha_ultim_actualizacion_autorizaciones else previous.fecha_ultim_actualizacion_autorizaciones 
                HistoricoAutirzacionesNotis.objects.create(
                    id_persona = previous,
                    respuesta_autorizacion_sms = previous.acepta_notificacion_sms,
                    respuesta_autorizacion_mail = previous.acepta_notificacion_email,
                    fecha_inicio = fecha,
                    fecha_fin = datetime.now()
                )
            #MODIFICA HISTORICO DE REPRESENTANTE LEGAL
            if previous.representante_legal != current.representante_legal:
                
                historico = HistoricoRepresentLegales.objects.filter(id_persona_empresa = previous).last()
                
                if historico:
                    consecutivo = historico.consec_representacion + 1
                else:
                    consecutivo = 1
                
                HistoricoRepresentLegales.objects.create(
                    id_persona_empresa = previous,
                    consec_representacion = consecutivo,
                    id_persona_represent_legal = previous.representante_legal,
                    fecha_cambio_sistema = datetime.now(),
                    fecha_inicio_cargo = previous.fecha_inicio_cargo_rep_legal
                )
                
            # MODIFICA CARGO
            if previous.id_cargo:
                if not current.id_cargo:
                    persona_cargo = Personas.objects.filter(Q(id_cargo=previous.id_cargo.id_cargo) & ~Q(id_persona=previous.id_persona)).first()
                    cargo = Cargos.objects.filter(id_cargo=previous.id_cargo.id_cargo).first()
                    if not persona_cargo:
                        cargo.item_usado=False
                        cargo.save()
                else:
                    if previous.id_cargo.id_cargo != current.id_cargo.id_cargo:
                        persona_cargo_current = Personas.objects.filter(id_cargo=current.id_cargo.id_cargo).first()
                        persona_cargo_previous = Personas.objects.filter(Q(id_cargo=previous.id_cargo.id_cargo) & ~Q(id_persona=previous.id_persona)).first()
                        cargo_current = Cargos.objects.filter(id_cargo=current.id_cargo.id_cargo).first()
                        cargo_previous = Cargos.objects.filter(id_cargo=previous.id_cargo.id_cargo).first()
                        if not persona_cargo_current:
                            cargo_current.item_usado=True
                            cargo_current.save()
                        if not persona_cargo_previous:
                            cargo_previous.item_usado=False
                            cargo_previous.save()
            else:
                if current.id_cargo:
                    persona_cargo = Personas.objects.filter(id_cargo=current.id_cargo.id_cargo).first()
                    cargo = Cargos.objects.filter(id_cargo=current.id_cargo.id_cargo).first()
                    if not persona_cargo:
                        cargo.item_usado=True
                        cargo.save()
                
            
            # MODIFICA DIRECCION
            if previous.direccion_laboral!= current.direccion_laboral:
                if current.direccion_laboral:
                    direccion = current.direccion_laboral
                else:
                    direccion = ''
                cod_municipio = current.cod_municipio_laboral_nal if previous.cod_municipio_laboral_nal.cod_municipio != current.cod_municipio_laboral_nal.cod_municipio else None
                cod_pais_exterior = current.pais_residencia if previous.pais_residencia.cod_pais != current.pais_residencia.cod_pais else None
                
                historico_direccion = HistoricoDireccion.objects.create(
                    direccion = direccion,
                    tipo_direccion = 'Lab',
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
                cod_municipio = current.municipio_residencia if previous.municipio_residencia.cod_municipio != current.municipio_residencia.cod_municipio else None
                cod_pais_exterior = current.pais_residencia if previous.pais_residencia.cod_pais != current.pais_residencia.cod_pais else None
                
                historico_direccion = HistoricoDireccion.objects.create(
                    direccion = direccion,
                    tipo_direccion = 'Res',
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
                    cod_pais_exterior = current.cod_pais_nacionalidad_empresa if previous.cod_pais_nacionalidad_empresa.cod_pais != current.cod_pais_nacionalidad_empresa.cod_pais else None
                else:
                    cod_pais_exterior = current.pais_residencia if previous.pais_residencia.cod_pais != current.pais_residencia.cod_pais else None
                cod_municipio = current.cod_municipio_notificacion_nal if previous.cod_municipio_notificacion_nal.cod_municipio != current.cod_municipio_notificacion_nal.cod_municipio else None
                
                historico_direccion = HistoricoDireccion.objects.create(
                    direccion = direccion,
                    tipo_direccion = 'Not',
                    id_persona = current,
                    cod_municipio = cod_municipio,
                    cod_pais_exterior = cod_pais_exterior
                )
                historico_direccion.save()
            
            # MODIFICA TIPO DOCUMENTO
            if previous.tipo_documento:
                if current.tipo_documento:
                    if previous.tipo_documento.cod_tipo_documento != current.tipo_documento.cod_tipo_documento:
                        persona_current = Personas.objects.filter(tipo_documento=current.tipo_documento.cod_tipo_documento).first()
                        tipo_documento_current = TipoDocumento.objects.filter(cod_tipo_documento=current.tipo_documento.cod_tipo_documento).first()
                        if not persona_current:
                            tipo_documento_current.item_ya_usado=True
                            tipo_documento_current.save()
            else:
                if current.tipo_documento:
                    persona = Personas.objects.filter(tipo_documento=current.tipo_documento.cod_tipo_documento).first()
                    tipo_documento = TipoDocumento.objects.filter(tipo_documento=current.tipo_documento.cod_tipo_documento).first()
                    if not persona:
                        tipo_documento.item_ya_usado=True
                        tipo_documento.save()
            
            # MODIFICA ESTADO CIVIL
            if previous.estado_civil:
                if current.estado_civil:
                    if previous.estado_civil.cod_estado_civil != current.estado_civil.cod_estado_civil:
                        persona_current = Personas.objects.filter(estado_civil=current.estado_civil.cod_estado_civil).first()
                        estado_civil_current = EstadoCivil.objects.filter(cod_estado_civil=current.estado_civil.cod_estado_civil).first()
                        if not persona_current:
                            estado_civil_current.item_ya_usado=True
                            estado_civil_current.save()
            else:
                if current.estado_civil:
                    persona = Personas.objects.filter(estado_civil=current.estado_civil.cod_estado_civil).first()
                    estado_civil = EstadoCivil.objects.filter(cod_estado_civil=current.estado_civil.cod_estado_civil).first()
                    if not persona:
                        estado_civil.item_ya_usado=True
                        estado_civil.save()