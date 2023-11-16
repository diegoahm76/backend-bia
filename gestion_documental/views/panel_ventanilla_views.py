from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
from gestion_documental.models.radicados_models import PQRSDF, ComplementosUsu_PQR, Estados_PQR, EstadosSolicitudes, SolicitudDeDigitalizacion, T262Radicados
from gestion_documental.serializers.permisos_serializers import DenegacionPermisosGetSerializer, PermisosGetSerializer, PermisosPostDenegacionSerializer, PermisosPostSerializer, PermisosPutDenegacionSerializer, PermisosPutSerializer, SerieSubserieUnidadCCDGetSerializer
from gestion_documental.serializers.ventanilla_pqrs_serializers import ComplementosUsu_PQRGetSerializer, Estados_PQRPostSerializer, EstadosSolicitudesGetSerializer, PQRSDFGetSerializer, PQRSDFPutSerializer, SolicitudDeDigitalizacionPostSerializer
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
    


        
class Estados_PQRCreate(generics.CreateAPIView):
    serializer_class = Estados_PQRPostSerializer
    queryset =Estados_PQR.objects.all()
    permission_classes = [IsAuthenticated]

    def crear_estado(self,data):
        data_in = data
        data_in['fecha_iniEstado'] = datetime.now()

        serializer = Estados_PQRPostSerializer(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'succes': True, 'detail':'Se creo el estado de la solicitud', 'data':serializer.data,}, status=status.HTTP_200_OK)
    
    def post(self, request):
        respuesta = self.crear_estado(request.data)
        return respuesta
    

class SolicitudDeDigitalizacionCreate(generics.CreateAPIView):
    serializer_class = SolicitudDeDigitalizacionPostSerializer
    serializer_pqrs = PQRSDFPutSerializer
    queryset =SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]
    creador_estados = Estados_PQRCreate
    def post(self, request):

        pqr= PQRSDF.objects.filter(id_PQRSDF=request.data['id_pqrsdf']).first()
        if not pqr:
            raise NotFound("No existe pqrsdf")
        
        if  not pqr.requiere_digitalizacion:
            raise ValidationError("No requiere digitalizacion")
        #CREA UN ESTADO NUEVO DE PQR T255
        data_estado = {}
        data_estado['PQRSDF'] = request.data['id_pqrsdf']
        data_estado['estado_solicitud'] = 3
        respuesta_estado = self.creador_estados.crear_estado(self,data_estado)
        data_respuesta_estado_asociado = respuesta_estado.data['data']
        #ASOCIAR ESTADO
        data_estado_asociado = {}
        data_estado_asociado['PQRSDF'] = request.data['id_pqrsdf'] 
        data_estado_asociado['estado_solicitud'] = 9
        data_estado_asociado['estado_PQR_asociado'] =data_respuesta_estado_asociado['id_estado_PQR']
        respuesta_estado_asociado = self.creador_estados.crear_estado(self,data_estado_asociado)
        print(respuesta_estado_asociado.data['data'])
        
        #CAMBIAMOS EL ESTADO ACTUAL DE LA PQRSDF  self.serializer_class(unidad_medida,data)
        serializador_pqrs = self.serializer_pqrs(pqr,data={'id_estado_actual_solicitud':9,'id_estado_actual_solicitud':datetime.now()},partial=True)
        serializador_pqrs.is_valid(raise_exception=True)
        prueba = serializador_pqrs.save()
        print(prueba)
        #raise ValidationError("HOLA")
        data_in = request.data
        data_in['fecha_solicitud'] = datetime.now()
        data_in['digitalizacion_completada'] = False
        data_in['devuelta_sin_completar'] = False
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,}, status=status.HTTP_200_OK)