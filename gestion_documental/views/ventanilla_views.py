from gestion_documental.serializers.ventanilla_serializers import PersonasSerializer, ActualizarAutorizacionesPersonaSerializer, AutorizacionNotificacionesSerializer
from seguridad.models import Personas,HistoricoEmails,HistoricoDireccion
from rest_framework import generics,status
from rest_framework.response import Response
import datetime
import copy
from seguridad.utils import Util


class BusquedaPersonaParaRegistro(generics.RetrieveAPIView):
    
    serializer_class = PersonasSerializer
    queryset = Personas.objects.all()
    
    def get (self,request):
        
        tipo_documento = request.query_params.get('tipo_documento')
        numero_documento = request.query_params.get('numero_documento')
        
        
        if not tipo_documento or not numero_documento:
            return Response ({'success':False,'detail':'Debe de enviar el tipo de documento junto con el número de documento'},status=status.HTTP_403_FORBIDDEN)
        
        persona = self.queryset.all().filter(tipo_documento=tipo_documento, numero_documento=numero_documento).first()
        
        if persona:
            
            serializador = self.serializer_class(persona,many = False)
            
            return Response({'success':True,'detail':'Ya existe una persona registrada en la base de datos con estos datos','data':serializador.data},status=status.HTTP_200_OK)
        
        else:
            return Response({'success':True,'detail':'Está disponible para crear una persona con estos datos'},status=status.HTTP_200_OK)
        
        
class ActualizacionPersonaNatural(generics.UpdateAPIView):
    
    serializer_class = PersonasSerializer
    queryset = Personas.objects.all()
    
    def put (self,request,id_persona):
        
        data = request.data
        persona_actualiza = request.user.persona
        
        persona = self.queryset.all().filter(id_persona=id_persona).first()
        
        if not persona:
            return Response({'success':False,'detail':'No existe la persona'},status=status.HTTP_404_NOT_FOUND)
        
        if persona.id_persona_crea != persona_actualiza:
            persona.fecha_ultim_actualiz_diferente_crea
            persona.id_persona_ultim_actualiz_diferente_crea
            
            persona.save()
            
            
        seriializador = self.serializer_class(data, many=False)
        
        return Response ({'success':True,'detail':'Actualización exitosa','data':seriializador.data})
    

class ActualizacionAutorizaciones(generics.UpdateAPIView):
    
    serializer_class = ActualizarAutorizacionesPersonaSerializer
    queryset = Personas.objects.all()
    
    def put(self,request,id_persona):
        
        persona = self.queryset.all().filter(id_persona=id_persona).first()
            
        if not persona:
            return Response({'success':False,'detail':'No existe la persona'},status=status.HTTP_404_NOT_FOUND)
       
class AutorizacionNotificaciones(generics.RetrieveUpdateAPIView):
    serializer_class = AutorizacionNotificacionesSerializer
    queryset = Personas.objects.all()

    def put(self, request, id_persona):
        persona_ = self.request.user.id_usuario
        persona = Personas.objects.filter(id_persona=id_persona).first()
        data = request.data
        previous_user = copy.copy(persona)

        if persona is not None:
            if 'acepta_autorizacion_email' in data and 'acepta_autorizacion_sms' in data:
                acepta_autorizacion_email = data['acepta_autorizacion_email']
                acepta_autorizacion_sms = data['acepta_autorizacion_sms']

                persona.acepta_notificacion_email = acepta_autorizacion_email
                persona.acepta_notificacion_sms = acepta_autorizacion_sms
                persona.save()

                # AUDITORIA AUTORIZACION NOTIFICACIONES
                dirip = Util.get_client_ip(request)
                descripcion = {'tipo_documento': persona.tipo_documento, 'numero_documento':persona.numero_documento}
                valores_actualizados = {'current': persona, 'previous': previous_user}

                auditoria_data = {
                    'id_usuario': persona_,
                    'id_modulo': 69,
                    'cod_permiso': 'AC',
                    'subsistema': 'SEG',
                    'dirip': dirip,
                    'descripcion': descripcion,
                    'valores_actualizados': valores_actualizados
                }

                Util.save_auditoria(auditoria_data)

                if acepta_autorizacion_email and acepta_autorizacion_sms:
                    return Response({'success': True, 'detail': 'Autorización por correo electrónico y teléfono aceptada'}, status=status.HTTP_200_OK)
                elif acepta_autorizacion_email:
                    return Response({'success': True, 'detail': 'Autorización por correo electrónico aceptada'}, status=status.HTTP_200_OK)
                elif acepta_autorizacion_sms:
                    return Response({'success': True, 'detail': 'Autorización por teléfono aceptada'}, status=status.HTTP_200_OK)
                else:
                    return Response({'success': False, 'detail': 'Autorización no aceptada'}, status=status.HTTP_200_OK)
            else: 
                return Response({'success': False, 'detail': 'Autorización no aceptada'}, status=status.HTTP_200_OK) 
        else:
            return Response({'success': False, 'detail': 'La persona no existe'}, status=status.HTTP_404_NOT_FOUND)
        # if persona.tipo_persona == 'N':
            
        #     if data['email'] != persona.email:
        #         HistoricoEmails.objects.create(
        #             id_persona = persona,
        #             email = persona.email,
        #             fecha_cambio = datetime.now()
        #         )
        #     if data['direccion_residencia'] != persona.direccion_residencia:
        #         HistoricoDireccion.objects.create(
        #             id_persona = persona,
        #             direccion = persona.direccion_residencia,
        #             tipo_direccion = "RES"
        #         )
        #     if data['direccion_notificaciones'] != persona.direccion_notificaciones:
        #         HistoricoDireccion.objects.create(
        #             id_persona = persona,
        #             direccion = persona.direccion_notificaciones,
        #             tipo_direccion = "NOT"
        #         )
        #     if data['direccion_laboral'] != persona.direccion_laboral:
        #         HistoricoDireccion.objects.create(
        #             id_persona = persona,
        #             direccion = persona.direccion_laboral,
        #             tipo_direccion = "LAB"
        #         )
            
        # else 
            
            
        

            