from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from gestion_documental.models.tca_models import TablasControlAcceso
from gestion_documental.models.trd_models import TablaRetencionDocumental
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental
from transversal.models.organigrama_models import Organigramas
from gestion_documental.serializers.activacion_ccd_serializers import CCDSerializer, CCDPosiblesSerializer, TRDSerializer, TCASerializer


class CCDActualGetView(generics.ListAPIView):
    serializer_class = CCDSerializer
    permission_classes = [IsAuthenticated]

    def get_ccd_actual(self):
        ccd_actual = CuadrosClasificacionDocumental.objects.filter(actual=True).first()
        return ccd_actual
    
    def get(self, request):
        ccd_actual = self.get_ccd_actual()

        if not ccd_actual:
            raise NotFound('No existe un CCD actual')
        
        serializer = self.serializer_class(ccd_actual)
        
        return Response({'success':True, 'detail':'CCD Actual', 'data': serializer.data}, status=status.HTTP_200_OK)


class GetCCDPosiblesActivar(generics.ListAPIView):
    serializer_class = CCDPosiblesSerializer
    queryset = CuadrosClasificacionDocumental.objects.filter(fecha_retiro_produccion=None, actual=False).exclude(fecha_terminado=None)

    def get(self, request):
        id_organigrama = request.query_params.get('id_organigrama')

        ccd_queryset = self.queryset.filter(id_organigrama__actual=True).select_related('tablaretenciondocumental__tablascontrolacceso') if not id_organigrama else self.queryset.filter(id_organigrama=id_organigrama).select_related('tablaretenciondocumental__tablascontrolacceso')

        ccd_posibles = [ccd for ccd in ccd_queryset if ccd.tablaretenciondocumental.tablascontrolacceso is not None]

        serializer = self.serializer_class(ccd_posibles, many=True)

        return Response({'success':True, 'detail':'Los CCD posibles que se pueden activar son los siguientes', 'data': serializer.data}, status=status.HTTP_200_OK)


class CCDTerminadoByOrganigramaGetListView(generics.ListAPIView):
    serializer_class = CCDSerializer
    permission_classes = [IsAuthenticated]

    def get_ccd_terminado_by_organigrama(self, id_organigrama):

        try: 
            organigrama = Organigramas.objects.get(id_organigrama=id_organigrama)
        except Organigramas.DoesNotExist:
            raise NotFound('El organigrama ingresado no existe')
        
        if organigrama.fecha_terminado == None or organigrama.fecha_retiro_produccion != None:
            raise PermissionDenied('El organigrama ingresado ya está retirado o no está terminado')
        
        ccd_terminado_by_organigrama = CuadrosClasificacionDocumental.objects.filter(id_organigrama=organigrama.id_organigrama, fecha_retiro_produccion=None).exclude(fecha_terminado=None)
        
        return ccd_terminado_by_organigrama

    def get(self, request, id_organigrama):
        ccd_terminado_by_organigrama = self.get_ccd_terminado_by_organigrama(id_organigrama)
        serializer = self.serializer_class(ccd_terminado_by_organigrama, many=True)
        return Response({'success':True, 'detail':'CCD', 'data': serializer.data}, status=status.HTTP_200_OK)