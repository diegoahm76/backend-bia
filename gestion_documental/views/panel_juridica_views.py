from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import status, generics
from rest_framework.response import Response
from django.forms import model_to_dict
from datetime import datetime
from gestion_documental.serializers.panel_juridica_serializers import SolicitudesJuridicaGetSerializer, SolicitudesJuridicaInformacionOPAGetSerializer
from rest_framework.permissions import IsAuthenticated
from gestion_documental.serializers.ventanilla_pqrs_serializers import TramitePutSerializer
from gestion_documental.views.panel_ventanilla_views import Estados_PQRCreate
from tramites.models.tramites_models import PermisosAmbSolicitudesTramite, SolicitudesDeJuridica

class SolicitudesJuridicaGet(generics.ListAPIView):
    serializer_class = SolicitudesJuridicaGetSerializer
    queryset = SolicitudesDeJuridica.objects.all().exclude(id_solicitud_tramite=None).order_by('fecha_solicitud')
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        filter={}
        radicado = request.query_params.get('radicado', '')
        
        for key, value in request.query_params.items():
            if key =='id_persona_solicita_revision':
                if value != '':
                    filter[key] = value
            if key == 'nombre_proyecto':
                if value != '':
                    filter['id_solicitud_tramite__nombre_proyecto__icontains'] = value
            if key == 'expediente':
                if value != '':
                    filter['id_solicitud_tramite__id_expediente__titulo_expediente__icontains'] = value
            if key == 'pago':
                if value != '':
                    filter['id_solicitud_tramite__pago'] = True if 'true' in value else False
            if key == 'id_estado_actual_solicitud':
                if value != '':
                    filter['id_solicitud_tramite__id_estado_actual_solicitud'] = value
        
        solicitudes_juridica_opas = self.queryset.filter(**filter)
        opas = PermisosAmbSolicitudesTramite.objects.filter(id_permiso_ambiental__cod_tipo_permiso_ambiental = 'O')
        opas_id_list = [opa.id_solicitud_tramite.id_solicitud_tramite for opa in opas]
        solicitudes_juridica_opas = solicitudes_juridica_opas.filter(id_solicitud_tramite__in = opas_id_list)

        serializador = self.serializer_class(solicitudes_juridica_opas,many=True)
        serializador_data = serializador.data
        
        if radicado:
            serializador_data = [item for item in serializador_data if radicado in item.get('radicado', '')]
        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador_data}, status=status.HTTP_200_OK)
    
class SolicitudesJuridicaInformacionOPAGet(generics.ListAPIView):
    serializer_class = SolicitudesJuridicaInformacionOPAGetSerializer
    queryset = SolicitudesDeJuridica.objects.all().exclude(id_solicitud_tramite=None).order_by('fecha_solicitud')
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_solicitud_tramite):
        opa = PermisosAmbSolicitudesTramite.objects.filter(id_solicitud_tramite=id_solicitud_tramite, id_permiso_ambiental__cod_tipo_permiso_ambiental='O').first()
        if not opa:
            raise NotFound('No existe el OPA ingresado')
        
        serializador = self.serializer_class(opa)
        serializador_data = serializador.data
        
        return Response({'succes': True, 'detail':'Se encontró la siguiente información', 'data':serializador_data}, status=status.HTTP_200_OK)
    
class SolicitudesJuridicaRevisionCreate(generics.CreateAPIView):
    serializer_class = SolicitudesJuridicaGetSerializer
    serializer_tramite = TramitePutSerializer
    permission_classes = [IsAuthenticated]
    creador_estados = Estados_PQRCreate
    
    def create(self, request, id_solicitud_de_juridica):
        fecha_actual = datetime.now()
        
        aprueba_solicitud_tramite = request.data.get('aprueba_solicitud_tramite', None)
        observacion = request.data.get('observacion', None)
        
        if not aprueba_solicitud_tramite:
            raise ValidationError('El campo de aprobación es obligatorio')
        
        solicitud_juridica = SolicitudesDeJuridica.objects.filter(id_solicitud_de_juridica=id_solicitud_de_juridica).first()
        
        if not solicitud_juridica:
            raise NotFound('No existe la solicitud jurídica ingresada')
        
        #ACTUALIZACIONES EN LA T296
        solicitud_juridica.aprueba_solicitud_tramite = aprueba_solicitud_tramite
        solicitud_juridica.solicitud_completada = True
        solicitud_juridica.solicitud_sin_completar = False
        solicitud_juridica.fecha_rta_solicitud = fecha_actual
        solicitud_juridica.id_persona_revisa = request.user.persona
        solicitud_juridica.observacion = observacion
        solicitud_juridica.cod_estado_tipo_solicitud_juridica = "RE"
        solicitud_juridica.save()
        
        #CREA UN ESTADO NUEVO T255 EN VENTANILLA CON PENDIENTES
        data_estado = {}
        data_estado['id_tramite'] = solicitud_juridica.id_solicitud_tramite.id_solicitud_tramite
        data_estado['estado_solicitud'] = 16
        data_estado['fecha_iniEstado'] = fecha_actual
        data_estado['persona_genera_estado'] = request.user.persona.id_persona
        respuesta_estado = self.creador_estados.crear_estado(self,data_estado)
        data_respuesta_estado_asociado = respuesta_estado.data['data']
        
        #CAMBIAMOS EL ESTADO ACTUAL DEL OPA
        serializador_opa = self.serializer_tramite(solicitud_juridica.id_solicitud_tramite, data={'id_estado_actual_solicitud':16}, partial=True)
        serializador_opa.is_valid(raise_exception=True)
        serializador_opa.save()
        
        solicitud_data = model_to_dict(solicitud_juridica)
        
        #PENDIENTE AL MÓDULO DE LIQUIDACIÓN PARA INTRODUCIR LA LÓGICA QUE APLIQUE ACÁ
        
        return Response({'succes': True, 'detail':'Se finalizó la revisión correctamente', 'data':solicitud_data, 'estados':data_respuesta_estado_asociado}, status=status.HTTP_200_OK)
    