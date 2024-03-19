from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404, JsonResponse
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from gestion_documental.models.radicados_models import T262Radicados
from django.utils import timezone

from transversal.models.base_models import HistoricoCargosUndOrgPersona, ClasesTercero

from gestion_documental.models.notificaciones_models import (
    NotificacionesCorrespondencia, 
    Registros_NotificacionesCorrespondecia, 
    AsignacionNotificacionCorrespondencia, 
    TiposNotificacionesCorrespondencia, 
    TiposAnexosSoporte, 
    Anexos_NotificacionesCorrespondencia, 
    EstadosNotificacionesCorrespondencia, 
    HistoricosEstados, 
    CausasOAnomalias
    )

from gestion_documental.serializers.notificaciones_serializers import (
    NotificacionesCorrespondenciaSerializer,
    AsignacionNotificacionCorrespondenciaSerializer,
    AsignacionNotiCorresCreateSerializer
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
    

class CrearAsignacionNotificacion(generics.CreateAPIView):
    serializer_class = AsignacionNotiCorresCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        id_persona_asigna = request.user.persona
        
        #Asignar los valores a los campos de la solicitud de viaje
        asignacion_data = {
            'id_notificacion_correspondencia': data.get('id_notificacion_correspondencia'),
            'id_orden_notificacion': data.get('id_orden_notificacion'),
            'fecha_asignacion': timezone.now(),
            'id_persona_asigna': id_persona_asigna.id_persona,
            'id_persona_asignada': data.get('id_persona_asignada'),
            'id_und_org_seccion_asignada': id_persona_asigna.id_unidad_organizacional_actual.id_unidad_organizacional, 
        }

        serializer = self.serializer_class(data=asignacion_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return Response({'succes': True, 'detail':'Se creo el consecutivo correctamente', 'data':{**serializer.data}}, status=status.HTTP_201_CREATED)

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
        # if serializer.data:
        #     return Response({'succes': True, 'detail':'Tiene las siguientes asignaciones', 'data':serializer.data,}, status=status.HTTP_200_OK) 
        # else:
        #     data_valida = {"pendientes": 0, "resueltas": 0}
        #     return Response({'succes': True, 'detail':'Tiene las siguientes asignaciones', 'data':data_valida,}, status=status.HTTP_200_OK)
    
        

