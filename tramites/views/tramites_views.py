import json
import os
import hashlib
from rest_framework import status
from rest_framework import generics, views
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from gestion_documental.models.radicados_models import EstadosSolicitudes, T262Radicados
from gestion_documental.models.trd_models import FormatosTiposMedio
from gestion_documental.serializers.pqr_serializers import RadicadoPostSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.views.configuracion_tipos_radicados_views import ConfigTiposRadicadoAgnoGenerarN
from gestion_documental.views.pqr_views import RadicadoCreate
from seguridad.utils import Util

from tramites.models.tramites_models import AnexosTramite, PermisosAmbSolicitudesTramite, PermisosAmbientales, SolicitudesTramites
from tramites.serializers.tramites_serializers import AnexosGetSerializer, AnexosUpdateSerializer, InicioTramiteCreateSerializer, ListTramitesGetSerializer, PersonaTitularInfoGetSerializer, TramiteListGetSerializer
from transversal.models.base_models import Municipio
from transversal.models.personas_models import Personas

class ListTramitesGetView(generics.ListAPIView):
    serializer_class = ListTramitesGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, cod_tipo_permiso_ambiental):
        cod_tipo_permiso_ambiental_correctos = ['L', 'P', 'D', 'O']
        if cod_tipo_permiso_ambiental not in cod_tipo_permiso_ambiental_correctos:
            raise ValidationError('El código del tipo de permiso ambiental es incorrecto')
        
        permisos_ambientales = PermisosAmbientales.objects.filter(cod_tipo_permiso_ambiental=cod_tipo_permiso_ambiental)
        
        serializer = self.serializer_class(permisos_ambientales, many=True)
        
        return Response({'success': True, 'detail':'Se encontraron los siguientes resultados', 'data': serializer.data}, status=status.HTTP_200_OK)   

class PersonaTitularInfoGetView(generics.ListAPIView):
    serializer_class = PersonaTitularInfoGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_persona):
        persona = Personas.objects.filter(id_persona=id_persona).first()
        if not persona:
            raise NotFound('No se encontró la persona')
        
        serializer = self.serializer_class(persona, many=False)
        
        return Response({'success': True, 'detail':'Se encontró la siguiente información', 'data': serializer.data}, status=status.HTTP_200_OK)   

class TramiteListGetView(generics.ListAPIView):
    serializer_class = TramiteListGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_persona_titular):
        tramites_opas = PermisosAmbSolicitudesTramite.objects.filter(id_solicitud_tramite__id_medio_solicitud=2, id_solicitud_tramite__id_persona_titular=id_persona_titular, id_permiso_ambiental__cod_tipo_permiso_ambiental = 'O')

        serializer = self.serializer_class(tramites_opas, many=True)
        
        return Response({'success': True, 'detail':'Se encontró la siguiente información', 'data': serializer.data}, status=status.HTTP_200_OK)   

class InicioTramiteCreateView(generics.CreateAPIView):
    serializer_class = InicioTramiteCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        data = request.data
        
        direccion = request.data.get('direccion', '')
        descripcion_direccion = request.data.get('descripcion_direccion', '')
        coordenada_x = data.get('coordenada_x')
        coordenada_y = data.get('coordenada_y')
        cod_municipio = data.get('cod_municipio', '')
        if direccion == '':
            raise ValidationError('La dirección es obligatoria')
        if descripcion_direccion == '':
            raise ValidationError('La descripción de la dirección es obligatoria')
        if cod_municipio == '':
            raise ValidationError('El municipio es obligatorio')
        
        municipio = Municipio.objects.filter(cod_municipio=cod_municipio).first()
        if not municipio:
            raise ValidationError('El municipio es incorrecto')
        
        id_permiso_ambiental = data.get('id_permiso_ambiental')
        if not id_permiso_ambiental:
            raise ValidationError('El trámite o servicio es obligatorio')
        
        permiso_ambiental = PermisosAmbientales.objects.filter(id_permiso_ambiental=id_permiso_ambiental).first()
        if not permiso_ambiental:
            raise ValidationError('No se encontró el trámite elegido')
        
        id_persona_titular = data.get('id_persona_titular')
        id_persona_interpone = data.get('id_persona_interpone')
        
        if id_persona_titular == id_persona_interpone:
            data['cod_relacion_con_el_titular'] = 'MP'
        else:
            data['cod_relacion_con_el_titular'] = 'RL' # VALIDAR PARA CASO DE APODERADOS
        
        data['cod_tipo_operacion_tramite'] = 'N'
        data['nombre_proyecto'] = permiso_ambiental.nombre
        data['costo_proyecto'] = 0
        data['fecha_inicio_tramite'] = datetime.now()
        # data['id_medio_solicitud'] = 2 # QUE LO MANDE FRONTEND
        data['id_persona_registra'] = request.user.persona.id_persona
        data['id_estado_actual_solicitud'] = 1
        data['fecha_ini_estado_actual'] = datetime.now()
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        tramite_creado = serializer.save()
        
        # CREAR EN T280
        PermisosAmbSolicitudesTramite.objects.create(
            id_permiso_ambiental = permiso_ambiental,
            id_solicitud_tramite = tramite_creado,
            descripcion_direccion = descripcion_direccion,
            coordenada_x = coordenada_x,
            coordenada_y = coordenada_y,
            cod_municipio = municipio,
            direccion = direccion
        )
        
        data_serializada = serializer.data
        data_serializada['id_permiso_ambiental'] = id_permiso_ambiental
        data_serializada['descripcion_direccion'] = descripcion_direccion
        data_serializada['coordenada_x'] = coordenada_x
        data_serializada['coordenada_y'] = coordenada_y
        data_serializada['cod_municipio'] = cod_municipio
        data_serializada['direccion'] = direccion
        
        return Response({'success': True, 'detail':'Se realizó la creación del inicio del trámite correctamente', 'data': data_serializada}, status=status.HTTP_201_CREATED)   

class InicioTramiteUpdateView(generics.UpdateAPIView):
    serializer_class = InicioTramiteCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, id_solicitud_tramite):
        data = request.data
        
        solicitud = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not solicitud:
            raise NotFound('No se encontró la solicitud')
        
        permiso_amb_solicitud = PermisosAmbSolicitudesTramite.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        
        id_permiso_ambiental = data.get('id_permiso_ambiental')
        direccion = request.data.get('direccion', '')
        descripcion_direccion = request.data.get('descripcion_direccion', '')
        coordenada_x = data.get('coordenada_x')
        coordenada_y = data.get('coordenada_y')
        cod_municipio = data.get('cod_municipio', '')
        
        # ACTUALIZAR PERMISO AMBIENTAL SOLICITUD
        if id_permiso_ambiental != permiso_amb_solicitud.id_permiso_ambiental.id_permiso_ambiental:
            permiso_ambiental = PermisosAmbientales.objects.filter(id_permiso_ambiental=id_permiso_ambiental).first()
            if not permiso_ambiental:
                raise ValidationError('No se encontró el trámite elegido')
            
            permiso_amb_solicitud.id_permiso_ambiental = permiso_ambiental
            solicitud.nombre_proyecto = permiso_ambiental.nombre
            solicitud.save()
            
        if direccion != '' and direccion != permiso_amb_solicitud.direccion:
            permiso_amb_solicitud.direccion = direccion
        if descripcion_direccion != '' and descripcion_direccion != permiso_amb_solicitud.descripcion_direccion:
            permiso_amb_solicitud.descripcion_direccion = descripcion_direccion
        if coordenada_x != '' and coordenada_x != permiso_amb_solicitud.coordenada_x:
            permiso_amb_solicitud.coordenada_x = coordenada_x
        if coordenada_y != '' and coordenada_y != permiso_amb_solicitud.coordenada_y:
            permiso_amb_solicitud.coordenada_y = coordenada_y
        if cod_municipio != '' and cod_municipio != permiso_amb_solicitud.cod_municipio.cod_municipio:
            municipio = Municipio.objects.filter(cod_municipio=cod_municipio).first()
            if not municipio:
                raise ValidationError('El municipio es incorrecto')
            permiso_amb_solicitud.cod_municipio = municipio
        
        permiso_amb_solicitud.save()
        
        serializer = self.serializer_class(solicitud)
        
        data_serializada = serializer.data
        data_serializada['id_permiso_ambiental'] = id_permiso_ambiental
        # data_serializada['direccion'] = direccion
        data_serializada['descripcion_direccion'] = descripcion_direccion
        data_serializada['coordenada_x'] = coordenada_x
        data_serializada['coordenada_y'] = coordenada_y
        data_serializada['direccion'] = direccion
        data_serializada['cod_municipio'] = cod_municipio
        
        return Response({'success': True, 'detail':'Se realizó la actualización del inicio del trámite correctamente', 'data': data_serializada}, status=status.HTTP_201_CREATED)   

class AnexosUpdateView(generics.UpdateAPIView):
    serializer_class = AnexosUpdateSerializer
    serializer_get_class = AnexosGetSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, id_solicitud_tramite):
        data = request.data
        data_anexos = json.loads(data['data_anexos'])
        archivos = request.FILES.getlist('archivos')
        
        solicitud_tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not solicitud_tramite:
            raise NotFound('No se encontró el trámite del OPA elegido')
        
        anexos_instances = AnexosTramite.objects.filter(id_solicitud_tramite=id_solicitud_tramite)
        
        anexos_crear = [anexo for anexo in data_anexos if not anexo['id_anexo_tramite']]
        anexos_actualizar = [anexo for anexo in data_anexos if anexo['id_anexo_tramite']]
        anexos_eliminar = anexos_instances.exclude(id_anexo_tramite__in=[anexo['id_anexo_tramite'] for anexo in anexos_actualizar])
        
        if len(anexos_crear) != len(archivos):
            raise ValidationError('Debe enviar la data para cada archivo anexado')
        
        # ELIMINAR ANEXOS
        for anexo in anexos_eliminar:
            anexo.id_archivo.delete()
            anexo.delete()
        
        # CREAR ANEXOS
        for data, archivo in zip(anexos_crear, archivos):
            # VALIDAR FORMATO ARCHIVO 
            archivo_nombre = archivo.name
            nombre_sin_extension, extension = os.path.splitext(archivo_nombre)
            extension_sin_punto = extension[1:] if extension.startswith('.') else extension
            
            formatos_tipos_medio_list = FormatosTiposMedio.objects.all().values_list('nombre', flat=True)
            
            if extension_sin_punto.lower() not in list(formatos_tipos_medio_list) and extension_sin_punto.upper() not in list(formatos_tipos_medio_list):
                raise ValidationError(f'El formato del anexo {archivo_nombre} no es válido')
            
            # CREAR ARCHIVO EN T238
            # Obtiene el año actual para determinar la carpeta de destino
            current_year = datetime.now().year
            ruta = os.path.join("home", "BIA", "Otros", "GDEA", str(current_year))

            # Calcula el hash MD5 del archivo
            md5_hash = hashlib.md5()
            for chunk in archivo.chunks():
                md5_hash.update(chunk)

            # Obtiene el valor hash MD5
            md5_value = md5_hash.hexdigest()

            # Crea el archivo digital y obtiene su ID
            data_archivo = {
                'es_Doc_elec_archivo': True,
                'ruta': ruta,
                'md5_hash': md5_value  # Agregamos el hash MD5 al diccionario de datos
            }
            
            archivo_class = ArchivosDgitalesCreate()
            respuesta = archivo_class.crear_archivo(data_archivo, archivo)
            
            # CREAR DOCUMENTO EN T287
            data['id_solicitud_tramite'] = id_solicitud_tramite
            data['id_permiso_amb_solicitud_tramite'] = solicitud_tramite.permisosambsolicitudestramite_set.first().id_permiso_amb_solicitud_tramite
            data['nombre'] = archivo_nombre
            data['id_archivo'] = respuesta.data.get('data').get('id_archivo_digital')
            
            serializer_crear = self.serializer_class(data=data)
            serializer_crear.is_valid(raise_exception=True)
            serializer_crear.save()
        
        # ACTUALIZAR ANEXOS
        for anexo in anexos_actualizar:
            anexo_instance = anexos_instances.filter(id_anexo_tramite=anexo['id_anexo_tramite']).first()
            if anexo['descripcion'] != anexo_instance.descripcion:
                anexo_instance.descripcion = anexo['descripcion']
                anexo_instance.save()
        
        anexos_instances = AnexosTramite.objects.filter(id_solicitud_tramite=id_solicitud_tramite)
        serializer_get = self.serializer_get_class(anexos_instances, many=True, context={'request': request})
        
        return Response({'success':True, 'detail':'Anexos procesados correctamente', 'data':serializer_get.data}, status=status.HTTP_201_CREATED)

class AnexosGetView(generics.ListAPIView):
    serializer_class = AnexosGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_solicitud_tramite):
        solicitud_tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not solicitud_tramite:
            raise NotFound('No se encontró el trámite del OPA elegido')
        
        anexos_instances = AnexosTramite.objects.filter(id_solicitud_tramite=id_solicitud_tramite)
        serializer_get = self.serializer_class(anexos_instances, many=True, context={'request': request})
        
        return Response({'success':True, 'detail':'Se encontraron los siguientes anexos del trámite', 'data':serializer_get.data}, status=status.HTTP_200_OK)

class RadicarCreateView(generics.CreateAPIView):
    serializer_class = AnexosGetSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, id_solicitud_tramite):
        data = request.data
        current_date = datetime.now()
        
        solicitud = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not solicitud:
            raise NotFound('No se encontró el trámite del OPA elegido')
        
        if solicitud.id_radicado:
            raise ValidationError('El trámite ya ha sido radicado')
        
        data['fecha_actual'] = current_date
        data['id_usuario'] = request.user.id_usuario
        data['tipo_radicado'] = "E" # VALIDAR
        data['modulo_radica'] = "Trámites y Servicios" # VALIDAR
        
        radicado_class = RadicadoCreate()
        radicado_response = radicado_class.post(data)
        
        id_radicado = radicado_response.get('id_radicado')
        numero_radicado = radicado_response.get('nro_radicado')
        
        # ACTUALIZAR SOLICITUD
        radicado = T262Radicados.objects.filter(id_radicado=id_radicado).first()
        if not radicado:
            raise NotFound('No se encontró el radicado generado')
        
        estado_solicitud = EstadosSolicitudes.objects.filter(id_estado_solicitud=2).first()
        if not estado_solicitud:
            raise NotFound('No se encontró el estado de la solicitud')
        
        solicitud.id_radicado = radicado
        solicitud.fecha_radicado = current_date
        solicitud.id_estado_actual_solicitud = estado_solicitud
        solicitud.save()
        
        # ENVIAR CORREO CON RADICADO
        subject = "OPA radicado con éxito - "
        template = "envio-radicado-opas.html"
        Util.notificacion(request.user.persona,subject,template,nombre_de_usuario=request.user.nombre_de_usuario,numero_radicado=numero_radicado)
        
        return Response({'success': True, 'detail':'Se realizó la radicación correctamente', 'data':radicado_response}, status=status.HTTP_201_CREATED)   

class RadicarGetView(generics.ListAPIView):
    serializer_class = RadicadoPostSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_solicitud_tramite):
        solicitud = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not solicitud:
            raise NotFound('No se encontró el trámite del OPA elegido')
        
        if not solicitud.id_radicado:
            raise ValidationError('El trámite aún no ha sido radicado')
        
        serializer = self.serializer_class(solicitud.id_radicado, context={'request': request})
        
        return Response({'success': True, 'detail':'Se encontró la información de la radicación', 'data':serializer.data}, status=status.HTTP_200_OK)

class RadicarVolverEnviarGetView(generics.ListAPIView):
    serializer_class = RadicadoPostSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_solicitud_tramite):
        solicitud = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not solicitud:
            raise NotFound('No se encontró el trámite del OPA elegido')
        
        if not solicitud.id_radicado:
            raise ValidationError('El trámite aún no ha sido radicado')
        
        numero_radicado = solicitud.id_radicado.nro_radicado
        
        # ENVIAR CORREO CON RADICADO
        subject = "OPA radicado con éxito - "
        template = "envio-radicado-opas.html"
        Util.notificacion(request.user.persona,subject,template,nombre_de_usuario=request.user.nombre_de_usuario,numero_radicado=numero_radicado)
        
        serializer = self.serializer_class(solicitud.id_radicado, context={'request': request})
        
        return Response({'success': True, 'detail':'Se volvió a enviar la radicación correctamente', 'data':serializer.data}, status=status.HTTP_200_OK)   
