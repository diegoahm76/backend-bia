
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import status, generics
from rest_framework.response import Response
from gestion_documental.models.radicados_models import EstadosSolicitudes
from gestion_documental.serializers.consultar_estado_solicitud_serializer import SolicitudesTramitesEstadoSolicitudGetSerializer, TramitesEstadosSolicitudesGetSerializer

from seguridad.utils import Util
from gestion_documental.utils import UtilsGestor
from datetime import date, datetime
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from tramites.models.tramites_models import SolicitudesTramites


class EstadoSolicitudesTramitesGet(generics.ListAPIView):
    serializer_class = SolicitudesTramitesEstadoSolicitudGetSerializer
    queryset =SolicitudesTramites.objects.all()
                                         
    permission_classes = [IsAuthenticated]

    def get (self, request):
    
        data_respuesta = []
        filter={}
        
        for key, value in request.query_params.items():


            if key =='estado_actual_solicitud':
                if value != '':
                    filter['id_estado_actual_solicitud__nombre__icontains'] = value    
            if key == 'tipo_solicitud':
                if value != '':
                    tipo_busqueda = False

            if key == 'fecha_inicio':
                if value != '':
                    
                    filter['fecha_radicado__gte'] = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'fecha_fin':
                if value != '':
                    filter['fecha_radicado__lte'] = datetime.strptime(value, '%Y-%m-%d').date()


        filter['id_radicado__isnull'] = False
        instance = self.get_queryset().filter(**filter).order_by('fecha_radicado')
        radicado_value = request.query_params.get('radicado')
        print(radicado_value)
        print('TODO BEIN?')
        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance,many=True)
       
        data_respuesta = serializador.data
        print(data_respuesta)
        data_validada =[]
        if radicado_value and radicado_value != '':
            data_validada = [item for item in serializador.data if radicado_value.lower() in item.get('radicado', '').lower()]
        else :
            data_validada = data_respuesta
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_validada,}, status=status.HTTP_200_OK)
    


class TramitesEstadosSolicitudesGet(generics.ListAPIView):
    serializer_class = TramitesEstadosSolicitudesGetSerializer
    queryset =EstadosSolicitudes.objects.filter(aplica_para_otros=True)
    permission_classes = [IsAuthenticated]
    
    def get (self, request):
        queryset = self.queryset.all()
        if not queryset:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(queryset,many=True)
        return Response({'success': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
