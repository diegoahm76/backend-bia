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
    permission_classes = [IsAuthenticated]

    def get_ccd_posibles_activar(self, id_organigrama):

        ccd = CuadrosClasificacionDocumental.objects.filter(fecha_retiro_produccion=None, actual=False).exclude(fecha_terminado=None)

        try:
            organigrama = Organigramas.objects.get(id_organigrama=id_organigrama)
        except Organigramas.DoesNotExist:
            raise NotFound('El organigrama ingresado no existe')
        
        if organigrama.fecha_terminado == None or organigrama.fecha_retiro_produccion != None:
            raise PermissionDenied('El organigrama ingresado ya está retirado o no está terminado')
        
        ccd_posibles_activar = ccd.filter(id_organigrama=organigrama.id_organigrama).select_related('tablaretenciondocumental__tablascontrolacceso')
        ccd_posibles = [ccd for ccd in ccd_posibles_activar if ccd.tablaretenciondocumental.tablascontrolacceso is not None]
        
        return ccd_posibles


    def get(self, request):
        id_organigrama_in = request.query_params.get('id_organigrama')
        id_organigrama = id_organigrama_in if id_organigrama_in else Organigramas.objects.filter(actual=True).first().id_organigrama
        ccd_posibles = self.get_ccd_posibles_activar(id_organigrama)
        serializer = self.serializer_class(ccd_posibles, many=True)

        return Response({'success':True, 'detail':'Los CCD posibles que se pueden activar son los siguientes', 'data': serializer.data}, status=status.HTTP_200_OK)


