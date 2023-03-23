from datetime import datetime, timedelta,date
import time
from seguridad.models import Personas
from django.core.mail import EmailMessage
from email_validator import validate_email, EmailNotValidError, EmailUndeliverableError, EmailSyntaxError
from backend.settings.base import EMAIL_HOST_USER, AUTHENTICATION_360_NRS
from seguridad.models import Shortener, User, Modulos, Permisos, Auditorias
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
import re, requests
# from twilio.rest import Client
from django.template.loader import render_to_string
import os

class Util:
    
    @staticmethod
    def send_email(data):
        email = EmailMessage(subject= data['email_subject'], body=data['template'], to=[data['to_email']], from_email=EMAIL_HOST_USER)
        
        email.content_subtype ='html'
        response = email.send(fail_silently=False)
        print(response)
        return response

        # url = "https://dashboard.360nrs.com/api/rest/mailing"

        # # payload = {
        # #     "to":[data['to_email']],
        # #     "fromName": "Info",
        # #     "fromEmail": "info@360nrs.com",
        # #     "body": data['template'],
        # #     "replyTo": "replyto@example.com",
        # #     "subject": data['email_subject']
        # # }
        # # payload = "{ \"to\": [\"test@example.com\"], \"fromName\": \"Info\", \"fromEmail\": \"info@360nrs.com\", \"body\": \"<html><head><title>TEST</title></head><body><a href=\\\"https://example.com\\\">link</a></body></html>\", \"replyTo\": \"replyto@example.com\", \"subject\": \"TEST\" }"
        # # print("PAYLOAD 1: ", payload)
       
       
        # payload = "{ \"to\": [\"%s\"], \"fromName\": \"Info\", \"fromEmail\": \"info@360nrs.com\", \"body\": \"%s\", \"replyTo\": \"replyto@example.com\", \"subject\": \"%s\" }" % (data['to_email'],data['template'],data['email_subject'])
        # print("PAYLOAD 2: ", payload)
        # headers = {
        # 'Content-Type': 'application/json',
        # 'Authorization': 'Basic ' + AUTHENTICATION_360_NRS
        # }

        # response = requests.request("POST", url, headers=headers, data=str(payload))


        # print(response.text)
        # return response
            

    @staticmethod
    def validate_dns(email):
        try: 
            validation = validate_email(email, check_deliverability=True)
            validate = validation.email
            return True
        except EmailUndeliverableError as e:
            return False



        
    @staticmethod
    def send_sms(phone, sms):
        url = "https://dashboard.360nrs.com/api/rest/sms"

        telefono = phone
        mensaje = sms
        telefono = telefono.replace("+","")
        print("SMS: ", mensaje)
        print(telefono)
        print(len(sms))
        payload = "{ \"to\": [\"" + telefono + "\"], \"from\": \"TEST\", \"message\": \"" + mensaje + "\" }"
        print("PAYLOAD",payload)
        headers = {
        'Content-Type': 'application/json', 
        'Authorization': 'Basic ' + AUTHENTICATION_360_NRS
        }
        
        # account_sid = os.environ['TWILIO_ACCOUNT_SID']
        # auth_token = os.environ['TWILIO_AUTH_TOKEN']    
        # client = Client(account_sid, auth_token)
        # # this is the Twilio sandbox testing number
        # from_whatsapp_number='whatsapp:+14155238886'
        # # replace this number with your own WhatsApp Messaging number
        # to_whatsapp_number='whatsapp:+' + telefono

        # client.messages.create(body='Ingresó en Cormacarena-bia',
        #                     from_=from_whatsapp_number,
        #                     to=to_whatsapp_number)


        response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))

        print(response.text)
        #client.messages.create(messaging_service_sid=TWILIO_MESSAGING_SERVICE_SID, body=sms, from_=PHONE_NUMBER, to=phone)
        
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
        
    @staticmethod
    def get_client_device(request):
        client_device = request.META.get('HTTP_USER_AGENT')
        
        MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)

        if MOBILE_AGENT_RE.match(client_device):
            return 'mobile'
        else:
            return 'desktop'
        
    @staticmethod
    def get_short_url(request, url):
        try:
            create_short_url = Shortener.objects.create(
                long_url = url
            )
            new_url = request.build_absolute_uri('/short/') + create_short_url.short_url
            return new_url
        except:
            return url
        
    @staticmethod
    def change_token_expire_externo(user):
        token = RefreshToken.for_user(user)
        access_token = token.access_token
        access_token.set_exp(lifetime=timedelta(minutes=30))
        return {
            "refresh": str(token),
            "access": str(access_token),
        }
        
    @staticmethod
    def save_auditoria(data):
        try:
            usuario = None
            if data.get('id_usuario'):
                usuario = User.objects.get(id_usuario = data.get('id_usuario'))
                
            modulo = Modulos.objects.get(id_modulo = data.get('id_modulo'))
            permiso = Permisos.objects.get(cod_permiso = data.get('cod_permiso'))
            data_descripcion = data.get('descripcion')
            data_actualizados = data.get('valores_actualizados')
            descripcion = None
            
            if data_descripcion:
                descripcion = ''
                for field, value in data_descripcion.items():
                    descripcion += '' if not descripcion else '|'
                    descripcion += field + ":" + str(value)
                    
                descripcion += '.'
                
            valores_actualizados = None
            
            if data_actualizados:
                valores_actualizados = ""
                
                data_previous = data_actualizados.get('previous')
                data_current = data_actualizados.get('current')
                
                del data_previous.__dict__["_state"]
                del data_previous.__dict__["_django_version"]
                
                for field, value in data_previous.__dict__.items():
                    new_value = getattr(data_current,field)
                    if value != new_value:
                        valores_actualizados += '' if not valores_actualizados else '|'
                        valores_actualizados += field + ":" + str(value) + " con " + str(new_value)
                
                if not valores_actualizados:
                    valores_actualizados = None
                else:
                    valores_actualizados += '.'
                    auditoria_user = Auditorias.objects.create(
                        id_usuario = usuario,
                        id_modulo = modulo,
                        id_cod_permiso_accion = permiso,
                        subsistema = data.get('subsistema'),
                        dirip = data.get('dirip'),
                        descripcion = descripcion,
                        valores_actualizados = valores_actualizados
                    )
                    auditoria_user.save()
            else:
                auditoria_user = Auditorias.objects.create(
                    id_usuario = usuario,
                    id_modulo = modulo,
                    id_cod_permiso_accion = permiso,
                    subsistema = data.get('subsistema'),
                    dirip = data.get('dirip'),
                    descripcion = descripcion,
                    valores_actualizados = valores_actualizados
                )
                auditoria_user.save()
        
            return True
        except:
            return False
        
    @staticmethod
    def save_auditoria_maestro_detalle(data):
        try:
            usuario = None
            if data.get('id_usuario'):
                usuario = User.objects.get(id_usuario = data.get('id_usuario'))
                
            modulo = Modulos.objects.get(id_modulo = data.get('id_modulo'))
            permiso = Permisos.objects.get(cod_permiso = data.get('cod_permiso'))
            data_descripcion = data.get('descripcion')
            data_actualizados_detalles = data.get('valores_actualizados_detalles')
            data_creados_detalles = data.get('valores_creados_detalles')
            data_eliminados_detalles = data.get('valores_eliminados_detalles')
            
            descripcion_general = None
            descripcion_detalles = ''
            descripcion_creados = None
            descripcion_eliminados = None
            
            if data_descripcion:
                descripcion_general = ''
                for field, value in data_descripcion.items():
                    descripcion_general += '' if not descripcion_general else '|'
                    descripcion_general += field + ":" + str(value)
                    
                descripcion_general += '.'
                
            valores_actualizados = None
            
            if data_creados_detalles:
                for detalle_crear in data_creados_detalles:
                    descripcion_creados = ''
                    for field, value in detalle_crear.items():
                        descripcion_creados += '' if not descripcion_creados else '|'
                        descripcion_creados += field + ":" + str(value)
                    descripcion_creados += '.'
                    descripcion_detalles += ' ' if descripcion_detalles.endswith('.') else ''
                    descripcion_detalles += 'Se agregó en el detalle el ítem ' + descripcion_creados
            
            if data_actualizados_detalles:
                for detalle in data_actualizados_detalles:
                    valores_actualizados = ""
                    
                    data_descripcion_detalle = detalle.get('descripcion')
                    data_previous = detalle.get('previous')
                    data_current = detalle.get('current')
                    
                    description = None
                    
                    if data_descripcion_detalle:
                        description = ''
                        for field, value in data_descripcion_detalle.items():
                            description += '' if not description else '|'
                            description += field + ":" + str(value)

                    if data_previous.__dict__.get("_state"):
                        del data_previous.__dict__["_state"]
                    if data_previous.__dict__.get("_django_version"):
                        del data_previous.__dict__["_django_version"]
                    
                    for field, value in data_previous.__dict__.items():
                        new_value = getattr(data_current,field)
                        if value != new_value:
                            valores_actualizados += '' if not valores_actualizados else '|'
                            valores_actualizados += field + ":" + str(value) + " con " + str(new_value)
                    
                    if not valores_actualizados:
                        valores_actualizados = None
                    else:
                        valores_actualizados += '.'
                        descripcion_detalles += ' ' if descripcion_detalles.endswith('.') else ''
                        descripcion_detalles += 'Se actualizó en el detalle el ítem ' + description + ' en los siguientes campos: ' + valores_actualizados
            
            if data_eliminados_detalles:
                for detalle_eliminar in data_eliminados_detalles:
                    descripcion_eliminados = ''
                    for field, value in detalle_eliminar.items():
                        descripcion_eliminados += '' if not descripcion_eliminados else '|'
                        descripcion_eliminados += field + ":" + str(value)
                    descripcion_eliminados += '.'
                    descripcion_detalles += ' ' if descripcion_detalles.endswith('.') else ''
                    descripcion_detalles += 'Se eliminó en el detalle el ítem ' + descripcion_eliminados
                
            descripcion_detalles = descripcion_detalles if descripcion_detalles != '' else None
                
            auditoria_user = Auditorias.objects.create(
                id_usuario = usuario,
                id_modulo = modulo,
                id_cod_permiso_accion = permiso,
                subsistema = data.get('subsistema'),
                dirip = data.get('dirip'),
                descripcion = descripcion_general,
                valores_actualizados = descripcion_detalles
            )
            auditoria_user.save()
        
            return True
        except:
            return False
        
    @staticmethod
    def guardar_persona(data):
        
        if data['tipo_persona'] == "N":
                
            #Validación de tipo documento
            tipo_documento = data.get('tipo_documento')
            print(tipo_documento)
            if tipo_documento == 'NT':
                return {'success':False,'detail':'El tipo de documento debe ser el de una persona natural', 'status':status.HTTP_400_BAD_REQUEST}

            email_principal = data.get('email')
            email_secundario = data.get('email_empresarial')

            #Validación emails dns
            validate_email = Util.validate_dns(email_principal)
            if validate_email == False:
                return {'success':False,'detail':'Valide que el email principal ingresado exista', 'status':status.HTTP_400_BAD_REQUEST}

            if email_secundario:
                validate_second_email = Util.validate_dns(email_secundario)
                if validate_second_email == False:
                    return {'success':False,'detail':'Valide que el email secundario ingresado exista', 'status':status.HTTP_400_BAD_REQUEST}

            if email_principal == email_secundario:
                return {'success':False,'detail':'El email principal no puede ser el mismo email empresarial', 'status':status.HTTP_400_BAD_REQUEST}

            return ({'success':True})
        
        else:
            
            fecha_inicio = data.get("fecha_inicio_cargo_rep_legal")
            fecha_formateada = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            
            fecha_ahora = date.today()
            
            if fecha_formateada:
                
                if fecha_formateada > fecha_ahora:
                    return {'success':False,'detail':'La fecha de inicio del cargo del representante no debe ser superior a la del sistema', 'status':status.HTTP_403_FORBIDDEN}
            
            representante_legal = Personas.objects.filter(id_persona = data.get("representante_legal")).first()
            if representante_legal.tipo_persona == "J":
                return {'success':False,'detail':'El representante legal debe ser una persona natural', 'status':status.HTTP_403_FORBIDDEN}
            
            #Validación de tipo documento
            tipo_documento = data.get('tipo_documento')
            
            if tipo_documento and tipo_documento  != 'NT':
                return {'success':False,'detail':'El tipo de documento debe ser el de una persona juridica', 'status':status.HTTP_400_BAD_REQUEST}

            email_principal = data.get('email')
            email_secundario = data.get('email_empresarial')

            #Validación emails dns
            validate_email = Util.validate_dns(email_principal)
            if validate_email == False:
                return {'success':False,'detail':'Valide que el email principal ingresado exista', 'status':status.HTTP_400_BAD_REQUEST}

            if email_secundario:
                validate_second_email = Util.validate_dns(email_secundario)
                if validate_second_email == False:
                    return {'success':False,'detail':'Valide que el email secundario ingresado exista', 'status':status.HTTP_400_BAD_REQUEST}

            if email_principal == email_secundario:
                return {'success':False,'detail':'El email principal no puede ser el mismo email empresarial', 'status':status.HTTP_400_BAD_REQUEST}

            return ({'success':True})
    
    @staticmethod
    def notificacion(persona,subject_email,template_name,**kwargs):
        
        if persona.tipo_persona == "N":
            context = {'primer_nombre': persona.primer_nombre,'fecha_actual':str(datetime.now().replace(microsecond=0))}
            
            for field, value in kwargs.items():
                context[field] = value
            
            template = render_to_string((template_name), context)
            subject = subject_email + ' ' + persona.primer_nombre
            email_data = {'template': template, 'email_subject': subject, 'to_email': persona.email}
            Util.send_email(email_data)
        else:
            context = {'razon_social': persona.razon_social,'fecha_actual':str(datetime.now().replace(microsecond=0))}
            
            for field, value in kwargs.items():
                context[field] = value
            
            template = render_to_string((template_name), context)
            subject = subject_email + ' ' + persona.razon_social
            email_data = {'template': template, 'email_subject': subject, 'to_email': persona.email} 
            Util.send_email(email_data)
            
        return True
    
    @staticmethod
    def comparacion_campos_actualizados(data,instance):
        for field, value in data.items():
            valor_previous= getattr(instance,field)
            if value != valor_previous:
                return True
        return False