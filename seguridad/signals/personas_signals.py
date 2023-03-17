from django.db.models.signals import pre_save
from django.db.models import Q
from django.dispatch import receiver
from seguridad.models import Personas, HistoricoEmails, HistoricoDireccion, Cargos, TipoDocumento, EstadoCivil

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
            
            # MODIFICA TIPO DOCUMENTO
            if previous.tipo_documento:
                if not current.tipo_documento:
                    persona = Personas.objects.filter(Q(tipo_documento=previous.tipo_documento.cod_tipo_documento) & ~Q(id_persona=previous.id_persona)).first()
                    tipo_documento = TipoDocumento.objects.filter(cod_tipo_documento=previous.tipo_documento.cod_tipo_documento).first()
                    if not persona:
                        tipo_documento.item_ya_usado=False
                        tipo_documento.save()
                else:
                    if previous.tipo_documento.cod_tipo_documento != current.tipo_documento.cod_tipo_documento:
                        persona_current = Personas.objects.filter(tipo_documento=current.tipo_documento.cod_tipo_documento).first()
                        persona_previous = Personas.objects.filter(Q(tipo_documento=previous.tipo_documento.cod_tipo_documento) & ~Q(id_persona=previous.id_persona)).first()
                        tipo_documento_current = TipoDocumento.objects.filter(cod_tipo_documento=current.tipo_documento.cod_tipo_documento).first()
                        tipo_documento_previous = TipoDocumento.objects.filter(cod_tipo_documento=previous.tipo_documento.cod_tipo_documento).first()
                        if not persona_current:
                            tipo_documento_current.item_ya_usado=True
                            tipo_documento_current.save()
                        if not persona_previous:
                            tipo_documento_previous.item_ya_usado=False
                            tipo_documento_previous.save()
            else:
                if current.tipo_documento:
                    persona = Personas.objects.filter(tipo_documento=current.tipo_documento.cod_tipo_documento).first()
                    tipo_documento = TipoDocumento.objects.filter(tipo_documento=current.tipo_documento.cod_tipo_documento).first()
                    if not persona:
                        tipo_documento.item_ya_usado=True
                        tipo_documento.save()
            
            # MODIFICA ESTADO CIVIL
            if previous.estado_civil:
                if not current.estado_civil:
                    persona = Personas.objects.filter(Q(estado_civil=previous.estado_civil.cod_estado_civil) & ~Q(id_persona=previous.id_persona)).first()
                    estado_civil = EstadoCivil.objects.filter(cod_estado_civil=previous.estado_civil.cod_estado_civil).first()
                    if not persona:
                        estado_civil.item_ya_usado=False
                        estado_civil.save()
                else:
                    if previous.estado_civil.cod_estado_civil != current.estado_civil.cod_estado_civil:
                        persona_current = Personas.objects.filter(estado_civil=current.estado_civil.cod_estado_civil).first()
                        persona_previous = Personas.objects.filter(Q(estado_civil=previous.estado_civil.cod_estado_civil) & ~Q(id_persona=previous.id_persona)).first()
                        estado_civil_current = EstadoCivil.objects.filter(cod_estado_civil=current.estado_civil.cod_estado_civil).first()
                        estado_civil_previous = EstadoCivil.objects.filter(cod_estado_civil=previous.estado_civil.cod_estado_civil).first()
                        if not persona_current:
                            estado_civil_current.item_ya_usado=True
                            estado_civil_current.save()
                        if not persona_previous:
                            estado_civil_previous.item_ya_usado=False
                            estado_civil_previous.save()
            else:
                if current.estado_civil:
                    persona = Personas.objects.filter(estado_civil=current.estado_civil.cod_estado_civil).first()
                    estado_civil = EstadoCivil.objects.filter(cod_estado_civil=current.estado_civil.cod_estado_civil).first()
                    if not persona:
                        estado_civil.item_ya_usado=True
                        estado_civil.save()