from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
from gestion_documental.models.radicados_models import PQRSDF, ComplementosUsu_PQR, EstadosSolicitudes, SolicitudDeDigitalizacion, T262Radicados
from gestion_documental.serializers.permisos_serializers import DenegacionPermisosGetSerializer, PermisosGetSerializer, PermisosPostDenegacionSerializer, PermisosPostSerializer, PermisosPutDenegacionSerializer, PermisosPutSerializer, SerieSubserieUnidadCCDGetSerializer
from gestion_documental.serializers.ventanilla_pqrs_serializers import ComplementosUsu_PQRGetSerializer, EstadosSolicitudesGetSerializer, PQRSDFGetSerializer, SolicitudDeDigitalizacionPostSerializer
from seguridad.utils import Util
from datetime import datetime
from rest_framework.permissions import IsAuthenticated


class EstadosSolicitudesGet(generics.ListAPIView):
    serializer_class = EstadosSolicitudesGetSerializer
    queryset =EstadosSolicitudes.objects.all()
    permission_classes = [IsAuthenticated]
    def get (self, request):
        instance = self.get_queryset().filter(aplica_para_pqrsdf=True)

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
        tipo_busqueda = 'PQRSDF'
        data_respuesta = []
        filter={}
        
        for key, value in request.query_params.items():

            if key == 'radicado':
                if value !='':
                    filter['id_radicado__nro_radicado__icontains'] = value
            if key =='estado_actual_solicitud':
                if value != '':
                    filter['id_estado_actual_solicitud__estado_solicitud__nombre__icontains'] = value    
            if key == 'tipo_solicitud':
                if value != '':
                    tipo_busqueda = False
        
        if tipo_busqueda == 'PQRSDF':
            instance = self.get_queryset().filter(**filter).order_by('fecha_radicado')

            if not instance:
                raise NotFound("No existen registros")

            serializador = self.serializer_class(instance,many=True)
            data_respuesta = serializador.data
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_respuesta,}, status=status.HTTP_200_OK)
    

class PQRSDFGetDetalle(generics.ListAPIView):

    serializer_class = ComplementosUsu_PQRGetSerializer
    queryset =ComplementosUsu_PQR.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pqr):
        
        instance = self.get_queryset().filter(id_PQRSDF=pqr)
        if not instance:
            raise NotFound("No existen registros")
        
        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
    

class SolicitudDeDigitalizacionCreate(generics.CreateAPIView):
    serializer_class = SolicitudDeDigitalizacionPostSerializer
    queryset =SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data_in = request.data

        data_in['fecha_solicitud'] = datetime.now()
        data_in['digitalizacion_completada'] = False
        data_in['devuelta_sin_completar'] = False
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,}, status=status.HTTP_200_OK)
        
        