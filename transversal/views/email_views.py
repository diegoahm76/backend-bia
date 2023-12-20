

                    # if  email_persona and email_persona.email:
                    #     alerta_bandeja['email_usado'] = email_persona.email
                    #     subject = programada.nombre_clase_alerta
                        
                    #     template = "alerta.html"

                    #     context = {'Nombre_alerta':programada.nombre_clase_alerta,'primer_nombre': email_persona.primer_nombre,"mensaje":data_alerga_generada['mensaje']}
                    #     template = render_to_string((template), context)
                    #     email_data = {'template': template, 'email_subject': subject, 'to_email':email_persona.email}

import os
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import generics,status

from rest_framework.permissions import IsAuthenticated
from seguridad.utils import Util
from django.template.loader import render_to_string
from rest_framework.response import Response
class EnviarCorreoView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        data_in = request.data
        
        if 'plantilla' in request.FILES:
            plantilla = request.FILES['plantilla']
        else:
            raise ValidationError("No se ha enviado la plantilla")
        destinatario = data_in['destinatario']
        asunto = data_in['asunto']
        nombre_plantilla = plantilla.name
        nombre_sin_extension, extension = os.path.splitext(nombre_plantilla)
        extension_sin_punto = extension[1:] if extension.startswith('.') else extension

        if extension_sin_punto != 'html':
            
            raise ValidationError('El formato de la plantilla debe ser html')
        html_decodificado = plantilla.read().decode('utf-8')




        ##

        template = "alerta.html"
        context = {'Nombre_alerta':'hola','primer_nombre':'richard',"mensaje":'mensaje de prueba'}
        render = render_to_string((template), context)
        #raise ValidationError(type(render))
        email_data = {'template': html_decodificado, 'email_subject':asunto, 'to_email':destinatario}
        Util.send_email(email_data)

                
        return Response({
            'success': True,
            'detail': 'Correo enviado correctamente'
        }, status=status.HTTP_200_OK)