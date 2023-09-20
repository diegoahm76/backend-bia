from django.utils import timezone
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
import os
from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.serializers.expedientes_serializers import ArchivosDigitalesCreateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
class ArchivosInstrumentoCreate(generics.CreateAPIView):
    queryset = ArchivosDigitales.objects.all()
    serializer_class = ArchivosDigitalesCreateSerializer
    #parser_classes = (MultiPartParser,)
    def obtener_tamano_archivo(self,archivo):
        try:
            if hasattr(archivo, 'size'):
                # Para archivos en disco, el tamaño está disponible en el atributo 'size'
                return archivo.size / 1024.0  # Convertir a kilobytes
            else:
                # Para archivos en memoria, usa len() para obtener el tamaño en bytes
                return len(archivo.read()) / 1024.0  # Convertir a kilobytes
        except Exception as e:
            print(f"No se pudo obtener el tamaño del archivo: {str(e)}")
            return None

    def crear_archivo(self, data):
       
        data_in=data

        tamano=self.obtener_tamano_archivo(data_in['archivo'])
        nombre=data_in['archivo'].name
        archivo=data_in['archivo']

        nombre_sin_extension, extension = os.path.splitext(nombre)
        extension_sin_punto = extension[1:] if extension.startswith('.') else extension

        data_in['formato'] = extension_sin_punto
        
        data_in['tamagno_kb'] = int(tamano)
        data_in['nombre_de_Guardado'] = nombre_sin_extension
        
        ruta_personalizada = 'tu/ruta/personalizada/'
        ruta_archivo_personalizada = os.path.join(ruta_personalizada, nombre)

        data['ruta_archivo'] =  ruta_archivo_personalizada

        serializer = ArchivosDigitalesCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def post(self, request, *args, **kwargs):
        try:
            data=request.data
            archivo = request.FILES['archivo']
            #tamano=self.obtener_tamano_archivo(archivo)
            ruta=""
            if 'ruta' in data:
                ruta=data['ruta']
            nombre=archivo.name
            
            nombre_sin_extension, extension = os.path.splitext(nombre)
            extension_sin_punto = extension[1:] if extension.startswith('.') else extension

            data['formato'] = extension_sin_punto
            
            data['tamagno_kb'] =int(self.obtener_tamano_archivo(archivo))
            data['nombre_de_Guardado'] = nombre_sin_extension
            
        
            data['ruta_archivo'] = archivo

            serializer = ArchivosDigitalesCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save(subcarpeta=ruta)

            return Response({'data':serializer.data}, status=status.HTTP_201_CREATED)
    
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)