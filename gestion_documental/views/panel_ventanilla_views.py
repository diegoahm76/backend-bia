from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
from gestion_documental.models.radicados_models import PQRSDF, EstadosSolicitudes, T262Radicados
from gestion_documental.serializers.permisos_serializers import DenegacionPermisosGetSerializer, PermisosGetSerializer, PermisosPostDenegacionSerializer, PermisosPostSerializer, PermisosPutDenegacionSerializer, PermisosPutSerializer, SerieSubserieUnidadCCDGetSerializer
from gestion_documental.serializers.pqr_serializers import EstadosSolicitudesGetSerializer, PQRSDFGetSerializer
from seguridad.utils import Util
from datetime import datetime
from rest_framework.permissions import IsAuthenticated


class EstadosSolicitudesGet(generics.ListAPIView):
    serializer_class = EstadosSolicitudesGetSerializer
    queryset =EstadosSolicitudes.objects.all()
    permission_classes = [IsAuthenticated]
    def get (self, request):
        instance = self.get_queryset()

        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
    
#PQRSDF
class PQRSDFGet(generics.ListAPIView):
    serializer_class = PQRSDFGetSerializer
    queryset =PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request):

        filter={}
        
        for key, value in request.query_params.items():

            if key == 'radicado':
                if value !='':
                    filter['id_radicado__nro_radicado__icontains'] = value
            if key =='estado_actual_solicitud':
                if value != '':
                    filter['id_estado_actual_solicitud__estado_solicitud__nombre__icontains'] = value    
  
        instance = self.get_queryset().filter(**filter)

        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
    