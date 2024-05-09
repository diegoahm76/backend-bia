
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from gestion_documental.serializers.solicitudes_OPAS_serializers import OPAGetSerializer,RequerimientoSobreOPATramiteGetSerializer
from tramites.models.tramites_models import PermisosAmbSolicitudesTramite, Requerimientos, RespuestasRequerimientos

from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
import os
from rest_framework.permissions import IsAuthenticated

class TramiteListOpasGetView(generics.ListAPIView):
    serializer_class = OPAGetSerializer
    permission_classes = [IsAuthenticated]
    queryset = PermisosAmbSolicitudesTramite.objects.all()
    def get(self, request,id):
        

        filter={}
        filter['id_solicitud_tramite__id_medio_solicitud'] = 2
        filter['id_permiso_ambiental__cod_tipo_permiso_ambiental'] = 'OP'
        filter['id_solicitud_tramite__id_radicado__isnull'] = False
        filter['id_solicitud_tramite__id_persona_titular'] = id
        instance = self.get_queryset().filter(**filter).order_by('id_solicitud_tramite__fecha_radicado')
        serializer = self.serializer_class(instance, many=True)

        
        return Response({'success': True, 'detail':'Se encontró la siguiente información', 'data': serializer.data}, status=status.HTTP_200_OK)



class RequerimientosTramiteGetByTramiteOPA(generics.ListAPIView):

    serializer_class = RequerimientoSobreOPATramiteGetSerializer
    queryset =Requerimientos.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,tra):
        #Pendiente validar si estan sin responder
        ids_requerimientos_con_respuesta = RespuestasRequerimientos.objects.values_list('id_requerimiento', flat=True)
        instance = self.get_queryset().filter(id_solicitud_tramite=tra).exclude(id_requerimiento__in=ids_requerimientos_con_respuesta)
        if not instance:
            raise NotFound("No existen registros")
        
        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
