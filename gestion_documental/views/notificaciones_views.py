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
from transversal.models.organigrama_models import UnidadesOrganizacionales
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
        
        anexos = Anexos_NotificacionesCorrespondencia.objects.filter(id_notificacion_correspondecia=notificacion.id_notificacion_correspondencia)
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


class AnexosSoporteGacetaCreate(generics.CreateAPIView):
    serializer_class = AnexosNotificacionesCorrespondenciaSerializer
    permission_classes = [IsAuthenticated]

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
    

# class RegistrosNotificacionesCorrespondenciaGacetaCreate(generics.CreateAPIView):
#     serializer_class = Registros_NotificacionesCorrespondeciaSerializer
#     permission_classes = [IsAuthenticated]

#     def create_registro(self, data):
#         try:
#             notificacion = NotificacionesCorrespondencia.objects.get(id_notificacion_correspondencia=data.get('id_notificacion_correspondencia'))
#         except NotificacionesCorrespondencia.DoesNotExist:
#             raise ValidationError('La notificación no existe.')
        
#         try:
#             tipo_documento = TiposDocumentos.objects.get(id_tipo_documento=data.get('id_tipo_documento'))
#         except TiposDocumentos.DoesNotExist:
#             raise ValidationError('El tipo de documento no existe.')
        
#         serializer = self.serializer_class(data=data)
#         serializer.is_valid(raise_exception=True)
#         instance = serializer.save()
#         return serializer.data

#     def post(self, request):
#         data = request.data
#         registro = self.create_registro(data)
#         return Response({'succes': True, 'detail':'Se creo el registro correctamente', 'data':registro}, status=status.HTTP_201_CREATED)


class RegistrosNotificacionesCorrespondenciaGacetaUpdate(generics.UpdateAPIView):
    serializer_class = Registros_NotificacionesCorrespondeciaSerializer
    permission_classes = [IsAuthenticated]

    # @transaction.atomic
    # def update_registro_notificacion(self, id_registro_notificacion, data):
    #     registro_notificacion = Registros_NotificacionesCorrespondecia.objects.filter(id_registro_notificacion_correspondencia=id_registro_notificacion).first()
    #     if not registro_notificacion:
    #         raise ValidationError(f'El registro de la notificación con id {id_registro_notificacion} no existe.')
    #     else:
    #         data_anexos = data.pop('anexos')
    #         for anexo in data_anexos:
    #             try:
    #                 anexo_notificacion = Anexos_NotificacionesCorrespondencia.objects.get(id_anexo_notificacion_correspondencia=anexo.get('id_anexo_notificacion_correspondencia'))
    #             except Anexos_NotificacionesCorrespondencia.DoesNotExist:
    #                 raise ValidationError('El anexo no existe.')
    #             instancia_anexos = AnexosSoporteGacetaCreate()
    #             anexos_response = instancia_anexos.create_anexo(anexo)
    #             if not anexos_response:
    #                 raise ValidationError('No se pudo crear el anexo.')

    #         serializer = self.serializer_class(registro_notificacion, data=data, partial=True)
    #         serializer.is_valid(raise_exception=True)
    #         instance = serializer.save()
    #         return serializer.data

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
        
        if anexos:
            anexosCreate = AnexosCreate()
            valores_creados_detalles = anexosCreate.create_anexos_notificaciones(anexos, registro_notificacion.id_notificacion_correspondencia.id_notificacion_correspondencia, fecha_actual, persona_anexa)
        
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
        data = request.data
        instancia_registro = RegistrosNotificacionesCorrespondenciaGacetaUpdate()
        registro = instancia_registro.update_registro_notificacion(id_registro_notificacion, data, request.FILES)
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
        data = request.data
        instancia_registro = RegistrosNotificacionesCorrespondenciaGacetaUpdate()
        registro = instancia_registro.update_registro_notificacion(id_registro_notificacion, data, request.FILES)
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
    permission_classes = [IsAuthenticated]

    def put(self, request, id_registro_notificacion):
        data = request.data
        instancia_registro = RegistrosNotificacionesCorrespondenciaGacetaUpdate()
        registro = instancia_registro.update_registro_notificacion(id_registro_notificacion, data, request.FILES)
        return Response({'succes': True, 'detail':'Se creo el registro correctamente', 'data':registro}, status=status.HTTP_201_CREATED)


class RegistrosNotificacionesCorrespondenciaCorrespondenciaUpdate(generics.UpdateAPIView):
    serializer_class = Registros_NotificacionesCorrespondeciaCreateSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data
        estado = EstadosNotificacionesCorrespondencia.objects.filter(id_estado_notificacion_correspondencia=data.get('id_estado_actual_registro')).first()
        if not estado:
            raise ValidationError(f'El estado de la notificación con id {data.get("id_estado_actual_registro")} no existe.')
        registro_notificacion = get_object_or_404(Registros_NotificacionesCorrespondecia, id_registro_notificacion_correspondencia=pk)
        if not registro_notificacion:
            raise ValidationError(f'El registro de la notificación con id {pk} no existe.')
        else:
            registro_notificacion.id_estado_actual_registro = estado
            registro_notificacion.save()
            serializer = self.get_serializer(registro_notificacion)

        return Response({'succes': True, 'detail':'Se actualizó el registro de la notificación correctamente', 'data':{**serializer.data}}, status=status.HTTP_200_OK)
    

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
class GenerarConstanciaNotificacion(generics.CreateAPIView):
    serializer_class = ConstanciaNotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        data = request.query_params

        if not data.get('fecha_inicial'):
            raise ValidationError('fecha_inicial es un parametro requerido.')
        
        if not data.get('id_registro_notificacion_correspondencia'):
            raise ValidationError('id_registro_notificacion_correspondencia es un parametro requerido.')
        
        if not data.get('id_tipo_notificacion_correspondencia'):
            raise ValidationError('id_tipo_notificacion_correspondencia es un parametro requerido.')
        
        fecha_inicial = datetime.strptime(data.get('fecha_inicial'), '%Y-%m-%d').date()
        fecha_final = datetime.strptime(data.get('fecha_final'), '%Y-%m-%d').date()

        if not fecha_inicial:
            raise ValidationError('fecha_inicial es un parametro requerido.')
        
        if not fecha_final:
            raise ValidationError('fecha_final es un parametro requerido.')
        
        dias_habiles = UtilsGestor.get_dias_habiles(fecha_inicial, fecha_final)
        fecha_habil = UtilsGestor.get_fecha_habil(fecha_inicial, dias_habiles)

        data_out = {
            'fecha_inicial': fecha_inicial,
            'fecha_final': fecha_final,
            'dias_habiles': dias_habiles,
            'fecha_habil': fecha_habil
        }

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
        return Response({'succes': True, 'detail':'Se creo la constancia correctamente', 'data':data_out}, status=status.HTTP_201_CREATED)

     
class GeneradorDocumentos(generics.CreateAPIView):
    serializer_class = GeneradorDocumentosSerializer
    permission_classes = [IsAuthenticated]

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


class NotificacionesCorrespondenciaCreate(generics.CreateAPIView):
    serializer_class = NotificacionesCorrespondenciaCreateSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        data_total = request.data
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
            
            radicado = T262Radicados.objects.filter(prefijo_radicado=numero_radicado[0], agno_radicado=numero_radicado[1], nro_radicado=numero_radicado[2]).first()
            
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
            'permite_notificacion_email': data.get('permite_notificacion_email'),
            'persona_a_quien_se_dirige': data.get('persona_a_quien_se_dirige'),
            'cod_tipo_documentoID': data.get('cod_tipo_documentoID'),
            'nro_documentoID': data.get('nro_documentoID'),
            'cod_municipio_notificacion_nal': data.get('cod_municipio_notificacion_nal'),
            'dir_notificacion_nal': data.get('dir_notificacion_nal'),
            'tel_celular': data.get('tel_celular'),
            'tel_fijo': data.get('tel_fijo'),
            'email_notificacion': data.get('email_notificacion'),
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
        

        if anexos:
            anexosCreate = AnexosSistemaCreate()
            valores_creados_detalles = anexosCreate.create_anexos_notificaciones(anexos, serializer.data['id_notificacion_correspondencia'], fecha_actual, persona_solicita.id_persona)

        return Response({'succes': True, 'detail':'Se creo el consecutivo correctamente', 'data':{**serializer.data}}, status=status.HTTP_201_CREATED)



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
            data_metadatos['fecha_creacion_doc'] = fecha_actual
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

