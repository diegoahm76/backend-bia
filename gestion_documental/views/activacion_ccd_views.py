from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from gestion_documental.models.tca_models import TablasControlAcceso
from gestion_documental.models.trd_models import TablaRetencionDocumental
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental
from transversal.models.organigrama_models import Organigramas
from gestion_documental.serializers.activacion_ccd_serializers import CCDSerializer, CCDPosiblesSerializer, TRDSerializer, TCASerializer
from seguridad.utils import Util

from django.db import transaction
from datetime import datetime
import copy

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
    
class TCACambioActualPut(generics.UpdateAPIView):
    serializer_class = TCASerializer
    permission_classes = [IsAuthenticated]

    def activar_tca(self, tca_seleccionado, data_desactivar, data_activar, data_auditoria):

        previous_activacion_tca = copy.copy(tca_seleccionado)
        tca_actual = TablasControlAcceso.objects.filter(actual=True).first()

        if tca_actual:

            previous_desactivacion_tca = copy.copy(tca_actual)
            serializer = self.serializer_class(tca_actual, data=data_desactivar)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Auditoria TCA desactivado
            descripcion = {"NombreTCA":str(tca_actual.nombre),"VersionTCA":str(tca_actual.version)}
            valores_actualizados={'previous':previous_desactivacion_tca, 'current':tca_actual}
            data_auditoria['descripcion'] = descripcion
            data_auditoria['valores_actualizados'] = valores_actualizados
            Util.save_auditoria(data_auditoria)

        serializer = self.serializer_class(tca_seleccionado, data=data_activar)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Auditoria TCA activado
        descripcion = {"NombreTCA":str(tca_seleccionado.nombre),"VersionTCA":str(tca_seleccionado.version)}
        valores_actualizados={'previous':previous_activacion_tca, 'current':tca_seleccionado}
        data_auditoria['descripcion'] = descripcion
        data_auditoria['valores_actualizados'] = valores_actualizados
        Util.save_auditoria(data_auditoria)

        return Response({'success':True, 'detail':'Tabla de control de acceso activado'}, status=status.HTTP_200_OK)

class TRDCambioActualPut(generics.UpdateAPIView):
    serializer_class = TRDSerializer
    permission_classes = [IsAuthenticated]

    def activar_trd(self, trd_seleccionado, data_desactivar, data_activar, data_auditoria):

        previous_activacion_trd = copy.copy(trd_seleccionado)
        trd_actual = TablaRetencionDocumental.objects.filter(actual=True).first()

        if trd_actual:
    
            previous_desactivacion_trd = copy.copy(trd_actual)
            serializer = self.serializer_class(trd_actual, data=data_desactivar)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Auditoria TRD desactivado
            descripcion = {"NombreTRD":str(trd_actual.nombre),"VersionTRD":str(trd_actual.version)}
            valores_actualizados={'previous':previous_desactivacion_trd, 'current':trd_actual}
            data_auditoria['descripcion'] = descripcion
            data_auditoria['valores_actualizados'] = valores_actualizados
            Util.save_auditoria(data_auditoria)

        serializer = self.serializer_class(trd_seleccionado, data=data_activar)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        tca_seleccionado = TablasControlAcceso.objects.filter(id_trd=trd_seleccionado.id_trd).first()
        instancia_tca = TCACambioActualPut()
        response_tca = instancia_tca.activar_tca(tca_seleccionado, data_desactivar, data_activar, data_auditoria)

        if response_tca.status_code != status.HTTP_200_OK:
            return response_tca

        # Auditoria TRD activado
        descripcion = {"NombreTRD":str(trd_seleccionado.nombre),"VersionTRD":str(trd_seleccionado.version)}
        valores_actualizados={'previous':previous_activacion_trd, 'current':trd_seleccionado}
        data_auditoria['descripcion'] = descripcion
        data_auditoria['valores_actualizados'] = valores_actualizados
        Util.save_auditoria(data_auditoria)

        return Response({'success':True, 'detail':'Tabla de retencion documental activado'}, status=status.HTTP_200_OK)
        

@transaction.atomic
class CCDCambioActualPut(generics.UpdateAPIView):
    serializer_class = CCDSerializer
    permission_classes = [IsAuthenticated]

    def activar_ccd(self, ccd_seleccionado, data_desactivar, data_activar, data_auditoria):

        previous_activacion_ccd = copy.copy(ccd_seleccionado)
        ccd_actual = CuadrosClasificacionDocumental.objects.filter(actual=True).first()

        if ccd_actual:
    
            previous_desactivacion_ccd = copy.copy(ccd_actual)
            serializer = self.serializer_class(ccd_actual, data=data_desactivar)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Auditoria CCD desactivado
            descripcion = {"NombreCCD":str(ccd_actual.nombre),"VersionCCD":str(ccd_actual.version)}
            valores_actualizados={'previous':previous_desactivacion_ccd, 'current':ccd_actual}
            data_auditoria['descripcion'] = descripcion
            data_auditoria['valores_actualizados'] = valores_actualizados
            Util.save_auditoria(data_auditoria)

        serializer = self.serializer_class(ccd_seleccionado, data=data_activar)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        del data_activar['justificacion_nueva_version']

        trd_seleccionado = TablaRetencionDocumental.objects.filter(id_ccd=ccd_seleccionado.id_ccd).first()
        instancia_trd = TRDCambioActualPut()
        response_trd = instancia_trd.activar_trd(trd_seleccionado, data_desactivar, data_activar, data_auditoria)

        if response_trd.status_code != status.HTTP_200_OK:
            return response_trd

        # Auditoria CCD activado
        descripcion = {"NombreCCD":str(ccd_seleccionado.nombre),"VersionCCD":str(ccd_seleccionado.version)}
        valores_actualizados={'previous':previous_activacion_ccd, 'current':ccd_seleccionado}
        data_auditoria['descripcion'] = descripcion
        data_auditoria['valores_actualizados'] = valores_actualizados
        Util.save_auditoria(data_auditoria)

        return Response({'success':True, 'detail':'Cuadro de clasificacion docuemntal activado'}, status=status.HTTP_200_OK)


    def put(self, request):
        data = request.data
        ccd_actual = CuadrosClasificacionDocumental.objects.filter(actual=True).first()
        
        data_auditoria = {
            'id_usuario': request.user.id_usuario,
            'id_modulo': 16,
            'cod_permiso': 'AC',
            'subsistema': 'TRSV',
            'dirip': Util.get_client_ip(request)
        }
        
        data_desactivar = {
            'actual': False,
            'fecha_retiro_produccion': datetime.now()
            }
        
        data_activar = {
            'actual': True,
            'fecha_puesta_produccion': datetime.now()
            }
        
        try:
            ccd_seleccionado = CuadrosClasificacionDocumental.objects.get(id_ccd=data['id_ccd'])
        except CuadrosClasificacionDocumental.DoesNotExist:
            raise NotFound("El CCD seleccionado no existe")
        
        if not ccd_actual:
            data_activar['justificacion_nueva_version'] = data['justificacion']
            response_ccd = self.activar_ccd(ccd_seleccionado, data_desactivar, data_activar, data_auditoria)

        else:
            data_activar_ccd = data_activar
            data_activar_ccd['justificacion_nueva_version'] = data['justificacion']
            response_ccd = self.activar_ccd(ccd_seleccionado, data_desactivar, data_activar_ccd, data_auditoria)

        if response_ccd.status_code != status.HTTP_200_OK:
            return response_ccd

        return Response({'success':True, 'detail':'Cuadro de clasificacion docuemntal activado'}, status=status.HTTP_200_OK)
    
        