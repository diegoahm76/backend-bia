import json
import os
import hashlib
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import generics, views
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.models.radicados_models import Anexos, ConfigTiposRadicadoAgno, Estados_PQR, EstadosSolicitudes, MetadatosAnexosTmp, T262Radicados
from gestion_documental.models.trd_models import FormatosTiposMedio
from gestion_documental.serializers.pqr_serializers import MetadatosPostSerializer, RadicadoPostSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.views.configuracion_tipos_radicados_views import ConfigTiposRadicadoAgnoGenerarN
from gestion_documental.views.pqr_views import RadicadoCreate
from jobs.jobs import update_tramites_bia
from seguridad.utils import Util
from datetime import datetime, date, timedelta
from django.db.models import Max
from django.db.models import Q
from gestion_documental.models.bandeja_tareas_models import TareasAsignadas, ReasignacionesTareas
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, AsignacionTramites, ComplementosUsu_PQR, EstadosSolicitudes, MediosSolicitud, MetadatosAnexosTmp, Otros, RespuestaPQR, SolicitudAlUsuarioSobrePQRSDF, T262Radicados, TiposPQR, modulos_radican
from tramites.models.tramites_models import AnexosTramite, PermisosAmbSolicitudesTramite, PermisosAmbientales, SolicitudesTramites, Tramites
from tramites.serializers.tramites_serializers import AnexosGetSerializer, AnexosUpdateSerializer, GeneralTramitesGetSerializer, GetTiposTramitesSerializer, InicioTramiteCreateSerializer, ListTramitesGetSerializer, OPASSerializer, PersonaTitularInfoGetSerializer, PostTiposTramitesSerializer, TramiteListGetSerializer
from transversal.models.base_models import Municipio
from transversal.models.personas_models import Personas
from jobs.updater import scheduler

class GeneralTramitesCreateView(generics.CreateAPIView):
    serializer_class = InicioTramiteCreateSerializer
    serializer_anexos_class = AnexosUpdateSerializer
    serializer_get_tramite_class = GeneralTramitesGetSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        data = request.data
        data_tramite = json.loads(data['data_tramite'])
        archivos = request.FILES.getlist('archivos')
        current_date = datetime.now()
        persona_logueada = request.user.persona
        
        data_tramite['fecha_inicio_tramite'] = datetime.now()
        data_tramite['id_persona_interpone'] = request.user.persona.id_persona
        data_tramite['id_persona_registra'] = request.user.persona.id_persona
        data_tramite['id_medio_solicitud'] = 2
        data_tramite['id_estado_actual_solicitud'] = 13
        data_tramite['requiere_digitalizacion'] = True
        data_tramite['fecha_ini_estado_actual'] = datetime.now()
        
        serializer = self.serializer_class(data=data_tramite)
        serializer.is_valid(raise_exception=True)
        tramite_creado = serializer.save()
        
        # Insertar en T255 con estado PENDIENTE POR RADICAR
        estado_solicitud_instance = EstadosSolicitudes.objects.filter(id_estado_solicitud=13).first()
        Estados_PQR.objects.create(
            id_tramite = tramite_creado,
            estado_solicitud = estado_solicitud_instance,
            fecha_iniEstado = current_date,
            persona_genera_estado = persona_logueada
        )
        
        # CREAR ANEXOS
        for index, (archivo) in enumerate(archivos):
            cont = index + 1
            
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
            ruta = os.path.join("home", "BIA", "Otros", "Tramites", str(current_year))

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
            
            # CREAR ARCHIVO EN T238
            archivo_class = ArchivosDgitalesCreate()
            respuesta = archivo_class.crear_archivo(data_archivo, archivo)
            archivo_digital_instance = ArchivosDigitales.objects.filter(id_archivo_digital=respuesta.data.get('data').get('id_archivo_digital')).first()
            
            # CREAR ANEXO EN T258
            anexo_creado = Anexos.objects.create(
                nombre_anexo = nombre_sin_extension,
                orden_anexo_doc = cont,
                cod_medio_almacenamiento = 'Na',
                numero_folios = 0,
                ya_digitalizado = False
            )
            
            # CREAR ANEXO EN T260
            MetadatosAnexosTmp.objects.create(
                id_anexo = anexo_creado,
                nombre_original_archivo = nombre_sin_extension,
                fecha_creacion_doc = current_date.date(),
                id_archivo_sistema = archivo_digital_instance
            )
            
            # CREAR DOCUMENTO EN 
            data_anexo = {}
            data_anexo['id_solicitud_tramite'] = tramite_creado.id_solicitud_tramite
            data_anexo['id_anexo'] = anexo_creado.id_anexo
            
            serializer_anexos_crear = self.serializer_anexos_class(data=data_anexo)
            serializer_anexos_crear.is_valid(raise_exception=True)
            serializer_anexos_crear.save()
        
        # RADICAR TRAMITE
        data_radicar = {}
        data_radicar['fecha_actual'] = current_date
        data_radicar['id_persona'] = request.user.persona.id_persona
        data_radicar['tipo_radicado'] = data_tramite['tipo_radicado']
        data_radicar['modulo_radica'] = "Trámites y servicios"
        
        radicado_class = RadicadoCreate()
        radicado_response = radicado_class.post(data_radicar)
        
        id_radicado = radicado_response.get('id_radicado')
        radicado_nuevo = radicado_response.get('radicado_nuevo')
        radicado = T262Radicados.objects.filter(id_radicado=id_radicado).first()
        estado_solicitud = EstadosSolicitudes.objects.filter(id_estado_solicitud=2).first()
        
        tramite_creado.id_radicado = radicado
        tramite_creado.fecha_radicado = current_date
        tramite_creado.id_estado_actual_solicitud = estado_solicitud
        tramite_creado.save()
        
        # Insertar en T255 con estado RADICADO
        estado_solicitud_radicado_instance = EstadosSolicitudes.objects.filter(id_estado_solicitud=2).first()
        Estados_PQR.objects.create(
            id_tramite = tramite_creado,
            estado_solicitud = estado_solicitud_radicado_instance,
            fecha_iniEstado = current_date,
            persona_genera_estado = persona_logueada
        )
        
        tramite_instance_updated = SolicitudesTramites.objects.filter(id_solicitud_tramite=tramite_creado.id_solicitud_tramite).first()
        serializer_tramite = self.serializer_get_tramite_class(tramite_instance_updated)
        serializer_tramite_data = serializer_tramite.data
        serializer_tramite_data['radicado_nuevo'] = radicado_nuevo
        
        if scheduler:
            execution_time = datetime.now() + timedelta(minutes=1)
            scheduler.add_job(update_tramites_bia, args=[radicado_nuevo], trigger='date', run_date=execution_time)
        
        return Response({'success': True, 'detail':'Se realizó la creación del del trámite correctamente', 'data': serializer_tramite_data}, status=status.HTTP_201_CREATED)   

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
        current_date = datetime.now()
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
        data['requiere_digitalizacion'] = True
        data['nombre_proyecto'] = permiso_ambiental.nombre
        data['costo_proyecto'] = 0
        data['fecha_inicio_tramite'] = datetime.now()
        # data['id_medio_solicitud'] = 2 # QUE LO MANDE FRONTEND
        data['id_persona_registra'] = request.user.persona.id_persona
        data['id_estado_actual_solicitud'] = 13
        data['fecha_ini_estado_actual'] = datetime.now()
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        tramite_creado = serializer.save()
        
        # Insertar en T255 con estado PENDIENTE POR RADICAR
        estado_solicitud_instance = EstadosSolicitudes.objects.filter(id_estado_solicitud=13).first()
        Estados_PQR.objects.create(
            id_tramite = tramite_creado,
            estado_solicitud = estado_solicitud_instance,
            fecha_iniEstado = current_date,
            persona_genera_estado = request.user.persona
        )
        
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
        
        if solicitud.id_radicado:
            raise ValidationError('No puede actualizar un trámite que ya ha sido radicado')
        
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
        current_date = datetime.now()
        
        solicitud_tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not solicitud_tramite:
            raise NotFound('No se encontró el trámite del OPA elegido')
        
        if solicitud_tramite.id_radicado:
            raise ValidationError('No puede actualizar un trámite que ya ha sido radicado')
        
        anexos_instances = AnexosTramite.objects.filter(id_solicitud_tramite=id_solicitud_tramite)
        
        anexos_crear = [anexo for anexo in data_anexos if not anexo['id_anexo_tramite']]
        anexos_actualizar = [anexo for anexo in data_anexos if anexo['id_anexo_tramite']]
        anexos_eliminar = anexos_instances.exclude(id_anexo_tramite__in=[anexo['id_anexo_tramite'] for anexo in anexos_actualizar])
        
        if len(anexos_crear) != len(archivos):
            raise ValidationError('Debe enviar la data para cada archivo anexado')
        
        # ELIMINAR ANEXOS
        for anexo in anexos_eliminar:
            metadata_instance = MetadatosAnexosTmp.objects.filter(id_anexo=anexo.id_anexo).first()
            metadata_instance.id_archivo_sistema.delete()
            metadata_instance.delete()
            anexo.id_anexo.delete()
            anexo.delete()
        
        last_orden = anexos_instances.aggregate(Max('id_anexo__orden_anexo_doc'))
        last_orden = last_orden['id_anexo__orden_anexo_doc__max'] if last_orden['id_anexo__orden_anexo_doc__max'] else 0
        
        # CREAR ANEXOS
        for index, (data, archivo) in enumerate(zip(anexos_crear, archivos)):
            cont = index + 1
            
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
            ruta = os.path.join("home", "BIA", "Otros", "OPAS", str(current_year))

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
            
            # CREAR ARCHIVO EN T238
            archivo_class = ArchivosDgitalesCreate()
            respuesta = archivo_class.crear_archivo(data_archivo, archivo)
            archivo_digital_instance = ArchivosDigitales.objects.filter(id_archivo_digital=respuesta.data.get('data').get('id_archivo_digital')).first()
            
            # CREAR ANEXO EN T258
            anexo_creado = Anexos.objects.create(
                nombre_anexo = nombre_sin_extension,
                orden_anexo_doc = last_orden + cont,
                cod_medio_almacenamiento = 'Na',
                numero_folios = 0,
                ya_digitalizado = False
            )
            
            # CREAR ANEXO EN T260
            MetadatosAnexosTmp.objects.create(
                id_anexo = anexo_creado,
                nombre_original_archivo = nombre_sin_extension,
                fecha_creacion_doc = current_date.date(),
                descripcion = data['descripcion'],
                id_archivo_sistema = archivo_digital_instance
            )
            
            # CREAR DOCUMENTO EN T287
            data['id_solicitud_tramite'] = id_solicitud_tramite
            data['id_permiso_amb_solicitud_tramite'] = solicitud_tramite.permisosambsolicitudestramite_set.first().id_permiso_amb_solicitud_tramite
            data['id_anexo'] = anexo_creado.id_anexo
            
            serializer_crear = self.serializer_class(data=data)
            serializer_crear.is_valid(raise_exception=True)
            serializer_crear.save()
        
        # ACTUALIZAR ANEXOS
        for anexo in anexos_actualizar:
            anexo_instance = anexos_instances.filter(id_anexo_tramite=anexo['id_anexo_tramite']).first()
            metadata_instance = MetadatosAnexosTmp.objects.filter(id_anexo=anexo_instance.id_anexo.id_anexo).first()
            if metadata_instance and anexo['descripcion'] != metadata_instance.descripcion:
                metadata_instance.descripcion = anexo['descripcion']
                metadata_instance.save()
        
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
        data['id_persona'] = request.user.persona.id_persona
        data['tipo_radicado'] = "E" # VALIDAR
        data['modulo_radica'] = "Trámites y servicios" # VALIDAR
        
        radicado_class = RadicadoCreate()
        radicado_response = radicado_class.post(data)
        
        id_radicado = radicado_response.get('id_radicado')
        radicado_nuevo = radicado_response.get('radicado_nuevo')
        
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
        
        # Insertar en T255 con estado RADICADO
        Estados_PQR.objects.create(
            id_tramite = solicitud,
            estado_solicitud = estado_solicitud,
            fecha_iniEstado = current_date,
            persona_genera_estado = request.user.persona
        )
        
        # ENVIAR CORREO CON RADICADO
        subject = "OPA radicado con éxito - "
        template = "envio-radicado-opas.html"
        Util.notificacion(request.user.persona,subject,template,nombre_de_usuario=request.user.nombre_de_usuario,numero_radicado=radicado_nuevo)
        
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
        
        instance_config_tipo_radicado =ConfigTiposRadicadoAgno.objects.filter(agno_radicado=solicitud.id_radicado.agno_radicado,cod_tipo_radicado=solicitud.id_radicado.cod_tipo_radicado).first()
        numero_con_ceros = str(solicitud.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
        radicado_nuevo= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
        serializer = self.serializer_class(solicitud.id_radicado, context={'request': request})
        serializer_data = serializer.data
        serializer_data['radicado_nuevo'] = radicado_nuevo
        
        return Response({'success': True, 'detail':'Se encontró la información de la radicación', 'data':serializer_data}, status=status.HTTP_200_OK)

class RadicarVolverEnviarGetView(generics.ListAPIView):
    serializer_class = RadicadoPostSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_solicitud_tramite):
        solicitud = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not solicitud:
            raise NotFound('No se encontró el trámite del OPA elegido')
        
        if not solicitud.id_radicado:
            raise ValidationError('El trámite aún no ha sido radicado')
        
        instance_config_tipo_radicado =ConfigTiposRadicadoAgno.objects.filter(agno_radicado=solicitud.id_radicado.agno_radicado,cod_tipo_radicado=solicitud.id_radicado.cod_tipo_radicado).first()
        numero_con_ceros = str(solicitud.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
        radicado_nuevo= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
        # ENVIAR CORREO CON RADICADO
        subject = "OPA radicado con éxito - "
        template = "envio-radicado-opas.html"
        Util.notificacion(request.user.persona,subject,template,nombre_de_usuario=request.user.nombre_de_usuario,numero_radicado=radicado_nuevo)
        
        serializer = self.serializer_class(solicitud.id_radicado, context={'request': request})
        serializer_data = serializer.data
        serializer_data['radicado_nuevo'] = radicado_nuevo
        
        return Response({'success': True, 'detail':'Se volvió a enviar la radicación correctamente', 'data':serializer_data}, status=status.HTTP_200_OK)   



################################################################################################################################################
#CONSULTA_ESTADO_OPAS
class ConsultaEstadoOPAS(generics.ListAPIView):
    serializer_class = OPASSerializer

    def get_queryset(self):
        opas = PermisosAmbSolicitudesTramite.objects.filter(
            id_permiso_ambiental__cod_tipo_permiso_ambiental='O'
        )

        fecha_radicado_desde = self.request.query_params.get('fecha_radicado_desde')
        fecha_radicado_hasta = self.request.query_params.get('fecha_radicado_hasta')
        radicado = self.request.query_params.get('radicado')
        estado_solicitud = self.request.query_params.get('estado_solicitud')



        if fecha_radicado_desde:
            opas = opas.filter(id_solicitud_tramite__fecha_radicado__gte=fecha_radicado_desde)

        if fecha_radicado_hasta:
            opas = opas.filter(id_solicitud_tramite__fecha_radicado__lte=fecha_radicado_hasta)

        if radicado:
            # Filtrar por el radicado en la tabla T262Radicados con flexibilidad
            if '-' in radicado:
                try:
                    prefijo, agno, numero = radicado.split('-')
                except ValueError:
                    # Si no se puede dividir en prefijo, año y número, continuar sin filtrar por radicado
                    pass
                else:
                    opas = opas.filter(
                        id_solicitud_tramite__id_radicado__prefijo_radicado__icontains=prefijo,
                        id_solicitud_tramite__id_radicado__agno_radicado__icontains=agno,
                        id_solicitud_tramite__id_radicado__nro_radicado__icontains=numero
                    )
            else:
                # Si no hay guion ('-'), buscar en cualquier parte del radicado
                opas = opas.filter(
                    Q(id_solicitud_tramite__id_radicado__prefijo_radicado__icontains=radicado) |
                    Q(id_solicitud_tramite__id_radicado__agno_radicado__icontains=radicado) |
                    Q(id_solicitud_tramite__id_radicado__nro_radicado__icontains=radicado)
                )

            
        if estado_solicitud:
            opas = opas.filter(id_solicitud_tramite__id_estado_actual_solicitud__nombre=estado_solicitud)
            
        return opas

    def get_location_info(self, tramites):
        estado_actual = tramites.id_estado_actual_solicitud

        if estado_actual and estado_actual.nombre in ['RADICADO', 'EN VENTANILLA CON PENDIENTES', 'EN VENTANILLA SIN PENDIENTES','PENDIENTE DE REVISIÓN JURIDICA DE VENTANILLA']:
            return 'EN VENTANILLA'

        elif estado_actual and estado_actual.nombre == 'EN GESTION':
            try:
                asignacion = AsignacionTramites.objects.filter(
                    id_tramites=tramites,
                    cod_estado_asignacion='Ac'
                ).latest('fecha_asignacion')

                tarea_reasignada = ReasignacionesTareas.objects.filter(
                    id_tarea_asignada=asignacion.id_asignacion_otros,
                    cod_estado_reasignacion='Ac'
                ).first()

                if tarea_reasignada:
                    # Si hay reasignación
                    if tarea_reasignada.cod_estado_reasignacion == 'Ep':
                        # Reasignación en espera
                        unidad_reasignada = tarea_reasignada.id_und_org_reasignada
                    elif tarea_reasignada.cod_estado_reasignacion == 'Re':
                        # Reasignación rechazada
                        unidad_reasignada = tarea_reasignada.id_und_org_reasignada
                    elif tarea_reasignada.cod_estado_reasignacion == 'Ac':
                        # Reasignación aceptada
                        persona_reasignada = Personas.objects.get(id_persona=tarea_reasignada.id_persona_a_quien_se_reasigna)
                        unidad_reasignada = persona_reasignada.id_unidad_organizacional_actual

                    if unidad_reasignada:
                        if unidad_reasignada.cod_agrupacion_documental == 'SEC':
                            return f'SECCION - {unidad_reasignada.codigo} - {unidad_reasignada.nombre}'
                        elif unidad_reasignada.cod_agrupacion_documental == 'SUB':
                            return f'SUBSECCION - {unidad_reasignada.codigo} - {unidad_reasignada.nombre}'
                        elif unidad_reasignada.cod_agrupacion_documental is None:
                            return f'{unidad_reasignada.codigo} - {unidad_reasignada.nombre}'

                # Si no hay reasignación, mostrar la unidad original
                unidad_asignada = asignacion.id_und_org_seccion_asignada
                if unidad_asignada:
                    if unidad_asignada.cod_agrupacion_documental == 'SEC':
                        return f'SECCION - {unidad_asignada.codigo} - {unidad_asignada.nombre}'
                    elif unidad_asignada.cod_agrupacion_documental == 'SUB':
                        return f'SUBSECCION - {unidad_asignada.codigo} - {unidad_asignada.nombre}'
                    elif unidad_asignada.cod_agrupacion_documental is None:
                        return f'{unidad_asignada.codigo} - {unidad_asignada.nombre}'

            except AsignacionTramites.DoesNotExist:
                pass

        return None

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        data = serializer.data

        for item in data:
            solicitud_id = item['id_solicitud_tramite']
            solicitud = get_object_or_404(SolicitudesTramites, pk=solicitud_id)
            if solicitud.id_persona_titular:
                titular = solicitud.id_persona_titular
                if titular.tipo_persona == 'N':
                    titular_nombre = f'{titular.primer_nombre} {titular.segundo_nombre} {titular.primer_apellido} {titular.segundo_apellido}'
                elif titular.tipo_persona == 'J':
                    titular_nombre = titular.razon_social
                else:
                    titular_nombre = 'Anónimo'
                item['Persona_titular'] = titular_nombre
                item['ID_persona_titular'] = titular.id_persona
            else:
                item['Persona_titular'] = 'Anónimo'
                item['ID_persona_titular'] = 'N/A'

            solicitud = get_object_or_404(SolicitudesTramites, pk=solicitud_id)
            radicado_id = solicitud.id_radicado_id
            radicado = T262Radicados.objects.filter(id_radicado=radicado_id).first()
            if radicado:
                radicado_str = f"{radicado.prefijo_radicado}-{radicado.agno_radicado}-{radicado.nro_radicado}"
                fecha_radicado = radicado.fecha_radicado.strftime("%Y-%m-%d %H:%M:%S")
                persona_radica_id = radicado.id_persona_radica_id
                persona_radica_nombre = f"{radicado.id_persona_radica.primer_nombre} {radicado.id_persona_radica.segundo_nombre} {radicado.id_persona_radica.primer_apellido} {radicado.id_persona_radica.segundo_apellido}"
            else:
                radicado_str = 'N/A'
                fecha_radicado = 'N/A'
                persona_radica_id = 'N/A'
                persona_radica_nombre = 'N/A'
            item['Radicado'] = radicado_str
            item['Fecha_Radicado'] = fecha_radicado
            item['Persona_radica_id'] = persona_radica_id
            item['Persona_radica_nombre'] = persona_radica_nombre

            estado_actual = solicitud.id_estado_actual_solicitud
            if estado_actual:
                item['Estado_actual_nombre'] = estado_actual.nombre
                item['Estado_actual_id'] = estado_actual.id_estado_solicitud
            else:
                item['Estado_actual_nombre'] = 'N/A'
                item['Estado_actual_id'] = 'N/A'

            location_info = self.get_location_info(solicitud)
            item['Location_info'] = location_info
            item['Tiempo de respuesta'] = None
            item['Documento'] = None
            item['Tipo Solicitud'] = "OPAS"



        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': data}, status=status.HTTP_200_OK)
    
class TramitesPivotGetView(generics.ListAPIView):
    serializer_class = AnexosGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        filter = {}
        
        for key, value in request.query_params.items():
            if key in ['procedure_id','radicado']:
                if key == 'radicado':
                    if value != '':
                        filter['radicate_bia__icontains'] = value
                elif value != '':
                    filter[key] = value
        
        tramites_values = Tramites.objects.filter(**filter).values()
        
        if tramites_values:
            organized_data = {
                'procedure_id': tramites_values[0]['procedure_id'],
                'radicate_bia': tramites_values[0]['radicate_bia'],
                'proceeding_id': tramites_values[0]['proceeding_id'],
            }
            
            for item in tramites_values:
                field_name = item['name_key']
                if item['type_key'] == 'json':
                    value = json.loads(item['value_key'])
                else:
                    value = item['value_key']
                organized_data[field_name] = value
        else:
            raise NotFound('No se encontró el detalle del trámite elegido')
        
        return Response({'success':True, 'detail':'Se encontró el detalle del trámite', 'data':organized_data}, status=status.HTTP_200_OK)

class AnexosMetadatosUpdateView(generics.UpdateAPIView):
    serializer_class = AnexosUpdateSerializer
    serializer_get_class = AnexosGetSerializer
    serializer_metadatos_class = MetadatosPostSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, id_solicitud_tramite):
        data = request.data
        data_anexos = json.loads(data['data_anexos'])
        archivos = request.FILES.getlist('archivos')
        current_date = datetime.now()
        
        solicitud_tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not solicitud_tramite:
            raise NotFound('No se encontró el trámite del OPA elegido')
        
        if solicitud_tramite.id_radicado:
            raise ValidationError('No puede actualizar un trámite que ya ha sido radicado')
        
        anexos_instances = AnexosTramite.objects.filter(id_solicitud_tramite=id_solicitud_tramite)
        
        anexos_crear = [anexo for anexo in data_anexos if not anexo['id_anexo_tramite']]
        anexos_actualizar = [anexo for anexo in data_anexos if anexo['id_anexo_tramite']]
        anexos_eliminar = anexos_instances.exclude(id_anexo_tramite__in=[anexo['id_anexo_tramite'] for anexo in anexos_actualizar])
        
        if len(anexos_crear) != len(archivos):
            raise ValidationError('Debe enviar la data para cada archivo anexado')
        
        # ELIMINAR ANEXOS
        for anexo in anexos_eliminar:
            metadata_instance = MetadatosAnexosTmp.objects.filter(id_anexo=anexo.id_anexo).first()
            metadata_instance.id_archivo_sistema.delete()
            metadata_instance.delete()
            anexo.id_anexo.delete()
            anexo.delete()
        
        last_orden = anexos_instances.aggregate(Max('id_anexo__orden_anexo_doc'))
        last_orden = last_orden['id_anexo__orden_anexo_doc__max'] if last_orden['id_anexo__orden_anexo_doc__max'] else 0
        
        # CREAR ANEXOS
        for index, (data, archivo) in enumerate(zip(anexos_crear, archivos)):
            cont = index + 1
            
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
            ruta = os.path.join("home", "BIA", "Otros", "OPAS", str(current_year))

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
            
            # CREAR ARCHIVO EN T238
            archivo_class = ArchivosDgitalesCreate()
            respuesta = archivo_class.crear_archivo(data_archivo, archivo)
            archivo_digital_instance = ArchivosDigitales.objects.filter(id_archivo_digital=respuesta.data.get('data').get('id_archivo_digital')).first()
            
            # CREAR ANEXO EN T258
            nro_folios_documento = data.get('nro_folios_documento') if data.get('nro_folios_documento') else 0
            anexo_creado = Anexos.objects.create(
                nombre_anexo = nombre_sin_extension,
                orden_anexo_doc = last_orden + cont,
                cod_medio_almacenamiento = 'Na',
                numero_folios = nro_folios_documento,
                ya_digitalizado = False
            )
            
            # VALIDACIÓN TIPOLOGIA
            if data.get('id_tipologia_doc') and data.get('tipologia_no_creada_TRD'):
                raise ValidationError('Solo puede elegir la tipologia o ingresar el nombre de la tipología, no las dos cosas')
            elif not data.get('id_tipologia_doc') and not data.get('tipologia_no_creada_TRD'):
                raise ValidationError('Debe elegir una tipologia o ingresar el nombre de la tipología')
            
            # CREAR ANEXO EN T260
            data['id_anexo'] = anexo_creado.id_anexo
            data['nombre_original_archivo'] = nombre_sin_extension
            data['fecha_creacion_doc'] = current_date.date()
            data['id_archivo_sistema'] = archivo_digital_instance.id_archivo_digital
            
            serializer_anexo = self.serializer_metadatos_class(data=data)
            serializer_anexo.is_valid(raise_exception=True)
            serializer_anexo.save()
            
            # CREAR DOCUMENTO EN T287
            data['id_solicitud_tramite'] = id_solicitud_tramite
            data['id_permiso_amb_solicitud_tramite'] = solicitud_tramite.permisosambsolicitudestramite_set.first().id_permiso_amb_solicitud_tramite
            
            serializer_crear = self.serializer_class(data=data)
            serializer_crear.is_valid(raise_exception=True)
            serializer_crear.save()
        
        # ACTUALIZAR ANEXOS
        for anexo in anexos_actualizar:
            anexo_instance = anexos_instances.filter(id_anexo_tramite=anexo['id_anexo_tramite']).first()
            metadata_instance = MetadatosAnexosTmp.objects.filter(id_anexo=anexo_instance.id_anexo.id_anexo).first()
            if metadata_instance:
                anexo['id_anexo'] = metadata_instance.id_anexo.id_anexo
                serializer_anexo = self.serializer_metadatos_class(metadata_instance, data=anexo, partial=True)
                serializer_anexo.is_valid(raise_exception=True)
                serializer_anexo.save()
        
        anexos_instances = AnexosTramite.objects.filter(id_solicitud_tramite=id_solicitud_tramite)
        serializer_get = self.serializer_get_class(anexos_instances, many=True, context={'request': request})
        
        return Response({'success':True, 'detail':'Anexos procesados correctamente', 'data':serializer_get.data}, status=status.HTTP_201_CREATED)

# CRUD TIPOS TRAMITES
class GetTiposTramitesByFilterView(generics.ListAPIView):
    serializer_class = GetTiposTramitesSerializer
    queryset = PermisosAmbientales.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter={}
        
        for key,value in request.query_params.items():
            if key == 'nombre':
                filter[key+'__icontains'] = value
            elif key == 'tiene_pago':
                filter[key] = True if value.lower() == 'true' else False
            else:
                if value != '':
                    filter[key]=value
        
        tipos_tramites = self.queryset.filter(**filter)
        serializador = self.serializer_class(tipos_tramites, many=True)
        
        return Response({'success':True, 'detail':'Se encontró la siguiente información', 'data':serializador.data}, status=status.HTTP_200_OK)

class CreateTiposTramitesView(generics.CreateAPIView):
    serializer_class =  PostTiposTramitesSerializer
    queryset = PermisosAmbientales.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success':True, 'detail':'Se ha creado el tipo de tramite', 'data':serializador.data}, status=status.HTTP_201_CREATED)

class UpdateTiposTramitesView(generics.RetrieveUpdateAPIView):
    serializer_class = PostTiposTramitesSerializer
    queryset = PermisosAmbientales.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data=request.data
        tipo_tramite = self.queryset.filter(id_permiso_ambiental=pk).first()
        if tipo_tramite:
            if tipo_tramite.registro_precargado:
                raise PermissionDenied('No se puede actualizar el tipo de tramite de un registro precargado.')
            if tipo_tramite.item_ya_usado:
                raise PermissionDenied('No se puede actualizar el tipo de tramite porque se encuentra en uso.')
            
            serializer = self.serializer_class(tipo_tramite, data=data, many=False, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'success':True, 'detail':'Tipo tramite actualizado exitosamente','data':serializer.data}, status=status.HTTP_201_CREATED)

        else:
            raise NotFound('No existe el tipo de tramite')

class DeleteTiposTramitesView(generics.DestroyAPIView):
    serializer_class = GetTiposTramitesSerializer
    queryset = PermisosAmbientales.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        tipo_tramite = self.queryset.filter(id_permiso_ambiental=pk).first()
        if tipo_tramite:
            if not tipo_tramite.registro_precargado:
                if tipo_tramite.item_ya_usado:
                    raise PermissionDenied('Este tipo de tramite ya está siendo usado, no se pudo eliminar')

                tipo_tramite.delete()
                return Response({'success':True, 'detail':'Este tipo de tramite ha sido eliminado exitosamente'}, status=status.HTTP_200_OK)
            else:
                raise PermissionDenied('No puedes eliminar un tipo de tramite precargado')
        else:
            raise NotFound('No existe el tipo de tramite')