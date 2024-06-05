import io
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
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from gestion_documental.serializers.expedientes_serializers import ArchivoSoporteSerializer, DocsIndiceElectronicoSerializer
from gestion_documental.models.expedientes_models import ArchivosDigitales, Docs_IndiceElectronicoExp, DocumentosDeArchivoExpediente, ExpedientesDocumentales, IndicesElectronicosExp
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
    serializer_permisos_class = OPASSerializer
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

        # DATOS INTERMEDIOS
        tipo_tramite = data_tramite.get('tipo_tramite')
        cod_municipio = data_tramite.get('cod_municipio')
        direccion = data_tramite.get('direccion')
        coordenada_x = data_tramite.get('coordenada_x')
        coordenada_y = data_tramite.get('coordenada_y')

        if tipo_tramite and cod_municipio and direccion:
            tipo_tramite_instance = PermisosAmbientales.objects.filter(nombre=tipo_tramite).first()
            municipio = Municipio.objects.filter(cod_municipio=cod_municipio).first()

            if tipo_tramite_instance:
                # Insertar en T280
                PermisosAmbSolicitudesTramite.objects.create(
                    id_permiso_ambiental = tipo_tramite_instance,
                    id_solicitud_tramite = tramite_creado,
                    coordenada_x = coordenada_x,
                    coordenada_y = coordenada_y,
                    cod_municipio = municipio,
                    direccion = direccion
                )
        
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
                fecha_creacion_doc = current_date,
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
            execution_time = datetime.now() + timedelta(minutes=2)
            scheduler.add_job(update_tramites_bia, args=[radicado_nuevo], trigger='date', run_date=execution_time)
        
        return Response({'success': True, 'detail':'Se realizó la creación del del trámite correctamente', 'data': serializer_tramite_data}, status=status.HTTP_201_CREATED)   

class GeneralTramitesUpdateView(generics.UpdateAPIView):
    serializer_class = GeneralTramitesGetSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, id_solicitud_tramite):
        data = request.data
        tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not tramite:
            raise NotFound('No se encontró el trámite ingresado')
        
        serializer = self.serializer_class(tramite, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({'success': True, 'detail':'Se realizó la actualización del del trámite correctamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)   

class ListTramitesGetView(generics.ListAPIView):
    serializer_class = ListTramitesGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, cod_tipo_permiso_ambiental):
        cod_tipo_permiso_ambiental_correctos = ['LA', 'DA', 'PA', 'PR', 'CE', 'EV', 'RE', 'PM', 'OP']
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
        tramites_opas = PermisosAmbSolicitudesTramite.objects.filter(id_solicitud_tramite__id_medio_solicitud=2, id_solicitud_tramite__id_persona_titular=id_persona_titular, id_permiso_ambiental__cod_tipo_permiso_ambiental = 'OP')

        serializer = self.serializer_class(tramites_opas, many=True)
        
        return Response({'success': True, 'detail':'Se encontró la siguiente información', 'data': serializer.data}, status=status.HTTP_200_OK)

class TramiteListGetViewPM(generics.ListAPIView):
    serializer_class = TramiteListGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_persona_titular):
        tramites_opas = PermisosAmbSolicitudesTramite.objects.filter(id_solicitud_tramite__id_medio_solicitud=2, id_solicitud_tramite__id_persona_titular=id_persona_titular, id_permiso_ambiental__cod_tipo_permiso_ambiental = 'PM')

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
                fecha_creacion_doc = current_date,
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

class AnexosUpdatePMView(generics.UpdateAPIView):
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
            raise NotFound('No se encontró el trámite del Permiso Menor elegido')
        
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
            ruta = os.path.join("home", "BIA", "Otros", "PermisoMenor", str(current_year))

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
                fecha_creacion_doc = current_date,
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
    
class AnexosGetPMView(generics.ListAPIView):
    serializer_class = AnexosGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_solicitud_tramite):
        solicitud_tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not solicitud_tramite:
            raise NotFound('No se encontró el trámite del Permiso Menor elegido')
        
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

class RadicarCreatePMView(generics.CreateAPIView):
    serializer_class = AnexosGetSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, id_solicitud_tramite):
        data = request.data
        current_date = datetime.now()
        
        solicitud = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not solicitud:
            raise NotFound('No se encontró el trámite del Permiso Menor elegido')
        
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
        subject = "PM radicado con éxito - "
        template = "envio-radicado-pm.html"
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

class RadicarGetPMView(generics.ListAPIView):
    serializer_class = RadicadoPostSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_solicitud_tramite):
        solicitud = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not solicitud:
            raise NotFound('No se encontró el trámite del Permiso Menor elegido')
        
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

class RadicarVolverEnviarGetPMView(generics.ListAPIView):
    serializer_class = RadicadoPostSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_solicitud_tramite):
        solicitud = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not solicitud:
            raise NotFound('No se encontró el trámite del Permiso Menor elegido')
        
        if not solicitud.id_radicado:
            raise ValidationError('El trámite aún no ha sido radicado')
        
        instance_config_tipo_radicado =ConfigTiposRadicadoAgno.objects.filter(agno_radicado=solicitud.id_radicado.agno_radicado,cod_tipo_radicado=solicitud.id_radicado.cod_tipo_radicado).first()
        numero_con_ceros = str(solicitud.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
        radicado_nuevo= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
        # ENVIAR CORREO CON RADICADO
        subject = "PM radicado con éxito - "
        template = "envio-radicado-pm.html"
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
            id_permiso_ambiental__cod_tipo_permiso_ambiental='OP'
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
            data['fecha_creacion_doc'] = current_date
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


class AnexosMetadatosUpdatePMView(generics.UpdateAPIView):
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
            raise NotFound('No se encontró el trámite del Permiso Menor elegido')
        
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
            data['fecha_creacion_doc'] = current_date
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
        
class GetTiposTramitesSasoftcoGetView(generics.ListAPIView):
    serializer_class = GetTiposTramitesSerializer
    queryset = PermisosAmbientales.objects.filter(id_permiso_ambiental__gte=15, id_permiso_ambiental__lte=40)
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipos_tramites = self.queryset.all()
        serializador = self.serializer_class(tipos_tramites, many=True)
        
        return Response({'success':True, 'detail':'Se encontró la siguiente información', 'data':serializador.data}, status=status.HTTP_200_OK)
    

class ArchiarSolicitudPQRSDF(generics.UpdateAPIView):
    serializer_class = ArchivoSoporteSerializer
    permission_classes = [IsAuthenticated]

    def post(self,request):
        data_in = request.data

        persona_logueada = request.user.persona
        current_date = datetime.now()

        solicitud_pqrsdf = SolicitudesTramites.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite']).first()
        
        
        print(solicitud_pqrsdf.id_expediente_doc)
        expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental = solicitud_pqrsdf.id_expediente_doc.id_expediente_documental).first()

        if not expediente:
            raise ValidationError('No se encontró un expediente para PQRSDF para el año actual y no se puede radicar la solicitud hasta que se cree uno')

        data_docarch = {
            "nombre_asignado_documento": f"Documento de soporte para la solicitud PQRSDF {solicitud_pqrsdf.id_PQRSDF}",
            "fecha_creacion_doc": current_date,
            "fecha_incorporacion_doc_a_Exp": current_date,
            "descripcion": solicitud_pqrsdf.descripcion,
            "asunto": solicitud_pqrsdf.asunto,
            "cod_categoria_archivo": "TX",
            "es_version_original": True,
            "tiene_replica_fisica": False,
            "nro_folios_del_doc": solicitud_pqrsdf.nro_folios_totales,
            "cod_origen_archivo": "E",
            "es_un_archivo_anexo": False,
            "anexo_corresp_a_lista_chequeo": False,
            "cantidad_anexos": solicitud_pqrsdf.cantidad_anexos,
            "palabras_clave_documento": f"Documento|Soporte|PQRSDF|{solicitud_pqrsdf.id_PQRSDF}",
            "sub_sistema_incorporacion": "GEST",
            "documento_requiere_rta": False,
            "creado_automaticamente": True,
            "id_und_org_oficina_creadora": persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional,
            "id_persona_que_crea": persona_logueada.id_persona,
            "id_und_org_oficina_respon_actual": persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional,
        }
        data_docarch['id_expediente_documental'] = expediente.id_expediente_documental

        
        orden_expediente = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=expediente.id_expediente_documental).order_by('orden_en_expediente').last()
        if orden_expediente != None:
            ultimo_orden = orden_expediente.orden_en_expediente
            data_docarch['orden_en_expediente'] = ultimo_orden + 1
        else:
            data_docarch['orden_en_expediente'] = 1

        if expediente.cod_tipo_expediente == "S":
            data_docarch['identificacion_doc_en_expediente'] = f"{expediente.codigo_exp_Agno}{expediente.cod_tipo_expediente}{str(data_docarch['orden_en_expediente']).zfill(10)}"
        else:
            cantidad_digitos = 10 - len(str(expediente.codigo_exp_consec_por_agno))
            data_docarch['identificacion_doc_en_expediente'] = f"{expediente.codigo_exp_Agno}{expediente.cod_tipo_expediente}{expediente.codigo_exp_consec_por_agno}{str(data_docarch['orden_en_expediente']).zfill(cantidad_digitos)}"
            print(len(data_docarch['identificacion_doc_en_expediente']))

        anexo = self.crear_pdf(solicitud_pqrsdf)
        ruta = os.path.join("home", "BIA", "Gestor", "GDEA", "PQRSDF", str(expediente.codigo_exp_Agno))

        md5_hash = hashlib.md5()
        for chunk in anexo.chunks():
            md5_hash.update(chunk)
        
        md5_value = md5_hash.hexdigest()

        data_archivo = {
            'es_Doc_elec_archivo': True,
            'ruta': ruta,
            'md5_hash': md5_value
        }
            
        archivo_class = ArchivosDgitalesCreate()
        respuesta = archivo_class.crear_archivo(data_archivo, anexo)

        data_docarch['id_archivo_sistema'] = respuesta.data.get('data').get('id_archivo_digital')

        serializer = self.serializer_class(data=data_docarch)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        data_indice = {
            "id_doc_archivo_exp": serializer.data['id_documento_de_archivo_exped'],
            "identificación_doc_exped": serializer.data['identificacion_doc_en_expediente'],
            "nombre_documento": serializer.data['nombre_asignado_documento'],
            "id_tipologia_documental": serializer.data['id_tipologia_documental'],
            "fecha_creacion_doc": serializer.data['fecha_creacion_doc'],
            "fecha_incorporacion_exp": serializer.data['fecha_incorporacion_doc_a_Exp'],
            "valor_huella": respuesta.data.get('data').get('nombre_de_Guardado'),
            "funcion_resumen": "MD5",
            "orden_doc_expediente": serializer.data['orden_en_expediente'],
            "formato": respuesta.data.get('data').get('formato'),
            "tamagno_kb": respuesta.data.get('data').get('tamagno_kb'),
            "cod_origen_archivo": serializer.data['cod_origen_archivo'],
            "es_un_archivo_anexo": serializer.data['es_un_archivo_anexo'],
            "id_expediente_documental": expediente.id_expediente_documental,
            "nro_folios_del_doc": solicitud_pqrsdf.nro_folios_totales,
        }

        doc_indice = self.crear_indice(data_indice)
        serializer.data['indice'] = doc_indice
        solicitud_pqrsdf.id_doc_dearch_exp = instance
        solicitud_pqrsdf.save()

        data_anexos = {
            "id_expediente_documental": expediente.id_expediente_documental,
            "fehca_registro": current_date,
        }

        #Archivar Anexos
        if solicitud_pqrsdf.cantidad_anexos > 0:
            anexos_archivado = self.archivar_anexos(solicitud_pqrsdf, None, None, data_anexos, instance, persona_logueada)

        #Archivar Solicitudes o Requerimientos con su respuesta
        requerimientos = self.archivar_requerimientos(solicitud_pqrsdf, expediente, current_date, persona_logueada)
        

        return Response({'success': True, 'detail': 'Se archivó el soporte correctamente', 'data': serializer.data}, status=status.HTTP_200_OK)

    
    def crear_pdf(self, data):
        pqrsdf = data

        nombre_titular = ""
        nombre_interpone = ""
        nombre_persona_recibe = f"{pqrsdf.id_persona_recibe.primer_nombre} {pqrsdf.id_persona_recibe.segundo_nombre} {pqrsdf.id_persona_recibe.primer_apellido} {pqrsdf.id_persona_recibe.segundo_apellido}" if pqrsdf.id_persona_recibe else ""
        radicado = f"{pqrsdf.id_radicado.prefijo_radicado}-{pqrsdf.id_radicado.agno_radicado}-{pqrsdf.id_radicado.nro_radicado}" if pqrsdf.id_radicado else ""
        numero_documento_interpone = pqrsdf.id_persona_interpone.numero_documento if pqrsdf.id_persona_interpone else ""
        recepcion_fisica = pqrsdf.id_sucursal_recepcion_fisica.id_persona_empresa.razon_social if pqrsdf.id_sucursal_recepcion_fisica else ""

        if pqrsdf.id_persona_titular.tipo_persona == 'N':
            nombre_titular = f"{pqrsdf.id_persona_titular.primer_nombre} {pqrsdf.id_persona_titular.segundo_nombre} {pqrsdf.id_persona_titular.primer_apellido} {pqrsdf.id_persona_titular.segundo_apellido}"
        else:
            nombre_titular = f"{pqrsdf.id_persona_titular.razon_social}"

        if pqrsdf.id_persona_interpone:
            if pqrsdf.id_persona_interpone.tipo_persona == 'N':
                nombre_interpone = f"{pqrsdf.id_persona_interpone.primer_nombre} {pqrsdf.id_persona_interpone.segundo_nombre} {pqrsdf.id_persona_interpone.primer_apellido} {pqrsdf.id_persona_interpone.segundo_apellido}" if pqrsdf.id_persona_interpone else ""
            else:
                nombre_interpone = f"{pqrsdf.id_persona_interpone.razon_social}" if pqrsdf.id_persona_interpone else ""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)


        c.drawString(200, 820, "INFORMACIÓN DE LA SOLICITUD PQRSDF")

        c.rect(20, 720, 550, 80)
        c.drawString(30, 770, f"Nombre Titular: {nombre_titular}")
        c.drawString(30, 740, f"Número de Documento: {pqrsdf.id_persona_titular.numero_documento}")

        c.rect(20, 595, 550, 100)
        c.drawString(30, 670, f"Nombre Interpone: {nombre_interpone}")
        c.drawString(30, 640, f"Número de Documento: {numero_documento_interpone}")
        c.drawString(30, 610, f"Relación Con el Titular: {pqrsdf.cod_relacion_con_el_titular}")

        c.rect(20, 230, 550, 340)
        c.drawString(30, 550, f"Fecha de Solicitud: {pqrsdf.fecha_registro}")
        c.drawString(30, 520, f"Medio de Solicitud: {pqrsdf.id_medio_solicitud.nombre}")
        c.drawString(30, 490, f"Forma de Presentación: {pqrsdf.cod_forma_presentacion}")
        c.drawString(30, 460, f"Asunto: {pqrsdf.asunto}")
        c.drawString(30, 430, f"Descripción: {pqrsdf.descripcion}")
        c.drawString(30, 400, f"Cantidad de Anexos: {pqrsdf.cantidad_anexos}")
        c.drawString(30, 370, f"Número de Folios{pqrsdf.nro_folios_totales}")
        c.drawString(30, 340, f"Nombre Recibe: {nombre_persona_recibe}")
        c.drawString(30, 310, f"Sucursal: {recepcion_fisica}")
        c.drawString(30, 280, f"Número de Radicado: {radicado}")
        c.drawString(30, 250, f"Fecha de Radicado: {pqrsdf.fecha_radicado}")


        c.showPage()
        c.save()

        buffer.seek(0)

        # Ahora puedes usar 'buffer' como una variable que contiene tu PDF.
        # Por ejemplo, puedes guardarlo en una variable así:
        pdf_en_variable = buffer.getvalue()
        pdf_content_file = ContentFile(pdf_en_variable,name="PQRSDF.pdf")

        # Recuerda cerrar el buffer cuando hayas terminado
        buffer.close()

        return pdf_content_file
    
    def crear_indice(self, data_indice):
        serializer_class = DocsIndiceElectronicoSerializer

        indice = IndicesElectronicosExp.objects.filter(id_expediente_doc=data_indice['id_expediente_documental']).first()
        if indice.abierto:
            docs_indice = Docs_IndiceElectronicoExp.objects.filter(id_indice_electronico_exp=indice.id_indice_electronico_exp).order_by('orden_doc_expediente').last()
            print(docs_indice)
            pagina_inicio = docs_indice.pagina_fin + 1 if docs_indice != None else 1
            pagina_fin = pagina_inicio + data_indice['nro_folios_del_doc']

            data_indice["id_indice_electronico_exp"]= indice.id_indice_electronico_exp
            data_indice["pagina_inicio"] = pagina_inicio
            data_indice["pagina_fin"] = pagina_fin

            serializer = serializer_class(data=data_indice)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()

            return serializer.data
        else:
            raise ValidationError("El índice del expediente está cerrado")

    def archivar_anexos(self, solicitud_pqrsdf, solicitud_usuario, respuesta_solicitud, data_in, id_doc_de_arch_del_cual_es_anexo, persona_logueada):
        if solicitud_pqrsdf:
            anexos_pqrsdf = Anexos_PQR.objects.filter(id_PQRSDF=solicitud_pqrsdf.id_PQRSDF)
        elif solicitud_usuario:
            anexos_pqrsdf = Anexos_PQR.objects.filter(id_solicitud_usu_sobre_PQR=solicitud_usuario.id_solicitud_al_usuario_sobre_pqrsdf)
        elif respuesta_solicitud:
            anexos_pqrsdf = Anexos_PQR.objects.filter(id_complemento_usu_PQR=respuesta_solicitud.idComplementoUsu_PQR)

        
        expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=data_in['id_expediente_documental']).first()

        for anexo in anexos_pqrsdf:
            info_anexo = Anexos.objects.filter(id_anexo=anexo.id_anexo.id_anexo).first()
            info_metadatos = MetadatosAnexosTmp.objects.filter(id_anexo=anexo.id_anexo.id_anexo).first()

            archivo_digital = ArchivosDigitales.objects.filter(id_archivo_digital=info_metadatos.id_archivo_sistema.id_archivo_digital).first()
            data_docarch = {
                "nombre_asignado_documento": info_metadatos.nombre_original_archivo,
                "fecha_creacion_doc": info_metadatos.fecha_creacion_doc,
                "fecha_incorporacion_doc_a_Exp": data_in['fehca_registro'],
                "descripcion": info_metadatos.descripcion,
                "asunto": info_metadatos.asunto,
                "cod_categoria_archivo": info_metadatos.cod_categoria_archivo if info_metadatos.cod_categoria_archivo else "TX",
                "es_version_original": info_metadatos.es_version_original if info_metadatos.es_version_original else False,
                "tiene_replica_fisica": info_metadatos.tiene_replica_fisica if info_metadatos.tiene_replica_fisica else False,
                "nro_folios_del_doc": info_metadatos.nro_folios_documento if info_metadatos.nro_folios_documento else 0,
                "cod_origen_archivo": info_metadatos.cod_origen_archivo if info_metadatos.cod_origen_archivo else "E",
                "id_tipologia_documental": info_metadatos.id_tipologia_doc.id_tipologia_documental if info_metadatos.id_tipologia_doc else None,
                "codigo_tipologia_doc_prefijo": info_metadatos.cod_tipologia_doc_Prefijo if info_metadatos.cod_tipologia_doc_Prefijo else None,
                "codigo_tipologia_doc_agno": info_metadatos.cod_tipologia_doc_agno if info_metadatos.cod_tipologia_doc_agno else None,
                "codigo_tipologia_doc_consecutivo": info_metadatos.cod_tipologia_doc_Consecutivo if info_metadatos.cod_tipologia_doc_Consecutivo else None,
                "es_un_archivo_anexo": True,
                "anexo_corresp_a_lista_chequeo": False,
                "id_doc_de_arch_del_cual_es_anexo": id_doc_de_arch_del_cual_es_anexo.id_documento_de_archivo_exped,
                "id_archivo_sistema": archivo_digital.id_archivo_digital,
                "palabras_clave_documento": info_metadatos.palabras_clave_doc,
                "sub_sistema_incorporacion": "GEST",
                "documento_requiere_rta": False,
                "creado_automaticamente": True,
                "id_und_org_oficina_creadora": persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional,
                "id_persona_que_crea": persona_logueada.id_persona,
                "id_und_org_oficina_respon_actual": persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional,
            }
            data_docarch['id_expediente_documental'] = data_in['id_expediente_documental']

        
            orden_expediente = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=data_in['id_expediente_documental']).order_by('orden_en_expediente').last()
            if orden_expediente != None:
                ultimo_orden = orden_expediente.orden_en_expediente
                data_docarch['orden_en_expediente'] = ultimo_orden + 1
            else:
                data_docarch['orden_en_expediente'] = 1

            if expediente.cod_tipo_expediente == "S":
                data_docarch['identificacion_doc_en_expediente'] = f"{expediente.codigo_exp_Agno}{expediente.cod_tipo_expediente}{str(data_docarch['orden_en_expediente']).zfill(10)}"
            else:
                cantidad_digitos = 10 - len(str(expediente.codigo_exp_consec_por_agno))
                data_docarch['identificacion_doc_en_expediente'] = f"{expediente.codigo_exp_Agno}{expediente.cod_tipo_expediente}{expediente.codigo_exp_consec_por_agno}{str(data_docarch['orden_en_expediente']).zfill(cantidad_digitos)}"

        
            serializer = self.serializer_class(data=data_docarch)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            
            data_indice = {
                "id_doc_archivo_exp": serializer.data['id_documento_de_archivo_exped'],
                "identificación_doc_exped": serializer.data['identificacion_doc_en_expediente'],
                "nombre_documento": serializer.data['nombre_asignado_documento'],
                "id_tipologia_documental": serializer.data['id_tipologia_documental'],
                "fecha_creacion_doc": serializer.data['fecha_creacion_doc'],
                "fecha_incorporacion_exp": serializer.data['fecha_incorporacion_doc_a_Exp'],
                "valor_huella": archivo_digital.nombre_de_Guardado,
                "funcion_resumen": "MD5",
                "orden_doc_expediente": serializer.data['orden_en_expediente'],
                "formato": archivo_digital.formato,
                "tamagno_kb": archivo_digital.tamagno_kb,
                "cod_origen_archivo": serializer.data['cod_origen_archivo'],
                "es_un_archivo_anexo": serializer.data['es_un_archivo_anexo'],
                "id_expediente_documental": data_in['id_expediente_documental'],
                "nro_folios_del_doc": info_metadatos.nro_folios_documento,
            }

            doc_indice = self.crear_indice(data_indice)
            info_anexo.id_docu_arch_exp = instance
            info_anexo.save()

            info_metadatos.delete()


    def archivar_requerimientos(self, data, expediente, current_date, persona_logueada):
        solicitudes = SolicitudAlUsuarioSobrePQRSDF.objects.filter(id_pqrsdf=data.id_PQRSDF)

        for solicitud in solicitudes:
            nombre_solicita = ""
            radicado = f"{solicitud.id_radicado_salida.prefijo_radicado}-{solicitud.id_radicado_salida.agno_radicado}-{solicitud.id_radicado_salida.nro_radicado}" if solicitud.id_radicado_salida else ""

            if solicitud.id_persona_solicita:
                if solicitud.id_persona_solicita.tipo_persona == 'N':
                    nombre_solicita = f"{solicitud.id_persona_solicita.primer_nombre} {solicitud.id_persona_solicita.segundo_nombre} {solicitud.id_persona_solicita.primer_apellido} {solicitud.id_persona_solicita.segundo_apellido}" if solicitud.id_persona_solicita else ""
                else:
                    nombre_solicita = f"{solicitud.id_persona_solicita.razon_social}" if solicitud.id_persona_solicita else ""
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer)


            c.drawString(120, 820, "INFORMACIÓN DE LA SOLICITUD O REQUERIMIENTO AL USUARIO")

            c.rect(20, 700, 550, 100)
            c.drawString(30, 770, f"Nombre Solicita: {nombre_solicita}")
            c.drawString(30, 740, f"Número de Documento: {solicitud.id_persona_solicita.numero_documento}")
            c.drawString(30, 710, f"Unidad Orgsanizacional: {solicitud.id_und_org_oficina_solicita.nombre}")

            c.rect(20, 345, 550, 340)
            c.drawString(30, 670, f"Fecha de Solicitud: {solicitud.fecha_solicitud}")
            c.drawString(30, 640, f"Asunto: {solicitud.asunto}")
            c.drawString(30, 610, f"Descripción: {solicitud.descripcion}")
            c.drawString(30, 580, f"Cantidad de Anexos: {solicitud.cantidad_anexos}")
            c.drawString(30, 550, f"Número de Folios{solicitud.nro_folios_totales}")
            c.drawString(30, 520, f"Número de Radicado: {radicado}")
            c.drawString(30, 490, f"Fecha de Radicado: {solicitud.fecha_radicado_salida}")


            c.showPage()
            c.save()

            buffer.seek(0)

            # Ahora puedes usar 'buffer' como una variable que contiene tu PDF.
            # Por ejemplo, puedes guardarlo en una variable así:
            pdf_en_variable = buffer.getvalue()
            pdf_content_file = ContentFile(pdf_en_variable,name="solicitud.pdf")

            # Recuerda cerrar el buffer cuando hayas terminado
            buffer.close()

            #Crear el documento de archivo en el expediente
            data_docarch = {
                "nombre_asignado_documento": f"Documento de soporte para la solicitud PQRSDF {solicitud.id_solicitud_al_usuario_sobre_pqrsdf}",
                "fecha_creacion_doc": current_date,
                "fecha_incorporacion_doc_a_Exp": current_date,
                "descripcion": solicitud.descripcion,
                "asunto": solicitud.asunto,
                "cod_categoria_archivo": "TX",
                "es_version_original": True,
                "tiene_replica_fisica": False,
                "nro_folios_del_doc": solicitud.nro_folios_totales,
                "cod_origen_archivo": "E",
                "es_un_archivo_anexo": False,
                "anexo_corresp_a_lista_chequeo": False,
                "cantidad_anexos": solicitud.cantidad_anexos,
                "palabras_clave_documento": f"requerimientos|solicitudes|PQRSDF|{solicitud.id_solicitud_al_usuario_sobre_pqrsdf}",
                "sub_sistema_incorporacion": "GEST",
                "documento_requiere_rta": False,
                "creado_automaticamente": True,
                "id_und_org_oficina_creadora": persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional,
                "id_persona_que_crea": persona_logueada.id_persona,
                "id_und_org_oficina_respon_actual": persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional,
            }
            data_docarch['id_expediente_documental'] = expediente.id_expediente_documental

            
            orden_expediente = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=expediente.id_expediente_documental).order_by('orden_en_expediente').last()
            if orden_expediente != None:
                ultimo_orden = orden_expediente.orden_en_expediente
                data_docarch['orden_en_expediente'] = ultimo_orden + 1
            else:
                data_docarch['orden_en_expediente'] = 1

            if expediente.cod_tipo_expediente == "S":
                data_docarch['identificacion_doc_en_expediente'] = f"{expediente.codigo_exp_Agno}{expediente.cod_tipo_expediente}{str(data_docarch['orden_en_expediente']).zfill(10)}"
            else:
                cantidad_digitos = 10 - len(str(expediente.codigo_exp_consec_por_agno))
                data_docarch['identificacion_doc_en_expediente'] = f"{expediente.codigo_exp_Agno}{expediente.cod_tipo_expediente}{expediente.codigo_exp_consec_por_agno}{str(data_docarch['orden_en_expediente']).zfill(cantidad_digitos)}"
                print(len(data_docarch['identificacion_doc_en_expediente']))

            respuesta = self.guardar_archivo(expediente, pdf_content_file)

            data_docarch['id_archivo_sistema'] = respuesta.data.get('data').get('id_archivo_digital')

            serializer = self.serializer_class(data=data_docarch)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()

            #Crear el índice electrónico
            data_indice = {
                "id_doc_archivo_exp": serializer.data['id_documento_de_archivo_exped'],
                "identificación_doc_exped": serializer.data['identificacion_doc_en_expediente'],
                "nombre_documento": serializer.data['nombre_asignado_documento'],
                "id_tipologia_documental": serializer.data['id_tipologia_documental'],
                "fecha_creacion_doc": serializer.data['fecha_creacion_doc'],
                "fecha_incorporacion_exp": serializer.data['fecha_incorporacion_doc_a_Exp'],
                "valor_huella": respuesta.data.get('data').get('nombre_de_Guardado'),
                "funcion_resumen": "MD5",
                "orden_doc_expediente": serializer.data['orden_en_expediente'],
                "formato": respuesta.data.get('data').get('formato'),
                "tamagno_kb": respuesta.data.get('data').get('tamagno_kb'),
                "cod_origen_archivo": serializer.data['cod_origen_archivo'],
                "es_un_archivo_anexo": serializer.data['es_un_archivo_anexo'],
                "id_expediente_documental": expediente.id_expediente_documental,
                "nro_folios_del_doc": solicitud.nro_folios_totales,
            }

            doc_indice = self.crear_indice(data_indice)
            solicitud.id_doc_de_archivo_exp = instance
            solicitud.save()

            data_anexos = {
                "id_expediente_documental": expediente.id_expediente_documental,
                "fehca_registro": current_date,
            }

            #Archivar Anexos
            if solicitud.cantidad_anexos > 0:
                anexos_archivado = self.archivar_anexos(None, solicitud, None, data_anexos, instance, persona_logueada)

            respuesta = ComplementosUsu_PQR.objects.filter(id_solicitud_usu_PQR=solicitud.id_solicitud_al_usuario_sobre_pqrsdf).first()

            if respuesta:
                buffer = io.BytesIO()
                c = canvas.Canvas(buffer)
                radicado_respuesta = f"{respuesta.id_radicado.prefijo_radicado}-{respuesta.id_radicado.agno_radicado}-{respuesta.id_radicado.nro_radicado}" if respuesta.id_radicado else ""


                c.drawString(120, 820, "INFORMACIÓN DE LA RESPUESTA A LA SOLICITUD O REQUERIMIENTO AL USUARIO")

                c.rect(20, 700, 550, 100)
                c.drawString(30, 770, f"Nombre Responde: {respuesta.id_persona_interpone.primer_nombre} {respuesta.id_persona_interpone.segundo_nombre} {respuesta.id_persona_interpone.primer_apellido} {respuesta.id_persona_interpone.segundo_apellido}")
                c.drawString(30, 740, f"Número de Documento: {respuesta.id_persona_interpone.numero_documento}")
                c.drawString(30, 710, f"Unidad Organizacional: {respuesta.cod_relacion_titular}")

                c.rect(20, 345, 550, 340)
                c.drawString(30, 670, f"Fecha de Respuesta: {respuesta.fecha_complemento}")
                c.drawString(30, 640, f"Asunto: {respuesta.asunto}")
                c.drawString(30, 610, f"Descripción: {respuesta.descripcion}")
                c.drawString(30, 580, f"Cantidad de Anexos: {respuesta.cantidad_anexos}")
                c.drawString(30, 550, f"Número de Folios{respuesta.nro_folios_totales}")
                c.drawString(30, 520, f"Número de Radicado: {radicado_respuesta}")
                c.drawString(30, 490, f"Fecha de Radicado: {respuesta.fecha_radicado}")

                c.drawString(120, 820, "INFORMACIÓN DE LA SOLICITUD O REQUERIMIENTO AL USUARIO")


                c.showPage()
                c.save()

                buffer.seek(0)

                # Ahora puedes usar 'buffer' como una variable que contiene tu PDF.
                # Por ejemplo, puedes guardarlo en una variable así:
                pdf_en_variable = buffer.getvalue()
                pdf_content_file_respuesta = ContentFile(pdf_en_variable,name="respuesta.pdf")

                # Recuerda cerrar el buffer cuando hayas terminado
                buffer.close()

                data_docarch_respuesta = {
                    "nombre_asignado_documento": f"Documento de soporte para la solicitud PQRSDF {respuesta.idComplementoUsu_PQR}",
                    "fecha_creacion_doc": current_date,
                    "fecha_incorporacion_doc_a_Exp": current_date,
                    "descripcion": respuesta.descripcion,
                    "asunto": respuesta.asunto,
                    "cod_categoria_archivo": "TX",
                    "es_version_original": True,
                    "tiene_replica_fisica": False,
                    "nro_folios_del_doc": respuesta.nro_folios_totales,
                    "cod_origen_archivo": "E",
                    "es_un_archivo_anexo": False,
                    "anexo_corresp_a_lista_chequeo": False,
                    "cantidad_anexos": respuesta.cantidad_anexos,
                    "palabras_clave_documento": f"Documento|Soporte|PQRSDF|{respuesta.idComplementoUsu_PQR}",
                    "sub_sistema_incorporacion": "GEST",
                    "documento_requiere_rta": False,
                    "creado_automaticamente": True,
                    "id_und_org_oficina_creadora": persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional,
                    "id_persona_que_crea": persona_logueada.id_persona,
                    "id_und_org_oficina_respon_actual": persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional,
                }
                data_docarch_respuesta['id_expediente_documental'] = expediente.id_expediente_documental

                
                orden_expediente = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=expediente.id_expediente_documental).order_by('orden_en_expediente').last()
                if orden_expediente != None:
                    ultimo_orden = orden_expediente.orden_en_expediente
                    data_docarch_respuesta['orden_en_expediente'] = ultimo_orden + 1
                else:
                    data_docarch_respuesta['orden_en_expediente'] = 1

                if expediente.cod_tipo_expediente == "S":
                    data_docarch_respuesta['identificacion_doc_en_expediente'] = f"{expediente.codigo_exp_Agno}{expediente.cod_tipo_expediente}{str(data_docarch_respuesta['orden_en_expediente']).zfill(10)}"
                else:
                    cantidad_digitos = 10 - len(str(expediente.codigo_exp_consec_por_agno))
                    data_docarch_respuesta['identificacion_doc_en_expediente'] = f"{expediente.codigo_exp_Agno}{expediente.cod_tipo_expediente}{expediente.codigo_exp_consec_por_agno}{str(data_docarch_respuesta['orden_en_expediente']).zfill(cantidad_digitos)}"
                    print(len(data_docarch_respuesta['identificacion_doc_en_expediente']))

                respuesta_archivo = self.guardar_archivo(expediente, pdf_content_file_respuesta)

                data_docarch_respuesta['id_archivo_sistema'] = respuesta_archivo.data.get('data').get('id_archivo_digital')

                serializer = self.serializer_class(data=data_docarch_respuesta)
                serializer.is_valid(raise_exception=True)
                instance_respuesta = serializer.save()

                 #Crear el índice electrónico
                data_indice_respuesta = {
                    "id_doc_archivo_exp": serializer.data['id_documento_de_archivo_exped'],
                    "identificación_doc_exped": serializer.data['identificacion_doc_en_expediente'],
                    "nombre_documento": serializer.data['nombre_asignado_documento'],
                    "id_tipologia_documental": serializer.data['id_tipologia_documental'],
                    "fecha_creacion_doc": serializer.data['fecha_creacion_doc'],
                    "fecha_incorporacion_exp": serializer.data['fecha_incorporacion_doc_a_Exp'],
                    "valor_huella": respuesta_archivo.data.get('data').get('nombre_de_Guardado'),
                    "funcion_resumen": "MD5",
                    "orden_doc_expediente": serializer.data['orden_en_expediente'],
                    "formato": respuesta_archivo.data.get('data').get('formato'),
                    "tamagno_kb": respuesta_archivo.data.get('data').get('tamagno_kb'),
                    "cod_origen_archivo": serializer.data['cod_origen_archivo'],
                    "es_un_archivo_anexo": serializer.data['es_un_archivo_anexo'],
                    "id_expediente_documental": expediente.id_expediente_documental,
                    "nro_folios_del_doc": respuesta.nro_folios_totales,
                }

                doc_indice = self.crear_indice(data_indice_respuesta)
                respuesta.id_doc_arch_exp = instance_respuesta
                respuesta.save()

                data_anexos_respuesta = {
                    "id_expediente_documental": expediente.id_expediente_documental,
                    "fehca_registro": current_date,
                }

                #Archivar Anexos
                if respuesta.cantidad_anexos > 0:
                    anexos_archivado = self.archivar_anexos(respuesta, data_anexos_respuesta, instance_respuesta, persona_logueada)

    
    def guardar_archivo(self, expediente, anexo):

        ruta = os.path.join("home", "BIA", "Gestor", "GDEA", "PQRSDF", str(expediente.codigo_exp_Agno))

        md5_hash = hashlib.md5()
        for chunk in anexo.chunks():
            md5_hash.update(chunk)
        
        md5_value = md5_hash.hexdigest()

        data_archivo = {
            'es_Doc_elec_archivo': True,
            'ruta': ruta,
            'md5_hash': md5_value
        }
            
        archivo_class = ArchivosDgitalesCreate()
        respuesta = archivo_class.crear_archivo(data_archivo, anexo)

        return respuesta