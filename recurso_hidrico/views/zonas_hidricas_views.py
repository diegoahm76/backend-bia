from seguridad.utils import Util
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from recurso_hidrico.models.zonas_hidricas_models import TipoAguaZonaHidrica, ZonaHidrica, MacroCuencas,TipoZonaHidrica,SubZonaHidrica
from recurso_hidrico.serializers.zonas_hidricas_serializers import TipoAguaZonaHidricaSerializer, ZonaHidricaSerializer, MacroCuencasSerializer,TipoZonaHidricaSerializer,SubZonaHidricaSerializer
import copy
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

# Vista get para las 4 tablas de zonas hidricas
class MacroCuencasListView (generics.ListAPIView):
    queryset = MacroCuencas.objects.all()
    serializer_class = MacroCuencasSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cuencas = MacroCuencas.objects.all()
        serializer = self.serializer_class(cuencas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    

class ZonaHidricaListView (generics.ListCreateAPIView):
    queryset = ZonaHidrica.objects.all()
    serializer_class = ZonaHidricaSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request,pk):
        zonas = ZonaHidrica.objects.filter(id_macro_cuenca=pk)
        serializer = self.serializer_class(zonas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    

class TipoZonaHidricaListView (generics.ListCreateAPIView):
    queryset = TipoZonaHidrica.objects.all()
    serializer_class = TipoZonaHidricaSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        zonas = TipoZonaHidrica.objects.all()
        serializer = self.serializer_class(zonas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    

class SubZonaHidricaListView (generics.ListCreateAPIView):
    queryset = SubZonaHidrica.objects.all()
    serializer_class = SubZonaHidricaSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request,pk):
        zonas = SubZonaHidrica.objects.filter(id_zona_hidrica=pk)
        serializer = self.serializer_class(zonas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    
#crear datos

class CrearSubZonaHidricaVista(generics.CreateAPIView):
    queryset = SubZonaHidrica.objects.all()
    serializer_class = SubZonaHidricaSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
                      
            # Agregar lógica adicional si es necesario, por ejemplo, asignar valores antes de guardar
            # serializer.validated_data['campo_adicional'] = valor

            serializer.save()

            return Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({'error': 'Error al crear el registro', 'detail': e.detail})
           

#borrar lugar y rio 
class BorrarZonaHidricaVista(generics.DestroyAPIView):
    queryset = ZonaHidrica.objects.all()
    serializer_class = ZonaHidricaSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'success': True, 'detail': 'Registro eliminado correctamente'},
                            status=status.HTTP_200_OK)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({e.detail})
        

class BorrarSubZonaHidricaVista(generics.DestroyAPIView):
    queryset = SubZonaHidrica.objects.all()
    serializer_class = SubZonaHidricaSerializer

    def destroy(self, request, *args, **kwargs):
            
            instance = self.get_object()
            
            if not instance:
                raise NotFound('No se encontró el registro')
            previus = copy.copy(instance)
            instance.delete()
            serializer = self.get_serializer(previus)
            return Response({'success': True, 'detail': 'Registro eliminado correctamente','data':serializer.data},
                            status=status.HTTP_200_OK)
        
        
class ActualizarZonaHidricaVista(generics.UpdateAPIView):
    queryset = ZonaHidrica.objects.all()
    serializer_class = ZonaHidricaSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene la instancia existente
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)  # Valida los datos
        serializer.save()  # Guarda la instancia con los datos actualizados

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ActualizarSubZonaHidricaVista(generics.UpdateAPIView):
    queryset = SubZonaHidrica.objects.all()
    serializer_class = SubZonaHidricaSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene la instancia existente
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)  # Valida los datos
        serializer.save()  # Guarda la instancia con los datos actualizados

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class TipoAguaZonaHidricaListView (generics.ListAPIView):
    queryset = TipoAguaZonaHidrica.objects.all()
    serializer_class = TipoAguaZonaHidricaSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cuencas = TipoAguaZonaHidrica.objects.all()
        serializer = self.serializer_class(cuencas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    

class CrearZonaHidricaVista(generics.CreateAPIView):
    queryset = ZonaHidrica.objects.all()
    serializer_class = ZonaHidricaSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
                  
            # Agregar lógica adicional si es necesario, por ejemplo, asignar valores antes de guardar
            # serializer.validated_data['campo_adicional'] = valor

            serializer.save()

            return Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({'error': 'Error al crear el registro', 'detail': e.detail})
        
    



class EnviarSMSView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        telefono = request.data.get('telefono')
        mensaje = request.data.get('mensaje')

        if telefono and mensaje:
            # Llama a la función send_sms con los datos proporcionados
            Util.send_sms(telefono, mensaje)

            # Puedes personalizar la respuesta según tus necesidades
            return Response({'mensaje': 'SMS enviado correctamente'}, status=status.HTTP_200_OK)
        else:
            # Maneja el caso en el que no se proporcionan el teléfono o el mensaje
            return Response({'error': 'Por favor, proporciona el teléfono y el mensaje.'}, status=status.HTTP_400_BAD_REQUEST)
        



class EnviarCORREOView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        correo = request.data.get('correo')
        nombre = request.data.get('nombre')
        subject = request.data.get('asunto')
        mensaje = request.data.get('mensaje')

        if correo and nombre and subject:
            # Configuración del correo electrónico
            template = "alerta.html"

            # Crear el contexto para la plantilla
            context = {'Nombre_alerta': mensaje}

            # Renderizar la plantilla
            html_content = render_to_string(template, context)

            # Configuración del correo electrónico en formato HTML y texto plano
            email = EmailMessage()
            email.subject = subject
            email.body = html_content
            email.to = [correo]
            email.content_subtype = 'html'

            # Enviar el correo electrónico
            email.send()

            # Puedes personalizar la respuesta según tus necesidades
            return Response({'mensaje': 'Correo electrónico enviado correctamente'}, status=status.HTTP_200_OK)
        else:
            # Maneja el caso en el que no se proporciona el correo, el nombre o el asunto
            return Response({'error': 'Por favor, proporciona el correo, el nombre y el asunto.'}, status=status.HTTP_400_BAD_REQUEST)