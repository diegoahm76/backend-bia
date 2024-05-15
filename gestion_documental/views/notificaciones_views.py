from rest_framework.views import APIView
from rest_framework.response import Response
import os
import json
from django.db.models import Q
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db import transaction
from gestion_documental.models.radicados_models import T262Radicados
from gestion_documental.models.expedientes_models import ExpedientesDocumentales
from seguridad.permissions.permissions_notificaciones import PermisoActualizarAsignacionTareasNotificaciones, PermisoActualizarAutorizarAsignaciones, PermisoActualizarCausasAnomaliasNotificaciones, PermisoActualizarEstadosNotificaciones, PermisoActualizarRechazarNotificaciones, PermisoActualizarTiposAnexosNotificaciones, PermisoActualizarTiposDocumentoNoti, PermisoActualizarTiposNotificaciones, PermisoBorrarCausasAnomaliasNotificaciones, PermisoBorrarEstadosNotificaciones, PermisoBorrarTiposAnexosNotificaciones, PermisoBorrarTiposDocumentoNoti, PermisoBorrarTiposNotificaciones, PermisoCrearAsignacionTareasNotificaciones, PermisoCrearCausasAnomaliasNotificaciones, PermisoCrearCrearNotificaciones, PermisoCrearEstadosNotificaciones, PermisoCrearGeneradorDocumentosNotificaciones, PermisoCrearPublicarGacetaAmbiental, PermisoCrearTiposAnexosNotificaciones, PermisoCrearTiposDocumentoNoti, PermisoCrearTiposNotificaciones
from transversal.models.organigrama_models import UnidadesOrganizacionales
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, time

from tramites.models.tramites_models import SolicitudesTramites
from gestion_documental.serializers.pqr_serializers import AnexosPostSerializer, MetadatosPostSerializer
from gestion_documental.views.pqr_views import Util_PQR
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.models.trd_models import FormatosTiposMedio
from gestion_documental.utils import UtilsGestor
from tramites.models.tramites_models import SolicitudesTramites, TiposActosAdministrativos, ActosAdministrativos

from transversal.models.base_models import Personas

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
    AsignacionNotiCorresGetSerializer,
    TramitesSerializer,
    TiposActosAdministrativosSerializer,
    ActosAdministrativosSerializer,
    Registros_NotificacionesCorrespondeciaSerializer,
    NotificacionesCorrespondenciaAnexosSerializer,
    RegistroNotificacionesCorrespondenciaPaginasSerializer,
    AnexosNotificacionesCorrespondenciaDatosSerializer,
    TiposAnexosSoporteSerializer,
    CausasOAnomaliasSerializer,
    AnexosNotificacionesCorrespondenciaSerializer,
    DatosTitularesCorreoSerializer,
    DocumentosDeArchivoExpedienteSerializer,
    ConstanciaNotificacionSerializer,
    GeneradorDocumentosSerializer
    )

class ListaNotificacionesCorrespondencia(generics.ListAPIView):
    serializer_class = NotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = NotificacionesCorrespondencia.objects.all()  # Obtiene las notificaciones de correspondencia
        
        id_radicado = ''
        data_final = []

        # Obtener parámetros de consulta
        tipo_documento = self.request.query_params.get('tipo_documento')
        radicado = self.request.query_params.get('radicado')
        expediente = self.request.query_params.get('expediente')
        grupo_solicitante = self.request.query_params.get('grupo_solicitante')
        estado = self.request.query_params.get('estado')
        estado_asignacion = self.request.query_params.get('estado_asignacion')
        funcionario_asignado = self.request.query_params.get('funcionario_asignado')

        # Filtrar por tipo de documento si es válido
        if tipo_documento:
            tipo_documento_valido = ['OF', 'AC', 'AA', 'AI', 'OT']
            if tipo_documento in tipo_documento_valido:
                queryset = queryset.filter(cod_tipo_documento=tipo_documento)
            else:
                raise ValidationError(f'El tipo de documento {tipo_documento} no es válido.')
        

        if grupo_solicitante:
            queryset = queryset.filter(id_und_org_oficina_solicita=grupo_solicitante)

        if funcionario_asignado:
            queryset = queryset.filter(id_persona_asignada=funcionario_asignado)

        if estado:
            estado_valido = ['RE', 'DE', 'EG', 'PE', 'NT']
            if estado in estado_valido:
                queryset = queryset.filter(cod_estado=estado)
            else:
                raise ValidationError(f'El estado {estado} no es válido.')
            
        if estado_asignacion:
            estado_valido = ['Ac', 'Pe', 'Re']
            if estado_asignacion in estado_valido:
                queryset = queryset.filter(cod_estado_asignacion=estado_asignacion)
            else:
                raise ValidationError(f'El estado de la asignación {estado_asignacion} no es válido.')
            
        if expediente:
            if '-' in expediente:
                try:
                    serie_subserie, agno, consecutivo = expediente.split('-')
                except ValueError:
                    pass
                else:
                    queryset = queryset.filter(
                        id_expediente_documental__codigo_exp_und_serie_subserie__icontains=serie_subserie,
                        id_expediente_documental__codigo_exp_Agno__icontains=agno,
                        id_expediente_documental__codigo_exp_consec_por_agno__icontains=consecutivo
                    )
            else:
                queryset = queryset.filter(
                    Q(id_expediente_documental__codigo_exp_und_serie_subserie__icontains=serie_subserie) |
                    Q(id_expediente_documental__codigo_exp_Agno__icontains=agno) |
                    Q(id_expediente_documental__codigo_exp_consec_por_agno__icontains=consecutivo)
                )



        return  queryset, radicado

    def get(self, request, *args, **kwargs):
        queryset, radicado = self.get_queryset()
        print(queryset)
        serializer = self.get_serializer(queryset, many=True)
        data_validada =[]
        #data_validada = serializer.data
        print(radicado)
        if radicado != None:
            #data_validada = [item for item in serializer.data if radicado in item.get('radicado', '')]
            for item in serializer.data:
                item_registro = item.get('registros_notificaciones')
                print(item_registro)
                if item_registro != None:
                    for registro in item_registro:
                        if radicado == registro.get('radicado', ''):
                            data_validada.append(item)
        else :
            data_validada = serializer.data
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_validada,}, status=status.HTTP_200_OK)    
    

class NotificacionesCorrespondenciaYTareasGet(generics.ListAPIView):
    serializer_class = NotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = NotificacionesCorrespondencia.objects.all()  # Obtiene las notificaciones de correspondencia


        # Obtener parámetros de consulta
        tipo_documento = self.request.query_params.get('tipo_documento')
        radicado = self.request.query_params.get('radicado')
        expediente = self.request.query_params.get('expediente')
        grupo_solicitante = self.request.query_params.get('grupo_solicitante')
        estado = self.request.query_params.get('estado')
        estado_asignacion = self.request.query_params.get('estado_asignacion')
        #funcionario_asignado = self.request.query_params.get('funcionario_asignado')

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
            
        if estado_asignacion:
            estado_valido = ['Ac', 'Pe', 'Re']
            if estado_asignacion in estado_valido:
                queryset = queryset.filter(cod_estado_asignacion=estado_asignacion)
            else:
                raise ValidationError(f'El estado de la asignación {estado_asignacion} no es válido.')
            
        if expediente:
            if '-' in expediente:
                try:
                    serie_subserie, agno, consecutivo = expediente.split('-')
                except ValueError:
                    pass
                else:
                    queryset = queryset.filter(
                        id_expediente_documental__codigo_exp_und_serie_subserie__icontains=serie_subserie,
                        id_expediente_documental__codigo_exp_Agno__icontains=agno,
                        id_expediente_documental__codigo_exp_consec_por_agno__icontains=consecutivo
                    )
            else:
                queryset = queryset.filter(
                    Q(id_expediente_documental__codigo_exp_und_serie_subserie__icontains=serie_subserie) |
                    Q(id_expediente_documental__codigo_exp_Agno__icontains=agno) |
                    Q(id_expediente_documental__codigo_exp_consec_por_agno__icontains=consecutivo)
                )



        return  queryset#, funcionario_asignado

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        funcionario_asignado = request.user.persona.id_persona
        serializer = self.get_serializer(queryset, many=True)
        data_validada =[]
        data_temporal = []
        funcionario_asignado = int(funcionario_asignado)
        for item in serializer.data:
            id_persona_asignada = item.get('id_persona_asignada')
            if funcionario_asignado == id_persona_asignada:
                data_validada.append(item)
            else:
                data_temporal.append(item)
        for temporal in data_temporal:
            item_registro =  temporal.get('registros_notificaciones')
            if item_registro != None:
                data_registro = []
                for registro in item_registro:
                    if funcionario_asignado == registro.get('id_persona_asignada'):
                        data_registro.append(registro)
                if data_registro:
                    temporal['registros_notificaciones'] = data_registro
                    data_validada.append(temporal)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_validada,}, status=status.HTTP_200_OK)   

    
class GetNotificacionesCorrespondeciaAnexos(generics.RetrieveAPIView):
    serializer_class = NotificacionesCorrespondenciaAnexosSerializer
    queryset = NotificacionesCorrespondencia.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_notificacion_correspondencia):
        try:
            data_notificaciones = self.queryset.filter(id_notificacion_correspondencia = id_notificacion_correspondencia).first()
            
            if data_notificaciones:
                serializador = self.serializer_class(data_notificaciones, many = False)
                return Response({'success':True, 'detail':'Se encontro la solicitud de notificación por el id consultado','data':serializador.data},status=status.HTTP_200_OK)
            else:
                return Response({'success':True, 'detail':'No Se encontro la solicitud de notificación por el id consultado'},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
class UpdateSolicitudNotificacionAsignacion(generics.UpdateAPIView):
    serializer_class = NotificacionesCorrespondenciaCreateSerializer

    def put(self, data_asignacion, pk):
        data = data_asignacion
        registro_tarea = NotificacionesCorrespondencia.objects.filter(id_notificacion_correspondencia=pk).first()

        serializer = self.serializer_class(registro_tarea, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return instance

 
class CrearAsignacionNotificacion(generics.CreateAPIView):
    serializer_class = AsignacionNotiCorresCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        fecha_actual = timezone.now()
        id_persona_asigna = request.user.persona

        if not data.get('id_persona_asignada'):
            raise ValidationError({'id_persona_asignada': 'La persona asignada es obligatorio'})
   
        asignacion_data = {
            'id_notificacion_correspondencia': data.get('id_notificacion_correspondencia'),
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
                'fecha_eleccion_estado': fecha_actual,
                'id_persona_asigna': id_persona_asigna.id_persona,
                'id_persona_asignada': data.get('id_persona_asignada'),
                'cod_estado_asignacion': 'Pe',
                'cod_estado': 'RE',
            }
            actualizar_notificacion = UpdateSolicitudNotificacionAsignacion()
            if not actualizar_notificacion.put(data_asignacion, data.get('id_notificacion_correspondencia')):
                raise ValidationError({'id_notificacion_correspondencia': 'No se pudo actualizar el estado de la tarea'})
        return Response({'succes': True, 'detail':'Se la asigncación correctamente', 'data':{**serializer.data}}, status=status.HTTP_201_CREATED)
    

class CrearTareas(generics.CreateAPIView):
    serializer_class = Registros_NotificacionesCorrespondeciaCreateSerializer

    def post(self, request, fecha_actual):
        data = NotificacionesCorrespondencia.objects.filter(id_notificacion_correspondencia=request.get('id_notificacion')).first()
        print(request.get('id_notificacion'))

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
            'cod_estado': request.get('cod_estado'),
            'id_estado_actual_registro': 2,
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
    

class CrearAsignacionTarea(generics.CreateAPIView):
    serializer_class = AsignacionNotiCorresCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        fecha_actual = timezone.now()
        id_persona_asigna = request.user.persona

        if not data.get('id_persona_asignada'):
            raise ValidationError({'id_persona_asignada': 'La persona asignada es obligatorio'})
        
        registro = CrearTareas()
        data_tarea = {
            'id_notificacion': data.get('id_notificacion_correspondencia'),
            'id_tipo_notificacion_correspondencia': data.get('id_tipo_notificacion_correspondencia'),
        }

        if id_persona_asigna.id_persona == data.get('id_persona_asignada'):
            data_tarea['cod_estado'] = 'RE'
        else:
            data_tarea['cod_estado'] = 'PE'
        tarea = registro.post(data_tarea, fecha_actual)
        asignacion_data = {
            'id_orden_notificacion': tarea.id_registro_notificacion_correspondencia,
            'fecha_asignacion': fecha_actual,
            'id_persona_asigna': id_persona_asigna.id_persona,
            'id_persona_asignada': data.get('id_persona_asignada'),
            'fecha_eleccion_estado': fecha_actual,
            'id_und_org_seccion_asignada': id_persona_asigna.id_unidad_organizacional_actual.id_unidad_organizacional, 
        }

        if id_persona_asigna.id_persona == data.get('id_persona_asignada'):
            asignacion_data['cod_estado_asignacion'] = 'Ac'
        else:
            asignacion_data['cod_estado_asignacion'] = 'Pe'
        serializer = self.serializer_class(data=asignacion_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if instance:
            data_asignacion = {
                'fecha_asignacion': instance.fecha_asignacion,
                'fecha_eleccion_estado': instance.fecha_eleccion_estado,
                'id_persona_asigna': instance.id_persona_asigna.id_persona,
                'id_persona_asignada': instance.id_persona_asignada.id_persona,
                'cod_estado_asignacion': instance.cod_estado_asignacion,
            }
            tarea_actualizada = UpdateTareasAsignacion()
            if not tarea_actualizada.put(data_asignacion, tarea.id_registro_notificacion_correspondencia):
                raise ValidationError({'id_notificacion_correspondencia': 'No se pudo actualizar el estado de la tarea'})
        return Response({'succes': True, 'detail':'Se la asigncación correctamente', 'data':{**serializer.data}}, status=status.HTTP_201_CREATED)
    

class GetAsignacionesCorrespondencia(generics.ListAPIView):
    serializer_class = AsignacionNotificacionCorrespondenciaSerializer

    def get_queryset(self):
        queryset = AsignacionNotificacionCorrespondencia.objects.all()  # Obtiene las notificaciones de correspondencia # Obtiene las notificaciones de correspondencia
        permission_classes = [IsAuthenticated]
        persona = {}

        id_persona_asignada = self.request.query_params.get('id_persona_asignada')
        if id_persona_asignada:
            queryset = queryset.filter(id_persona_asignada=id_persona_asignada)
            if not queryset:
                persona = Personas.objects.filter(id_persona=id_persona_asignada).first()
        else:
            raise ValidationError(f'La persona {id_persona_asignada} no es valida.')

        return queryset, persona

    def get(self, request, *args, **kwargs):
        queryset, persona = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        persona_asignada = ''
        vigencia_contrato = ''
        id_persona_asignada = 0
        tarear_pendientes = 0
        tarear_resueltas = 0
        tarear_asignadas = 0
        notificaciones_pendientes = 0
        notificaciones_resueltas = 0
        notificaciones_asignadas = 0
        if queryset:
            for item in serializer.data:
                if item.get('id_notificacion_correspondencia'):
                    persona_asignada = item.get('persona_asignada')
                    vigencia_contrato = item.get('vigencia_contrato')
                    id_persona_asignada = item.get('id_persona_asignada')
                    notificaciones_asignadas = notificaciones_asignadas+1
                    notificacion_correspondencia = NotificacionesCorrespondencia.objects.filter(id_notificacion_correspondencia = item.get('id_notificacion_correspondencia')).first()
                    if notificacion_correspondencia.cod_estado == 'PE' or notificacion_correspondencia.cod_estado == 'EG' or notificacion_correspondencia.cod_estado == 'RE':
                        notificaciones_pendientes = notificaciones_pendientes+1
                    if notificacion_correspondencia.cod_estado == 'NT':
                        notificaciones_resueltas = notificaciones_resueltas+1
                else:
                    persona_asignada = item.get('persona_asignada')
                    vigencia_contrato = item.get('vigencia_contrato')
                    id_persona_asignada = item.get('id_persona_asignada')
                    tarear_asignadas = tarear_asignadas+1
                    tarea = Registros_NotificacionesCorrespondecia.objects.filter(id_registro_notificacion_correspondencia = item.get('id_orden_notificacion')).first()
                    if tarea.cod_estado == 'PE' or tarea.cod_estado == 'EG' or tarea.cod_estado == 'RE':
                        tarear_pendientes = tarear_pendientes+1
                    if tarea.cod_estado == 'NT':
                        tarear_resueltas = tarear_resueltas+1
        else:
            persona_asignada = f"{persona.primer_nombre} {persona.segundo_nombre} {persona.primer_apellido} {persona.segundo_apellido}"
            id_persona_asignada = persona.id_persona
        data_valida = {"persona_asignada": persona_asignada, "id_persona_asignada": id_persona_asignada, "vigencia_contrato": vigencia_contrato, "tarear_asignadas": tarear_asignadas, "tarear_resueltas": tarear_resueltas, "tarear_pendientes": tarear_pendientes, "notificaciones_asignadas": notificaciones_asignadas, "notificaciones_resueltas": notificaciones_resueltas, "notificaciones_pendientes": notificaciones_pendientes, "asignaciones": serializer.data}
        return Response({'succes': True, 'detail':'Tiene las siguientes asignaciones', 'data':data_valida,}, status=status.HTTP_200_OK) 
  
    
class CrearNotiicacionManual(generics.CreateAPIView):
    serializer_class = NotificacionesCorrespondenciaCreateSerializer
    permission_classes = [IsAuthenticated, PermisoCrearCrearNotificaciones]

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
            'cod_estado': 'PE',
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
            data_anexos['usuario_notificado'] = False
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
            # Agregue usuario notificado
            if 'usuario_notificado' in data_anexo:
                data_anexos['usuario_notificado'] = data_anexo['usuario_notificado']
            else:
                data_anexos['usuario_notificado'] = False
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
        metadato['fecha_creacion_doc'] = data_metadatos['fecha_registro']
        metadato['cod_origen_archivo'] = "E"
        metadato['es_version_original'] = True
        metadato['id_archivo_sistema'] = data_metadatos['id_archivo_digital']

        
        return metadato
    
#TiposNotificacionesCorrespondencia
class TiposNotificacionesCorrespondenciaCreate(generics.CreateAPIView):
    serializer_class = TiposNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated, PermisoCrearTiposNotificaciones]

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
    permission_classes = [IsAuthenticated, PermisoActualizarTiposNotificaciones]

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
    permission_classes = [IsAuthenticated, PermisoBorrarTiposNotificaciones]

    def delete(self, request, pk):
        tipo_notificacion = TiposNotificacionesCorrespondencia.objects.filter(id_tipo_notificacion_correspondencia=pk).first()
        if not tipo_notificacion:
            raise ValidationError(f'El tipo de notificación con id {pk} no existe.')
        
        if tipo_notificacion.registro_precargado:
            raise ValidationError(f'El tipo de notificación con id {pk} es un registro precargado y no se puede eliminar.')
        if tipo_notificacion.item_ya_usado:
            raise ValidationError(f'El tipo de notificación con id {pk} ya fue utilizado.')
        else:
            tipo_notificacion.delete()
        return Response({'succes': True, 'detail':'Se eliminó el tipo de notificación correctamente', 'data':{}}, status=status.HTTP_200_OK)


#EstadosNotificacionesCorrespondencia
class EstadosNotificacionesCorrespondenciaCreate(generics.CreateAPIView):
    serializer_class = EstadosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated, PermisoCrearEstadosNotificaciones]

    def post(self, request):
        data = request.data

        tipo_notificacion_correspondencia = get_object_or_404(TiposNotificacionesCorrespondencia, id_tipo_notificacion_correspondencia=data.get('cod_tipo_notificacion_correspondencia'))
        if tipo_notificacion_correspondencia.activo == False:
            raise ValidationError(f'El tipo de notificación con id {data.get("cod_tipo_notificacion_correspondencia")} no esta activo.')
        else:
            if tipo_notificacion_correspondencia.item_ya_usado == False:
                tipo_notificacion_correspondencia.item_ya_usado = True
                tipo_notificacion_correspondencia.save()

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
    permission_classes = [IsAuthenticated, PermisoActualizarEstadosNotificaciones]

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
    permission_classes = [IsAuthenticated, PermisoBorrarEstadosNotificaciones]

    def delete(self, request, pk):
        estado_notificacion = EstadosNotificacionesCorrespondencia.objects.filter(id_estado_notificacion_correspondencia=pk).first()
        if not estado_notificacion:
            raise ValidationError(f'El estado de notificación con id {pk} no existe.')
        if estado_notificacion.registro_precargado:
            raise ValidationError(f'El estado de notificación con id {pk} es un registro precargado y no se puede eliminar.')
        if estado_notificacion.item_ya_usado:
            raise ValidationError(f'El estado de notificación con id {pk} ya fue utilizado.')
        else:
            estado_notificacion.delete()
        return Response({'succes': True, 'detail':'Se eliminó el estado de notificación correctamente', 'data':{}}, status=status.HTTP_200_OK)
    

#CausasOAnomaliasNotificacionesCorrespondencia
class CausaOAnomaliasNotificacionesCorrespondenciaCreate(generics.CreateAPIView):
    serializer_class = CausasOAnomaliasNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated, PermisoCrearCausasAnomaliasNotificaciones]

    def post(self, request):
        data = request.data

        tipo_notificacion_correspondencia = get_object_or_404(TiposNotificacionesCorrespondencia, id_tipo_notificacion_correspondencia=data.get('id_tipo_notificacion_correspondencia'))
        if tipo_notificacion_correspondencia.activo == False:
            raise ValidationError(f'El tipo de notificación con id {data.get("id_tipo_notificacion_correspondencia")} no esta activo.')
        else:
            if tipo_notificacion_correspondencia.item_ya_usado == False:
                tipo_notificacion_correspondencia.item_ya_usado = True
                tipo_notificacion_correspondencia.save()

            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            return Response({'succes': True, 'detail':'Se creo el estado de notificaciones correctamente', 'data':{**serializer.data}}, status=status.HTTP_201_CREATED)


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
    permission_classes = [IsAuthenticated, PermisoActualizarCausasAnomaliasNotificaciones]

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
    permission_classes = [IsAuthenticated, PermisoBorrarCausasAnomaliasNotificaciones]

    def delete(self, request, pk):
        causa_notificacion = CausasOAnomalias.objects.filter(id_causa_o_anomalia=pk).first()
        if not causa_notificacion:
            raise ValidationError(f'La causa o anomalia de notificación con id {pk} no existe.')
        
        if causa_notificacion.registro_precargado:
            raise ValidationError(f'La causa o anomalia de notificación con id {pk} es un registro precargado y no se puede eliminar.')
        if causa_notificacion.item_ya_usado:
            raise ValidationError(f'La causa o anomalia de notificación con id {pk} ya fue utilizado.')
        else:
            causa_notificacion.delete()
        return Response({'succes': True, 'detail':'Se eliminó la causa o anomalia de notificación correctamente', 'data':{}}, status=status.HTTP_200_OK)
    

#TiposAnexosNotificacionesCorrespondencia
class TiposAnexosNotificacionesCorrespondenciaCreate(generics.CreateAPIView):
    serializer_class = TiposAnexosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated, PermisoCrearTiposAnexosNotificaciones]

    def post(self, request):
        data = request.data

        tipo_notificacion_correspondencia = get_object_or_404(TiposNotificacionesCorrespondencia, id_tipo_notificacion_correspondencia=data.get('id_tipo_notificacion_correspondencia'))
        if tipo_notificacion_correspondencia.activo == False:
            raise ValidationError(f'El tipo de notificación con id {data.get("id_tipo_notificacion_correspondencia")} no esta activo.')
        else:
            if tipo_notificacion_correspondencia.item_ya_usado == False:
                tipo_notificacion_correspondencia.item_ya_usado = True
                tipo_notificacion_correspondencia.save()

            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            return Response({'succes': True, 'detail':'Se creo el estado de notificaciones correctamente', 'data':{**serializer.data}}, status=status.HTTP_201_CREATED)
    

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
    permission_classes = [IsAuthenticated, PermisoActualizarTiposAnexosNotificaciones]

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
    permission_classes = [IsAuthenticated, PermisoBorrarTiposAnexosNotificaciones]

    def delete(self, request, pk):
        tipo_anexo_notificacion = TiposAnexosSoporte.objects.filter(id_tipo_anexo_soporte=pk).first()
        if not tipo_anexo_notificacion:
            raise ValidationError(f'El tipo de anexo de notificación con id {pk} no existe.')
        
        if tipo_anexo_notificacion.registro_precargado:
            raise ValidationError(f'El tipo de anexo de notificación con id {pk} es un registro precargado y no se puede eliminar.')
        if tipo_anexo_notificacion.item_ya_usado:
            raise ValidationError(f'El tipo de anexo de notificación con id {pk} ya fue utilizado.')
        else:
            tipo_anexo_notificacion.delete()
        return Response({'succes': True, 'detail':'Se eliminó el tipo de anexo de notificación correctamente', 'data':{}}, status=status.HTTP_200_OK)
    
    
#TiposDocumentosNotificacionesCorrespondencia
class TiposDocumentosNotificacionesCorrespondenciaCreate(generics.CreateAPIView):
    serializer_class = TiposDocumentosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated, PermisoCrearTiposDocumentoNoti]

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
    permission_classes = [IsAuthenticated, PermisoActualizarTiposDocumentoNoti]

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
    permission_classes = [IsAuthenticated, PermisoBorrarTiposDocumentoNoti]

    def delete(self, request, pk):
        tipo_documento_notificacion = TiposDocumentos.objects.filter(id_tipo_documento=pk).first()
        if not tipo_documento_notificacion:
            raise ValidationError(f'El tipo de documento de notificación con id {pk} no existe.')
        if tipo_documento_notificacion.registro_precargado:
            raise ValidationError(f'El tipo de documento de notificación con id {pk} es un registro precargado y no se puede eliminar.')
        if tipo_documento_notificacion.item_ya_usado:
            raise ValidationError(f'El tipo de documento de notificación con id {pk} ya fue utilizado.')
        else:
            tipo_documento_notificacion.delete()
        return Response({'succes': True, 'detail':'Se eliminó el tipo de documento de notificación correctamente', 'data':{}}, status=status.HTTP_200_OK)
    

class ListaTareasFuncionario(generics.ListAPIView):
    serializer_class = Registros_NotificacionesCorrespondeciaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        queryset = Registros_NotificacionesCorrespondecia.objects.all()  
        id_persona_logueada = request.user.persona.id_persona
        # Obtener parámetros de consulta
        tipo_documento = self.request.query_params.get('tipo_documento')
        tipo_notificacion = self.request.query_params.get('tipo_notificacion')
        radicado = self.request.query_params.get('radicado')
        expediente = self.request.query_params.get('expediente')
        grupo_solicitante = self.request.query_params.get('grupo_solicitante')
        estado = self.request.query_params.get('estado')

        queryset = queryset.filter(id_persona_asignada=id_persona_logueada)

        # Filtrar por tipo de documento si es válido
        if tipo_documento:
            tipo_documento_valido = ['OF', 'AC', 'AA', 'AI', 'OT']
            if tipo_documento in tipo_documento_valido:
                queryset = queryset.filter(cod_tipo_documento=tipo_documento)
            else:
                raise ValidationError(f'El tipo de documento {tipo_documento} no es válido.')
        

        if grupo_solicitante:
            queryset = queryset.filter(id_und_org_oficina_solicita=grupo_solicitante)

        if tipo_notificacion:
            queryset = queryset.filter(id_tipo_notificacion_correspondencia=tipo_notificacion)

        if estado:
            estado_valido = ['RE', 'DE', 'EG', 'PE', 'NT']
            if estado in estado_valido:
                queryset = queryset.filter(cod_estado=estado)
            else:
                raise ValidationError(f'El estado {estado} no es válido.')
            
        if radicado:
            # Filtrar por el radicado en la tabla T262Radicados con flexibilidad
            if '-' in radicado:
                try:
                    prefijo, agno, numero = radicado.split('-')
                    numero = numero.lstrip('0')
                except ValueError:
                    # Si no se puede dividir en prefijo, año y número, continuar sin filtrar por radicado
                    pass
                else:
                    queryset = queryset.filter(
                        id_radicado__prefijo_radicado__icontains=prefijo,
                        id_radicado__agno_radicado__icontains=agno,
                        id_radicado__nro_radicado__icontains=numero
                    )
            else:
                # Si no hay guion ('-'), buscar en cualquier parte del radicado
                queryset = queryset.filter(
                    Q(id_radicado__prefijo_radicado__icontains=radicado) |
                    Q(id_radicado__agno_radicado__icontains=radicado) |
                    Q(id_radicado__nro_radicado__icontains=radicado)
                )

        if expediente:
            # Filtrar por el radicado en la tabla T262Radicados con flexibilidad
            if '-' in expediente:
                try:
                    serie_subserie, agno, consecutivo = expediente.split('-')
                except ValueError:
                    # Si no se puede dividir en prefijo, año y número, continuar sin filtrar por radicado
                    pass
                else:
                    queryset = queryset.filter(
                        id_notificacion_correspondencia__id_expediente__codigo_exp_und_serie_subserie__icontains=serie_subserie,
                        id_notificacion_correspondencia__id_expediente__codigo_exp_Agno__icontains=agno,
                        id_notificacion_correspondencia__id_expediente__codigo_exp_consec_por_agno__icontains=consecutivo
                    )
            else:
                # Si no hay guion ('-'), buscar en cualquier parte del radicado
                queryset = queryset.filter(
                    Q(id_notificacion_correspondencia__id_expediente__codigo_exp_und_serie_subserie__icontains=serie_subserie) |
                    Q(id_notificacion_correspondencia__id_expediente__codigo_exp_Agno__icontains=agno) |
                    Q(id_notificacion_correspondencia__id_expediente__codigo_exp_consec_por_agno__icontains=consecutivo)
                )

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)
        print(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    

class GetTramite(generics.ListAPIView):
    serializer_class = TramitesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = SolicitudesTramites.objects.all()  # Obtiene las notificaciones de correspondencia

        nombre_proyecto = self.request.query_params.get('nombre_proyecto')
        radicado = self.request.query_params.get('radicado')
        expediente = self.request.query_params.get('expediente')
        persona_titular = self.request.query_params.get('persona_titular')

        
        if radicado:
            # Filtrar por el radicado en la tabla T262Radicados con flexibilidad
            if '-' in radicado:
                try:
                    prefijo, agno, numero = radicado.split('-')
                    numero = numero.lstrip('0')
                except ValueError:
                    # Si no se puede dividir en prefijo, año y número, continuar sin filtrar por radicado
                    pass
                else:
                    queryset = queryset.filter(
                        id_radicado__prefijo_radicado__icontains=prefijo,
                        id_radicado__agno_radicado__icontains=agno,
                        id_radicado__nro_radicado__icontains=numero
                    )
            else:
                # Si no hay guion ('-'), buscar en cualquier parte del radicado
                queryset = queryset.filter(
                    Q(id_radicado__prefijo_radicado__icontains=radicado) |
                    Q(id_radicado__agno_radicado__icontains=radicado) |
                    Q(id_radicado__nro_radicado__icontains=radicado)
                )

        if nombre_proyecto:
            queryset = queryset.filter(nombre_proyecto__icontains=nombre_proyecto)

        if expediente:
            # Filtrar por el radicado en la tabla T262Radicados con flexibilidad
            if '-' in expediente:
                try:
                    serie_subserie, agno, consecutivo = expediente.split('-')
                except ValueError:
                    # Si no se puede dividir en prefijo, año y número, continuar sin filtrar por radicado
                    pass
                else:
                    queryset = queryset.filter(
                        id_expediente__codigo_exp_und_serie_subserie__icontains=serie_subserie,
                        id_expediente__codigo_exp_Agno__icontains=agno,
                        id_expediente__codigo_exp_consec_por_agno__icontains=consecutivo
                    )
            else:
                # Si no hay guion ('-'), buscar en cualquier parte del radicado
                queryset = queryset.filter(
                    Q(id_expediente__codigo_exp_und_serie_subserie__icontains=serie_subserie) |
                    Q(id_expediente__codigo_exp_Agno__icontains=agno) |
                    Q(id_expediente__codigo_exp_consec_por_agno__icontains=consecutivo)
                )

        if persona_titular:
            queryset = queryset.filter(id_persona_titular=persona_titular)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class TipoActosAdministrativos(generics.ListAPIView):
    serializer_class = TiposActosAdministrativosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset =  TiposActosAdministrativos.objects.all()  
        
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    

class ActosAdministrativosGet(generics.ListAPIView):
    serializer_class = ActosAdministrativosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset =  ActosAdministrativos.objects.all()
        
        nro_acto = self.request.query_params.get('nro_acto')
        fecha_acto = self.request.query_params.get('fecha_acto')
        tipo_acto = self.request.query_params.get('tipo_acto')

        # if nro_acto:
        #     queryset = queryset.filter(numero_acto_administrativo__icontains=nro_acto)
        
        if fecha_acto:
            queryset = queryset.filter(fecha_acto_administrativo=fecha_acto)
        
        if tipo_acto:
            queryset = queryset.filter(id_tipo_acto_administrativo=tipo_acto)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    

class UpdateAsignacionNotificacion(generics.UpdateAPIView):
    serializer_class = AsignacionNotiCorresCreateSerializer
    permission_classes = [IsAuthenticated, PermisoActualizarAutorizarAsignaciones]

    def put(self, request, pk):

        asignacion = get_object_or_404(AsignacionNotificacionCorrespondencia, id_notificacion_correspondencia=pk, cod_estado_asignacion='Pe')

        notificacion = get_object_or_404(NotificacionesCorrespondencia, id_notificacion_correspondencia=asignacion.id_notificacion_correspondencia.id_notificacion_correspondencia)
        
        justificacion_rechazo = request.data.get('justificacion_rechazo')
        flag = request.data.get('flag')

        if flag:
            asignacion.cod_estado_asignacion = 'Ac'
            asignacion.fecha_eleccion_estado = timezone.now()
            asignacion.save()
            serializer = self.get_serializer(asignacion)
            data = serializer.data

            notificacion.cod_estado_asignacion = 'Ac'
            notificacion.fecha_eleccion_estado = timezone.now()
            notificacion.cod_estado = 'EG'
            notificacion.save()

            return Response({'succes': True, 'detail': 'La asignación se actualizo.', 'data': data}, status=status.HTTP_200_OK)
        else:
            if justificacion_rechazo:
                asignacion.cod_estado_asignacion = 'Re'
                asignacion.fecha_eleccion_estado = timezone.now()
                asignacion.justificacion_rechazo = justificacion_rechazo
                asignacion.save()
                serializer = self.get_serializer(asignacion)
                data = serializer.data

                notificacion.cod_estado_asignacion = 'Re'
                notificacion.fecha_eleccion_estado = timezone.now()
                notificacion.justificacion_rechazo_asignacion = justificacion_rechazo
                notificacion.cod_estado = 'DE'
                notificacion.save()

                return Response({'succes': True, 'detail': 'La asignación se actualizo.', 'data': data}, status=status.HTTP_200_OK)
            else:
                return Response({'succes': False, 'detail': 'justificacion_rechazo es un parametro requerido.'}, status=status.HTTP_400_BAD_REQUEST)


class RechazoNotificacionCorrespondencia(generics.UpdateAPIView):
    serializer_class = NotificacionesCorrespondenciaCreateSerializer
    permission_classes = [IsAuthenticated, PermisoActualizarRechazarNotificaciones]

    def put(self, request, pk):

        notificacion = get_object_or_404(NotificacionesCorrespondencia, id_notificacion_correspondencia=pk)
        
        justificacion_rechazo = request.data.get('justificacion_rechazo')

        if justificacion_rechazo:
            notificacion.cod_estado = 'DE'
            notificacion.fecha_devolucion = timezone.now()
            notificacion.justificacion_rechazo = justificacion_rechazo
            notificacion.save()
            serializer = self.get_serializer(notificacion)
            data = serializer.data

            return Response({'succes': True, 'detail': 'La notificación se devolvio correctamente.', 'data': data}, status=status.HTTP_200_OK)
        else:
            return Response({'succes': False, 'detail': 'justificacion_rechazo es un parametro requerido.'}, status=status.HTTP_400_BAD_REQUEST)

      
class UpdateAsignacionTarea(generics.UpdateAPIView):
    serializer_class = AsignacionNotiCorresCreateSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):

        asignacion = get_object_or_404(AsignacionNotificacionCorrespondencia, id_orden_notificacion=pk, cod_estado_asignacion='Pe')

        tarea = get_object_or_404(Registros_NotificacionesCorrespondecia, id_registro_notificacion_correspondencia=asignacion.id_orden_notificacion.id_registro_notificacion_correspondencia)
        
        justificacion_rechazo = request.data.get('justificacion_rechazo')
        flag = request.data.get('flag')
        fecha_actual = timezone.now()

        if flag:
            asignacion.cod_estado_asignacion = 'Ac'
            asignacion.fecha_eleccion_estado = fecha_actual
            asignacion.save()
            serializer = self.get_serializer(asignacion)
            data = serializer.data

            tarea.cod_estado_asignacion = 'Ac'
            tarea.fecha_eleccion_estado = fecha_actual
            tarea.cod_estado = 'EG'
            tarea.save()

            return Response({'succes': True, 'detail': 'La asignación se actualizo.', 'data': data}, status=status.HTTP_200_OK)
        else:
            if justificacion_rechazo:
                asignacion.cod_estado_asignacion = 'Re'
                asignacion.fecha_eleccion_estado = fecha_actual
                asignacion.justificacion_rechazo = justificacion_rechazo
                asignacion.save()
                serializer = self.get_serializer(asignacion)
                data = serializer.data

                tarea.cod_estado_asignacion = 'Re'
                tarea.fecha_eleccion_estado = fecha_actual
                tarea.justificacion_rechazo_asignacion = justificacion_rechazo
                tarea.cod_estado = 'DE'
                tarea.save()

                return Response({'succes': True, 'detail': 'La asignación se actualizo.', 'data': data}, status=status.HTTP_200_OK)
            else:
                return Response({'succes': False, 'detail': 'justificacion_rechazo es un parametro requerido.'}, status=status.HTTP_400_BAD_REQUEST)


class CancelarAsignacionNotificacion(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        queryset = AsignacionNotificacionCorrespondencia.objects.filter(id_notificacion_correspondencia=pk, cod_estado_asignacion='Pe').first()
        if not queryset:
            raise ValidationError(f'La asignación de la notificación con id {pk} no existe.')
        else:
            notificacion = get_object_or_404(NotificacionesCorrespondencia, id_notificacion_correspondencia=pk)
            notificacion.id_persona_asignada = None
            notificacion.id_persona_asigna = None
            notificacion.fecha_eleccion_estado = None
            notificacion.cod_estado_asignacion = None
            notificacion.save()
            queryset.delete()
            return Response({'succes': True, 'detail':'Se canceló la asignación de la notificación correctamente'}, status=status.HTTP_200_OK)


class CancelarAsignacionTarea(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        queryset = AsignacionNotificacionCorrespondencia.objects.filter(id_orden_notificacion=pk, cod_estado_asignacion='Pe').first()
        if not queryset:
            raise ValidationError(f'La asignación de la tarea con id {pk} no existe.')
        else:
            tarea = Registros_NotificacionesCorrespondecia.objects.filter(id_registro_notificacion_correspondencia=pk).first()
            tarea.delete()
            queryset.delete()
            return Response({'succes': True, 'detail':'Se canceló la asignación de la notificación correctamente'}, status=status.HTTP_200_OK)
        

## Endpoints para la gaceta

class DatosNotificacionGacetaGet(generics.RetrieveAPIView):
    serializer_class = RegistroNotificacionesCorrespondenciaPaginasSerializer
    permission_classes = [IsAuthenticated]

    def get_registro_notificacion(self, id_registro_notificacion):
        notificacion = Registros_NotificacionesCorrespondecia.objects.filter(id_registro_notificacion_correspondencia=id_registro_notificacion).first()
        if not notificacion:
            raise ValidationError(f'El registro de la notificacion con id {id_registro_notificacion} no existe.')
        return notificacion
    
    def get(self, request, id_registro_notificacion):
        registro_notificacion = self.get_registro_notificacion(id_registro_notificacion)
        serializer = self.serializer_class(registro_notificacion)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class AnexosNotificacionGacetaGet(generics.ListAPIView):
    serializer_class = AnexosNotificacionesCorrespondenciaDatosSerializer
    permission_classes = [IsAuthenticated]

    def get_anexos(self, id_registro_notificacion):

        try:
            notificacion = Registros_NotificacionesCorrespondecia.objects.get(id_registro_notificacion_correspondencia=id_registro_notificacion)
        except Registros_NotificacionesCorrespondecia.DoesNotExist:
            raise ValidationError('El registro de la notificación no existe.')
        
        anexos = Anexos_NotificacionesCorrespondencia.objects.filter(id_notificacion_correspondecia=notificacion.id_notificacion_correspondencia, id_registro_notificacion__isnull=True)
        return anexos

    def get(self, request, id_registro_notificacion):
        anexos = self.get_anexos(id_registro_notificacion)
        serializer = self.serializer_class(anexos, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)

class AnexosNotificacionRegistroGet(generics.ListAPIView):
    serializer_class = AnexosNotificacionesCorrespondenciaDatosSerializer
    permission_classes = [IsAuthenticated]

    def get_anexos(self, id_registro_notificacion):

        try:
            notificacion = Registros_NotificacionesCorrespondecia.objects.get(id_registro_notificacion_correspondencia=id_registro_notificacion)
        except Registros_NotificacionesCorrespondecia.DoesNotExist:
            raise ValidationError('El registro de la notificación no existe.')
        
        anexos = Anexos_NotificacionesCorrespondencia.objects.filter(id_notificacion_correspondecia=notificacion.id_notificacion_correspondencia, id_registro_notificacion=notificacion.id_registro_notificacion_correspondencia)
        return anexos

    def get(self, request, id_registro_notificacion):
        anexos = self.get_anexos(id_registro_notificacion)
        serializer = self.serializer_class(anexos, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class TipoAnexosSoporteGacetaGet(generics.ListAPIView):
    serializer_class = TiposAnexosSoporteSerializer
    permission_classes = [IsAuthenticated]

    def get_tipos_anexos(self, id_tipo_notificacion):
        try:
            tipo_notificacion = TiposNotificacionesCorrespondencia.objects.get(id_tipo_notificacion_correspondencia=id_tipo_notificacion)
        except TiposNotificacionesCorrespondencia.DoesNotExist:
            raise ValidationError('El tipo de notificación no existe.')
        
        tipos_anexos = TiposAnexosSoporte.objects.filter(id_tipo_notificacion_correspondencia=tipo_notificacion.id_tipo_notificacion_correspondencia, activo=True) 
        return tipos_anexos

    def get(self, request, id_tipo_notificacion):
        tipos_anexos = self.get_tipos_anexos(id_tipo_notificacion)
        serializer = self.serializer_class(tipos_anexos, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class CausasOAnomaliasGacetaGet(generics.ListAPIView):
    serializer_class = CausasOAnomaliasSerializer
    permission_classes = [IsAuthenticated]

    def get_causas_o_anomalias(self, id_tipo_notificacion):
        try:
            tipo_notificacion = TiposNotificacionesCorrespondencia.objects.get(id_tipo_notificacion_correspondencia=id_tipo_notificacion)
        except TiposNotificacionesCorrespondencia.DoesNotExist:
            raise ValidationError('El tipo de notificación no existe.')
        
        causas_o_anomalias = CausasOAnomalias.objects.filter(id_tipo_notificacion_correspondencia=tipo_notificacion.id_tipo_notificacion_correspondencia, activo=True) 
        return causas_o_anomalias

    def get(self, request, id_tipo_notificacion):
        causas_o_anomalias = self.get_causas_o_anomalias(id_tipo_notificacion)
        serializer = self.serializer_class(causas_o_anomalias, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class AnexosSoporteCreate(generics.CreateAPIView):
    serializer_class = AnexosPostSerializer

    @transaction.atomic
    def create_anexos_notificaciones(self, anexos, id_registro_notificacion, fecha_actual, id_persona_recibe_solicitud):

        nombres_anexos = [anexo['nombre_anexo'] for anexo in anexos]
        # Validar que no haya valores repetidos
        if len(nombres_anexos) != len(set(nombres_anexos)):
            raise ValidationError("error': 'No se permiten nombres de anexos repetidos.")
        
        try:
            registro_notificacion = Registros_NotificacionesCorrespondecia.objects.get(id_registro_notificacion_correspondencia=id_registro_notificacion)
        except Registros_NotificacionesCorrespondecia.DoesNotExist:
            raise ValidationError('El registro de la notificación no existe.')
         
        for anexo in anexos:

            data_anexo = self.crear_anexo(anexo)

            data_anexo_soporte = {}
            data_anexo_soporte['id_notificacion_correspondecia'] = registro_notificacion.id_notificacion_correspondencia.id_notificacion_correspondencia
            data_anexo_soporte['id_registro_notificacion'] = registro_notificacion.id_registro_notificacion_correspondencia
            data_anexo_soporte['id_acto_administrativo'] = None
            data_anexo_soporte['doc_entrada_salida'] = 'EN'
            if anexo['uso_del_documento']:
                data_anexo_soporte['uso_del_documento'] = 'IN'
            else:
                data_anexo_soporte['uso_del_documento'] = 'PU'
            if anexo['id_tipo_anexo_soporte']:
                try:
                    tipo_documento = TiposAnexosSoporte.objects.get(id_tipo_anexo_soporte=anexo['id_tipo_anexo_soporte'])
                except TiposAnexosSoporte.DoesNotExist:
                    raise ValidationError(f'El tipo de documento con id {anexo["id_tipo_anexo_soporte"]} no existe.')
                data_anexo_soporte['cod_tipo_documento'] = tipo_documento.id_tipo_anexo_soporte
            
            data_anexo_soporte['doc_generado'] = 'SI'
            data_anexo_soporte['id_persona_anexa_documento'] = id_persona_recibe_solicitud.id_persona
            data_anexo_soporte['fecha_anexo'] = fecha_actual
            if anexo['id_causa_o_anomalia'] is not None:
                try:
                    causa_o_anomalia = CausasOAnomalias.objects.get(id_causa_o_anomalia=anexo['id_causa_o_anomalia'])
                except CausasOAnomalias.DoesNotExist:
                    raise ValidationError(f'La causa o anomalia con id {anexo["id_causa_o_anomalia"]} no existe.')
                data_anexo_soporte['id_causa_o_anomalia'] = causa_o_anomalia.id_causa_o_anomalia
            else:
                data_anexo_soporte['id_causa_o_anomalia'] = None
            data_anexo_soporte['link_publicacion'] = anexo['link_publicacion']
            data_anexo_soporte['observaciones'] = anexo['observaciones']
            if 'usuario_notificado' in data_anexo:
                data_anexo_soporte['usuario_notificado'] = data_anexo['usuario_notificado']
            else:
                data_anexo_soporte['usuario_notificado'] = False     
            data_anexo_soporte['id_anexo'] = data_anexo['id_anexo']
            
            anexosNotificacionCreate = AnexoNotificacionesCreate()
            anexosNotificacionCreate.crear_anexo_notificacion(data_anexo_soporte)

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

        return True

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
            'ruta': ruta
        }
        
        archivos_Digitales = ArchivosDgitalesCreate()
        archivo_creado = archivos_Digitales.crear_archivo(data_archivo, uploaded_file)
        return archivo_creado

class AnexosSoporteGacetaCreate(generics.CreateAPIView):
    serializer_class = AnexosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated, PermisoCrearPublicarGacetaAmbiental]

    def create_anexo(self, data):
        try:
            notificacion = NotificacionesCorrespondencia.objects.get(id_notificacion_correspondencia=data.get('id_notificacion_correspondencia'))
        except NotificacionesCorrespondencia.DoesNotExist:
            raise ValidationError('La notificación no existe.')
        
        try:
            tipo_anexo = TiposAnexosSoporte.objects.get(id_tipo_anexo_soporte=data.get('id_tipo_anexo_soporte'))
        except TiposAnexosSoporte.DoesNotExist:
            raise ValidationError('El tipo de anexo no existe.')
        
        try:
            causa = CausasOAnomalias.objects.get(id_causa_o_anomalia=data.get('id_causa_o_anomalia'))
        except CausasOAnomalias.DoesNotExist:
            raise ValidationError('La causa o anomalia no existe.')
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        print(instance)
        return serializer.data

    def post(self, request):
        data = request.data
        anexo = self.create_anexo(data)
        return Response({'succes': True, 'detail':'Se creo el anexo correctamente', 'data':anexo}, status=status.HTTP_201_CREATED)
    

class RegistrosNotificacionesCorrespondenciaGacetaUpdate(generics.UpdateAPIView):
    serializer_class = Registros_NotificacionesCorrespondeciaSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def update_registro_notificacion(self, id_registro_notificacion, request):
        data_total = request.data
        data = json.loads(data_total.get('data'))
        try:
            registro_notificacion = Registros_NotificacionesCorrespondecia.objects.get(id_registro_notificacion_correspondencia=id_registro_notificacion)
        except Registros_NotificacionesCorrespondecia.DoesNotExist:
            raise ValidationError('El registro de la notificación no existe.')
        
        fecha_actual = timezone.now()
        persona_anexa = request.user.persona
        util_PQR = Util_PQR()
        anexos = util_PQR.set_archivo_in_anexo(data['anexos'], request.FILES, "create")
        valores_creados_detalles = None
        cant_anexos = 0
        numero_folios = 0
        
        if anexos:
            anexosCreate = AnexosSoporteCreate()
            valores_creados_detalles = anexosCreate.create_anexos_notificaciones(anexos, registro_notificacion.id_registro_notificacion_correspondencia, fecha_actual, persona_anexa)

        if valores_creados_detalles:
            cant_anexos = len(anexos)
            for anexo in anexos:
                if anexo['numero_folios']:
                    numero_folios += anexo['numero_folios']
            print(valores_creados_detalles)

        

        registro_notificacion.nro_folios_totales += numero_folios
        registro_notificacion.cantidad_anexos += cant_anexos
        registro_notificacion.save()
        

        serializer = self.serializer_class(registro_notificacion, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return serializer.data

    def put(self, request, id_registro_notificacion):
        registro = self.update_registro_notificacion(id_registro_notificacion, request)
        return Response({'succes': True, 'detail':'Se actualizó el registro correctamente', 'data':registro}, status=status.HTTP_200_OK)


## Endpoints para la pagina edictos

class DatosNotificacionEdictosGet(generics.RetrieveAPIView):
    serializer_class = RegistroNotificacionesCorrespondenciaPaginasSerializer
    permission_classes = [IsAuthenticated]

    def get_registro_notificacion(self, id_registro_notificacion):
        notificacion = Registros_NotificacionesCorrespondecia.objects.filter(id_registro_notificacion_correspondencia=id_registro_notificacion).first()
        if not notificacion:
            raise ValidationError(f'El registro de la notificacion con id {id_registro_notificacion} no existe.')
        return notificacion
    
    def get(self, request, id_registro_notificacion):
        registro_notificacion = self.get_registro_notificacion(id_registro_notificacion)
        serializer = self.serializer_class(registro_notificacion)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class AnexosNotificacionEdictosGet(generics.ListAPIView):
    serializer_class = AnexosNotificacionesCorrespondenciaDatosSerializer
    permission_classes = [IsAuthenticated]

    def get_anexos(self, id_registro_notificacion):

        try:
            notificacion = Registros_NotificacionesCorrespondecia.objects.get(id_registro_notificacion_correspondencia=id_registro_notificacion)
        except Registros_NotificacionesCorrespondecia.DoesNotExist:
            raise ValidationError('El registro de la notificación no existe.')
        
        anexos = Anexos_NotificacionesCorrespondencia.objects.filter(id_notificacion_correspondecia=notificacion.id_notificacion_correspondencia)
        return anexos

    def get(self, request, id_registro_notificacion):
        anexos = self.get_anexos(id_registro_notificacion)
        serializer = self.serializer_class(anexos, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class AnexosSoporteEdictosCreate(generics.CreateAPIView):
    serializer_class = AnexosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        instancia_anexos = AnexosSoporteGacetaCreate()
        anexo = instancia_anexos.create_anexo(data)
        return Response({'succes': True, 'detail':'Se creo el anexo correctamente', 'data':anexo}, status=status.HTTP_201_CREATED)
    

class RegistrosNotificacionesCorrespondenciaEdictosUpdate(generics.CreateAPIView):
    serializer_class = Registros_NotificacionesCorrespondeciaSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, id_registro_notificacion):
        instancia_registro = RegistrosNotificacionesCorrespondenciaGacetaUpdate()
        registro = instancia_registro.update_registro_notificacion(id_registro_notificacion, request)
        return Response({'succes': True, 'detail':'Se creo el registro correctamente', 'data':registro}, status=status.HTTP_201_CREATED)

## Endpoints para la correo electronico

class DatosNotificacionCorreoGet(generics.RetrieveAPIView):
    serializer_class = RegistroNotificacionesCorrespondenciaPaginasSerializer
    permission_classes = [IsAuthenticated]

    def get_registro_notificacion(self, id_registro_notificacion):
        notificacion = Registros_NotificacionesCorrespondecia.objects.filter(id_registro_notificacion_correspondencia=id_registro_notificacion).first()
        if not notificacion:
            raise ValidationError(f'El registro de la notificacion con id {id_registro_notificacion} no existe.')
        return notificacion
    
    def get(self, request, id_registro_notificacion):
        registro_notificacion = self.get_registro_notificacion(id_registro_notificacion)
        serializer = self.serializer_class(registro_notificacion)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class DatosTitularesCorreoGet(generics.ListAPIView):
    serializer_class = DatosTitularesCorreoSerializer
    permission_classes = [IsAuthenticated]

    def get_titular(self, id_notificacion):
        try:
            notificacion = NotificacionesCorrespondencia.objects.get(id_notificacion_correspondencia=id_notificacion)
        except NotificacionesCorrespondencia.DoesNotExist:
            raise ValidationError('La notificación no existe.')
        
        if notificacion.id_persona_titular:
            persona = Personas.objects.filter(id_persona=notificacion.id_persona_titular.id_persona).first()
        else:
            persona = None
        
        
        return persona

    def get(self, request, id_notificacion):
        titular = self.get_titular(id_notificacion)
        serializer = self.serializer_class(titular, many=False)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class AnexosNotificacionCorreoGet(generics.ListAPIView):
    serializer_class = AnexosNotificacionesCorrespondenciaDatosSerializer
    permission_classes = [IsAuthenticated]

    def get_anexos(self, id_registro_notificacion):

        try:
            notificacion = Registros_NotificacionesCorrespondecia.objects.get(id_registro_notificacion_correspondencia=id_registro_notificacion)
        except Registros_NotificacionesCorrespondecia.DoesNotExist:
            raise ValidationError('El registro de la notificación no existe.')
        
        anexos = Anexos_NotificacionesCorrespondencia.objects.filter(id_notificacion_correspondecia=notificacion.id_notificacion_correspondencia)
        return anexos

    def get(self, request, id_registro_notificacion):
        anexos = self.get_anexos(id_registro_notificacion)
        serializer = self.serializer_class(anexos, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class AnexosSoporteCorreoCreate(generics.CreateAPIView):
    serializer_class = AnexosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        instancia_anexos = AnexosSoporteGacetaCreate()
        anexo = instancia_anexos.create_anexo(data)
        return Response({'succes': True, 'detail':'Se creo el anexo correctamente', 'data':anexo}, status=status.HTTP_201_CREATED)
    

class RegistrosNotificacionesCorrespondenciaCorreoUpdate(generics.CreateAPIView):
    serializer_class = Registros_NotificacionesCorrespondeciaSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, id_registro_notificacion):
        # data = request.data
        instancia_registro = RegistrosNotificacionesCorrespondenciaGacetaUpdate()
        registro = instancia_registro.update_registro_notificacion(id_registro_notificacion, request)
        return Response({'succes': True, 'detail':'Se creo el registro correctamente', 'data':registro}, status=status.HTTP_201_CREATED)

## Endpoints para la pagina avisos

class DatosNotificacionAvisosGet(generics.RetrieveAPIView):
    serializer_class = RegistroNotificacionesCorrespondenciaPaginasSerializer
    permission_classes = [IsAuthenticated]

    def get_registro_notificacion(self, id_registro_notificacion):
        notificacion = Registros_NotificacionesCorrespondecia.objects.filter(id_registro_notificacion_correspondencia=id_registro_notificacion).first()
        if not notificacion:
            raise ValidationError(f'El registro de la notificacion con id {id_registro_notificacion} no existe.')
        return notificacion
    
    def get(self, request, id_registro_notificacion):
        registro_notificacion = self.get_registro_notificacion(id_registro_notificacion)
        serializer = self.serializer_class(registro_notificacion)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class AnexosNotificacionAvisosGet(generics.ListAPIView):
    serializer_class = AnexosNotificacionesCorrespondenciaDatosSerializer
    permission_classes = [IsAuthenticated]

    def get_anexos(self, id_registro_notificacion):

        try:
            notificacion = Registros_NotificacionesCorrespondecia.objects.get(id_registro_notificacion_correspondencia=id_registro_notificacion)
        except Registros_NotificacionesCorrespondecia.DoesNotExist:
            raise ValidationError('El registro de la notificación no existe.')
        
        anexos = Anexos_NotificacionesCorrespondencia.objects.filter(id_notificacion_correspondecia=notificacion.id_notificacion_correspondencia)
        return anexos

    def get(self, request, id_registro_notificacion):
        anexos = self.get_anexos(id_registro_notificacion)
        serializer = self.serializer_class(anexos, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class AnexosSoporteAvisosCreate(generics.CreateAPIView):
    serializer_class = AnexosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        instancia_anexos = AnexosSoporteGacetaCreate()
        anexo = instancia_anexos.create_anexo(data)
        return Response({'succes': True, 'detail':'Se creo el anexo correctamente', 'data':anexo}, status=status.HTTP_201_CREATED)
    

class RegistrosNotificacionesCorrespondenciaAvisosUpdate(generics.CreateAPIView):
    serializer_class = Registros_NotificacionesCorrespondeciaSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, id_registro_notificacion):
        # data = request.data
        instancia_registro = RegistrosNotificacionesCorrespondenciaGacetaUpdate()
        registro = instancia_registro.update_registro_notificacion(id_registro_notificacion, request)
        return Response({'succes': True, 'detail':'Se creo el registro correctamente', 'data':registro}, status=status.HTTP_201_CREATED)

## Endpoints para la pagina personal

class DatosNotificacionPersonalGet(generics.RetrieveAPIView):
    serializer_class = RegistroNotificacionesCorrespondenciaPaginasSerializer
    permission_classes = [IsAuthenticated]

    def get_registro_notificacion(self, id_registro_notificacion):
        notificacion = Registros_NotificacionesCorrespondecia.objects.filter(id_registro_notificacion_correspondencia=id_registro_notificacion).first()
        if not notificacion:
            raise ValidationError(f'El registro de la notificacion con id {id_registro_notificacion} no existe.')
        return notificacion
    
    def get(self, request, id_registro_notificacion):
        registro_notificacion = self.get_registro_notificacion(id_registro_notificacion)
        serializer = self.serializer_class(registro_notificacion)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class AnexosNotificacionPersonalGet(generics.ListAPIView):
    serializer_class = AnexosNotificacionesCorrespondenciaDatosSerializer
    permission_classes = [IsAuthenticated]

    def get_anexos(self, id_registro_notificacion):

        try:
            notificacion = Registros_NotificacionesCorrespondecia.objects.get(id_registro_notificacion_correspondencia=id_registro_notificacion)
        except Registros_NotificacionesCorrespondecia.DoesNotExist:
            raise ValidationError('El registro de la notificación no existe.')
        
        anexos = Anexos_NotificacionesCorrespondencia.objects.filter(id_notificacion_correspondecia=notificacion.id_notificacion_correspondencia)
        return anexos

    def get(self, request, id_registro_notificacion):
        anexos = self.get_anexos(id_registro_notificacion)
        serializer = self.serializer_class(anexos, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class AnexosSoportePersonalCreate(generics.CreateAPIView):
    serializer_class = AnexosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        instancia_anexos = AnexosSoporteGacetaCreate()
        anexo = instancia_anexos.create_anexo(data)
        return Response({'succes': True, 'detail':'Se creo el anexo correctamente', 'data':anexo}, status=status.HTTP_201_CREATED)
    

class RegistrosNotificacionesCorrespondenciaPersonalUpdate(generics.CreateAPIView):
    serializer_class = Registros_NotificacionesCorrespondeciaSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, id_registro_notificacion):
        # data = request.data
        instancia_registro = RegistrosNotificacionesCorrespondenciaGacetaUpdate()
        registro = instancia_registro.update_registro_notificacion(id_registro_notificacion, request)
        return Response({'succes': True, 'detail':'Se creo el registro correctamente', 'data':registro}, status=status.HTTP_201_CREATED)


## Endpoints para la correspondencia fisica

class DatosNotificacionCorrespondenciaGet(generics.RetrieveAPIView):
    serializer_class = RegistroNotificacionesCorrespondenciaPaginasSerializer
    permission_classes = [IsAuthenticated]

    def get_registro_notificacion(self, id_registro_notificacion):
        notificacion = Registros_NotificacionesCorrespondecia.objects.filter(id_registro_notificacion_correspondencia=id_registro_notificacion).first()
        if not notificacion:
            raise ValidationError(f'El registro de la notificacion con id {id_registro_notificacion} no existe.')
        return notificacion
    
    def get(self, request, id_registro_notificacion):
        registro_notificacion = self.get_registro_notificacion(id_registro_notificacion)
        serializer = self.serializer_class(registro_notificacion)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class DatosTitularesCorrespondenciaGet(generics.ListAPIView):
    serializer_class = DatosTitularesCorreoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Personas.objects.all()
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class AnexosNotificacionCorrespondenciaGet(generics.ListAPIView):
    serializer_class = AnexosNotificacionesCorrespondenciaDatosSerializer
    permission_classes = [IsAuthenticated]

    def get_anexos(self, id_registro_notificacion):

        try:
            notificacion = Registros_NotificacionesCorrespondecia.objects.get(id_registro_notificacion_correspondencia=id_registro_notificacion)
        except Registros_NotificacionesCorrespondecia.DoesNotExist:
            raise ValidationError('El registro de la notificación no existe.')
        
        anexos = Anexos_NotificacionesCorrespondencia.objects.filter(id_notificacion_correspondecia=notificacion.id_notificacion_correspondencia)
        return anexos

    def get(self, request, id_registro_notificacion):
        anexos = self.get_anexos(id_registro_notificacion)
        serializer = self.serializer_class(anexos, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class AnexosSoporteCorrespondenciaCreate(generics.CreateAPIView):
    serializer_class = AnexosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        instancia_anexos = AnexosSoporteGacetaCreate()
        anexo = instancia_anexos.create_anexo(data)
        return Response({'succes': True, 'detail':'Se creo el anexo correctamente', 'data':anexo}, status=status.HTTP_201_CREATED)
    

class RegistrosNotificacionesCorrespondenciaCorrespondenciaUpdate(generics.CreateAPIView):
    serializer_class = Registros_NotificacionesCorrespondeciaSerializer
    permission_classes = [IsAuthenticated, PermisoCrearAsignacionTareasNotificaciones]

    def put(self, request, id_registro_notificacion):
        # data = request.data
        instancia_registro = RegistrosNotificacionesCorrespondenciaGacetaUpdate()
        registro = instancia_registro.update_registro_notificacion(id_registro_notificacion, request)
        return Response({'succes': True, 'detail':'Se creo el registro correctamente', 'data':registro}, status=status.HTTP_201_CREATED)


# class RegistrosNotificacionesCorrespondenciaCorrespondenciaUpdate(generics.UpdateAPIView):
#     serializer_class = Registros_NotificacionesCorrespondeciaCreateSerializer
#     permission_classes = [IsAuthenticated]

#     def put(self, request, pk):
#         data = request.data
#         estado = EstadosNotificacionesCorrespondencia.objects.filter(id_estado_notificacion_correspondencia=data.get('id_estado_actual_registro')).first()
#         if not estado:
#             raise ValidationError(f'El estado de la notificación con id {data.get("id_estado_actual_registro")} no existe.')
#         registro_notificacion = get_object_or_404(Registros_NotificacionesCorrespondecia, id_registro_notificacion_correspondencia=pk)
#         if not registro_notificacion:
#             raise ValidationError(f'El registro de la notificación con id {pk} no existe.')
#         else:
#             registro_notificacion.id_estado_actual_registro = estado
#             registro_notificacion.save()
#             serializer = self.get_serializer(registro_notificacion)

#         return Response({'succes': True, 'detail':'Se actualizó el registro de la notificación correctamente', 'data':{**serializer.data}}, status=status.HTTP_200_OK)
    
## Generador de Constancias

class DocumentosConstanciaNotificacionCreate(generics.CreateAPIView):
    serializer_class = DocumentosDeArchivoExpedienteSerializer
    permission_classes = [IsAuthenticated]

    def create_documento(self, data):
        try:
            tipo_documento = TiposDocumentos.objects.get(id_tipo_documento=data.get('id_tipo_documento'))
        except TiposDocumentos.DoesNotExist:
            raise ValidationError('El tipo de documento no existe.')
        
        try:
            notificacion = NotificacionesCorrespondencia.objects.get(id_notificacion_correspondencia=data.get('id_notificacion_correspondencia'))
        except NotificacionesCorrespondencia.DoesNotExist:
            raise ValidationError('La notificación no existe.')
        
        try:
            persona = Personas.objects.get(id_persona=data.get('id_persona'))
        except Personas.DoesNotExist:
            raise ValidationError('La persona no existe.')
        
        try:
            expediente = ExpedientesDocumentales.objects.get(id_expediente=data.get('id_expediente'))
        except ExpedientesDocumentales.DoesNotExist:
            raise ValidationError('El expediente no existe.')
        
        try:
            tipo_acto = TiposActosAdministrativos.objects.get(id_tipo_acto_administrativo=data.get('id_tipo_acto_administrativo'))
        except TiposActosAdministrativos.DoesNotExist:
            raise ValidationError('El tipo de acto administrativo no existe.')
        
        try:
            acto_administrativo = ActosAdministrativos.objects.get(id_acto_administrativo=data.get('id_acto_administrativo'))
        except ActosAdministrativos.DoesNotExist:
            raise ValidationError('El acto administrativo no existe.')
        
        try:
            causa = CausasOAnomalias.objects.get(id_causa_o_anomalia=data.get('id_causa_o_anomalia'))
        except CausasOAnomalias.DoesNotExist:
            raise ValidationError('La causa o anomalia no existe.')
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return serializer.data


class GenerarConstanciaNotificacion(generics.CreateAPIView):
    serializer_class = ConstanciaNotificacionSerializer
    permission_classes = [IsAuthenticated]

    def create_constancia(self, data):
        instacia_archivo = DocumentosConstanciaNotificacionCreate()

        # documento_de_archivo_exped = {
        #     'identificacion_doc_en_expediente': identificacion_doc_en_expediente,
        #     'nombre_asignado_documento': nombre_asignado_documento,
        #     'nombre_original_del_archivo': nombre_original_del_archivo,
        #     'fecha_creacion_doc': fecha_creacion_doc,
        #     'fecha_incorporacion_doc_a_Exp': fecha_incorporacion_doc_a_Exp,
        #     'descripcion': descripcion,
        #     'asunto': asunto,
        #     'id_persona_titular': id_persona_titular,
        #     'cod_categoria_archivo': cod_categoria_archivo,
        #     'es_version_original': es_version_original,
        #     'tiene_replica_fisica': tiene_replica_fisica,
        #     'nro_folios_del_doc': nro_folios_del_doc,
        #     'cod_origen_archivo': cod_origen_archivo,
        #     'orden_en_expediente': orden_en_expediente,
        #     'id_tipologia_documental': id_tipologia_documental,
        #     'codigo_tipologia_doc_prefijo': codigo_tipologia_doc_prefijo,
        #     'codigo_tipologia_doc_agno': codigo_tipologia_doc_agno,
        #     'codigo_tipologia_doc_consecutivo': codigo_tipologia_doc_consecutivo,
        #     'es_un_archivo_anexo': es_un_archivo_anexo,
        #     'id_doc_de_arch_del_cual_es_anexo': id_doc_de_arch_del_cual_es_anexo,
        #     'tipologia_no_creada_trd': tipologia_no_creada_trd,
        #     'anexo_corresp_a_lista_chequeo': anexo_corresp_a_lista_chequeo,
        #     'cantidad_anexos': cantidad_anexos,
        #     'id_archivo_sistema': id_archivo_sistema,
        #     'palabras_clave_documento': palabras_clave_documento,
        #     'sub_sistema_incorporacion': sub_sistema_incorporacion,
        #     'cod_tipo_radicado': cod_tipo_radicado,
        #     'codigo_radicado_prefijo': codigo_radicado_prefijo,
        #     'codigo_radicado_agno': codigo_radicado_agno,
        #     'codigo_radicado_consecutivo': codigo_radicado_consecutivo,
        #     'es_radicado_inicial_de_solicitud': es_radicado_inicial_de_solicitud,
        #     'documento_requiere_rta': documento_requiere_rta,
        #     'creado_automaticamente': creado_automaticamente,
        #     'fecha_indexacion_manual_sistema': fecha_indexacion_manual_sistema,
        #     'anulado': anulado,
        #     'observacion_anulacion': observacion_anulacion,
        #     'fecha_anulacion': fecha_anulacion,
        #     'id_persona_anula': id_persona_anula,
        #     'id_doc_arch_respondido': id_doc_arch_respondido,
        #     'id_doc_arch_rad_ini_exp_simple': id_doc_arch_rad_ini_exp_simple,
        #     'id_und_org_oficina_creadora': id_und_org_oficina_creadora,
        #     'id_persona_que_crea': id_persona_que_crea,
        #     'id_und_org_oficina_respon_actual': id_und_org_oficina_respon_actual
        # }


        archivo = instacia_archivo.create_documento(data)
        return archivo
    
    def get_numero_expesiente_acto(self, id_notificacion):
        try:
            notificacion = NotificacionesCorrespondencia.objects.get(id_notificacion_correspondencia=id_notificacion)
        except NotificacionesCorrespondencia.DoesNotExist:
            raise ValidationError('La notificación no existe.')
        
        if not notificacion.id_expediente_documental or not notificacion.id_acto_administrativo:
            num_expediente = None
            num_acto = None
            return num_expediente, num_acto
        
        num_expediente = notificacion.id_expediente_documental.codigo_exp_und_serie_subserie + '-' + notificacion.id_expediente_documental.codigo_exp_Agno + '-' + notificacion.id_expediente_documental.codigo_exp_consec_por_agno
        num_acto = notificacion.id_acto_administrativo.numero_acto_administrativo
        return num_expediente, num_acto



    def get(self, request, id_registro_notificacion, *args, **kwargs):

        data = request.query_params
        fecha_actual = timezone.now()

        if not data.get('fecha_inicial'):
            raise ValidationError('fecha_inicial es un parametro requerido.')
        
        if not data.get('fecha_final'):
            raise ValidationError('fecha_final es un parametro requerido.')
        
        if not data.get('tipo_notificacion'):
            raise ValidationError('tipo_notificacion es un parametro requerido.')
        
        fecha_inicial = datetime.strptime(data.get('fecha_inicial'), '%Y-%m-%d').date()
        fecha_final = datetime.strptime(data.get('fecha_final'), '%Y-%m-%d').date()
        tipo_notificacion = data.get('tipo_notificacion')

        if fecha_inicial > fecha_final:
            raise ValidationError('La fecha inicial no puede ser mayor a la fecha final.')
        
        if fecha_final > fecha_actual.date():
            raise ValidationError('La fecha final no puede ser mayor a la fecha actual.')

        try:
            registro_notificacion = Registros_NotificacionesCorrespondecia.objects.get(id_registro_notificacion_correspondencia=id_registro_notificacion)
        except Registros_NotificacionesCorrespondecia.DoesNotExist:
            raise ValidationError('El registro de la notificación no existe.')
        
        try:
            notificacion = NotificacionesCorrespondencia.objects.get(id_notificacion_correspondencia=registro_notificacion.id_notificacion_correspondencia.id_notificacion_correspondencia)
        except NotificacionesCorrespondencia.DoesNotExist:
            raise ValidationError('La notificación no existe.')
        
        num_expediente, num_acto = self.get_numero_expesiente_acto(notificacion.id_notificacion_correspondencia)
        
        if notificacion.id_persona_titular is not None:
            persona = Personas.objects.filter(id_persona=notificacion.id_persona_titular.id_persona).first()
            razon_social = persona.razon_social
            nombre_completo = [persona.primer_nombre, persona.segundo_nombre, persona.primer_apellido, persona.segundo_apellido]
            nombre_completo =  ' '.join(filter(None, nombre_completo))
            tipo_documento = persona.tipo_documento.cod_tipo_documento
            numero_documento = persona.numero_documento
        else:
            razon_social = None
            nombre_completo = None
            tipo_documento = None
            numero_documento = None
        
        data_out = {
            'fecha_inicial': fecha_inicial,
            'fecha_final': fecha_final,
            'fecha_dia': fecha_actual.strftime('%d'),
            'fecha_mes': UtilsGestor.get_mes(fecha_actual.strftime('%m')),
            'fecha_agno': fecha_actual.strftime('%Y'),
            'fecha_hora': fecha_actual.strftime('%H:%M'),
            'fecha_am_pm': fecha_actual.strftime('%p'),
            'razon_social': razon_social,
            'nombre_completo': nombre_completo,
            'tipo_documento': tipo_documento,
            'numero_documento': numero_documento,
            'num_expediente': num_expediente,
            'num_acto': num_acto,
            'emitido': notificacion.id_und_org_oficina_solicita.nombre,
        }

        if tipo_notificacion == 'GACETA':
            data_out['tipo_notificacion'] = 'Gaceta Ambiental'
            del data_out['razon_social']
            del data_out['nombre_completo']
            del data_out['tipo_documento']
            del data_out['numero_documento']
            del data_out['num_expediente']
            del data_out['num_acto']
            del data_out['emitido']
            data_out['publicaciones'] = []
            # publicaciones = .objects.filter(fecha_publicacion__range=[fecha_inicial, fecha_final])
            tipo_correspondencia = TiposNotificacionesCorrespondencia.objects.filter(publicar_pagina_gaceta=True)
            
            registros_notificados = Registros_NotificacionesCorrespondecia.objects.filter(fecha_registro__range=[fecha_inicial, fecha_final]).order_by('fecha_registro')
            registros_notificados = registros_notificados.filter(id_tipo_notificacion_correspondencia__in=tipo_correspondencia)    
            for registro in registros_notificados:
                
                notificacion = NotificacionesCorrespondencia.objects.get(id_notificacion_correspondencia=registro.id_notificacion_correspondencia.id_notificacion_correspondencia)
                num_expediente, num_acto = self.get_numero_expesiente_acto(notificacion.id_notificacion_correspondencia)
                if num_expediente is None:
                    num_expediente = ''
                if num_acto is None:
                    num_acto = ''
                
                publicacion = {
                    'fecha_publicacion': registro.fecha_registro.date(),
                    'num_expediente': 'ACTO ' + num_acto  + ' EXPEDIENTE ' + num_expediente,
                    'descripcion': notificacion.descripcion,
                }
                data_out['publicaciones'].append(publicacion)

        elif tipo_notificacion == 'EDICTOS':
            data_out['tipo_notificacion'] = 'Página Web - Edictos'
        elif tipo_notificacion == 'CORREO':
            data_out['tipo_notificacion'] = 'Correo Electrónico'
        elif tipo_notificacion == 'AVISOS':
            data_out['tipo_notificacion'] = 'Avisos'
            fecha_publicacion = registro_notificacion.fecha_registro
            data_out['fecha_dia_publicacion'] = fecha_publicacion.strftime('%d')
            data_out['fecha_mes_publicacion'] = UtilsGestor.get_mes(fecha_publicacion.strftime('%m'))
            data_out['fecha_agno_publicacion'] = fecha_publicacion.strftime('%Y')
            data_out['fecha_hora_publicacion'] = fecha_publicacion.strftime('%H:%M')
            data_out['fecha_am_pm_publicacion'] = fecha_publicacion.strftime('%p')
            fecha_publicacion_fin = UtilsGestor.get_fecha_habil(fecha_publicacion, 5)
            tipo = type(fecha_publicacion_fin)
            data_out['fecha_dia_publicacion_fin'] = fecha_publicacion_fin.strftime('%d')
            data_out['fecha_mes_publicacion_fin'] = UtilsGestor.get_mes(fecha_publicacion_fin.strftime('%m'))
            data_out['fecha_agno_publicacion_fin'] = fecha_publicacion_fin.strftime('%Y')
            data_out['fecha_hora_publicacion_fin'] = fecha_publicacion_fin.strftime('%H:%M')
            data_out['fecha_am_pm_publicacion_fin'] = fecha_publicacion_fin.strftime('%p')
        elif tipo_notificacion == 'PERSONAL':
            data_out['tipo_notificacion'] = 'Notificacion Personal'
        elif tipo_notificacion == 'CORRESPONDENCIA':
            data_out['tipo_notificacion'] = 'Correspondencia Física'
        else:
            ValidationError('El tipo de notificación no es valido.')

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_out}, status=status.HTTP_200_OK)

    # def post(self, request):
    #     data = request.data
    #     fecha_inicial = datetime.strptime(data.get('fecha_inicial'), '%Y-%m-%d').date()
    #     fecha_final = datetime.strptime(data.get('fecha_final'), '%Y-%m-%d').date()

    #     if not fecha_inicial:
    #         raise ValidationError('fecha_inicial es un parametro requerido.')
        
    #     if not fecha_final:
    #         raise ValidationError('fecha_final es un parametro requerido.')
        
    #     dias_habiles = UtilsGestor.get_dias_habiles(fecha_inicial, fecha_final)
    #     fecha_habil = UtilsGestor.get_fecha_habil(fecha_inicial, dias_habiles)

    #     data_out = {
    #         'fecha_inicial': fecha_inicial,
    #         'fecha_final': fecha_final,
    #         'dias_habiles': dias_habiles,
    #         'fecha_habil': fecha_habil
    #     }


        # instancia_constancia = ConstanciaNotificacionCreate()
        # constancia = instancia_constancia.create_constancia(data)
        # return Response({'succes': True, 'detail':'Se creo la constancia correctamente', 'data':data_out}, status=status.HTTP_201_CREATED)

     
class GeneradorDocumentos(generics.CreateAPIView):
    serializer_class = GeneradorDocumentosSerializer
    permission_classes = [IsAuthenticated, PermisoCrearGeneradorDocumentosNotificaciones]

    def generador_documentos(self, data):
        try:
            tipo_documento = TiposDocumentos.objects.get(id_tipo_documento=data.get('id_tipo_documento'))
        except TiposDocumentos.DoesNotExist:
            raise ValidationError('El tipo de documento no existe.')
        
        try:
            notificacion = NotificacionesCorrespondencia.objects.get(id_notificacion_correspondencia=data.get('id_notificacion_correspondencia'))
        except NotificacionesCorrespondencia.DoesNotExist:
            raise ValidationError('La notificación no existe.')
        
        # try:
        #     persona = Personas.objects.get(id_persona=data.get('id_persona'))
        # except Personas.DoesNotExist:
        #     raise ValidationError('La persona no existe.')
        
        # try:
        #     expediente = Expedientes.objects.get(id_expediente=data.get('id_expediente'))
        # except Expedientes.DoesNotExist:
        #     raise ValidationError('El expediente no existe.')
        
        # try:
        #     tipo_acto = TiposActosAdministrativos.objects.get(id_tipo_acto_administrativo=data.get('id_tipo_acto_administrativo'))
        # except TiposActosAdministrativos.DoesNotExist:
        #     raise ValidationError('El tipo de acto administrativo no existe.')
        
        # try:
        #     acto_administrativo = ActosAdministrativos.objects.get(id_acto_administrativo=data.get('id_acto_administrativo'))
        # except ActosAdministrativos.DoesNotExist:
        #     raise ValidationError('El acto administrativo no existe.')
        
        # try:
        #     causa = CausasOAnomalias.objects.get(id_causa_o_anomalia=data.get('id_causa_o_anomalia'))
        # except CausasOAnomalias.DoesNotExist:
        #     raise ValidationError('La causa o anomalia no existe.')
        
        # try:
        #     entidad = Entidades.objects.get(id_entidad=data.get('id_entidad'))
        # except Entidades.DoesNotExist:
        #     raise ValidationError('La entidad no existe.')
        
        # try:
        #     persona_titular = Personas.objects.get(id_persona=data.get('id_persona_titular'))
        # except Personas.DoesNotExist:
        #     raise ValidationError('La persona titular no existe.')
        

    def post(self, request):
        data = request.data
        documento = self.generador_documentos(data)

        return Response({'succes': True, 'detail':'Se creo el documento correctamente', 'data':documento}, status=status.HTTP_201_CREATED)


class DatosDocumentosNotificacion(generics.ListAPIView):
    serializer_class = DocumentosDeArchivoExpedienteSerializer
    permission_classes = [IsAuthenticated]

    def get_datos_documentos(self, id_notificacion):
        try:
            notificacion = NotificacionesCorrespondencia.objects.get(id_notificacion_correspondencia=id_notificacion)
        except NotificacionesCorrespondencia.DoesNotExist:
            raise ValidationError('La notificación no existe.')
        
        serializer = self.serializer_class(notificacion, many=False)
        return serializer.data 

    def get(self, request, id_registro_notificacion, *args, **kwargs):
        try:
            registro_notificacion = Registros_NotificacionesCorrespondecia.objects.get(id_registro_notificacion_correspondencia=id_registro_notificacion)
        except Registros_NotificacionesCorrespondecia.DoesNotExist:
            raise ValidationError('El registro de la notificación no existe.')
        
        try:
            notificacion = NotificacionesCorrespondencia.objects.get(id_notificacion_correspondencia=registro_notificacion.id_notificacion_correspondencia.id_notificacion_correspondencia)
        except NotificacionesCorrespondencia.DoesNotExist:
            raise ValidationError('La notificación no existe.')
        
        data = self.get_datos_documentos(notificacion.id_notificacion_correspondencia)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data,}, status=status.HTTP_200_OK)


class DocumentosGeneradosCreate(generics.CreateAPIView):
    serializer_class = DocumentosDeArchivoExpedienteSerializer
    permission_classes = [IsAuthenticated]

    def create_documento(self, data):
        try:
            tipo_documento = TiposDocumentos.objects.get(id_tipo_documento=data.get('id_tipo_documento'))
        except TiposDocumentos.DoesNotExist:
            raise ValidationError('El tipo de documento no existe.')
        
        try:
            notificacion = NotificacionesCorrespondencia.objects.get(id_notificacion_correspondencia=data.get('id_notificacion_correspondencia'))
        except NotificacionesCorrespondencia.DoesNotExist:
            raise ValidationError('La notificación no existe.')
        
        try:
            persona = Personas.objects.get(id_persona=data.get('id_persona'))
        except Personas.DoesNotExist:
            raise ValidationError('La persona no existe.')
        
        try:
            expediente = ExpedientesDocumentales.objects.get(id_expediente=data.get('id_expediente'))
        except ExpedientesDocumentales.DoesNotExist:
            raise ValidationError('El expediente no existe.')
        
        try:
            tipo_acto = TiposActosAdministrativos.objects.get(id_tipo_acto_administrativo=data.get('id_tipo_acto_administrativo'))
        except TiposActosAdministrativos.DoesNotExist:
            raise ValidationError('El tipo de acto administrativo no existe.')
        
        try:
            acto_administrativo = ActosAdministrativos.objects.get(id_acto_administrativo=data.get('id_acto_administrativo'))
        except ActosAdministrativos.DoesNotExist:
            raise ValidationError('El acto administrativo no existe.')
        
        try:
            causa = CausasOAnomalias.objects.get(id_causa_o_anomalia=data.get('id_causa_o_anomalia'))
        except CausasOAnomalias.DoesNotExist:
            raise ValidationError('La causa o anomalia no existe.')

        
        try:
            persona_titular = Personas.objects.get(id_persona=data.get('id_persona_titular'))
        except Personas.DoesNotExist:
            raise ValidationError('La persona titular no existe.')
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return serializer.data
    
    def post(self, request):
        data = request.data
        documento = self.create_documento(data)

        return Response({'succes': True, 'detail':'Se creo el documento correctamente', 'data':documento}, status=status.HTTP_201_CREATED)

"""
{
  "cod_tipo_solicitud": "NO", ## SAS
  "cod_tipo_documento": 1, ## SAS endpoint para buscar el servicio
  "id_expediente_documental": 1, --> numero expediente ## SAS 
                codigo_exp_und_serie_subserie - codigo_exp_Agno - codigo_exp_consec_por_agno ## // Hablarlo con Diana
  "id_solicitud_tramite": 1, --> identificador solicitud ## SAS  ## id expediente o radicado
  "id_acto_administrativo": 1,  --> NULL
  "procede_recurso_reposicion": false,  --> NULL -- False preguntar en el Daily
  "id_persona_titular": 1,  --> Se saca del id_solicitud_tramite
  "id_persona_interpone": 2,  --> Se saca del id_solicitud_tramite
  "cod_relacion_con_titular": "MP", --> Se saca del id_solicitud_tramite
  "es_anonima": false,  Fijo
  "permite_notificacion_email": true, --> se saca de la T010 si es vacio
  "persona_a_quien_se_dirige": "Guillermo", --> se saca de la T010 si es vacio
  "cod_tipo_documentoID": 1, --> se saca de la T010 si es vacio
  "nro_documentoID": "123456", --> se saca de la T010 si es vacio
  "cod_municipio_notificacion_nal": 1,  --> se saca de la T010 si es vacio
  "dir_notificacion_nal": "Dirección de notificación nacional",  --> se saca de la T010 si es vacio
  "tel_celular": "123456789", --> se saca de la T010 si es vacio
  "tel_fijo": "987654321", --> se saca de la T010 si es vacio
  "email_notificacion": "correo@ejemplo.com",  --> se saca de la T010 si es vacio
  "asunto": "Asunto de la notificación", ## SAS
  "descripcion": "Descripción de la notificación",  ## SAS
  "cod_medio_solicitud": "SI",  Fijo
  "fecha_solicitud": "2024-04-22T12:00:00Z",  ---> fecha de creación sistema
  "id_persona_solicita": 1, ## SAS
  "id_und_org_oficina_solicita": 1, --> Saca del id_persona_solicita
  "allega_copia_fisica": false, Fijo
  "cantidad_anexos": 2, depende de los anexos ## SAS
  "nro_folios_totales": 10, depende de los anexos la suma de todos los folios de los anexos ## SAS
  "id_persona_recibe_solicitud_manual": NULL, Fijo
  "id_persona_asigna": 2,  --> NULL
  "id_persona_asignada": 4, --> NULL
  "cod_estado_asignacion": "Pe", --> NULL
  "fecha_eleccion_estado": "2024-04-22T12:00:00Z", --> NULL
  "justificacion_rechazo_asignacion": "Justificación del rechazo", --> NULL
  "requiere_digitalizacion": False, Fijo  --> NULL
  "fecha_envio_definitivo_a_digitalizacion": "2024-04-22T12:00:00Z", --> NULL
  "fecha_digitalizacion_completada": "2024-04-22T12:00:00Z", --> NULL
  "ya_digitizado": true, --> NULL
  "fecha_rta_final_gestion": "2024-04-22T12:00:00Z", --> NULL
  "id_persona_rta_final_gestion": 5, --> NULL
  "solicitud_aceptada_rechazada": true, --> NULL
  "fecha_devolucion": "2024-04-22T12:00:00Z", --> NULL
  "justificacion_rechazo": "Justificación del rechazo", --> NULL
  "cod_estado": "PE", fijo
  "id_doc_de_arch_exp": 1 --> NULL
  "anexos": [
    {
        "nombre_anexo": "Nombre anexo",
        "orden_anexo_doc": 0,
        "cod_medio_almacenamiento": "Na",
		"medio_almacenamiento_otros_Cual": null,
        "numero_folios": 0,
        "ya_digitalizado": true,
        "uso_del_documento": true,
        "cod_tipo_documento": 3
        },
        {
		"nombre_anexo": "Nombre anexo 1",
		"orden_anexo_doc": 0,
		"cod_medio_almacenamiento": "Na",
		"medio_almacenamiento_otros_Cual": null,
		"numero_folios": 0,
		"ya_digitalizado": true,
        "uso_del_documento": true,
        "cod_tipo_documento": 3
		}
	]
}
"""
#
############################################

"""
{
  "cod_tipo_solicitud": "NO",
  "cod_tipo_documento": 1, 
  "numero_expediente_documental": null,
  "indicador_solicitud_tramite": "UNICO-2024-93",
  "permite_notificacion_email": true,
  "persona_a_quien_se_dirige": "Guillermo",
  "cod_tipo_documentoID": "CC",
  "nro_documentoID": "123456",
  "cod_municipio_notificacion_nal": "05001", 
  "dir_notificacion_nal": "Dirección de notificación nacional", 
  "tel_celular": "123456789",
  "tel_fijo": "987654321",
  "email_notificacion": "correo@ejemplo.com",
  "asunto": "Asunto de la notificación",
  "descripcion": "Descripción de la notificación",
  "id_persona_solicita": 1,
  "cantidad_anexos": 2,
  "nro_folios_totales": 10,
  "anexos": [
    {
        "nombre_anexo": "Nombre anexo",
		"orden_anexo_doc": 0,
		"cod_medio_almacenamiento": "Na",
		"medio_almacenamiento_otros_Cual": null,
		"numero_folios": 0,
		"ya_digitalizado": true,
        "uso_del_documento": true,
        "cod_tipo_documento": 3
    },
    {
        "nombre_anexo": "Nombre anexo 1",
		"orden_anexo_doc": 0,
		"cod_medio_almacenamiento": "Na",
		"medio_almacenamiento_otros_Cual": null,
		"numero_folios": 0,
		"ya_digitalizado": true,
        "uso_del_documento": true,
        "cod_tipo_documento": 3
    }
]
}
"""


class NotificacionesAutomaticasCreate(generics.CreateAPIView):
    serializer_class = NotificacionesCorrespondenciaCreateSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create_notificacion_sistema(self, request, sistema):
        data_total = request.data
        print(str(type(data_total.get('data'))))
        #raise ValidationError(str(type(data_total.get('data'))))
        # if type(data_total.get('data') == dict):
        #    data = data_total.get('data') 
        # else:
        data = json.loads(data_total.get('data'))
        fecha_actual = timezone.now()

        if not data.get('cod_tipo_solicitud'):
            raise ValidationError('El cod_tipo_solicitud es obligatorio')
        
        if not data.get('cod_tipo_documento'):
            raise ValidationError('El cod_tipo_documento es obligatorio')
        
        try:
            tipo_documento = TiposDocumentos.objects.get(id_tipo_documento=data.get('cod_tipo_documento'))
        except TiposDocumentos.DoesNotExist:
            raise ValidationError('El tipo de documento no existe.')
        
        numero_expediente_documental = data.get('numero_expediente_documental')
        if numero_expediente_documental:
            nro_expediente_documental = numero_expediente_documental.split('-')
            if len(nro_expediente_documental) != 3:
                raise ValidationError('El numero_expediente_documental no tiene el formato correcto.')
            
            expediente_documental = ExpedientesDocumentales.objects.filter(codigo_exp_und_serie_subserie=nro_expediente_documental[0],
                                                                           codigo_exp_Agno=nro_expediente_documental[1], codigo_exp_consec_por_agno=nro_expediente_documental[1]).first()
            if not expediente_documental:
                raise ValidationError('El expediente documental no existe.')
            id_expediente_documental = expediente_documental.id_expediente_documental
        else:
            id_expediente_documental = None


        indicador_solicitud_tramite = data.get('indicador_solicitud_tramite')

        if indicador_solicitud_tramite:
            numero_radicado = indicador_solicitud_tramite.split('-')
            if len(numero_radicado) != 3:
                raise ValidationError('El indicador_solicitud_tramite no tiene el formato correcto.')
            
            radicado = T262Radicados.objects.filter(prefijo_radicado=numero_radicado[0], agno_radicado=numero_radicado[1], nro_radicado=int(numero_radicado[2])).first()
            
            if not radicado:
                raise ValidationError('El radicado no existe.')
            
            try:
                solicitud_tramite = SolicitudesTramites.objects.filter(id_radicado=radicado.id_radicado).first()
            except SolicitudesTramites.DoesNotExist:
                raise ValidationError('La solicitud tramite no existe.')
            
            id_solicitud_tramite = solicitud_tramite.id_solicitud_tramite
            id_persona_titular = solicitud_tramite.id_persona_titular.id_persona
            id_persona_interpone = solicitud_tramite.id_persona_interpone.id_persona
            cod_relacion_con_titular = solicitud_tramite.cod_relacion_con_el_titular
        else:
            id_solicitud_tramite = None
            id_persona_titular = None
            id_persona_interpone = None
            cod_relacion_con_titular = None

        
        if not data.get('asunto'):
            raise ValidationError('El asunto es obligatorio')
        
        if not data.get('id_persona_solicita'):
            raise ValidationError('El id_persona_solicita es obligatorio')
        
        try:
            persona_solicita = Personas.objects.get(id_persona=data.get('id_persona_solicita'))
        except Personas.DoesNotExist:
            raise ValidationError('La persona solicitante no existe.')
        
        if sistema == 'SAS':
            permite_notificacion_email = data.get('permite_notificacion_email')
            persona_a_quien_se_dirige = data.get('persona_a_quien_se_dirige')
            cod_tipo_documentoID = data.get('cod_tipo_documentoID')
            nro_documentoID = data.get('nro_documentoID')
            cod_municipio_notificacion_nal = data.get('cod_municipio_notificacion_nal')
            dir_notificacion_nal = data.get('dir_notificacion_nal')
            tel_celular = data.get('tel_celular')
            tel_fijo = data.get('tel_fijo')
            email_notificacion = data.get('email_notificacion')

        if sistema == 'BIA':
            persona_titular = Personas.objects.filter(id_persona=id_persona_titular).first()
            permite_notificacion_email = persona_titular.acepta_notificacion_email
            if persona_titular.primer_nombre is not None:
                nombre_completo = [persona_titular.primer_nombre, persona_titular.segundo_nombre, persona_titular.primer_apellido, persona_titular.segundo_apellido]
                persona_a_quien_se_dirige =  ' '.join(filter(None, nombre_completo))
            else:
                persona_a_quien_se_dirige = persona_titular.razon_social
            cod_tipo_documentoID = persona_titular.tipo_documento.cod_tipo_documento
            nro_documentoID = persona_titular.numero_documento
            cod_municipio_notificacion_nal = persona_titular.cod_municipio_notificacion_nal.cod_municipio
            dir_notificacion_nal = persona_titular.direccion_notificaciones
            tel_celular = persona_titular.telefono_celular

            if persona_titular.telefono_fijo_residencial == '':
                tel_fijo = None
            else:
                tel_fijo = persona_titular.telefono_fijo_residencial
            email_notificacion = persona_titular.email

        

        data_notificacion = {
            'id_acto_administrativo': None,
            'procede_recurso_reposicion': None,
            'es_anonima': False,
            'cod_medio_solicitud': 'SI',
            'allega_copia_fisica': False,
            'id_persona_recibe_solicitud_manual': None,
            'requiere_digitalizacion': False,
            'cod_estado': 'PE',
            'cod_tipo_solicitud': data.get('cod_tipo_solicitud'),
            'cod_tipo_documento': tipo_documento.id_tipo_documento,
            'id_expediente_documental': id_expediente_documental,
            'id_solicitud_tramite': id_solicitud_tramite,
            'id_persona_titular': id_persona_titular,
            'id_persona_interpone': id_persona_interpone,
            'cod_relacion_con_titular': cod_relacion_con_titular,
            'permite_notificacion_email': permite_notificacion_email,
            'persona_a_quien_se_dirige': persona_a_quien_se_dirige,
            'cod_tipo_documentoID': cod_tipo_documentoID,
            'nro_documentoID': nro_documentoID,
            'cod_municipio_notificacion_nal': cod_municipio_notificacion_nal,
            'dir_notificacion_nal': dir_notificacion_nal,
            'tel_celular': tel_celular,
            'tel_fijo': tel_fijo,
            'email_notificacion': email_notificacion,
            'asunto': data.get('asunto'),
            'descripcion': data.get('descripcion'),
            'fecha_solicitud': fecha_actual,
            'id_persona_solicita': persona_solicita.id_persona,
            'id_und_org_oficina_solicita': persona_solicita.id_unidad_organizacional_actual.id_unidad_organizacional,
            'cantidad_anexos': data.get('cantidad_anexos'),
            'nro_folios_totales': data.get('nro_folios_totales')
        }
        
        serializer = self.serializer_class(data=data_notificacion)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        util_PQR = Util_PQR()

        anexos = util_PQR.set_archivo_in_anexo(data['anexos'], request.FILES, "create")
        print(anexos)
        #raise ValidationError("NONE")

        if anexos:
            anexosCreate = AnexosSistemaCreate()
            valores_creados_detalles = anexosCreate.create_anexos_notificaciones(anexos, serializer.data['id_notificacion_correspondencia'], fecha_actual, persona_solicita.id_persona)

        return  serializer.data
    
    def post(self, request):
        sistema = 'SAS'
        data = self.create_notificacion_sistema(request, sistema)
        return Response({'succes': True, 'detail':'Se creo la notificación correctamente', 'data':data}, status=status.HTTP_201_CREATED)


class NotificacionesAutomaticasBiaCreate(generics.CreateAPIView):
    serializer_class = NotificacionesCorrespondenciaCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        instancia_notificacion = NotificacionesAutomaticasCreate()
        sistema = 'BIA'
        data = instancia_notificacion.create_notificacion_sistema(request, sistema)
        return Response({'succes': True, 'detail':'Se creo la notificación correctamente', 'data':data}, status=status.HTTP_201_CREATED)

        

class AnexosSistemaCreate(generics.CreateAPIView):
    serializer_class = AnexosPostSerializer

    def create_anexos_notificaciones(self, anexos, id_notificacion, fecha_actual, id_persona_recibe_solicitud):
         nombres_anexos = [anexo['nombre_anexo'] for anexo in anexos]
         instancia_anexos = AnexosCreate()
         nombres_anexos_auditoria = []
         # Validar que no haya valores repetidos
         if len(nombres_anexos) != len(set(nombres_anexos)):
            raise ValidationError("error': 'No se permiten nombres de anexos repetidos.")
         
         for anexo in anexos:

            data_anexo = instancia_anexos.crear_anexo(anexo)

            data_anexos = {}
            data_anexos['id_notificacion_correspondecia'] = id_notificacion
            data_anexos['usuario_notificado'] = False
            data_anexos['uso_del_documento'] = 'PU'
            data_anexos['doc_entrada_salida'] = 'EN'
            if anexo['cod_tipo_documento']:
                tipo_documento = TiposAnexosSoporte.objects.filter(id_tipo_anexo_soporte=anexo['cod_tipo_documento']).first()
                data_anexos['cod_tipo_documento'] = tipo_documento.id_tipo_anexo_soporte
            data_anexos['doc_generado'] = 'SI'
            data_anexos['id_persona_anexa_documento'] = id_persona_recibe_solicitud
            data_anexos['fecha_anexo'] = fecha_actual
            data_anexos['id_anexo'] = data_anexo['id_anexo']

            # Agregue usuario notificado
            if 'usuario_notificado' in data_anexo:
                data_anexos['usuario_notificado'] = data_anexo['usuario_notificado']
            else:
                data_anexos['usuario_notificado'] = False
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


class NotificacionesOPASCreate(generics.CreateAPIView):
    serializer_class = NotificacionesCorrespondenciaCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        instancia_notificacion = NotificacionesAutomaticasCreate()
        sistema = 'BIA'
        data = instancia_notificacion.create_notificacion_sistema(request, sistema)
        return Response({'succes': True, 'detail':'Se creo la notificación correctamente', 'data':data}, status=status.HTTP_201_CREATED)


class NotificacionesOtrosCreate(generics.CreateAPIView):
    serializer_class = NotificacionesCorrespondenciaCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        instancia_notificacion = NotificacionesAutomaticasCreate()
        sistema = 'BIA'
        data = instancia_notificacion.create_notificacion_sistema(request, sistema)
        return Response({'succes': True, 'detail':'Se creo la notificación correctamente', 'data':data}, status=status.HTTP_201_CREATED)


