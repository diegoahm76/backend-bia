from gestion_documental.serializers.ventanilla_serializers import PersonasSerializer, ActualizarAutorizacionesPersonaSerializer, AutorizacionNotificacionesSerializer
from seguridad.models import Personas,HistoricoEmails,HistoricoDireccion
from rest_framework import generics,status
from rest_framework.response import Response
from datetime import datetime
import copy
from seguridad.serializers.personas_serializers import PersonaJuridicaPostSerializer, PersonaJuridicaUpdateSerializer, PersonaNaturalPostSerializer, PersonaNaturalUpdateSerializer
from seguridad.signals.roles_signals import IsAuthenticated
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
        
class RegisterPersonaNatural(generics.CreateAPIView):
    serializer_class = PersonaNaturalPostSerializer
    
    def post(self, request):
        persona = request.data
        persona_logueada = request.user.persona.id_persona
        persona['id_persona_crea'] = persona_logueada 
        
        serializer = self.serializer_class(data=persona)
        serializer.is_valid(raise_exception=True)
        
        validaciones_persona = Util.guardar_persona(persona)
        
        print(validaciones_persona)
        if not validaciones_persona['success']:
            return Response({'success': validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
        
        serializador=serializer.save()

        # auditoria crear persona
        descripcion = {"TipodeDocumentoID": str(serializador.tipo_documento), "NumeroDocumentoID": str(serializador.numero_documento), "PrimerNombre": str(serializador.primer_nombre), "PrimerApellido": str(serializador.primer_apellido)}
        direccion=Util.get_client_ip(request)

        auditoria_data = {
            "id_modulo" : 9,
            "cod_permiso": "CR",
            "subsistema": 'TRSV',
            "dirip": direccion,
            "descripcion": descripcion, 
        }
        Util.save_auditoria(auditoria_data)
        
        subject = "Registro exitoso"
        template = "email-register-personanatural.html"
        
        Util.notificacion(serializador,subject,template)

        return Response({'success':True, 'detail':'Se creo la persona natural correctamente', 'data':serializer.data}, status=status.HTTP_201_CREATED)

class RegisterPersonaJuridica(generics.CreateAPIView):
    serializer_class = PersonaJuridicaPostSerializer

    def post(self, request):
        persona = request.data
        persona_logueada = request.user.persona.id_persona
        persona['id_persona_crea'] = persona_logueada 
        
        serializer = self.serializer_class(data=persona)
        serializer.is_valid(raise_exception=True)

        validaciones_persona = Util.guardar_persona(persona)
        
        if not validaciones_persona['success']:
            return Response({'success': validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
        
        serializador = serializer.save()
        
        # auditoria crear persona
        descripcion = {"TipodeDocumentoID": str(serializador.tipo_documento), "NumeroDocumentoID": str(serializador.numero_documento), "RazonSocial": str(serializador.razon_social), "NombreComercial": str(serializador.nombre_comercial)}
        direccion=Util.get_client_ip(request)

        auditoria_data = {
            "id_modulo" : 9,
            "cod_permiso": "CR",
            "subsistema": 'TRSV',
            "dirip": direccion,
            "descripcion": descripcion, 
        }
        Util.save_auditoria(auditoria_data)

        subject = "Registro exitoso"
        template = "email-register-personajuridica.html"
        
        Util.notificacion(serializador,subject,template)
        
        return Response({'success':True, 'detail': 'Se creo la persona jurídica correctamente', 'data':serializer.data}, status=status.HTTP_201_CREATED)

class UpdatePersonaNaturalByVentanilla(generics.RetrieveUpdateAPIView):
    http_method_names = ['patch']
    serializer_class = PersonaNaturalUpdateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Personas.objects.all()
    
    def patch(self, request, id_persona):
        data = request.data
        persona_logueada = request.user.persona.id_persona
        persona = self.queryset.all().filter(id_persona = id_persona).first()
        previous_persona = copy.copy(persona)
        
        if persona:
            if persona.tipo_persona != "N":
                return Response ({'success':False,'detail':'No se puede actualizar una persona jurídica con este servicio'},status=status.HTTP_403_FORBIDDEN)
            
            persona_serializada = self.serializer_class(persona, data=data, many=False)
            persona_serializada.is_valid(raise_exception=True)
            
            if persona_logueada != id_persona:
                
                cambio = Util.comparacion_campos_actualizados(data,persona)
                if cambio:
                    data['fecha_ultim_actualiz_diferente_crea'] = datetime.now()
                    data['id_persona_ultim_actualiz_diferente_crea'] = persona_logueada
            
            data['tipo_persona'] = persona.tipo_persona
            
            validaciones_persona = Util.guardar_persona(data)
            
            if not validaciones_persona['success']:
                return Response({'success': validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
            
            serializador = persona_serializada.save()
            
            # auditoria actualizar persona
            usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"TipodeDocumentoID": str(serializador.tipo_documento), "NumeroDocumentoID": str(serializador.numero_documento), "PrimerNombre": str(serializador.primer_nombre), "PrimerApellido": str(serializador.primer_apellido)}
            valores_actualizados = {'current': persona, 'previous': previous_persona}

            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 1,
                "cod_permiso": "AC",
                "subsistema": 'TRSV',
                "dirip": direccion,
                "descripcion": descripcion, 
                "valores_actualizados": valores_actualizados
            }
            Util.save_auditoria(auditoria_data)
            
            subject = "Actualización de datos exitosa"
            template = "email-update-personanatural-externa.html"
            
            Util.notificacion(persona,subject,template)
            
            return Response({'success': True, 'detail': 'Persona actualizada y notificada correctamente', 'data': persona_serializada.data}, status=status.HTTP_201_CREATED)
        return Response({'success':False,'detail':"No existe la persona"},status=status.HTTP_404_NOT_FOUND)

    
class UpdatePersonaJuridicaByVentanilla(generics.UpdateAPIView):
    http_method_names = ['patch']
    serializer_class = PersonaJuridicaUpdateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Personas.objects.all()
    
    def patch(self,request,id_persona):
        
        data = request.data
        persona_logueada = request.user.persona.id_persona
        persona = self.queryset.all().filter(id_persona = id_persona).first()
        previous_persona = copy.copy(persona)
        if persona:
            if persona.tipo_persona != "J":
                return Response ({'success':False,'detail':'No se puede actualizar una persona natural con este servicio'},status=status.HTTP_403_FORBIDDEN)
            
            #VALIDACION DE REPRESENTANTE LEGAL
            if persona.representante_legal != data.get('representante_legal'):
                data['fecha_cambio_representante_legal'] = datetime.now()  
            
            persona_serializada = self.serializer_class(persona, data=data, many=False)
            persona_serializada.is_valid(raise_exception=True)
            
            if persona_logueada != id_persona:
                cambio = Util.comparacion_campos_actualizados(data,persona)
                if cambio:
                    data['fecha_ultim_actualiz_diferente_crea'] = datetime.now()
                    data['id_persona_ultim_actualiz_diferente_crea'] = persona_logueada
                
            data['tipo_persona'] = persona.tipo_persona
            
            validaciones_persona = Util.guardar_persona(data)
            
            if not validaciones_persona['success']:
                return Response({'success': validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
            
            serializador = persona_serializada.save()
            
            # auditoria actualizar persona
            usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"TipodeDocumentoID": str(serializador.tipo_documento), "NumeroDocumentoID": str(serializador.numero_documento), "PrimerNombre": str(serializador.primer_nombre), "PrimerApellido": str(serializador.primer_apellido)}
            valores_actualizados = {'current': persona, 'previous': previous_persona}

            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 1,
                "cod_permiso": "AC",
                "subsistema": 'TRSV',
                "dirip": direccion,
                "descripcion": descripcion, 
                "valores_actualizados": valores_actualizados
            }
            Util.save_auditoria(auditoria_data)
            
            subject = "Actualización de datos exitosa"
            template = "email-update-personajuridica-externo.html"
            
            Util.notificacion(persona,subject,template)
            
            return Response({'success': True, 'detail': 'Persona actualizada y notificada correctamente', 'data': persona_serializada.data}, status=status.HTTP_201_CREATED)
        return Response({'success':False,'detail':"No existe la persona"},status=status.HTTP_404_NOT_FOUND)
    
class AutorizacionNotificacionesVentanilla(generics.RetrieveUpdateAPIView):
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
                    'id_modulo': 70,
                    'cod_permiso': 'AC',
                    'subsistema': 'TRSV',
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
                    return Response({'success': True, 'detail': 'Autorizacion no aceptada'}, status=status.HTTP_200_OK)
            else: 
                return Response({'success': False, 'detail': 'No envió las autorizaciones'}, status=status.HTTP_400_BAD_REQUEST) 
        else:
            return Response({'success': False, 'detail': 'La persona no existe'}, status=status.HTTP_404_NOT_FOUND)