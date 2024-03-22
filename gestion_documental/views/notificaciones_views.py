from rest_framework.views import APIView
from rest_framework.response import Response
import os
import json
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from gestion_documental.models.radicados_models import T262Radicados
from django.utils import timezone

from tramites.models.tramites_models import SolicitudesTramites
from gestion_documental.serializers.pqr_serializers import AnexosPostSerializer, MetadatosPostSerializer
from gestion_documental.views.pqr_views import Util_PQR
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.models.trd_models import FormatosTiposMedio

from transversal.models.base_models import HistoricoCargosUndOrgPersona, ClasesTercero, Personas

from gestion_documental.models.notificaciones_models import (
    NotificacionesCorrespondencia, 
    Registros_NotificacionesCorrespondecia, 
    AsignacionNotificacionCorrespondencia, 
    TiposNotificacionesCorrespondencia, 
    TiposAnexosSoporte, 
    Anexos_NotificacionesCorrespondencia, 
    EstadosNotificacionesCorrespondencia, 
    HistoricosEstados, 
    CausasOAnomalias,
    TiposDocumentos
    )

from gestion_documental.serializers.notificaciones_serializers import (
    NotificacionesCorrespondenciaSerializer,
    AsignacionNotificacionCorrespondenciaSerializer,
    AsignacionNotiCorresCreateSerializer,
    NotificacionesCorrespondenciaCreateSerializer,
    AnexosNotificacionPostSerializer,
    TiposNotificacionesCorrespondenciaSerializer,
    EstadosNotificacionesCorrespondenciaSerializer,
    CausasOAnomaliasNotificacionesCorrespondenciaSerializer,
    TiposAnexosNotificacionesCorrespondenciaSerializer,
    Registros_NotificacionesCorrespondeciaCreateSerializer,
    TiposDocumentosNotificacionesCorrespondenciaSerializer,
    AsignacionNotiCorresGetSerializer
    )

class ListaNotificacionesCorrespondencia(generics.ListAPIView):
    serializer_class = NotificacionesCorrespondenciaSerializer

    def get_queryset(self):
        queryset = NotificacionesCorrespondencia.objects.all()  # Obtiene las notificaciones de correspondencia
        permission_classes = [IsAuthenticated]
        id_radicado = ''

        # Obtener parámetros de consulta
        tipo_documento = self.request.query_params.get('tipo_documento')
        radicado = self.request.query_params.get('radicado')
        expediente = self.request.query_params.get('expediente')
        grupo_solicitante = self.request.query_params.get('grupo_solicitante')
        estado = self.request.query_params.get('estado')

        # Filtrar por tipo de documento si es válido
        if tipo_documento:
            tipo_documento_valido = ['OF', 'AC', 'AA', 'AI', 'OT']
            if tipo_documento in tipo_documento_valido:
                queryset = queryset.filter(cod_tipo_documento=tipo_documento)
            else:
                raise ValidationError(f'El tipo de documento {tipo_documento} no es válido.')
        

        if grupo_solicitante:
            queryset = queryset.filter(id_und_org_oficina_solicita=grupo_solicitante)

        if estado:
            estado_valido = ['RE', 'DE', 'EG', 'PE', 'NT']
            if estado in estado_valido:
                queryset = queryset.filter(cod_estado=estado)
            else:
                raise ValidationError(f'El estado {estado} no es válido.')

        return queryset, id_radicado

    def get(self, request, *args, **kwargs):
        queryset, radicado = self.get_queryset()
        print(queryset)
        serializer = self.get_serializer(queryset, many=True)
        data_validada =[]
        data_validada = serializer.data
        if radicado != '':
            data_validada = [item for item in serializer.data if radicado in item.get('radicado', '')]
        else :
            data_validada = serializer.data
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_validada,}, status=status.HTTP_200_OK)    
    

class CrearTareasAsignacion(generics.CreateAPIView):
    serializer_class = Registros_NotificacionesCorrespondeciaCreateSerializer

    def post(self, request, fecha_actual):
        data = NotificacionesCorrespondencia.objects.filter(id_notificacion_correspondencia=request.get('id_notificacion')).first()

        notificacion_data = {
            'id_notificacion_correspondencia': request.get('id_notificacion'),
            'fecha_registro': fecha_actual,
            'id_tipo_notificacion_correspondencia': request.get('id_tipo_notificacion_correspondencia'),
            'id_persona_titular': data.id_persona_titular.id_persona,
            'id_persona_interpone': data.id_persona_interpone.id_persona,
            'cod_relacion_con_titular': data.cod_relacion_con_titular,
            'cod_tipo_documentoID': data.cod_tipo_documentoID.cod_tipo_documento,
            'numero_identificacion': data.nro_documentoID,
            'persona_a_quien_se_dirige': data.persona_a_quien_se_dirige,
            'dir_notificacion_nal': data.dir_notificacion_nal,
            'cod_municipio_notificacion_nal': data.cod_municipio_notificacion_nal.cod_municipio,
            'tel_fijo': data.tel_fijo,
            'tel_celular': data.tel_celular,
            'email_notificacion': data.email_notificacion,
            'asunto': data.asunto,
            'descripcion': data.descripcion,
            'cantidad_anexos': data.cantidad_anexos,
            'nro_folios_totales': data.nro_folios_totales,
            'requiere_digitalizacion': data.requiere_digitalizacion,
            'fecha_inicial_registro': fecha_actual,
            'fecha_eleccion_estado': fecha_actual
        }

        serializer = self.serializer_class(data=notificacion_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return instance
    
class UpdateTareasAsignacion(generics.UpdateAPIView):
    serializer_class = Registros_NotificacionesCorrespondeciaCreateSerializer

    def put(self, data_asignacion, pk):
        data = data_asignacion
        registro_tarea = Registros_NotificacionesCorrespondecia.objects.filter(id_registro_notificacion_correspondencia=pk).first()

        serializer = self.serializer_class(registro_tarea, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return instance
    
class AsignacionesCorrespondenciaGet(generics.ListAPIView):
    serializer_class = AsignacionNotiCorresGetSerializer

    def get(self, idAsignacion_noti_corre):
        queryset = AsignacionNotificacionCorrespondencia.objects.all() 
        queryset = queryset.filter(idAsignacion_noti_corr=idAsignacion_noti_corre)
        
        serializer = self.get_serializer(queryset)
        return serializer.data

    # def get(self, request, *args, **kwargs):
    #     queryset = self.get_queryset(request)
    #     serializer = self.get_serializer(queryset)
    #     return serializer.data

class CrearAsignacionNotificacion(generics.CreateAPIView):
    serializer_class = AsignacionNotiCorresCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        fecha_actual = timezone.now()
        id_persona_asigna = request.user.persona

        if not data.get('id_persona_asignada'):
            raise ValidationError({'id_persona_asignada': 'La persona asignada es obligatorio'})
        
        registro = CrearTareasAsignacion()
        data_tarea = {
            'id_notificacion': data.get('id_notificacion_correspondencia'),
            'id_tipo_notificacion_correspondencia': data.get('id_tipo_notificacion_correspondencia'),
        }
        tarea = registro.post(data_tarea, fecha_actual)
        asignacion_data = {
            'id_notificacion_correspondencia': data.get('id_notificacion_correspondencia'),
            'id_orden_notificacion': tarea.id_registro_notificacion_correspondencia,
            'fecha_asignacion': fecha_actual,
            'id_persona_asigna': id_persona_asigna.id_persona,
            'id_persona_asignada': data.get('id_persona_asignada'),
            'cod_estado_asignacion': 'Pe',
            'fecha_eleccion_estado': fecha_actual,
            'id_und_org_seccion_asignada': id_persona_asigna.id_unidad_organizacional_actual.id_unidad_organizacional, 
        }

        serializer = self.serializer_class(data=asignacion_data) 
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if instance:
            data_asignacion = {
                'fecha_asignacion': fecha_actual,
                'id_persona_asigna': id_persona_asigna.id_persona,
                'id_persona_asignada': data.get('id_persona_asignada'),
                'cod_estado_asignacion': 'Pe',
            }
            tarea_actualizada = UpdateTareasAsignacion()
            if not tarea_actualizada.put(data_asignacion, tarea.id_registro_notificacion_correspondencia):
                raise ValidationError({'id_notificacion_correspondencia': 'No se pudo actualizar el estado de la tarea'})
        #response = AsignacionesCorrespondenciaGet()
        return Response({'succes': True, 'detail':'Se la asigncación correctamente', 'data':{**serializer.data}}, status=status.HTTP_201_CREATED)
    

class GetAsignacionesCorrespondencia(generics.ListAPIView):
    serializer_class = AsignacionNotificacionCorrespondenciaSerializer

    def get_queryset(self):
        queryset = AsignacionNotificacionCorrespondencia.objects.all()  # Obtiene las notificaciones de correspondencia # Obtiene las notificaciones de correspondencia
        permission_classes = [IsAuthenticated]

        id_persona_asignada = self.request.query_params.get('id_persona_asignada')
        if id_persona_asignada:
            queryset = queryset.filter(id_persona_asignada=id_persona_asignada)
        else:
            raise ValidationError(f'La persona {id_persona_asignada} no es valida.')

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        persona_asignada = ''
        vigencia_contrato = ''
        id_persona_asignada = 0
        pendientes = 0
        resueltas = 0
        asignadas = 0
        for item in serializer.data:
            #print(item)
            persona_asignada = item.get('persona_asignada')
            vigencia_contrato = item.get('vigencia_contrato')
            id_persona_asignada = item.get('id_persona_asignada')
            asignadas = asignadas+1
            notificacion_correspondencia = NotificacionesCorrespondencia.objects.filter(id_notificacion_correspondencia = item.get('id_notificacion_correspondencia')).first()
            if notificacion_correspondencia.cod_estado == 'PE':
                pendientes = pendientes+1
            if notificacion_correspondencia.cod_estado == 'RE':
                resueltas = resueltas+1
        data_valida = {"Persona Asignada": persona_asignada, "ID Persona Asignada": id_persona_asignada, "Vigencia del Contrato": vigencia_contrato, "Asignadas": asignadas, "resueltas": resueltas, "pendientes": pendientes, "asignaciones": serializer.data}
        return Response({'succes': True, 'detail':'Tiene las siguientes asignaciones', 'data':data_valida,}, status=status.HTTP_200_OK) 
  
    
class CrearNotiicacionManual(generics.CreateAPIView):
    serializer_class = NotificacionesCorrespondenciaCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data_total = request.data
        data = json.loads(data_total.get('data'))
        id_persona_recibe_solicitud = request.user.persona
        fecha_actual = timezone.now()

        tipo_documento = data.get('tipo_documento')
        if not tipo_documento:
            raise ValidationError({'tipo_documento': 'El tipo de documento es obligatorio'})
        
        asunto = data.get('asunto')
        if not asunto:
            raise ValidationError({'asunto': 'El asunto es obligatorio'})

        notificacion_data = {
            'cod_tipo_solicitud': 'NO',
            'cod_tipo_documento': tipo_documento,
            'id_expediente_documental': data.get('id_expediente_documental'),
            'id_solicitud_tramite': data.get('id_solicitud_tramite'),
            'id_acto_administrativo': data.get('id_acto_administrativo'),
            'procede_recurso_reposicion': data.get('procede_recurso_reposicion'),
            'es_anonima': data.get('es_anonima'),
            'asunto': asunto,
            'descripcion': data.get('descripcion'),
            'cod_medio_solicitud': 'MA',
            'fecha_solicitud': fecha_actual,
            'id_persona_solicita': data.get('id_persona_solicita'),
            'id_und_org_oficina_solicita': data.get('id_und_org_oficina_solicita'), 
            'allega_copia_fisica': data.get('allega_copia_fisica'),
            'cantidad_anexos': data.get('cantidad_anexos'),
            'nro_folios_totales': data.get('nro_folios_totales'),
            'id_persona_recibe_solicitud_manual': id_persona_recibe_solicitud.id_persona,
            'requiere_digitalizacion': data.get('requiere_digitalizacion'),
            'cod_estado': 'RE',
        }
        
        
        id_solicitud_tramite = data.get('id_solicitud_tramite')
        if id_solicitud_tramite:
            solicitud_tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
            notificacion_data['id_persona_titular'] = solicitud_tramite.id_persona_titular.id_persona
            notificacion_data['id_persona_interpone'] = solicitud_tramite.id_persona_interpone.id_persona
            notificacion_data['cod_relacion_con_el_titular'] = solicitud_tramite.cod_relacion_con_el_titular
            #raise ValidationError({'cod_departamento': 'El código de departamento es obligatorio'})
        
        datos_manual = data.get('datos_manual')
        if datos_manual:
            notificacion_data['permite_notificacion_email'] = data.get('permite_notificacion_email')
            notificacion_data['cod_tipo_documentoID'] = data.get('cod_tipo_documentoID')
            notificacion_data['nro_documentoID'] = data.get('nro_documentoID')
            notificacion_data['persona_a_quien_se_dirige'] = data.get('persona_a_quien_se_dirige')
            notificacion_data['dir_notificacion_nal'] = data.get('dir_notificacion_nal')
            notificacion_data['cod_municipio_notificacion_nal'] = data.get('cod_municipio_notificacion_nal')
            notificacion_data['tel_fijo'] = data.get('tel_fijo')
            notificacion_data['tel_celular'] = data.get('tel_celular')
            notificacion_data['email_notificacion'] = data.get('email_notificacion')
        else:
            id_persona_notificada = data.get('id_persona_notificada')
            persona = Personas.objects.filter(id_persona=id_persona_notificada).first()
            notificacion_data['permite_notificacion_email'] = persona.acepta_notificacion_email
            notificacion_data['cod_tipo_documentoID'] = persona.tipo_documento.cod_tipo_documento
            notificacion_data['nro_documentoID'] = persona.numero_documento
            notificacion_data['persona_a_quien_se_dirige'] = f'{persona.primer_nombre} {persona.segundo_nombre} {persona.primer_apellido} {persona.segundo_apellido}'
            notificacion_data['dir_notificacion_nal'] = persona.direccion_notificaciones
            notificacion_data['cod_municipio_notificacion_nal'] = persona.cod_municipio_notificacion_nal.cod_municipio
            notificacion_data['tel_fijo'] = persona.telefono_fijo_residencial
            notificacion_data['tel_celular'] = persona.telefono_celular
            notificacion_data['email_notificacion'] = persona.email
        
        

        serializer = self.serializer_class(data=notificacion_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        util_PQR = Util_PQR()
        anexos = util_PQR.set_archivo_in_anexo(data['anexos'], request.FILES, "create")

        if anexos:
            anexosCreate = AnexosCreate()
            valores_creados_detalles = anexosCreate.create_anexos_notificaciones(anexos, serializer.data['id_notificacion_correspondencia'], fecha_actual, id_persona_recibe_solicitud)

        return Response({'succes': True, 'detail':'Se creo el consecutivo correctamente', 'data':{**serializer.data}}, status=status.HTTP_201_CREATED)
        
class AnexosCreate(generics.CreateAPIView):
    serializer_class = AnexosPostSerializer

    def create_anexos_notificaciones(self, anexos, id_notificacion, fecha_actual, id_persona_recibe_solicitud):
         nombres_anexos = [anexo['nombre_anexo'] for anexo in anexos]
         nombres_anexos_auditoria = []
         # Validar que no haya valores repetidos
         if len(nombres_anexos) != len(set(nombres_anexos)):
            raise ValidationError("error': 'No se permiten nombres de anexos repetidos.")
         
         for anexo in anexos:
            data_anexo = self.crear_anexo(anexo)

            data_anexos = {}
            data_anexos['id_notificacion_correspondecia'] = id_notificacion
            if anexo['uso_del_documento']:
                data_anexos['uso_del_documento'] = 'IN'
            else:
                data_anexos['uso_del_documento'] = 'PU'
            data_anexos['doc_entrada_salida'] = 'EN'
            if anexo['cod_tipo_documento']:
                tipo_documento = TiposAnexosSoporte.objects.filter(id_tipo_anexo_soporte=anexo['cod_tipo_documento']).first()
                data_anexos['cod_tipo_documento'] = tipo_documento.id_tipo_anexo_soporte
            data_anexos['doc_generado'] = 'MA'
            data_anexos['id_persona_anexa_documento'] = id_persona_recibe_solicitud.id_persona
            data_anexos['fecha_anexo'] = fecha_actual
            data_anexos['id_anexo'] = data_anexo['id_anexo']
            anexosNotificacionCreate = AnexoNotificacionesCreate()
            anexosNotificacionCreate.crear_anexo_notificacion(data_anexos)

            #Guardar el archivo en la tabla T238
            if anexo['archivo']:
                archivo_creado = self.crear_archivos(anexo['archivo'], fecha_actual)
            else:
                raise ValidationError("No se puede crear anexos sin archivo adjunto")
            
            data_metadatos = {}
            #data_metadatos['metadatos'] = anexo['metadatos']
            data_metadatos['anexo'] = data_anexo
            data_metadatos['fecha_registro'] = fecha_actual
            data_metadatos['id_archivo_digital'] = archivo_creado.data.get('data').get('id_archivo_digital')
            metadatosNotificacionesCreate = MetadatosNotificacionesCreate()
            metadatosNotificacionesCreate.create_metadatos_notificaciones(data_metadatos)

    def crear_anexo(self, request):
        try:
            serializer = self.serializer_class(data=request)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data 

        except Exception as e:
            raise ValidationError(str(e))   
        
    def crear_archivos(self, uploaded_file, fecha_creacion):
        #Valida extensión del archivo
        nombre=uploaded_file.name
            
        extension = os.path.splitext(nombre)
        extension_sin_punto = extension[1][1:] if extension[1].startswith('.') else extension
        if not extension_sin_punto:
            raise ValidationError("No fue posible registrar el archivo")
        
        formatos=FormatosTiposMedio.objects.filter(nombre__iexact=extension_sin_punto,activo=True).first()
        if not formatos:
            raise ValidationError("Este formato "+str(extension_sin_punto)+" de archivo no esta permitido")

        # Obtiene el año actual para determinar la carpeta de destino
        current_year = fecha_creacion.year
        ruta = os.path.join("home", "BIA", "Otros", "GDEA", "Anexos_Notificaciones", str(current_year))

        # Crea el archivo digital y obtiene su ID
        data_archivo = {
            'es_Doc_elec_archivo': False,
            'ruta': ruta,
        }
        
        archivos_Digitales = ArchivosDgitalesCreate()
        archivo_creado = archivos_Digitales.crear_archivo(data_archivo, uploaded_file)
        return archivo_creado

class AnexoNotificacionesCreate(generics.CreateAPIView):
    serializer_class = AnexosNotificacionPostSerializer
    
    def crear_anexo_notificacion(self, request):
        try:
            serializer = self.serializer_class(data=request)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data

        except Exception as e:
            raise ValidationError(str(e))  
        
class MetadatosNotificacionesCreate(generics.CreateAPIView):
    serializer_class = MetadatosPostSerializer

    def create_metadatos_notificaciones(self, data_metadatos):
        try:
            data_to_create = self.set_data_metadato(data_metadatos)
            serializer = self.serializer_class(data=data_to_create)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data

        except Exception as e:
            raise ValidationError(str(e))
        
    def set_data_metadato(self, data_metadatos):
        metadato = {}
        anexo = data_metadatos['anexo']

        metadato['id_anexo'] = anexo['id_anexo']
        metadato['fecha_creacion_doc'] = data_metadatos['fecha_registro'].date()
        metadato['cod_origen_archivo'] = "E"
        metadato['es_version_original'] = True
        metadato['id_archivo_sistema'] = data_metadatos['id_archivo_digital']

        
        return metadato
    
#TiposNotificacionesCorrespondencia
class TiposNotificacionesCorrespondenciaCreate(generics.CreateAPIView):
    serializer_class = TiposNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'succes': True, 'detail':'Se creo el tipo de notificación correctamente', 'data':{**serializer.data}}, status=status.HTTP_201_CREATED)
    

class TiposNotificacionesCorrespondenciaGet(generics.ListAPIView):
    serializer_class = TiposNotificacionesCorrespondenciaSerializer

    def get_queryset(self):
        queryset = TiposNotificacionesCorrespondencia.objects.all()  # Obtiene las notificaciones de correspondencia
        permission_classes = [IsAuthenticated]
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    
class TiposNotificacionesCorrespondenciaUpdate(generics.UpdateAPIView):
    serializer_class = TiposNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data
        tipo_notificacion = TiposNotificacionesCorrespondencia.objects.filter(id_tipo_notificacion_correspondencia=pk).first()
        if not tipo_notificacion:
            raise ValidationError(f'El tipo de notificación con id {pk} no existe.')
        if tipo_notificacion.item_ya_usado and data['nombre']:
            raise ValidationError(f'El nombre no se puede actualizar si ya se utilizo.')
        else:
            serializer = self.serializer_class(tipo_notificacion, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
        return Response({'succes': True, 'detail':'Se actualizó el tipo de notificación correctamente', 'data':{**serializer.data}}, status=status.HTTP_200_OK)


class TiposNotificacionesCorrespondenciaDelete(generics.DestroyAPIView):
    serializer_class = TiposNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        tipo_notificacion = TiposNotificacionesCorrespondencia.objects.filter(id_tipo_notificacion_correspondencia=pk).first()
        if not tipo_notificacion:
            raise ValidationError(f'El tipo de notificación con id {pk} no existe.')
        if tipo_notificacion.item_ya_usado:
            raise ValidationError(f'El tipo de notificación con id {pk} ya fue utilizado.')
        else:
            tipo_notificacion.delete()
        return Response({'succes': True, 'detail':'Se eliminó el tipo de notificación correctamente', 'data':{}}, status=status.HTTP_200_OK)


#EstadosNotificacionesCorrespondencia
class EstadosNotificacionesCorrespondenciaCreate(generics.CreateAPIView):
    serializer_class = EstadosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'succes': True, 'detail':'Se creo el estado de notificaciones correctamente', 'data':{**serializer.data}}, status=status.HTTP_201_CREATED)
    

class EstadosNotificacionesCorrespondenciaGet(generics.ListAPIView):
    serializer_class = EstadosNotificacionesCorrespondenciaSerializer

    def get_queryset(self):
        queryset = EstadosNotificacionesCorrespondencia.objects.all() 
        permission_classes = [IsAuthenticated]
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    
class EstadosNotificacionesCorrespondenciaUpdate(generics.UpdateAPIView):
    serializer_class = EstadosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data
        estado_notificacion = EstadosNotificacionesCorrespondencia.objects.filter(id_estado_notificacion_correspondencia=pk).first()
        if not estado_notificacion:
            raise ValidationError(f'El estado de notificación con id {pk} no existe.')
        if estado_notificacion.item_ya_usado and data['nombre']:
            raise ValidationError(f'El nombre no se puede actualizar si ya se utilizo.')
        else:
            serializer = self.serializer_class(estado_notificacion, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
        return Response({'succes': True, 'detail':'Se actualizó el estado de notificación correctamente', 'data':{**serializer.data}}, status=status.HTTP_200_OK)


class EstadosNotificacionesCorrespondenciaDelete(generics.DestroyAPIView):
    serializer_class = EstadosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        estado_notificacion = EstadosNotificacionesCorrespondencia.objects.filter(id_estado_notificacion_correspondencia=pk).first()
        if not estado_notificacion:
            raise ValidationError(f'El estado de notificación con id {pk} no existe.')
        if estado_notificacion.item_ya_usado:
            raise ValidationError(f'El estado de notificación con id {pk} ya fue utilizado.')
        else:
            estado_notificacion.delete()
        return Response({'succes': True, 'detail':'Se eliminó el estado de notificación correctamente', 'data':{}}, status=status.HTTP_200_OK)
    

#CausasOAnomaliasNotificacionesCorrespondencia
class CausaOAnomaliasNotificacionesCorrespondenciaCreate(generics.CreateAPIView):
    serializer_class = CausasOAnomaliasNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'succes': True, 'detail':'Se creo la causa o anomalia de notificaciones correctamente', 'data':{**serializer.data}}, status=status.HTTP_201_CREATED)
    

class CausaOAnomaliasNotificacionesCorrespondenciaGet(generics.ListAPIView):
    serializer_class = CausasOAnomaliasNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CausasOAnomalias.objects.all() 
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    
class CausaOAnomaliasNotificacionesCorrespondenciaUpdate(generics.UpdateAPIView):
    serializer_class = CausasOAnomaliasNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data
        causa_notificacion = CausasOAnomalias.objects.filter(id_causa_o_anomalia=pk).first()
        if not causa_notificacion:
            raise ValidationError(f'La causa o anomalia de notificación con id {pk} no existe.')
        if causa_notificacion.item_ya_usado and data['nombre']:
            raise ValidationError(f'El nombre no se puede actualizar si ya se utilizo.')
        else:
            serializer = self.serializer_class(causa_notificacion, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
        return Response({'succes': True, 'detail':'Se actualizó la causa o anomalia de notificación correctamente', 'data':{**serializer.data}}, status=status.HTTP_200_OK)


class CausaOAnomaliasNotificacionesCorrespondenciaDelete(generics.DestroyAPIView):
    serializer_class = CausasOAnomaliasNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        causa_notificacion = CausasOAnomalias.objects.filter(id_causa_o_anomalia=pk).first()
        if not causa_notificacion:
            raise ValidationError(f'La causa o anomalia de notificación con id {pk} no existe.')
        if causa_notificacion.item_ya_usado:
            raise ValidationError(f'La causa o anomalia de notificación con id {pk} ya fue utilizado.')
        else:
            causa_notificacion.delete()
        return Response({'succes': True, 'detail':'Se eliminó la causa o anomalia de notificación correctamente', 'data':{}}, status=status.HTTP_200_OK)
    

#TiposAnexosNotificacionesCorrespondencia
class TiposAnexosNotificacionesCorrespondenciaCreate(generics.CreateAPIView):
    serializer_class = TiposAnexosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'succes': True, 'detail':'Se creo el tipo de anexo de notificaciones correctamente', 'data':{**serializer.data}}, status=status.HTTP_201_CREATED)
    

class TiposAnexosNotificacionesCorrespondenciaGet(generics.ListAPIView):
    serializer_class = TiposAnexosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = TiposAnexosSoporte.objects.all() 
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    
class TiposAnexosNotificacionesCorrespondenciaUpdate(generics.UpdateAPIView):
    serializer_class = TiposAnexosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data
        tipo_anexo_notificacion = TiposAnexosSoporte.objects.filter(id_tipo_anexo_soporte=pk).first()
        if not tipo_anexo_notificacion:
            raise ValidationError(f'El tipo de anexo de notificación con id {pk} no existe.')
        if tipo_anexo_notificacion.item_ya_usado and data['nombre']:
            raise ValidationError(f'El nombre no se puede actualizar si ya se utilizo.')
        else:
            serializer = self.serializer_class(tipo_anexo_notificacion, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
        return Response({'succes': True, 'detail':'Se actualizó el tipo de anexo de notificación correctamente', 'data':{**serializer.data}}, status=status.HTTP_200_OK)


class TiposAnexosNotificacionesCorrespondenciaDelete(generics.DestroyAPIView):
    serializer_class = TiposAnexosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        tipo_anexo_notificacion = TiposAnexosSoporte.objects.filter(id_tipo_anexo_soporte=pk).first()
        if not tipo_anexo_notificacion:
            raise ValidationError(f'El tipo de anexo de notificación con id {pk} no existe.')
        if tipo_anexo_notificacion.item_ya_usado:
            raise ValidationError(f'El tipo de anexo de notificación con id {pk} ya fue utilizado.')
        else:
            tipo_anexo_notificacion.delete()
        return Response({'succes': True, 'detail':'Se eliminó el tipo de anexo de notificación correctamente', 'data':{}}, status=status.HTTP_200_OK)
    
    
#TiposDocumentosNotificacionesCorrespondencia
class TiposDocumentosNotificacionesCorrespondenciaCreate(generics.CreateAPIView):
    serializer_class = TiposDocumentosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'succes': True, 'detail':'Se creo el tipo de documento de notificaciones y correspondecia correctamente', 'data':{**serializer.data}}, status=status.HTTP_201_CREATED)
    

class TiposDocumentosNotificacionesCorrespondenciaGet(generics.ListAPIView):
    serializer_class = TiposDocumentosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = TiposDocumentos.objects.all() 
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    
class TiposDocumentosNotificacionesCorrespondenciaUpdate(generics.UpdateAPIView):
    serializer_class = TiposDocumentosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data
        tipo_documento_notificacion = TiposDocumentos.objects.filter(id_tipo_documento=pk).first()
        if not tipo_documento_notificacion:
            raise ValidationError(f'El tipo de anexo de notificación con id {pk} no existe.')
        if tipo_documento_notificacion.item_ya_usado and data['nombre']:
            raise ValidationError(f'El nombre no se puede actualizar si ya se utilizo.')
        else:
            serializer = self.serializer_class(tipo_documento_notificacion, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
        return Response({'succes': True, 'detail':'Se actualizó el tipo de documento de notificación correctamente', 'data':{**serializer.data}}, status=status.HTTP_200_OK)


class TiposDocumentosNotificacionesCorrespondenciaDelete(generics.DestroyAPIView):
    serializer_class = TiposDocumentosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        tipo_documento_notificacion = TiposDocumentos.objects.filter(id_tipo_documento=pk).first()
        if not tipo_documento_notificacion:
            raise ValidationError(f'El tipo de documento de notificación con id {pk} no existe.')
        if tipo_documento_notificacion.item_ya_usado:
            raise ValidationError(f'El tipo de documento de notificación con id {pk} ya fue utilizado.')
        else:
            tipo_documento_notificacion.delete()
        return Response({'succes': True, 'detail':'Se eliminó el tipo de documento de notificación correctamente', 'data':{}}, status=status.HTTP_200_OK)