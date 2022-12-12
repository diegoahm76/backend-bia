from django.core.mail import EmailMessage
from email_validator import validate_email, EmailNotValidError, EmailUndeliverableError, EmailSyntaxError
from backend.settings import EMAIL_HOST_USER, AUTHENTICATION_360_NRS
from seguridad.models import Shortener, User, Modulos, Permisos, Auditorias
import re, requests

class Util:
    
    @staticmethod
    def send_email(data):
        email = EmailMessage(subject= data['email_subject'], body=data['template'], to=[data['to_email']], from_email=EMAIL_HOST_USER)
        
        email.content_subtype ='html'
        response = email.send(fail_silently=True)
        print(response)
        return response
       

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
        print(telefono)
        print(len(sms))
        payload = "{ \"to\": [\"" + telefono + "\"], \"from\": \"TEST\", \"message\": \"" + mensaje + "\" }"
        headers = {
        'Content-Type': 'application/json', 
        'Authorization': 'Basic ' + AUTHENTICATION_360_NRS
        }

        response = requests.request("POST", url, headers=headers, data=payload)

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
        
            return True
        except:
            return False