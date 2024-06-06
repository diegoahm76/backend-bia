import os
from io import BytesIO
import re
import requests
import base64

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from gestion_documental.models.bandeja_tareas_models import AdicionalesDeTareas, TareasAsignadas
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad,CatalogosSeriesUnidad,SeriesDoc,SubseriesDoc,CuadrosClasificacionDocumental
from gestion_documental.models.conf__tipos_exp_models import ConfiguracionTipoExpedienteAgno
from gestion_documental.models.configuracion_tiempos_respuesta_models import ConfiguracionTiemposRespuesta
from gestion_documental.models.expedientes_models import ArchivosDigitales, ExpedientesDocumentales, IndicesElectronicosExp
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
from gestion_documental.models.plantillas_models import PlantillasDoc
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, AsignacionOtros, AsignacionPQR, AsignacionTramites, BandejaTareasPersona, ComplementosUsu_PQR, ConfigTiposRadicadoAgno, Estados_PQR, EstadosSolicitudes, InfoDenuncias_PQRSDF, MetadatosAnexosTmp, Otros, SolicitudAlUsuarioSobrePQRSDF, SolicitudDeDigitalizacion, T262Radicados
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, ConfigTipologiasDocAgno, ConsecutivoTipologia, TipologiasDoc
from gestion_documental.serializers.expedientes_serializers import AperturaExpedienteComplejoSerializer, AperturaExpedienteSimpleSerializer
from gestion_documental.serializers.permisos_serializers import DenegacionPermisosGetSerializer, PermisosGetSerializer, PermisosPostDenegacionSerializer, PermisosPostSerializer, PermisosPutDenegacionSerializer, PermisosPutSerializer, SerieSubserieUnidadCCDGetSerializer
from gestion_documental.serializers.plantillas_serializers import PlantillasDocBusquedaAvanzadaSerializer
from gestion_documental.serializers.ventanilla_pqrs_serializers import ActosAdministrativosCreateSerializer, AdicionalesDeTareasCreateSerializer, AnexoArchivosDigitalesSerializer, Anexos_PQRAnexosGetSerializer, Anexos_PQRCreateSerializer, AnexosComplementoGetSerializer, AnexosCreateSerializer, AnexosDocumentoDigitalGetSerializer, AnexosGetSerializer, AsignacionOtrosGetSerializer, AsignacionOtrosPostSerializer, AsignacionPQRGetSerializer, AsignacionPQRPostSerializer, AsignacionTramiteGetSerializer, AsignacionTramiteOpaGetSerializer, AsignacionTramitesPostSerializer, ComplementosUsu_PQRGetSerializer, ComplementosUsu_PQRPutSerializer, Estados_OTROSSerializer, Estados_PQRPostSerializer, Estados_PQRSerializer, EstadosSolicitudesGetSerializer, InfoDenuncias_PQRSDFGetByPqrsdfSerializer, LiderGetSerializer, MetadatosAnexosTmpCreateSerializer, MetadatosAnexosTmpGetSerializer, MetadatosAnexosTmpSerializerGet, OPADetalleHistoricoSerializer, OPAGetHistoricoSerializer, OPAGetRefacSerializer, OPAGetSerializer, OtrosGetHistoricoSerializer, OtrosGetSerializer, OtrosPutSerializer, PQRSDFCabezeraGetSerializer, PQRSDFDetalleSolicitud, PQRSDFGetSerializer, PQRSDFHistoricoGetSerializer, PQRSDFPutSerializer, PQRSDFTitularGetSerializer, RespuestasRequerimientosOpaGetSerializer, RespuestasRequerimientosPutGetSerializer, RespuestasRequerimientosPutSerializer, SolicitudAlUsuarioSobrePQRSDFCreateSerializer, SolicitudAlUsuarioSobrePQRSDFGetDetalleSerializer, SolicitudAlUsuarioSobrePQRSDFGetSerializer, SolicitudDeDigitalizacionGetSerializer, SolicitudDeDigitalizacionPostSerializer, SolicitudJuridicaOPACreateSerializer, SolicitudesTramitesGetSerializer, TramitePutSerializer, TramitesComplementosUsu_PQRGetSerializer, TramitesGetHistoricoComplementoSerializer, TramitesGetHistoricoSerializer, UnidadesOrganizacionalesSecSubVentanillaGetSerializer, UnidadesOrganizacionalesSerializer,CatalogosSeriesUnidadGetSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.views.bandeja_tareas_views import  TareaBandejaTareasPersonaCreate, TareasAsignadasCreate
from django.core.files.base import ContentFile
from gestion_documental.views.conf__tipos_exp_views import ConfiguracionTipoExpedienteAgnoGetConsect
from recaudo.models.liquidaciones_models import LiquidacionesBase
from seguridad.permissions.permissions_gestor import PermisoActualizarResponderRequerimientoOPA, PermisoCrearAsignacionSubseccion, PermisoCrearResponderRequerimientoOPA, PermisoCrearSolicitudComplementoPQRSDF
from seguridad.utils import Util
from gestion_documental.utils import UtilsGestor
from datetime import date, datetime
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from tramites.models.tramites_models import ActosAdministrativos, AnexosTramite, PermisosAmbSolicitudesTramite, RespuestasRequerimientos, SolicitudesDeJuridica, SolicitudesTramites, Tramites
from transversal.models.lideres_models import LideresUnidadesOrg
from django.db.models import Max
from transversal.models.organigrama_models import Organigramas, UnidadesOrganizacionales
import json
from gestion_documental.choices.tipo_archivo_choices import tipo_archivo_CHOICES
from transversal.models.personas_models import Personas
from transversal.views.alertas_views import AlertaEventoInmediadoCreate
from docxtpl import DocxTemplate
from reportlab.pdfgen import canvas
from io import BytesIO
#from gestion_documental.views.trd_views import ConsecutivoTipologiaDoc


#CREACION DEL EXPEDIENTE
class SerieSubserioUnidadGet(generics.ListAPIView):

    serializer_class = CatalogosSeriesUnidadGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get (self, request,uni):

        instance=CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=uni)

        if not instance:
            raise NotFound("No existen registros asociados.")
        
        serializador=self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data}, status=status.HTTP_200_OK)


class EstadosSolicitudesGet(generics.ListAPIView):
    serializer_class = EstadosSolicitudesGetSerializer
    queryset =EstadosSolicitudes.objects.all()
    permission_classes = [IsAuthenticated]
    def get (self, request):
        instance = self.get_queryset().filter(aplica_para_pqrsdf=True)
        instance = self.get_queryset().filter(aplica_para_pqrsdf=True, id_estado_solicitud__in=[2,3,4,5])


        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
    
#PQRSDF
class PQRSDFGet(generics.ListAPIView):
    serializer_class = PQRSDFGetSerializer
    queryset =PQRSDF.objects.all()
    # queryset = PQRSDF.objects.annotate(mezcla=Concat(F('id_radicado__prefijo_radicado'), Value('-'), F('id_radicado__agno_radicado'),
    #                                                   Value('-'), F('id_radicado__nro_radicado'), output_field=CharField()))
                                              
    permission_classes = [IsAuthenticated]


    def get (self, request):
        tipo_busqueda = 'PQRSDF'
        data_respuesta = []
        filter={}
        
        for key, value in request.query_params.items():

            # if key == 'radicado':
            #     if value !='':
            #         filter['mezcla__icontains'] = value
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
            if key == 'tipo_PQRSDF':
                if value != '':
                    filter['cod_tipo_PQRSDF__icontains'] = value
        

        filter['id_radicado__isnull'] = False
        instance = self.get_queryset().filter(**filter).order_by('fecha_radicado')
        radicado_value = request.query_params.get('radicado')
        print(radicado_value)
        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance,many=True)
        data_respuesta = serializador.data
        data_validada =[]
        if radicado_value and radicado_value != '':
            data_validada = [item for item in serializador.data if radicado_value in item.get('radicado', '')]
        else :
            data_validada = data_respuesta
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_validada,}, status=status.HTTP_200_OK)
    

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
        

        serializer = Estados_PQRPostSerializer(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'succes': True, 'detail':'Se creo el estado de la solicitud', 'data':serializer.data,}, status=status.HTTP_200_OK)
    
    def post(self, request):
        respuesta = self.crear_estado(request.data)
        return respuesta
    
class Estados_PQRDelete(generics.RetrieveDestroyAPIView):
    serializer_class = Estados_PQRSerializer
    queryset = Estados_PQR.objects.all()

    @transaction.atomic
    def delete(self, id_PQRSDF):
        try:
            with transaction.atomic():
                estado_pqr = self.queryset.filter(PQRSDF = id_PQRSDF).first()
                if estado_pqr:
                    estado_pqr.delete()
                    return Response({'success':True, 'detail':'El estado del pqr ha sido eliminado exitosamente'}, status=status.HTTP_200_OK)
                else:
                    raise NotFound('No se encontró ningún estado pqr asociado al anexo')
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    



#OTROS
class Estados_OTROSDelete(generics.RetrieveDestroyAPIView):
    serializer_class = Estados_OTROSSerializer
    queryset = Estados_PQR.objects.all()

    @transaction.atomic
    def delete(self, id_otros):
        try:
            with transaction.atomic():
                estado_otros = self.queryset.filter(OTROS = id_otros).first()
                if estado_otros:
                    estado_otros.delete()
                    return Response({'success':True, 'detail':'El estado de la solicitud otro ha sido eliminado exitosamente'}, status=status.HTTP_200_OK)
                else:
                    raise NotFound('No se encontró ningún estado otro asociado al anexo')
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


        
class SolicitudDeDigitalizacionCreate(generics.CreateAPIView):
    serializer_class = SolicitudDeDigitalizacionPostSerializer
    serializer_pqrs = PQRSDFPutSerializer
    queryset =SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]
    creador_estados = Estados_PQRCreate
    def post(self, request):
        fecha_actual = datetime.now()    
        pqr= PQRSDF.objects.filter(id_PQRSDF=request.data['id_pqrsdf']).first()
        if not pqr:
            raise NotFound("No existe pqrsdf")
        
        if  not pqr.requiere_digitalizacion:
            raise ValidationError("No requiere digitalizacion")
        print(pqr.id_estado_actual_solicitud)
        if pqr.id_estado_actual_solicitud:
            if pqr.id_estado_actual_solicitud.id_estado_solicitud == 3:
                raise ValidationError('No se puede realizar la solicitud porque tiene pendientes')
        
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_pqrsdf=request.data['id_pqrsdf'])
        for solicitude in solicitudes:
            if  not solicitude.fecha_rta_solicitud:
                raise ValidationError('No se puede realizar la solicitud porque tiene pendientes')
        #CREA UN ESTADO NUEVO DE PQR T255
        data_estado = {}
        data_estado['PQRSDF'] = request.data['id_pqrsdf']
        data_estado['estado_solicitud'] = 3
        data_estado['fecha_iniEstado'] = fecha_actual
        respuesta_estado = self.creador_estados.crear_estado(self,data_estado)
        data_respuesta_estado_asociado = respuesta_estado.data['data']
        #ASOCIAR ESTADO
        data_estado_asociado = {}
        data_estado_asociado['PQRSDF'] = request.data['id_pqrsdf'] 
        data_estado_asociado['estado_solicitud'] = 9
        data_estado_asociado['estado_PQR_asociado'] =data_respuesta_estado_asociado['id_estado_PQR']
        data_estado_asociado['fecha_iniEstado'] = fecha_actual
        respuesta_estado_asociado = self.creador_estados.crear_estado(self,data_estado_asociado)
        
        
        #CAMBIAMOS EL ESTADO ACTUAL DE LA PQRSDF  self.serializer_class(unidad_medida,data)
        serializador_pqrs = self.serializer_pqrs(pqr,data={'id_estado_actual_solicitud':3,'fecha_envio_definitivo_a_digitalizacion':datetime.now(),'fecha_digitalizacion_completada':datetime.now()},partial=True)
        serializador_pqrs.is_valid(raise_exception=True)
        prueba = serializador_pqrs.save()
        
       
        data_in = request.data
        data_in['fecha_solicitud'] = fecha_actual
        data_in['digitalizacion_completada'] = False
        data_in['devuelta_sin_completar'] = False
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,'estados':respuesta_estado_asociado.data['data']}, status=status.HTTP_200_OK)
    



class SolicitudDeDigitalizacionComplementoCreate(generics.CreateAPIView):
    serializer_class = SolicitudDeDigitalizacionPostSerializer
    serializer_complemento = ComplementosUsu_PQRPutSerializer
    queryset =SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated, PermisoCrearSolicitudComplementoPQRSDF]
    #creador_estados = Estados_PQRCreate
    def post(self, request):
        data_in = request.data

        complemento= ComplementosUsu_PQR.objects.filter(idComplementoUsu_PQR=request.data['id_complemento_usu_pqr']).first()
        if not complemento:
            raise NotFound("No existe pqrsdf")
        
        if  not complemento.requiere_digitalizacion:
            raise ValidationError("No requiere digitalizacion")
        data_in['fecha_solicitud'] = datetime.now()
        data_in['digitalizacion_completada'] = False
        data_in['devuelta_sin_completar'] = False
        data_in['id_persona_digitalizo'] = request.user.persona.id_persona

        #print(pqr.id_estado_actual_solicitud)
        #valida si tiene solicitudess pendientes
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_complemento_usu_pqr=request.data['id_complemento_usu_pqr'])
        for solicitude in solicitudes:
            if  not solicitude.fecha_rta_solicitud:
                raise ValidationError('No se puede realizar la solicitud porque tiene pendientes')
        
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        #Actualizacion de fecha de complemento
        data_complemento = {}
        data_complemento['fecha_envio_definitivo_digitalizacion'] = datetime.now()
        complemento_serializer = self.serializer_complemento(complemento,data=data_complemento,partial=True )
        complemento_serializer.is_valid(raise_exception=True)
        complemento_serializer.save()
        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,'complemento':complemento_serializer.data}, status=status.HTTP_200_OK)



class CabezerasPQRSDFGet(generics.ListAPIView):
    serializer_class = PQRSDFCabezeraGetSerializer
    queryset =PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]

    def get (self, request):
        
        data_respuesta = []
        filter={}
        filter['id_radicado__isnull'] = False
        radicado = None
        for key, value in request.query_params.items():

            if key == 'radicado':
                if value !='':
                   
                    radicado = value

            if key == 'fecha_inicio':
                if value != '':
                    
                    filter['fecha_radicado__gte'] = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'fecha_fin':
                if value != '':
                    filter['fecha_radicado__lte'] = datetime.strptime(value, '%Y-%m-%d').date()
 
            if key =='estado_actual_solicitud':
                if value != '':
                    filter['id_estado_actual_solicitud__estado_solicitud__nombre__icontains'] = value  
            if key == 'fecha_radicado':
                if value != '':
                    filter['fecha_radicado'] = datetime.strptime(value, '%Y-%m-%d').date()  

        
        
        instance = self.queryset.filter(**filter).order_by('fecha_radicado')

        ##
        serializador = self.serializer_class(instance,many=True)
        data_respuesta = serializador.data


        serializador = self.serializer_class(instance,many=True)
        data_respuesta = serializador.data
        data_validada =[]
       
        if radicado and radicado != '':
            data_validada = [item for item in serializador.data if radicado in item.get('cabecera', {}).get('radicado', '')]
        else :
            data_validada = data_respuesta


        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_validada,}, status=status.HTTP_200_OK)


class Historico_Solicitud_PQRSDFGet(generics.ListAPIView):
    serializer_class = PQRSDFHistoricoGetSerializer
    queryset =PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pqr):

        instance =PQRSDF.objects.filter(id_PQRSDF=pqr).first()

        if not instance:
                raise NotFound("No existen registros")

        serializador = self.serializer_class(instance)
        data_respuesta = serializador.data
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_respuesta,}, status=status.HTTP_200_OK)



class PQRSDFInfoGet(generics.ListAPIView):
    serializer_class = AnexosGetSerializer
    queryset =PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pqr):
        data=[]
        instance =PQRSDF.objects.filter(id_PQRSDF=pqr).first()


        if not instance:
                raise NotFound("No existen registros")
        anexos_pqrs = Anexos_PQR.objects.filter(id_PQRSDF=instance)
        for x in anexos_pqrs:
            info_anexo =x.id_anexo
            data_anexo = self.serializer_class(info_anexo)
            data.append(data_anexo.data)
        
        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data,}, status=status.HTTP_200_OK)

class PQRSDFAnexoDocumentoDigitalGet(generics.ListAPIView):
    serializer_class = AnexoArchivosDigitalesSerializer
    queryset =Anexos.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
      
        instance =Anexos.objects.filter(id_anexo=pk).first()

        if not instance:
                raise NotFound("No existen registros")
        
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=instance.id_anexo).first()
        if not meta_data:
            raise NotFound("No existen registros")
        archivo = meta_data.id_archivo_sistema
        serializer= self.serializer_class(archivo)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'id_anexo':instance.id_anexo,**serializer.data},}, status=status.HTTP_200_OK)
    

class PQRSDFAnexoMetaDataGet(generics.ListAPIView):
    serializer_class = MetadatosAnexosTmpSerializerGet
    queryset =Anexos.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
      
        instance =Anexos.objects.filter(id_anexo=pk).first()

        if not instance:
                raise NotFound("No existen registros")
        
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=instance.id_anexo).first()
        if not meta_data:
            raise NotFound("No existen registros")
   
        serializer= self.serializer_class(meta_data)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'id_anexo':instance.id_anexo,**serializer.data},}, status=status.HTTP_200_OK)

class ComplementoPQRSDFInfoAnexosGet(generics.ListAPIView):
    serializer_class = AnexosComplementoGetSerializer
    queryset =ComplementosUsu_PQR.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
        data=[]
        instance =self.queryset.filter(idComplementoUsu_PQR=pk).first()


        if not instance:
                raise NotFound("No existen registros")
        anexos_pqrs = Anexos_PQR.objects.filter(id_complemento_usu_PQR=instance)
        for x in anexos_pqrs:
            info_anexo =x.id_anexo
            data_anexo = self.serializer_class(info_anexo)
            data.append(data_anexo.data)
        
        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data,}, status=status.HTTP_200_OK)



class ComplementoPQRSDFAnexoDocumentoDigitalGet(generics.ListAPIView):
    serializer_class = AnexoArchivosDigitalesSerializer
    queryset =Anexos.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
      
        instance =Anexos.objects.filter(id_anexo=pk).first()

        if not instance:
                raise NotFound("No existen registros")
        
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=instance.id_anexo).first()
        if not meta_data:
            raise NotFound("No existen registros")
        archivo = meta_data.id_archivo_sistema
        serializer= self.serializer_class(archivo)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'id_anexo':instance.id_anexo,**serializer.data},}, status=status.HTTP_200_OK)
    


class ComplementoPQRSDFAnexoMetaDataGet(generics.ListAPIView):
    serializer_class = MetadatosAnexosTmpSerializerGet
    queryset =Anexos.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
      
        instance =Anexos.objects.filter(id_anexo=pk).first()

        if not instance:
                raise NotFound("No existen registros")
        
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=instance.id_anexo).first()
        if not meta_data:
            raise NotFound("No existen registros")
   
        serializer= self.serializer_class(meta_data)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'id_anexo':instance.id_anexo,**serializer.data},}, status=status.HTTP_200_OK)
    


#ASIGNACION DE PQRSDF A SECCCION ,SUBSECCION O GRUPO
class SeccionSubseccionVentanillaGet(generics.ListAPIView):
    serializer_class = UnidadesOrganizacionalesSecSubVentanillaGetSerializer
    queryset = UnidadesOrganizacionales.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request):
        organigrama = Organigramas.objects.filter(actual=True)
        if not organigrama:
            raise NotFound('No existe ningún organigrama activado')
        if len(organigrama) > 1:
            raise PermissionDenied('Existe más de un organigrama actual, contacte a soporte')
        organigrama_actual = organigrama.first()
        #unidades_organigrama_actual = UnidadesOrganizacionales.objects.filter(id_organigrama=organigrama_actual.id_organigrama)

        unidades = UnidadesOrganizacionales.objects.filter(cod_agrupacion_documental__in = ['SEC','SUB'],id_organigrama=organigrama_actual.id_organigrama)
        
        
        serializer = self.serializer_class(unidades,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    
class SubseccionGrupoVentanillaGet(generics.ListAPIView):
    serializer_class = UnidadesOrganizacionalesSecSubVentanillaGetSerializer
    serializer_unidad = UnidadesOrganizacionalesSecSubVentanillaGetSerializer
    queryset = UnidadesOrganizacionales.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,uni):
        
        unidad = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = uni).first()
        if not unidad:
            raise NotFound("No existen registros")
        unidades = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre = unidad.id_unidad_organizacional)
        
        
        lista = list(unidades)
        lista.insert(0,unidad)
        serializer = self.serializer_class(lista,many=True)

        #return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'seccion':serializer_unidad.data,'hijos':serializer.data}}, status=status.HTTP_200_OK)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    
class PersonaLiderUnidadGet(generics.ListAPIView):
    serializer_class = LiderGetSerializer
    queryset = UnidadesOrganizacionales.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,uni):
        
        unidad = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = uni).first()
        if not unidad:
            raise NotFound("No existen registros")
        
        lider = LideresUnidadesOrg.objects.filter(id_unidad_organizacional = unidad.id_unidad_organizacional).first()
        if not lider:
            raise ValidationError("No tiene lider asignado")
        if not lider.id_persona:
            raise ValidationError("No tiene lider asignado")
        serializer = self.serializer_class(lider)


        #return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'seccion':serializer_unidad.data,'hijos':serializer.data}}, status=status.HTTP_200_OK)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    
class AsignacionPQRUpdate(generics.UpdateAPIView):

    serializer_class = AsignacionPQRPostSerializer
    permission_classes = [IsAuthenticated]
    queryset =AsignacionPQR.objects.all()

    def actualizar_asignacion(self,data,pk):
        data_in = data
        instance = AsignacionPQR.objects.filter(id_asignacion_pqr=pk).first()

        if not instance:
            raise NotFound("No existen registros")
        serializer = AsignacionPQRPostSerializer(instance,data=data_in,partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response	({'succes': True, 'detail':'Se actualizo el registro', 'data':serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        data_in = request.data
        respuesta = self.actualizar_asignacion(data_in,pk)
        return respuesta
       

class AsignacionPQRCreate(generics.CreateAPIView):
    serializer_class = AsignacionPQRPostSerializer
    queryset =AsignacionPQR.objects.all()
    permission_classes = [IsAuthenticated, PermisoCrearAsignacionSubseccion]
    creador_estados = Estados_PQRCreate
    def post(self, request):
        #CODIGO DE SERIE DOCUMENTAL DE PQRSDF
        codigo= 39      
        contador = 0  
        data_in = request.data

        if not 'id_pqrsdf' in data_in:
            raise ValidationError("No se envio la pqrsdf")
        
        instance= AsignacionPQR.objects.filter(id_pqrsdf = data_in['id_pqrsdf'])
        for asignacion in instance:
            #print(asignacion)
            if asignacion.cod_estado_asignacion == 'Ac':
                raise ValidationError("La solicitud  ya fue Aceptada.")
            if  not asignacion.cod_estado_asignacion:
                raise ValidationError("La solicitud esta pendiente por respuesta.")
        max_consecutivo = AsignacionPQR.objects.filter(id_pqrsdf=data_in['id_pqrsdf']).aggregate(Max('consecutivo_asign_x_pqrsdf'))

        if max_consecutivo['consecutivo_asign_x_pqrsdf__max'] == None:
             ultimo_consec= 1
        else:
            ultimo_consec = max_consecutivo['consecutivo_asign_x_pqrsdf__max'] + 1
        
        unidad_asignar = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=data_in['id_und_org_seccion_asignada']).first()
        if not unidad_asignar:
            raise ValidationError("No existe la unidad asignada")
        #VALIDACION ENTREGA 102 SERIE PQRSDF
        aux = unidad_asignar
        while aux:
            
            #print(str(aux.id_unidad_organizacional)+str(aux.cod_agrupacion_documental))
            if aux.cod_agrupacion_documental == 'SEC':
               
                catalogos = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=aux.id_unidad_organizacional,id_catalogo_serie__id_subserie_doc__isnull=True)
                #print(catalogos)
                contador = 0
                for catalogo in catalogos:
                    #print(str(catalogo.id_catalogo_serie.id_serie_doc.id_serie_doc)+"###"+str(catalogo.id_catalogo_serie.id_serie_doc.codigo)+" "+str(catalogo.id_catalogo_serie.id_serie_doc.nombre))
                    if int(catalogo.id_catalogo_serie.id_serie_doc.codigo) == codigo:
                        contador += 1

                break
            aux = aux.id_unidad_org_padre
        # if contador == 0:
        #     raise ValidationError("No se puede realizar la asignación de la PQRSDF a una  unidad organizacional seleccionada porque no tiene serie  documental de PQRSDF")
        data_in['consecutivo_asign_x_pqrsdf'] = ultimo_consec 
        data_in['fecha_asignacion'] = datetime.now()
        data_in['id_persona_asigna'] = request.user.persona.id_persona
        data_in['cod_estado_asignacion'] = None
        data_in['asignacion_de_ventanilla'] = True


        #ASOCIAR ESTADO
        data_estado_asociado = {}
        data_estado_asociado['PQRSDF'] = request.data['id_pqrsdf'] 
        data_estado_asociado['estado_solicitud'] = 5
        #data_estado_asociado['estado_PQR_asociado'] 
        data_estado_asociado['fecha_iniEstado'] =  datetime.now()
        data_estado_asociado['persona_genera_estado'] = request.user.persona.id_persona
        #raise ValidationError("NONE")
        respuesta_estado_asociado = self.creador_estados.crear_estado(self,data_estado_asociado)
        data_estado = respuesta_estado_asociado.data['data']
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        #Crear tarea y asignacion de tarea
       
        id_persona_asiganada = serializer.data['id_persona_asignada']

 
        #Creamos la tarea 315
        data_tarea = {}
        data_tarea['cod_tipo_tarea'] = 'Rpqr'
        data_tarea['id_asignacion'] = serializer.data['id_asignacion_pqr']
        data_tarea['fecha_asignacion'] = datetime.now()

        data_tarea['cod_estado_solicitud'] = 'Ep'
        vista_tareas = TareasAsignadasCreate()    
        respuesta_tareas = vista_tareas.crear_asignacion_tarea(data_tarea)
        if respuesta_tareas.status_code != status.HTTP_201_CREATED:
            return respuesta_tareas
        data_tarea_respuesta= respuesta_tareas.data['data']
        #Teniendo la bandeja de tareas,la tarea ahora tenemos que asignar esa tarea a la bandeja de tareas
        id_tarea_asiganada = data_tarea_respuesta['id_tarea_asignada']
        vista_asignacion = TareaBandejaTareasPersonaCreate()

        data_tarea_bandeja_asignacion = {}
        data_tarea_bandeja_asignacion['id_persona'] = id_persona_asiganada
        data_tarea_bandeja_asignacion['id_tarea_asignada'] = id_tarea_asiganada
        data_tarea_bandeja_asignacion['es_responsable_ppal'] = True
        respuesta_relacion = vista_asignacion.crear_tarea(data_tarea_bandeja_asignacion)
        if respuesta_relacion.status_code != status.HTTP_201_CREATED:
            return respuesta_relacion
        #CREAMOS LA ALERTA DE ASIGNACION A GRUPO 

        persona =Personas.objects.filter(id_persona = id_persona_asiganada).first()
        nombre_completo_persona = ''
        if persona:
            nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                            persona.primer_apellido, persona.segundo_apellido]
            nombre_completo_persona = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_persona = nombre_completo_persona if nombre_completo_persona != "" else None
       
        mensaje = "Tipo de solicitud : PQRSDF \n Unidad Organizacional : "+unidad_asignar.nombre+" \n Lider de Unidad Organizacional: "+nombre_completo_persona+" \n Fecha de asignacion : "+str(serializer.data['fecha_asignacion'])
        vista_alertas_programadas = AlertaEventoInmediadoCreate()
        data_alerta = {}
        data_alerta['cod_clase_alerta'] = 'Gst_SlALid'
        data_alerta['id_persona'] = id_persona_asiganada
        data_alerta['id_elemento_implicado'] = serializer.data['id_asignacion_pqr']
        data_alerta['informacion_complemento_mensaje'] = mensaje

        respuesta_alerta = vista_alertas_programadas.crear_alerta_evento_inmediato(data_alerta)
        if respuesta_alerta.status_code != status.HTTP_200_OK:
            return respuesta_alerta


        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,'estado':data_estado,'tarea':respuesta_relacion.data['data']}, status=status.HTTP_200_OK)




class AsignacionPQRGet(generics.ListAPIView):
    serializer_class = AsignacionPQRGetSerializer
    queryset = AsignacionPQR.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,pqr):
        
        instance = self.get_queryset().filter(id_pqrsdf=pqr)
        if not instance:
            raise NotFound("No existen registros")
        
        serializer = self.serializer_class(instance,many=True)

        #return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'seccion':serializer_unidad.data,'hijos':serializer.data}}, status=status.HTTP_200_OK)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    

##ENTREGA 99
class PQRSDFPersonaTitularGet(generics.ListAPIView):
    serializer_class = PQRSDFTitularGetSerializer
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,pqr):
        
        instance = self.get_queryset().filter(id_PQRSDF=pqr).first()
        if not instance:
            raise NotFound("No existen registros")
        persona_titular = instance.id_persona_titular 
        serializer = self.serializer_class(persona_titular)

        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)

class PQRSDFPersonaSolicitaGet(generics.ListAPIView):
    serializer_class = PQRSDFTitularGetSerializer
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request):
        persona = request.user.persona
        

        serializer = self.serializer_class(persona)

        #return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'seccion':serializer_unidad.data,'hijos':serializer.data}}, status=status.HTTP_200_OK)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    

class PQRSDFDetalleSolicitudGet(generics.ListAPIView):
    serializer_class = PQRSDFDetalleSolicitud
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,pqr):
        
        instance = self.get_queryset().filter(id_PQRSDF=pqr).first()
        if not instance:
            raise NotFound("No existen registros")
        persona_titular = instance.id_persona_titular 
        serializer = self.serializer_class(instance)

      
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    

class SolicitudAlUsuarioSobrePQRSDFGet(generics.ListAPIView):
    serializer_class = PQRSDFDetalleSolicitud
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,pqr):
        
        instance = self.get_queryset().filter(id_PQRSDF=pqr).first()
        if not instance:
            raise NotFound("No existen registros")
    
        serializer = self.serializer_class(instance)

      
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)


#Anexos

class AnexosCreate(generics.CreateAPIView):
    serializer_class = AnexosCreateSerializer
    queryset = Anexos.objects.all()
    permission_classes = [IsAuthenticated]
    archivos_Digitales = ArchivosDgitalesCreate()

    def crear_anexo(self,data):
        data_in = data

        # data_archivos=request.FILES['archivo']
        # data_archivo = {}
        # if  data_archivos:
        #     ruta = "home,BIA,Otros,PQRSDF,Complementos"
        #     respuesta_archivo = self.archivos_Digitales.crear_archivo({"ruta":ruta,'es_Doc_elec_archivo':False},data_archivos)
        #     data_archivo = respuesta_archivo.data['data']
        data_in['ya_digitalizado'] = True
        serializer = AnexosCreateSerializer(data=data_in)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'succes': True, 'detail':'Se creo el anexo', 'data':serializer.data,}, status=status.HTTP_200_OK)

    def post(self, request):
        respuesta = self.crear_anexo(request.data)
        return respuesta

class MetadatosAnexosTmpCreate(generics.CreateAPIView):
    serializer_class = MetadatosAnexosTmpCreateSerializer
    queryset = MetadatosAnexosTmp.objects.all()
    permission_classes = [IsAuthenticated]

    def crear_meta_data(self,data):
        data_in = data
        data_in['fecha_creacion_doc'] = datetime.now()
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'succes': True, 'detail':'Se creo el anexo', 'data':serializer.data}, status=status.HTTP_200_OK)

    
    def post(self, request):
        data_in = request.data
        respuesta = self.crear_meta_data(data_in)
        return respuesta

class SolicitudAlUsuarioSobrePQRSDFCreate(generics.CreateAPIView):
    serializer_class = SolicitudAlUsuarioSobrePQRSDFCreateSerializer
    serializer_class_anexo_pqr = Anexos_PQRCreateSerializer
    queryset = SolicitudAlUsuarioSobrePQRSDF.objects.all()
    vista_estados = Estados_PQRCreate()
    vista_anexos = AnexosCreate()
    vista_archivos = ArchivosDgitalesCreate()
    vista_meta_dato = MetadatosAnexosTmpCreate()
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        fecha_actual =datetime.now()
        solicitud_usu_PQRSDF = request.data.get('solicitud_usu_PQRSDF')
        persona = request.user.persona
        categoria = tipo_archivo_CHOICES
        id_unidad = None
        data_anexos =[]
        #DATOS PARA AUDITORIA MATESTRO DETALLE
        valores_creados_detalles=[]
       
       
        data_archivos=[]
        if persona.id_unidad_organizacional_actual:
            id_unidad = persona.id_unidad_organizacional_actual.id_unidad_organizacional
        if not solicitud_usu_PQRSDF:
            raise ValidationError("Se requiere informacion del complemento")
        
        archivos = request.FILES.getlist('archivo')
        anexos = request.data.getlist('anexo')

        
        archivos_blancos = len(anexos)-len(archivos)
        contador = 0 #cuenta los anexos que tienen archivos digitales
        json_anexos =[]
        for anexo in anexos:
            json_anexo = json.loads(anexo)
            json_anexos.append(json_anexo)

        data_in = json.loads(solicitud_usu_PQRSDF)

        #for archivo in archivos:
        for archivo in archivos:
            if  archivo:
                ruta = "home,BIA,Otros,PQRSDF,Complementos"
                respuesta_archivo = self.vista_archivos.crear_archivo({"ruta":ruta,'es_Doc_elec_archivo':False},archivo)
                data_archivo = respuesta_archivo.data['data']
                if respuesta_archivo.status_code != status.HTTP_201_CREATED:
                    return respuesta_archivo
                #print(respuesta_archivo.data['data'])
                data_archivos.append(respuesta_archivo.data['data'])
                contador = contador+1
        for i in range(archivos_blancos):
            anexo_temporal = json_anexos[contador]
            meta_dato = anexo_temporal['meta_data']
            info_archivo = {}
            info_archivo['Nombre del Anexo'] = anexo_temporal['nombre_anexo']
            info_archivo['Asunto'] = meta_dato['asunto']
            info_archivo['descripcion'] = meta_dato['descripcion']
            for x in categoria:
                if x[0] == meta_dato['cod_categoria_archivo']:
                    info_archivo['Categoria de Archivo'] = x[1]

            if meta_dato['id_tipologia_doc']:
                tipologia = TipologiasDoc.objects.filter(id_tipologia_documental= meta_dato['id_tipologia_doc']).first()
                if tipologia:
                    info_archivo['Tipologia Documental'] =tipologia.nombre
              
            else:
               info_archivo['Tipologia Documental'] = meta_dato['tipologia_no_creada_TRD']
            #info_archivo['Medio_de_Almacenamiento'] = anexo_temporal['medio_almacenamiento']
            
            arch_blanco =  UtilsGestor.generar_archivo_blanco(info_archivo)
            data_archivos.append(arch_blanco.data['data'])
            i= i+1
            contador = contador+1
      
        for anexo,archivo in zip(json_anexos,data_archivos):
            #print( archivo['id_archivo_digital'])
            #print(anexo)
            #print(anexo['meta_data'])
            respuesta_anexo = self.vista_anexos.crear_anexo(anexo)
            if respuesta_anexo.status_code != status.HTTP_200_OK:
                return respuesta_anexo
            
            ##AUDITORIA DETALLE
            valores_creados_detalles.append({"NombreAnexo":anexo['nombre_anexo']})
            data_anexo = respuesta_anexo.data['data']
            meta_dato = anexo['meta_data']
            meta_dato['id_anexo']= data_anexo['id_anexo']
            meta_dato['id_archivo_sistema'] = archivo['id_archivo_digital']
            meta_dato['nro_folios_documento'] = data_anexo['numero_folios']
            respuest_meta_dato = self.vista_meta_dato.crear_meta_data(meta_dato)
            if respuest_meta_dato.status_code != status.HTTP_200_OK:
                return respuest_meta_dato
            #print(respuest_meta_dato.data['data'])
            data_anexos.append({**data_anexo,"meta_data":respuest_meta_dato.data['data'],'archivo':archivo})

 
        # raise ValidationError("SIU")
        data_in['fecha_solicitud'] =fecha_actual
        data_in['cod_tipo_oficio'] ='S'
        data_in['id_persona_solicita'] = request.user.persona.id_persona
        data_in['id_und_org_oficina_solicita'] = id_unidad
        data_in['id_estado_actual_solicitud'] = 1 # 254 Estado guardado
        data_in['fecha_ini_estado_actual'] = fecha_actual
        data_in['cantidad_anexos'] =len(data_anexos)

        #Tiempo que tiene un usuario para responder una Solicitud de Complementación o Solicitud de Requerimientos. tabla T271
        tiempo_respuesta = ConfiguracionTiemposRespuesta.objects.filter(nombre_configuracion='Tiempo que tiene un usuario para responder una Solicitud de Complementación o Solicitud de Requerimientos.').first()

        if not tiempo_respuesta:
            raise ValidationError("No se encontro el tiempo de respuesta comuniquese con un administrador"
                                  )
        data_in['dias_para_respuesta'] =tiempo_respuesta.tiempo_respuesta_en_dias


        
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        intance =serializer.save()
         
        #CREA UN ESTADO NUEVO DE PQR T255
        data_estado = {}
        data_estado['solicitud_usu_sobre_PQR'] = intance.id_solicitud_al_usuario_sobre_pqrsdf
        data_estado['estado_solicitud'] = 1 # 254 Estado guardado
        data_estado['persona_genera_estado'] = persona.id_persona
        data_estado['fecha_iniEstado'] = fecha_actual
        respuesta_estado = self.vista_estados.crear_estado(data_estado)
        data_respuesta_estado_asociado = respuesta_estado.data['data']
        ##CREAR LA RELACION ENTRE EL ANEXO Y EL COMPLEMENTO T259
        relacion_pqr=[]
        for anexo in data_anexos:
            data_relacion ={}
            data_relacion['id_anexo'] = anexo['id_anexo']
            data_relacion['id_solicitud_usu_sobre_PQR'] = intance.id_solicitud_al_usuario_sobre_pqrsdf
            serializer_relacion = self.serializer_class_anexo_pqr(data=data_relacion) 
            serializer_relacion.is_valid(raise_exception=True)
            intance_3 =serializer_relacion.save()  
            relacion_pqr.append(serializer_relacion.data)
        descripcion = {"IdPqrsdf":intance.id_pqrsdf,"IdPersonaSolicita":intance.id_persona_solicita,"fecha_solicitud":intance.fecha_solicitud}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 178,
            "cod_permiso": "CR",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)

        return Response({'succes': True, 'detail':'Se crearon los siguientes registros', 'data':serializer.data,"estado":data_respuesta_estado_asociado,'anexos':data_anexos,'relacion_pqr':relacion_pqr}, status=status.HTTP_200_OK)

class SolicitudAlUsuarioSobrePQRSDFGetByPQRS(generics.ListAPIView):

    serializer_class = SolicitudAlUsuarioSobrePQRSDFGetSerializer
    queryset =SolicitudAlUsuarioSobrePQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pqr):
        
        instance = self.get_queryset().filter(id_pqrsdf=pqr,cod_tipo_oficio='S')
        if not instance:
            raise NotFound("No existen registros")
        
        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
    

class SolicitudAlUsuarioSobrePQRSDAnexosFGetByPQRS(generics.ListAPIView):

    serializer_class = Anexos_PQRAnexosGetSerializer
    queryset = Anexos_PQR.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,soli):
        
        instance = self.get_queryset().filter(id_solicitud_usu_sobre_PQR=soli)
        if not instance:
            raise NotFound("No existen registros")
        
        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
       

class SolicitudAlUsuarioSobrePQRSDFGetById(generics.ListAPIView):

    serializer_class = SolicitudAlUsuarioSobrePQRSDFGetDetalleSerializer
    queryset =SolicitudAlUsuarioSobrePQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        
        instance = self.get_queryset().filter(id_solicitud_al_usuario_sobre_pqrsdf=pk).first()
        if not instance:
            raise NotFound("No existen registros")
        
        serializador = self.serializer_class(instance)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
    
#MetadatosAnexosTmpGetSerializer

class MetadatosAnexosTmpFGetByIdAnexo(generics.ListAPIView):

    serializer_class = MetadatosAnexosTmpGetSerializer
    queryset =MetadatosAnexosTmp.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        
        instance = self.get_queryset().filter(id_anexo=pk).first()
        if not instance:
            raise NotFound("No existen registros")
        
        serializador = self.serializer_class(instance)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
    
class InfoDenuncias_PQRSDFGetByPQRSDF(generics.ListAPIView):
    serializer_class = InfoDenuncias_PQRSDFGetByPqrsdfSerializer
    queryset = InfoDenuncias_PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pqr):
        pqrsdf = PQRSDF.objects.filter(id_PQRSDF=pqr).first()

        if not pqrsdf:
            raise NotFound("No existen pqrsdf asociada a esta id")
        
        if pqrsdf.cod_tipo_PQRSDF != 'D':
            raise ValidationError("No es una denuncia")
        instance = self.get_queryset().filter(id_PQRSDF=pqr)

        
        if not instance:
            raise NotFound("No existen registros")
        
        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)

#Continuar con asignacion a grupo  entrega 108
    

class ComplementosUsu_PQRPut(generics.UpdateAPIView):
    serializer_class = ComplementosUsu_PQRPutSerializer
    serializer_adicion_tarea= AdicionalesDeTareasCreateSerializer
    queryset = ComplementosUsu_PQR.objects.all()
    permission_classes = [IsAuthenticated]
    def put(self, request,pk):
        instance = self.get_queryset().filter(idComplementoUsu_PQR=pk).first()


        if not instance:
            raise NotFound("No existen registros")
        pqrsdf_asociada = instance.id_PQRSDF
        #print(pqrsdf_asociada)

        asignacion = AsignacionPQR.objects.filter(id_pqrsdf=pqrsdf_asociada.id_PQRSDF,cod_estado_asignacion='Ac').first()
        if not asignacion:
            raise ValidationError("No se encontro una asignacion")
        #print(asignacion)
        #print(asignacion.cod_estado_asignacion)
        data_in = request.data
        serializer = self.serializer_class(instance, data=data_in, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        tarea = TareasAsignadas.objects.filter(id_asignacion=asignacion.id_asignacion_pqr).first()
        if not tarea:
            raise ValidationError("No se encontro una tarea asignada")

        data_adicion_tarea = {}
        data_adicion_tarea['id_complemento_usu_pqr'] = instance.idComplementoUsu_PQR
        data_adicion_tarea['id_tarea_asignada'] = tarea.id_tarea_asignada
        data_adicion_tarea['fecha_de_adicion'] = datetime.now()
        serializador_adicion = self.serializer_adicion_tarea(data=data_adicion_tarea)
        serializador_adicion.is_valid(raise_exception=True)
        serializador_adicion.save()


        return Response({'success': True, 'detail':'Se asigno correctamente el complemento', 'data': serializer.data,'adicion':serializador_adicion.data}, status=status.HTTP_200_OK)



        


class TramiteListOpasGetView(generics.ListAPIView):
    serializer_class = OPAGetRefacSerializer
    permission_classes = [IsAuthenticated]
    queryset = PermisosAmbSolicitudesTramite.objects.all()
    def get(self, request):
        

        filter={}
        filter['id_solicitud_tramite__id_medio_solicitud'] = 2
        filter['id_permiso_ambiental__cod_tipo_permiso_ambiental'] = 'OP'
        filter['id_solicitud_tramite__id_radicado__isnull'] = False
        #nombre_proyecto = serializers.ReadOnlyField(source='id_solicitud_tramite.nombre_proyecto', default=None)
        #nombre_opa = serializers.ReadOnlyField(source='id_permiso_ambiental.nombre', default=None)
        for key, value in request.query_params.items():

            if key == 'nombre_opa':
                if value != '':
                    filter['id_permiso_ambiental__nombre__icontains'] = value

            if key =='nombre_proyecto':
                if value != '':
                    filter['id_solicitud_tramite__nombre_proyecto__icontains']= value
                    
            if key =='estado_actual_solicitud':
                if value != '':
                    filter['id_solicitud_tramite__id_estado_actual_solicitud__nombre__icontains'] = value 
        
            if key == 'fecha_inicio':
                if value != '':
                    
                    filter['id_solicitud_tramite__fecha_radicado__gte'] = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'fecha_fin':
                if value != '':
                    filter['id_solicitud_tramite__fecha_radicado__lte'] = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'nombre_proyecto':
                if value != '':
                    filter['id_solicitud_tramite__nombre_proyecto__icontains']= value
        #tramites_opas = PermisosAmbSolicitudesTramite.objects.filter(id_solicitud_tramite__id_medio_solicitud=2,id_solicitud_tramite__id_radicado__isnull=False ,id_permiso_ambiental__cod_tipo_permiso_ambiental = 'OP')
        instance = self.get_queryset().filter(**filter).order_by('id_solicitud_tramite__fecha_radicado')
        serializer = self.serializer_class(instance, many=True)

        radicado_value = request.query_params.get('radicado')
        nombre_titular_value = request.query_params.get('nombre_titular')
        data_respuesta = serializer.data
        data_validada =[]
        if radicado_value and radicado_value != '':
            data_validada = [item for item in serializer.data if radicado_value in item.get('radicado', '')]
        else :
            data_validada = data_respuesta

        if nombre_titular_value and nombre_titular_value != '':
            data_validada = [item for item in data_validada if nombre_titular_value in item.get('nombre_completo_titular', '')]
        
        
        return Response({'success': True, 'detail':'Se encontró la siguiente información', 'data': data_validada}, status=status.HTTP_200_OK)
class VistaCreadoraArchivo3(generics.CreateAPIView):

    def post(self,request):
        data = request.data
        respuesta= UtilsGestor.generar_archivo_blanco(data)
        return respuesta
    

#PANEL DE VENTANILLA OPAS
    
class RespuestaRequerimientoOpaGet(generics.ListAPIView):
    serializer_class = RespuestasRequerimientosOpaGetSerializer
    queryset = RespuestasRequerimientos.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,tra):

        instance = self.get_queryset().filter(id_solicitud_tramite=tra,id_radicado__isnull=False).order_by('fecha_respuesta')

        if not instance:
            raise NotFound("No existen registros")
        
        serializer = self.serializer_class(instance, many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)

       
class RequerimientoOpaPut(generics.UpdateAPIView):#Continuar con asignacion a grupo
    serializer_class = RespuestasRequerimientosPutGetSerializer
    serializer_adicion_tarea= AdicionalesDeTareasCreateSerializer
    queryset = RespuestasRequerimientos.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarResponderRequerimientoOPA]
    def put(self, request,pk):
        instance = self.get_queryset().filter(id_respuesta_requerimiento=pk).first()


        if not instance:
            raise NotFound("No existen registros")
        opa_asociada = instance.id_solicitud_tramite
        #print(pqrsdf_asociada)

        asignacion = AsignacionTramites.objects.filter(id_solicitud_tramite=opa_asociada.id_solicitud_tramite,cod_estado_asignacion='Ac').first()
        if not asignacion:
            raise ValidationError("No se encontro una asignacion")
        #print(asignacion)
        #print(asignacion.cod_estado_asignacion)
        data_in = request.data
        serializer = self.serializer_class(instance, data=data_in, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        tarea = TareasAsignadas.objects.filter(id_asignacion=asignacion.id_asignacion_tramite).first()
        if not tarea:
            raise ValidationError("No se encontro una tarea asignada")
        adiciones_tarea = AdicionalesDeTareas.objects.filter(id_tarea_asignada=tarea.id_tarea_asignada,id_respuesta_requerimiento= instance.id_respuesta_requerimiento).first()

        if adiciones_tarea:
            raise ValidationError("Ya se agrego un complemento")
        data_adicion_tarea = {}
        data_adicion_tarea['id_respuesta_requerimiento'] = instance.id_respuesta_requerimiento
        data_adicion_tarea['id_tarea_asignada'] = tarea.id_tarea_asignada
        data_adicion_tarea['fecha_de_adicion'] = datetime.now()
        data_adicion_tarea['id_complemento_usu_pqr'] = None
        serializador_adicion = self.serializer_adicion_tarea(data=data_adicion_tarea)
        serializador_adicion.is_valid(raise_exception=True)
        serializador_adicion.save()


        return Response({'success': True, 'detail':'Se asigno correctamente el complemento', 'data': serializer.data,'adicion':serializador_adicion.data}, status=status.HTTP_200_OK)

class SolicitudDeDigitalizacionRequerimientoOpaCreate(generics.CreateAPIView):
    serializer_class = SolicitudDeDigitalizacionPostSerializer
    serializer_complemento = RespuestasRequerimientosPutSerializer
    queryset =SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated, PermisoCrearResponderRequerimientoOPA]
    #creador_estados = Estados_PQRCreate
    def post(self, request):
        data_in = request.data

        complemento= RespuestasRequerimientos.objects.filter(id_respuesta_requerimiento=request.data['id_respuesta_requerimiento']).first()
        if not complemento:
            raise NotFound("No existe pqrsdf")
        
        if  not complemento.requiere_digitalizacion:
            raise ValidationError("No requiere digitalizacion")
        data_in['fecha_solicitud'] = datetime.now()
        data_in['digitalizacion_completada'] = False
        data_in['devuelta_sin_completar'] = False
        data_in['id_persona_digitalizo'] = request.user.persona.id_persona

        #print(pqr.id_estado_actual_solicitud)
        #valida si tiene solicitudess pendientes
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_respuesta_requerimiento=request.data['id_respuesta_requerimiento'])
        for solicitude in solicitudes:
            if  not solicitude.fecha_rta_solicitud:
                raise ValidationError('No se puede realizar la solicitud porque tiene pendientes')
        
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        #Actualizacion de fecha de complemento
        data_complemento = {}
        data_complemento['fecha_envio_definitivo_digitalizacion'] = datetime.now()
        complemento_serializer = self.serializer_complemento(complemento,data=data_complemento,partial=True )
        complemento_serializer.is_valid(raise_exception=True)
        complemento_serializer.save()
        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,'complemento':complemento_serializer.data}, status=status.HTTP_200_OK)


class RespuestasOpaAnexoInfoGet(generics.ListAPIView):
    serializer_class = AnexosGetSerializer
    queryset =PermisosAmbSolicitudesTramite.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,res):
        data=[]
        instance =RespuestasRequerimientos.objects.filter(id_respuesta_requerimiento=res).first()
        if not instance:
                raise NotFound("No existen registros")
        
        
        tabla_intermedia_anexos_tramites = AnexosTramite.objects.filter(id_respuesta_requerimiento=instance)


        print(tabla_intermedia_anexos_tramites)
        #raise ValidationError("AQUI VAMOS")
        #anexos_pqrs = Anexos_PQR.objects.filter(id_PQRSDF=instance)
        for x in tabla_intermedia_anexos_tramites:
            info_anexo =x.id_anexo
            data_anexo = self.serializer_class(info_anexo)
            data.append(data_anexo.data)
        
               
        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':data}, status=status.HTTP_200_OK) 
class SolicitudDeDigitalizacionOPACreate(generics.CreateAPIView):
    serializer_class = SolicitudDeDigitalizacionPostSerializer
    serializer_tramite = TramitePutSerializer
    queryset =SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]
    creador_estados = Estados_PQRCreate
    def post(self, request):
        fecha_actual = datetime.now()    
      
        data_in = request.data
        solicitud_tramite =SolicitudesTramites.objects.filter(id_solicitud_tramite= data_in['id_solicitud_tramite']).first()

        if not solicitud_tramite:
            raise NotFound("No existe el OPA seleccionado.")
        print(solicitud_tramite)
        
        #raise ValidationError('SI SOMOS')

        if  not solicitud_tramite.requiere_digitalizacion:
            raise ValidationError("No requiere digitalizacion")
        
        if solicitud_tramite.id_estado_actual_solicitud:
            if solicitud_tramite.id_estado_actual_solicitud.id_estado_solicitud == 3:
                raise ValidationError('No se puede realizar la solicitud porque tiene pendientes')
        
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_tramite=request.data['id_solicitud_tramite'])
        for solicitude in solicitudes:
            if  not solicitude.fecha_rta_solicitud:
                raise ValidationError('No se puede realizar la solicitud porque tiene pendientes')
            
        #raise ValidationError('AQUI VA EL ASUNTO')
        #CREA UN ESTADO NUEVO  T255 EN VENTANILLA CON PENDIENTES
        data_estado = {}
        data_estado['id_tramite'] = request.data['id_solicitud_tramite']
        data_estado['estado_solicitud'] = 3
        data_estado['fecha_iniEstado'] = fecha_actual
        respuesta_estado = self.creador_estados.crear_estado(self,data_estado)
        data_respuesta_estado_asociado = respuesta_estado.data['data']
        # #ASOCIAR ESTADO
        data_estado_asociado = {}
        data_estado_asociado['id_tramite'] = request.data['id_solicitud_tramite']
        data_estado_asociado['estado_solicitud'] = 9
        data_estado_asociado['estado_PQR_asociado'] =data_respuesta_estado_asociado['id_estado_PQR']
        data_estado_asociado['fecha_iniEstado'] = fecha_actual
        respuesta_estado_asociado = self.creador_estados.crear_estado(self,data_estado_asociado)
        
        
        #CAMBIAMOS EL ESTADO ACTUAL DE LA PQRSDF  self.serializer_class(unidad_medida,data)
        serializador_pqrs = self.serializer_tramite(solicitud_tramite,data={'id_estado_actual_solicitud':3,'fecha_envio_definitivo_a_digitalizacion':datetime.now(),'fecha_digitalizacion_completada':datetime.now()},partial=True)
        serializador_pqrs.is_valid(raise_exception=True)
        prueba = serializador_pqrs.save()
        
        
        data_in['fecha_solicitud'] = fecha_actual
        data_in['digitalizacion_completada'] = False
        data_in['devuelta_sin_completar'] = False
        data_in['id_tramite'] = data_in['id_solicitud_tramite']
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,'estados':respuesta_estado_asociado.data['data']}, status=status.HTTP_200_OK)
        #return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data}, status=status.HTTP_200_OK)
    
class SolicitudJuridicaOPACreate(generics.CreateAPIView):
    serializer_class = SolicitudJuridicaOPACreateSerializer
    serializer_tramite = TramitePutSerializer
    queryset = SolicitudesDeJuridica.objects.all()
    permission_classes = [IsAuthenticated]
    creador_estados = Estados_PQRCreate
    
    def post(self, request):
        fecha_actual = datetime.now()
      
        data_in = request.data
        solicitud_tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite']).first()

        if not solicitud_tramite:
            raise NotFound("No existe el OPA seleccionado.")

        if solicitud_tramite.requiere_digitalizacion and not solicitud_tramite.fecha_envio_definitivo_a_digitalizacion:
            raise ValidationError("Se debe completar la digitalización del OPA antes de enviar la solicitud a jurídica")
        
        instance = AsignacionTramites.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite'])
        for asignacion in instance:
            if asignacion.cod_estado_asignacion != 'Ac':
                raise ValidationError("El OPA tiene que ser asignado a un grupo antes de enviar la solicitud a jurídica")
        
        solicitud_juridica = self.queryset.filter(id_solicitud_tramite=data_in['id_solicitud_tramite']).first()
        if solicitud_juridica:
            raise ValidationError("El OPA ya fue enviado a revisión jurídica")
        
        #CREA UN ESTADO NUEVO T255
        data_estado = {}
        data_estado['id_tramite'] = request.data['id_solicitud_tramite']
        data_estado['estado_solicitud'] = 15
        data_estado['fecha_iniEstado'] = fecha_actual
        data_estado['persona_genera_estado'] = request.user.persona.id_persona
        respuesta_estado = self.creador_estados.crear_estado(self,data_estado)
        data_respuesta_estado_asociado = respuesta_estado.data['data']
        
        
        #CAMBIAMOS EL ESTADO ACTUAL DEL OPA
        serializador_opa = self.serializer_tramite(solicitud_tramite, data={'id_estado_actual_solicitud':15}, partial=True)
        serializador_opa.is_valid(raise_exception=True)
        serializador_opa.save()
        
        data_in['cod_tipo_solicitud_juridica'] = 'RE'
        data_in['fecha_solicitud'] = fecha_actual
        data_in['solicitud_completada'] = False
        data_in['solicitud_sin_completar'] = True
        data_in['id_persona_solicita_revision'] = request.user.persona.id_persona
        data_in['cod_estado_tipo_solicitud_juridica'] = 'NR'
        
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return Response({'succes': True, 'detail':'Se creo la solicitud de jurídica', 'data':serializer.data, 'estados':data_respuesta_estado_asociado}, status=status.HTTP_201_CREATED)

class OPAFGetHitorico(generics.ListAPIView):
    serializer_class = OPAGetHistoricoSerializer
    #queryset =PQRSDF.objects.all()
    # queryset = PermisosAmbSolicitudesTramite.objects.annotate(mezcla=Concat(F('id_solicitud_tramite__id_radicado__prefijo_radicado'), Value('-'), F('id_solicitud_tramite__id_radicado__agno_radicado'),
    #                                                   Value('-'), F('id_solicitud_tramite__id_radicado__nro_radicado'), output_field=CharField()))

    queryset = PermisosAmbSolicitudesTramite.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request):
  
      
        filter={}
        filter['id_solicitud_tramite__id_medio_solicitud'] = 2
        filter['id_permiso_ambiental__cod_tipo_permiso_ambiental'] = 'OP'
        filter['id_solicitud_tramite__id_radicado__isnull'] = False
        radicado = None
        for key, value in request.query_params.items():

            if key == 'radicado':
                if value !='':
                    radicado = value
            if key =='fecha_radicado':
                if value != '':
                    filter['id_solicitud_tramite__fecha_radicado'] = datetime.strptime(value, '%Y-%m-%d').date()
           
    
        instance = self.get_queryset().filter(**filter).order_by('id_solicitud_tramite__fecha_radicado')
        serializer = self.serializer_class(instance, many=True)
        #serializer2 = self.serializer_class(instance, many=True)

        ##FILTRO POR RADICADO
        filter['id_radicado__isnull'] = False
        #instance = self.get_queryset().filter(**filter).order_by('fecha_radicado')
       
   
        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance,many=True)
        data_respuesta = serializador.data
        data_validada =[]
        if radicado and radicado != '':
            data_validada = [item for item in serializador.data if radicado in item.get('cabecera', {}).get('radicado', '')]
        else :
            data_validada = data_respuesta
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_validada,}, status=status.HTTP_200_OK)

    
class AsignacionOPACreate(generics.CreateAPIView):
    serializer_class = AsignacionTramitesPostSerializer
    queryset =AsignacionTramites.objects.all()
    permission_classes = [IsAuthenticated]
    creador_estados = Estados_PQRCreate

    def post(self, request):
        data_in = request.data
        agno_actual = datetime.now().year
        # Verificar si se envió el ID de solicitud de OPA
        if 'id_solicitud_tramite' not in data_in:
            raise ValidationError("No se envió la solicitud de OPA")
        
        if 'id_catalogo_serie_subserie' not in data_in:
            raise ValidationError("No se envió el ID de la Subserie")
        

        #id_catalogo_serie_subserie
        catalogo = CatalogosSeriesUnidad.objects.filter(id_cat_serie_und=data_in['id_catalogo_serie_subserie']).first()
        if not catalogo:
            raise ValidationError("No se encontró la Subserie")
        tripleta_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_cat_serie_und=data_in['id_catalogo_serie_subserie']).first()
        
        if not tripleta_trd:
            raise ValidationError('Debe enviar el id de la tripleta de TRD seleccionada')
        #BUSCAR EL AÑO

        configuracion_expediente = ConfiguracionTipoExpedienteAgno.objects.filter(id_cat_serie_undorg_ccd = tripleta_trd.id_catserie_unidadorg,agno_expediente=agno_actual).first()
        if not configuracion_expediente:
            raise ValidationError("Este catalogo de de series-suberie no cuenta con configuracion para este año.")


        # Verificar si la solicitud ya fue aceptada
        instance = AsignacionTramites.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite'])
        for asignacion in instance:
            if asignacion.cod_estado_asignacion == 'Ac':
                raise ValidationError("La solicitud ya fue aceptada.")
            if not asignacion.cod_estado_asignacion:
                raise ValidationError("La solicitud está pendiente por respuesta.")

        # Obtener el líder de la Subsección Gestión Ambiental
        subseccion_id = data_in.get('id_und_org_seccion_asignada')
        lider_subseccion = self.obtener_lider_subseccion(subseccion_id)

        # Validar si hay líder asignado
        if lider_subseccion:
            # Habilitar el control "Líder de la Subsección"
            data_in['lider_subseccion'] = lider_subseccion
            # Habilitar el botón "Asignar"
            data_in['asignacion_de_ventanilla'] = True
        else:
            raise ValidationError("No se puede asignar la OPA a una subsección que no tiene líder asignado.")
        
        instance= AsignacionTramites.objects.filter(id_solicitud_tramite = data_in['id_solicitud_tramite'])

        for asignacion in instance:
            print(asignacion)
            #print(asignacion)
            if asignacion.cod_estado_asignacion == 'Ac':
                raise ValidationError("La solicitud  ya fue Aceptada.")
            if  not asignacion.cod_estado_asignacion:
                raise ValidationError("La solicitud esta pendiente por respuesta.")
        max_consecutivo = AsignacionTramites.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite']).aggregate(Max('consecutivo_asign_x_tramite'))

        if max_consecutivo['consecutivo_asign_x_tramite__max'] == None:
             ultimo_consec= 1
        else:
            ultimo_consec = max_consecutivo['consecutivo_asign_x_tramite__max'] + 1
        
        unidad_asignar = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=data_in['id_und_org_seccion_asignada']).first()
        if not unidad_asignar:
            raise ValidationError("No existe la unidad asignada")

        data_in['consecutivo_asign_x_tramite'] = ultimo_consec 
        data_in['fecha_asignacion'] = datetime.now()
        data_in['id_persona_asigna'] = request.user.persona.id_persona
        data_in['cod_estado_asignacion'] = None
        data_in['asignacion_de_ventanilla'] = True


        #ASOCIAR ESTADO
        data_estado_asociado = {}
        data_estado_asociado['id_tramite'] = request.data['id_solicitud_tramite'] 
        data_estado_asociado['estado_solicitud'] = 5
        #data_estado_asociado['estado_PQR_asociado'] 
        data_estado_asociado['fecha_iniEstado'] =  datetime.now()
        data_estado_asociado['persona_genera_estado'] = request.user.persona.id_persona
        #raise ValidationError("NONE")
        respuesta_estado_asociado = self.creador_estados.crear_estado(self,data_estado_asociado)
        data_estado = respuesta_estado_asociado.data['data']
        print(data_in)
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        #Crear tarea y asignacion de tarea
       
        id_persona_asiganada = serializer.data['id_persona_asignada']

 
        #Creamos la tarea 315 #pendiente panel de ventanilla de tramite
        data_tarea = {}
        data_tarea['cod_tipo_tarea'] = 'ROpa'
        data_tarea['id_asignacion'] = serializer.data['id_asignacion_tramite']
        data_tarea['fecha_asignacion'] = datetime.now()

        data_tarea['cod_estado_solicitud'] = 'Ep'
        vista_tareas = TareasAsignadasCreate()    
        respuesta_tareas = vista_tareas.crear_asignacion_tarea(data_tarea)
        if respuesta_tareas.status_code != status.HTTP_201_CREATED:
            return respuesta_tareas
        data_tarea_respuesta= respuesta_tareas.data['data']
        #Teniendo la bandeja de tareas,la tarea ahora tenemos que asignar esa tarea a la bandeja de tareas
        id_tarea_asiganada = data_tarea_respuesta['id_tarea_asignada']
        vista_asignacion = TareaBandejaTareasPersonaCreate()

        data_tarea_bandeja_asignacion = {}
        data_tarea_bandeja_asignacion['id_persona'] = id_persona_asiganada
        data_tarea_bandeja_asignacion['id_tarea_asignada'] = id_tarea_asiganada
        data_tarea_bandeja_asignacion['es_responsable_ppal'] = True
        respuesta_relacion = vista_asignacion.crear_tarea(data_tarea_bandeja_asignacion)
        if respuesta_relacion.status_code != status.HTTP_201_CREATED:
            return respuesta_relacion
        #CREAMOS LA ALERTA DE ASIGNACION A GRUPO 

        persona =Personas.objects.filter(id_persona = id_persona_asiganada).first()
        nombre_completo_persona = ''
        if persona:
            nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                            persona.primer_apellido, persona.segundo_apellido]
            nombre_completo_persona = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_persona = nombre_completo_persona if nombre_completo_persona != "" else None
       
        mensaje = "Tipo de solicitud : OPAS \n Unidad Organizacional : "+unidad_asignar.nombre+" \n Lider de Unidad Organizacional: "+nombre_completo_persona+" \n Fecha de asignacion : "+str(serializer.data['fecha_asignacion'])
        vista_alertas_programadas = AlertaEventoInmediadoCreate()
        data_alerta = {}
        data_alerta['cod_clase_alerta'] = 'Gst_SlALid'
        data_alerta['id_persona'] = id_persona_asiganada
        data_alerta['id_elemento_implicado'] = serializer.data['id_asignacion_tramite']
        data_alerta['informacion_complemento_mensaje'] = mensaje

        respuesta_alerta = vista_alertas_programadas.crear_alerta_evento_inmediato(data_alerta)
        if respuesta_alerta.status_code != status.HTTP_200_OK:
            return respuesta_alerta


        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,'estado':data_estado,'tarea':respuesta_relacion.data['data']}, status=status.HTTP_200_OK)
    
    def obtener_lider_subseccion(self, subseccion_id):
        # Consultar el líder de la Subsección Gestión Ambiental
        lider_subseccion = LideresUnidadesOrg.objects.filter(id_unidad_organizacional=subseccion_id).first()

        if lider_subseccion:
            # Obtener información del líder desde la tabla Personas
            persona_lider = lider_subseccion.id_persona
            nombre_completo_lider = f"{persona_lider.primer_nombre} {persona_lider.segundo_nombre} {persona_lider.primer_apellido} {persona_lider.segundo_apellido}"
            return nombre_completo_lider if nombre_completo_lider.strip() else None
        else:
            return None

class AsignacionOPASGet(generics.ListAPIView):
    serializer_class = AsignacionTramiteOpaGetSerializer
    queryset = AsignacionTramites.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,tra):
        
        instance = self.get_queryset().filter(id_solicitud_tramite=tra)
        if not instance:
            raise NotFound("No existen registros")
        
        serializer = self.serializer_class(instance,many=True)

        #return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'seccion':serializer_unidad.data,'hijos':serializer.data}}, status=status.HTTP_200_OK)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    

class EstadosSolicitudesTramitesGet(generics.ListAPIView):
    serializer_class = EstadosSolicitudesGetSerializer
    queryset =EstadosSolicitudes.objects.all()
    permission_classes = [IsAuthenticated]
    def get (self, request):
        instance = self.get_queryset().filter(aplica_para_tramites=True)
        #instance = self.get_queryset().filter(aplica_para_pqrsdf=True, id_estado_solicitud__in=[2,3,4,5])


        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
    

class OpaAnexoInfoGet(generics.ListAPIView):
    serializer_class = AnexosGetSerializer
    queryset =PermisosAmbSolicitudesTramite.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,tra):
        data=[]
        instance =PermisosAmbSolicitudesTramite.objects.filter(id_solicitud_tramite=tra).first()
        if not instance:
                raise NotFound("No existen registros")
        
        tramite = instance.id_solicitud_tramite
        tabla_intermedia_anexos_tramites = AnexosTramite.objects.filter(id_solicitud_tramite=tramite)


        print(tabla_intermedia_anexos_tramites)
        #raise ValidationError("AQUI VAMOS")
        #anexos_pqrs = Anexos_PQR.objects.filter(id_PQRSDF=instance)
        for x in tabla_intermedia_anexos_tramites:
            info_anexo =x.id_anexo
            data_anexo = self.serializer_class(info_anexo)
            data.append(data_anexo.data)
        
        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data,}, status=status.HTTP_200_OK)

class OPASAnexoDocumentoDigitalGet(generics.ListAPIView):
    serializer_class = AnexoArchivosDigitalesSerializer
    queryset =Anexos.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
      
        instance =Anexos.objects.filter(id_anexo=pk).first()

        if not instance:
                raise NotFound("No existen registros")
        
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=instance.id_anexo).first()
        if not meta_data:
            raise NotFound("No existen registros")
        archivo = meta_data.id_archivo_sistema
        serializer= self.serializer_class(archivo)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'id_anexo':instance.id_anexo,**serializer.data},}, status=status.HTTP_200_OK)
class OPAAnexoMetaDataGet(generics.ListAPIView):
    serializer_class = MetadatosAnexosTmpSerializerGet
    queryset =Anexos.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
      
        instance =Anexos.objects.filter(id_anexo=pk).first()

        if not instance:
                raise NotFound("No existen registros")
        
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=instance.id_anexo).first()
        if not meta_data:
            raise NotFound("No existen registros")
   
        serializer= self.serializer_class(meta_data)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'id_anexo':instance.id_anexo,**serializer.data},}, status=status.HTTP_200_OK)

# OTROS

class OtrosGet(generics.ListAPIView):
    serializer_class = OtrosGetSerializer
    queryset = Otros.objects.annotate(
        mezcla=Concat(F('id_radicados__prefijo_radicado'),
                    Value('-'), F('id_radicados__agno_radicado'),
                    Value('-'), F('id_radicados__nro_radicado'),
                    output_field=CharField()
                )
        )                         
    permission_classes = [IsAuthenticated]

    def get (self, request):
        data_respuesta = []
        filter={}
        
        for key, value in request.query_params.items():
            if key == 'radicado':
                if value !='':
                    filter['mezcla__icontains'] = value
            if key =='estado_actual_solicitud':
                if value != '':
                    filter['id_estado_actual_solicitud__nombre__icontains'] = value
            if key == 'fecha_inicio':
                if value != '':
                    filter['fecha_radicado__gte'] = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'fecha_fin':
                if value != '':
                    filter['fecha_radicado__lte'] = datetime.strptime(value, '%Y-%m-%d').date()
        
        filter['id_radicados__isnull'] = False
        instance = self.get_queryset().filter(**filter).order_by('fecha_radicado')
        
        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance, many=True)
        data_respuesta = serializador.data
        return Response({'success': True, 'detail':'Se encontraron los siguientes registros', 'data':data_respuesta,}, status=status.HTTP_200_OK)

class OtrosEstadosSolicitudesGet(generics.ListAPIView):
    serializer_class = EstadosSolicitudesGetSerializer
    queryset =EstadosSolicitudes.objects.filter(aplica_para_otros=True)
    permission_classes = [IsAuthenticated]
    
    def get (self, request):
        queryset = self.queryset.all()
        if not queryset:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(queryset,many=True)
        return Response({'success': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)

class OtrosSolicitudDeDigitalizacionCreate(generics.CreateAPIView):
    serializer_class = SolicitudDeDigitalizacionPostSerializer
    serializer_otros = OtrosPutSerializer
    queryset =SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]
    creador_estados = Estados_PQRCreate
    
    def post(self, request):
        fecha_actual = datetime.now()    
        otro = Otros.objects.filter(id_otros=request.data['id_otros']).first()
        if not otro:
            raise NotFound("No existe registros de Otros")
        
        if  not otro.requiere_digitalizacion:
            raise ValidationError("No requiere digitalizacion")
        
        if otro.id_estado_actual_solicitud:
            if otro.id_estado_actual_solicitud.id_estado_solicitud == 3:
                raise ValidationError('No se puede realizar la solicitud porque tiene pendientes')
        
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_otro=request.data['id_otros'])
        for solicitud in solicitudes:
            if  not solicitud.fecha_rta_solicitud:
                raise ValidationError('No se puede realizar la solicitud porque tiene pendientes')
            
        #CREA UN ESTADO NUEVO DE PQR T255
        data_estado = {}
        data_estado['id_otros'] = request.data['id_otros']
        data_estado['estado_solicitud'] = 3
        data_estado['fecha_iniEstado'] = fecha_actual
        respuesta_estado = self.creador_estados.crear_estado(self,data_estado)
        data_respuesta_estado_asociado = respuesta_estado.data['data']
        print("data_respuesta_estado_asociado: ", data_respuesta_estado_asociado)
        
        #ASOCIAR ESTADO
        data_estado_asociado = {}
        data_estado_asociado['id_otros'] = request.data['id_otros'] 
        data_estado_asociado['estado_solicitud'] = 9
        data_estado_asociado['estado_PQR_asociado'] = data_respuesta_estado_asociado['id_estado_PQR']
        data_estado_asociado['fecha_iniEstado'] = fecha_actual
        respuesta_estado_asociado = self.creador_estados.crear_estado(self,data_estado_asociado)
        
        
        #CAMBIAMOS EL ESTADO ACTUAL DE LA PQRSDF  self.serializer_class(unidad_medida,data)
        serializador_otros = self.serializer_otros(otro, data = {
            'id_estado_actual_solicitud':3,
            'fecha_envio_definitivo_digitalizacion':datetime.now()
            }, partial=True
        )
        serializador_otros.is_valid(raise_exception=True)
        serializador_otros.save()
       
        data_in = request.data
        data_in['id_otro'] = data_in['id_otros']
        data_in['fecha_solicitud'] = fecha_actual
        data_in['digitalizacion_completada'] = False
        data_in['devuelta_sin_completar'] = False
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({'success': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,'estados':respuesta_estado_asociado.data['data']}, status=status.HTTP_200_OK)

class OtrosInfoGet(generics.ListAPIView):
    serializer_class = AnexosGetSerializer
    queryset = Otros.objects.all()
    permission_classes = [IsAuthenticated]

    def get (self, request, id_otros):
        data=[]
        instance = Otros.objects.filter(id_otros=id_otros).first()

        if not instance:
            raise NotFound("No existen el registro de otros ingresado")
        
        anexos_pqrs = Anexos_PQR.objects.filter(id_otros=instance.id_otros)
        for x in anexos_pqrs:
            info_anexo = x.id_anexo
            data_anexo = self.serializer_class(info_anexo)
            data.append(data_anexo.data)
        
        return Response({'success': True, 'detail':'Se encontraron los siguientes registros', 'data':data,}, status=status.HTTP_200_OK)

class AsignacionOtrosCreate(generics.CreateAPIView):
    serializer_class = AsignacionOtrosPostSerializer
    queryset = AsignacionOtros.objects.all()
    permission_classes = [IsAuthenticated]
    creador_estados = Estados_PQRCreate
    
    def post(self, request):
        #CODIGO DE SERIE DOCUMENTAL DE PQRSDF
        codigo = 39      
        contador = 0  
        data_in = request.data

        if not 'id_otros' in data_in:
            raise ValidationError("No se envio el registro de otros elegido")
        
        instance= AsignacionOtros.objects.filter(id_otros = data_in['id_otros'])
        for asignacion in instance:
            if asignacion.cod_estado_asignacion == 'Ac':
                raise ValidationError("La solicitud  ya fue Aceptada.")
            if  not asignacion.cod_estado_asignacion:
                raise ValidationError("La solicitud esta pendiente por respuesta.")
        max_consecutivo = AsignacionOtros.objects.filter(id_otros=data_in['id_otros']).aggregate(Max('consecutivo_asign_x_otros'))

        if max_consecutivo['consecutivo_asign_x_otros__max'] == None:
             ultimo_consec= 1
        else:
            ultimo_consec = max_consecutivo['consecutivo_asign_x_otros__max'] + 1
        
        unidad_asignar = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=data_in['id_und_org_seccion_asignada']).first()
        if not unidad_asignar:
            raise ValidationError("No existe la unidad asignada")
        
        #VALIDACION ENTREGA 102 SERIE PQRSDF
        aux = unidad_asignar
        while aux:
            if aux.cod_agrupacion_documental == 'SEC':
                catalogos = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=aux.id_unidad_organizacional,id_catalogo_serie__id_subserie_doc__isnull=True)
                contador = 0
                for catalogo in catalogos:
                    if int(catalogo.id_catalogo_serie.id_serie_doc.codigo) == codigo:
                        contador += 1
                break
            aux = aux.id_unidad_org_padre
        # if contador == 0:
        #     raise ValidationError("No se puede realizar la asignación de Otros a una unidad organizacional seleccionada porque no tiene serie OTROS")
        data_in['consecutivo_asign_x_otros'] = ultimo_consec 
        data_in['fecha_asignacion'] = datetime.now()
        data_in['id_persona_asigna'] = request.user.persona.id_persona
        data_in['cod_estado_asignacion'] = None
        data_in['asignacion_de_ventanilla'] = True

        #ASOCIAR ESTADO
        data_estado_asociado = {}
        data_estado_asociado['id_otros'] = request.data['id_otros'] 
        data_estado_asociado['estado_solicitud'] = 5
        data_estado_asociado['fecha_iniEstado'] =  datetime.now()
        data_estado_asociado['persona_genera_estado'] = request.user.persona.id_persona
        respuesta_estado_asociado = self.creador_estados.crear_estado(self,data_estado_asociado)
        data_estado = respuesta_estado_asociado.data['data']
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        #Crear tarea y asignacion de tarea
       
        id_persona_asignada = serializer.data['id_persona_asignada']

        #Creamos la tarea 315
        data_tarea = {}
        data_tarea['cod_tipo_tarea'] = 'ROtro'
        data_tarea['id_asignacion'] = serializer.data['id_asignacion_otros']
        data_tarea['fecha_asignacion'] = datetime.now()

        data_tarea['cod_estado_solicitud'] = 'Ep'
        vista_tareas = TareasAsignadasCreate()    
        respuesta_tareas = vista_tareas.crear_asignacion_tarea(data_tarea)
        if respuesta_tareas.status_code != status.HTTP_201_CREATED:
            return respuesta_tareas
        
        data_tarea_respuesta = respuesta_tareas.data['data']
        
        #Teniendo la bandeja de tareas,la tarea ahora tenemos que asignar esa tarea a la bandeja de tareas
        id_tarea_asignada = data_tarea_respuesta['id_tarea_asignada']
        vista_asignacion = TareaBandejaTareasPersonaCreate()

        data_tarea_bandeja_asignacion = {}
        data_tarea_bandeja_asignacion['id_persona'] = id_persona_asignada
        data_tarea_bandeja_asignacion['id_tarea_asignada'] = id_tarea_asignada
        data_tarea_bandeja_asignacion['es_responsable_ppal'] = True
        respuesta_relacion = vista_asignacion.crear_tarea(data_tarea_bandeja_asignacion)
        if respuesta_relacion.status_code != status.HTTP_201_CREATED:
            return respuesta_relacion
        
        return Response({'success': True, 'detail':'Se realizó la asignación a grupo', 'data':serializer.data, 'estado':data_estado, 'tarea':respuesta_relacion.data['data']}, status=status.HTTP_201_CREATED)

class AsignacionOtrosGet(generics.ListAPIView):
    serializer_class = AsignacionOtrosGetSerializer
    queryset = AsignacionOtros.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id_otros):
        instance = self.get_queryset().filter(id_otros=id_otros)
        if not instance:
            raise NotFound("No existen registros")
        
        serializer = self.serializer_class(instance, many=True)

        return Response({'success': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
 
class OtrosGetHistorico(generics.ListAPIView):
    serializer_class = OtrosGetHistoricoSerializer
    queryset = Otros.objects.all()                                 
    permission_classes = [IsAuthenticated]

    def get (self, request):
        filter = {}
        filter['id_radicados__isnull'] = False
        radicado = None
        for key, value in request.query_params.items():

            if key == 'radicado':
                if value !='':
                   
                    radicado = value
            if key == 'fecha_radicado':
                if value != '':
                    filter['fecha_radicado'] = datetime.strptime(value, '%Y-%m-%d').date()
 
            # if key =='estado_actual_solicitud':
            #     if value != '':
            #         filter['id_estado_actual_solicitud__estado_solicitud__nombre__icontains'] = value    

        
        
        instance = self.queryset.filter(**filter).order_by('fecha_radicado')
        serializer = self.serializer_class(instance, many=True)
        
        data_validada =[]
       
        if radicado and radicado != '':
            data_validada = [item for item in serializer.data if radicado in item.get('radicado', '')]
        else :
            data_validada = serializer.data

        #instance = self.get_queryset().exclude(id_radicados=None).order_by('fecha_radicado')
        

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_validada,}, status=status.HTTP_200_OK)
    





#ASIGNACION DE OPAS A SECCCION ,SUBSECCION O GRUPO
class SeccionSubseccionAsignacionGet(generics.ListAPIView):
    serializer_class = UnidadesOrganizacionalesSecSubVentanillaGetSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtener el organigrama actual
        organigrama = Organigramas.objects.filter(actual=True)
        if not organigrama:
            raise NotFound('No existe ningún organigrama activado')
        if len(organigrama) > 1:
            raise PermissionDenied('Existe más de un organigrama actual, contacte a soporte')
        organigrama_actual = organigrama.first()

        # Filtrar unidades organizacionales para obtener la subsección de Gestión Ambiental
        unidad_gestion_ambiental = UnidadesOrganizacionales.objects.filter(
            cod_agrupacion_documental='SUB',
            id_organigrama=organigrama_actual.id_organigrama,
            nombre__iexact='Subdirección De Gestión Ambiental'
        ).first()

        # Verificar si hay subsección de Gestión Ambiental
        if not unidad_gestion_ambiental:
            raise NotFound('No hay subsección de Gestión Ambiental')

        # Serializar la subsección de Gestión Ambiental
        serializer = UnidadesOrganizacionalesSecSubVentanillaGetSerializer(
            [unidad_gestion_ambiental],  
            many=True
        )

        return Response({
            'success': True,
            'detail': 'Se encontró la subsección de Gestión Ambiental',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

class SubseccionGestionAmbientalGruposGet(generics.ListAPIView):
    serializer_class = UnidadesOrganizacionalesSecSubVentanillaGetSerializer
    permission_classes = [IsAuthenticated]

    def get_children_recursive(self, parent_id, organigrama_id):
        children = UnidadesOrganizacionales.objects.filter(
            cod_agrupacion_documental=None,
            id_unidad_org_padre=parent_id,
            id_organigrama=organigrama_id
        )

        result = []
        for child in children:
            result.append(child)
            # Llamada recursiva para obtener los hijos de este hijo
            result += self.get_children_recursive(child.id_unidad_organizacional, organigrama_id)
        return result

    def get(self, request, subseccion_id):
        # Obtener el organigrama actual
        organigrama_actual = Organigramas.objects.filter(actual=True).first()
        if not organigrama_actual:
            raise NotFound('No existe ningún organigrama activado')

        # Obtener la subsección de Gestión Ambiental por su ID y validar que pertenezca al organigrama actual
        subseccion_gestion_ambiental = get_object_or_404(
            UnidadesOrganizacionales,
            id_unidad_organizacional=subseccion_id,
            id_organigrama=organigrama_actual.id_organigrama
        )

        # Obtener los hijos recursivamente
        unidades_organizacionales = [subseccion_gestion_ambiental]
        unidades_organizacionales += self.get_children_recursive(subseccion_id, organigrama_actual.id_organigrama)

        # Serializar los datos
        serializer = self.serializer_class(unidades_organizacionales, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron las siguientes unidades organizacionales',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
class UnidadesOrganizacionalesRelacionadasListView(generics.ListAPIView):
    serializer_class = UnidadesOrganizacionalesSerializer

    def get_queryset(self):
        # Obtener el organigrama actual
        organigrama_actual = Organigramas.objects.filter(actual=True).first()

        if not organigrama_actual:
            raise NotFound('No existe ningún organigrama activado')

        # Obtener las series relacionadas con el organigrama actual
        series_relacionadas = CatalogosSeriesUnidad.objects.filter(
            id_unidad_organizacional__id_organigrama=organigrama_actual
        ).values_list('id_catalogo_serie', flat=True).distinct()

        # Obtener todas las unidades organizacionales relacionadas con las series del organigrama actual
        unidades_relacionadas = UnidadesOrganizacionales.objects.filter(
            catalogosseriesunidad__id_catalogo_serie__in=series_relacionadas
        ).distinct()

        return unidades_relacionadas

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        return Response({
            'success': True,
            'detail': f'Se encontraron {queryset.count()} unidades organizacionales relacionadas al organigrama actual',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

#PANEL DE VENTANILLA TRAMITES 
class SolicitudesTramitesGet(generics.ListAPIView):
    serializer_class = SolicitudesTramitesGetSerializer
    queryset = SolicitudesTramites.objects.prefetch_related(
        'id_persona_titular',
        'id_persona_interpone',
        'id_medio_solicitud',
        'id_persona_registra',
        'id_persona_rta_final_gestion',
        'id_estado_actual_solicitud'
    )         
    permission_classes = [IsAuthenticated]

    def get (self, request):
        data_respuesta = []
        filter={}
        
        for key, value in request.query_params.items():
            if key =='estado_actual_solicitud':
                if value != '':
                    filter['id_estado_actual_solicitud__nombre__icontains'] = value
            if key == 'fecha_inicio':
                if value != '':
                    filter['fecha_radicado__gte'] = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'fecha_fin':
                if value != '':
                    filter['fecha_radicado__lte'] = datetime.strptime(value, '%Y-%m-%d').date()
            if key =='asunto_proyecto':
                if value != '':
                    filter['nombre_proyecto__icontains'] = value
            if key =='expediente':
                if value != '':
                    filter['id_expediente__titulo_expediente__icontains'] = value
            if key =='pagado':
                if value != '':
                    value = True if value.lower() == 'true' else False
                    filter['pago'] = value

        filter['id_radicado__isnull'] = False
        instance = self.get_queryset().filter(**filter).order_by('fecha_radicado')
        permisos_ambientales_solicitudes = PermisosAmbSolicitudesTramite.objects.filter(id_permiso_ambiental__cod_tipo_permiso_ambiental='OP').values_list('id_solicitud_tramite', flat=True).distinct()
        instance = instance.exclude(id_solicitud_tramite__in=list(permisos_ambientales_solicitudes))
        
        radicado_value = request.query_params.get('radicado')
        nombre_titular = request.query_params.get('nombre_titular')
        
        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance,many=True)
        data_respuesta = serializador.data
        data_validada =[]
        if radicado_value and radicado_value != '':
            data_validada = [item for item in data_respuesta if radicado_value in item.get('radicado', '')]
        else :
            data_validada = data_respuesta
            
        if nombre_titular and nombre_titular != '':
            data_validada = [item for item in data_respuesta if nombre_titular in item.get('nombre_completo_titular', '')]

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_validada,}, status=status.HTTP_200_OK)

class SolicitudDeDigitalizacionTramitesCreate(generics.CreateAPIView):
    serializer_class = SolicitudDeDigitalizacionPostSerializer
    serializer_tramite = TramitePutSerializer
    queryset =SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]
    creador_estados = Estados_PQRCreate
    
    def post(self, request):
        fecha_actual = datetime.now()    
      
        data_in = request.data
        solicitud_tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite']).first()
        permisos_ambientales_solicitud = PermisosAmbSolicitudesTramite.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite'], id_permiso_ambiental__cod_tipo_permiso_ambiental='OP')
        
        if not solicitud_tramite:
            raise NotFound("No existe el tramite seleccionado.")

        if not solicitud_tramite.requiere_digitalizacion:
            raise ValidationError("No requiere digitalizacion")
        
        if permisos_ambientales_solicitud:
            raise PermissionDenied("No se puede realizar la solicitud de digitalización de un OPA en este servicio")
        
        if solicitud_tramite.id_estado_actual_solicitud:
            if solicitud_tramite.id_estado_actual_solicitud.id_estado_solicitud == 3:
                raise ValidationError('No se puede realizar la solicitud porque tiene pendientes')
        
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_tramite=request.data['id_solicitud_tramite'])
        for solicitude in solicitudes:
            if  not solicitude.fecha_rta_solicitud:
                raise ValidationError('No se puede realizar la solicitud porque tiene pendientes')
        
        #CREA UN ESTADO NUEVO  T255 EN VENTANILLA CON PENDIENTES
        data_estado = {}
        data_estado['id_tramite'] = request.data['id_solicitud_tramite']
        data_estado['estado_solicitud'] = 3
        data_estado['fecha_iniEstado'] = fecha_actual
        respuesta_estado = self.creador_estados.crear_estado(self,data_estado)
        data_respuesta_estado_asociado = respuesta_estado.data['data']
        
        # #ASOCIAR ESTADO
        data_estado_asociado = {}
        data_estado_asociado['id_tramite'] = request.data['id_solicitud_tramite']
        data_estado_asociado['estado_solicitud'] = 9
        data_estado_asociado['estado_PQR_asociado'] =data_respuesta_estado_asociado['id_estado_PQR']
        data_estado_asociado['fecha_iniEstado'] = fecha_actual
        respuesta_estado_asociado = self.creador_estados.crear_estado(self,data_estado_asociado)
        
        #CAMBIAMOS EL ESTADO ACTUAL DEL TRAMITE  self.serializer_class(unidad_medida,data)
        serializador_tramite = self.serializer_tramite(solicitud_tramite, data={
            'id_estado_actual_solicitud':3,
            'fecha_envio_definitivo_a_digitalizacion':datetime.now()
        }, partial=True)
        serializador_tramite.is_valid(raise_exception=True)
        serializador_tramite.save()
        
        data_in['id_tramite'] = data_in['id_solicitud_tramite']
        data_in['fecha_solicitud'] = fecha_actual
        data_in['digitalizacion_completada'] = False
        data_in['devuelta_sin_completar'] = False
        
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,'estados':respuesta_estado_asociado.data['data']}, status=status.HTTP_200_OK)

class TramitesAnexoInfoGet(generics.ListAPIView):
    serializer_class = AnexosGetSerializer
    queryset =PermisosAmbSolicitudesTramite.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,tra):
        data=[]
        tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=tra).first()
        if not tramite:
            raise NotFound("No existen registros")
        
        tabla_intermedia_anexos_tramites = AnexosTramite.objects.filter(id_solicitud_tramite=tramite)

        for x in tabla_intermedia_anexos_tramites:
            info_anexo =x.id_anexo
            data_anexo = self.serializer_class(info_anexo)
            data.append(data_anexo.data)
        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data,}, status=status.HTTP_200_OK)

class TramitesGetHitorico(generics.ListAPIView):
    serializer_class = TramitesGetHistoricoSerializer
    serializer_complementos_class = TramitesGetHistoricoComplementoSerializer
    queryset = SolicitudesTramites.objects.all()
    queryset_complementos = ComplementosUsu_PQR.objects.filter(id_solicitud_usu_PQR__id_solicitud_tramite__isnull=False, id_solicitud_usu_PQR__cod_tipo_oficio='R')
    permission_classes = [IsAuthenticated]

    def get (self, request):
        filter={}
        filter['id_radicado__isnull'] = False
        radicado = None
        for key, value in request.query_params.items():

            if key == 'radicado':
                if value !='':
                    radicado = value
            if key =='fecha_radicado':
                if value != '':
                    filter['fecha_radicado'] = datetime.strptime(value, '%Y-%m-%d').date()
           
    
        instance = self.get_queryset().filter(**filter).order_by('fecha_radicado')
        permisos_ambientales_solicitudes = PermisosAmbSolicitudesTramite.objects.filter(id_permiso_ambiental__cod_tipo_permiso_ambiental='OP').values_list('id_solicitud_tramite', flat=True).distinct()
        instance = instance.exclude(id_solicitud_tramite__in=list(permisos_ambientales_solicitudes))
        
        instance_complementos = self.queryset_complementos.all().filter(**filter).order_by('fecha_radicado')
        instance_complementos = instance_complementos.filter(id_solicitud_usu_PQR__id_solicitud_tramite__in=list(instance.values_list('id_solicitud_tramite', flat=True)))
        
        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance,many=True)
        data_respuesta = serializador.data
        data_validada =[]
        if radicado and radicado != '':
            data_validada = [item for item in serializador.data if radicado in item.get('cabecera', {}).get('radicado', '')]
        else :
            data_validada = data_respuesta
            
        # Filtro radicado para complementos
        
        serializador_complementos = self.serializer_complementos_class(instance_complementos,many=True)
        data_respuesta_complementos = serializador_complementos.data
        data_validada_complementos =[]
        if radicado and radicado != '':
            data_validada_complementos = [item for item in serializador_complementos if radicado in item.get('cabecera', {}).get('radicado', '')]
        else :
            data_validada_complementos = data_respuesta_complementos
        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_validada, 'data_complementos':data_validada_complementos}, status=status.HTTP_200_OK)

#Asignacion_Tramites
class AsignacionTramiteSubseccionOGrupo(generics.CreateAPIView):
    serializer_class = AsignacionTramitesPostSerializer
    queryset = AsignacionTramites.objects.all()
    permission_classes = [IsAuthenticated]
    creador_estados = Estados_PQRCreate

    def post(self, request, *args, **kwargs):
        data_in = request.data
        subseccion_id = data_in.get('id_und_org_seccion_asignada')

        # # Validar si la subsección tiene configurada la serie documental para ambos trámites
        # if not self.tiene_serie_documental(subseccion_id, 'Determinantes ambientales de planes parciales'):
        #     raise ValidationError("La subsección no tiene configurada la serie documental para el de Trámite Determinantes ambientales de planes parciales.")
        # if not self.tiene_serie_documental(subseccion_id, 'Determinantes ambientales de propiedad privada'):
        #     raise ValidationError("La subsección no tiene configurada la serie documental para el tramite Determinantes ambientales de propiedad privada.")

        # Resto del código para validar la solicitud y obtener información

        with transaction.atomic():
            # Verificar si la solicitud ya fue aceptada
            instance = AsignacionTramites.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite'])
            for asignacion in instance:
                if asignacion.cod_estado_asignacion == 'Ac':
                    raise ValidationError("La solicitud ya fue aceptada.")
                if not asignacion.cod_estado_asignacion:
                    raise ValidationError("La solicitud está pendiente por respuesta.")


            agno_actual = datetime.now().year
            # Verificar si se envió el ID de solicitud de OPA

            if 'id_catalogo_serie_subserie' not in data_in:
                raise ValidationError("No se envió el ID de la Subserie")
            

            #id_catalogo_serie_subserie
            catalogo = CatalogosSeriesUnidad.objects.filter(id_cat_serie_und=data_in['id_catalogo_serie_subserie']).first()
            if not catalogo:
                raise ValidationError("No se encontró la Subserie")
            tripleta_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_cat_serie_und=data_in['id_catalogo_serie_subserie']).first()
            
            if not tripleta_trd:
                raise ValidationError('Debe enviar el id de la tripleta de TRD seleccionada')
            #BUSCAR EL AÑO

            configuracion_expediente = ConfiguracionTipoExpedienteAgno.objects.filter(id_cat_serie_undorg_ccd = tripleta_trd.id_catserie_unidadorg,agno_expediente=agno_actual).first()
            if not configuracion_expediente:
                raise ValidationError("Este catalogo de de series-suberie no cuenta con configuracion para este año.")




            # Obtener el líder de la Subsección planeacion
            lider_subseccion = self.obtener_lider_subseccion(subseccion_id)

            # Validar si hay líder asignado
            if lider_subseccion:
                # Habilitar el control "Líder de la Subsección"
                data_in['lider_subseccion'] = lider_subseccion
                # Habilitar el botón "Asignar"
                data_in['asignacion_de_ventanilla'] = True
            else:
                raise ValidationError("No se puede asignar el tramite a una subsección que no tiene líder asignado.")

            # Resto del código para validar la solicitud y obtener información

            # Validar si la asignación es para el líder de un grupo
            if data_in.get('asignar_a_lider_grupo'):
                id_grupo = data_in.get('id_grupo_asignado')
                lider_grupo = self.obtener_lider_grupo(id_grupo)

                if lider_grupo:
                    # Habilitar el control "Líder del Grupo"
                    data_in['lider_grupo'] = lider_grupo
                    # Habilitar el botón "Asignar"
                    data_in['asignacion_de_ventanilla'] = True
                else:
                    raise ValidationError("No puedes asignar el trámite a un grupo que no tiene líder asignado.")

            # Resto del código para validar la solicitud y obtener información

            max_consecutivo = AsignacionTramites.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite']).aggregate(Max('consecutivo_asign_x_tramite'))

            if max_consecutivo['consecutivo_asign_x_tramite__max'] is None:
                ultimo_consec = 1
            else:
                ultimo_consec = max_consecutivo['consecutivo_asign_x_tramite__max'] + 1

            unidad_asignar = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=data_in['id_und_org_seccion_asignada']).first()
            if not unidad_asignar:
                raise ValidationError("No existe la unidad asignada")

            data_in['consecutivo_asign_x_tramite'] = ultimo_consec
            data_in['fecha_asignacion'] = timezone.now()
            data_in['id_persona_asigna'] = request.user.persona.id_persona
            data_in['cod_estado_asignacion'] = None
            data_in['asignacion_de_ventanilla'] = True

            # AGREGAR LA VALIDACIÓN PARA ASIGNACIÓN DE GRUPO
            if data_in.get('asignar_a_lider_grupo'):
                id_grupo = data_in.get('id_grupo_asignado')
                lider_grupo = self.obtener_lider_grupo(id_grupo)

                if lider_grupo:
                    # Crear el registro en la tabla T279 para la asignación de grupo
                    registro_t279_grupo = SolicitudesTramites.objects.create(
                        T279Id_SolicitudTramite=data_in['id_solicitud_tramite'],
                        T279consecutivoAsignXTramite=ultimo_consec,
                        T279fechaAsignacion=timezone.now(),
                        T279Id_PersonaAsigna=request.user.persona.id_persona,
                        T279Id_PersonaAsignada=lider_grupo.id_persona,
                        T279codEstadoAsignacion=None,
                        T279fechaEleccionEstado=None,
                        T279asignacionDeVentanilla=True,
                        T268Id_UndOrgSeccion_Asignada=subseccion_id,
                        T268Id_UndOrgOficina_Asignada=id_grupo
                    )

                    # Crear el registro en la tabla T315TareasAsignadas
                    registro_t315_grupo = TareasAsignadas.objects.create(
                        cod_tipo_tarea ='Rtra',
                        id_asignacion=registro_t279_grupo.id_solicitud_tramite,
                        fecha_asignacion=timezone.now(),
                    )

                    # Crear el registro en la tabla T265Tareas_BandejaTareas_Persona
                    registro_t264_grupo = BandejaTareasPersona.objects.create(
                        T264Id_BandejaTareas_Persona=registro_t264_grupo.T264IdBandejaTareas_Persona,
                        T264Id_TareaAsignada=registro_t315_grupo.id_tarea_asignada,
                        T264leida=False,
                        T264esResponsablePpal=True
                    )

                    # Mostrar el grillado con la información básica de la asignación de grupo
                    grillado_info_grupo = {
                        'Acción': 'ASIGNACIÓN DE TRÁMITE',
                        'Fecha de asignación': registro_t279_grupo.fecha_envio_solicitud,
                        'Fecha respuesta de asignación': '',
                        'Asignado para': lider_grupo.nombre_completo_persona,
                        'Subsección': {
                            'Código': unidad_asignar.codigo,
                            'Agrupación documental': 'SUB',
                            'Nombre': unidad_asignar.nombre
                        },
                        'Grupo': {
                            'Código': lider_grupo.codigo_grupo,
                            'Nombre': lider_grupo.nombre_grupo
                        },
                        'Estado Asignación': 'EN ESPERA',
                        'Observación': ''
                    }

                    return Response({
                        'success': True,
                        'detail': "Asignación realizada con éxito, debes esperar a que el líder del grupo acepte la asignación.",
                        'data': serializer.data,
                        'estado': data_estado,
                        'tarea': respuesta_relacion.data['data'],
                        'grillado_info': grillado_info_grupo
                    }, status=status.HTTP_200_OK)

                else:
                    raise ValidationError("No puedes asignar el trámite a un grupo que no tiene líder asignado.")
                

            # Resto del código para validar la solicitud y obtener información

            max_consecutivo = AsignacionTramites.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite']).aggregate(Max('consecutivo_asign_x_tramite'))

            if max_consecutivo['consecutivo_asign_x_tramite__max'] is None:
                ultimo_consec = 1
            else:
                ultimo_consec = max_consecutivo['consecutivo_asign_x_tramite__max'] + 1

            unidad_asignar = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=data_in['id_und_org_seccion_asignada']).first()
            if not unidad_asignar:
                raise ValidationError("No existe la unidad asignada")

            data_in['consecutivo_asign_x_tramite'] = ultimo_consec
            data_in['fecha_asignacion'] = timezone.now()
            data_in['id_persona_asigna'] = request.user.persona.id_persona
            data_in['cod_estado_asignacion'] = None
            data_in['asignacion_de_ventanilla'] = True

            # ASOCIAR ESTADO
            data_estado_asociado = {}
            data_estado_asociado['id_tramite'] = request.data['id_solicitud_tramite']
            data_estado_asociado['estado_solicitud'] = 5
            data_estado_asociado['fecha_iniEstado'] = timezone.now()
            data_estado_asociado['persona_genera_estado'] = request.user.persona.id_persona
            respuesta_estado_asociado = self.creador_estados.crear_estado(self, data_estado_asociado)
            data_estado = respuesta_estado_asociado.data['data']

            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Crear tarea y asignación de tarea
            id_persona_asignada = serializer.data['id_persona_asignada']

            # Creamos la tarea 315 #pendiente panel de ventanilla de tramite
            data_tarea = {}
            data_tarea['cod_tipo_tarea'] = 'Rtra' #KEVIN NO ES ROpa es Rtra
            data_tarea['id_asignacion'] = serializer.data['id_asignacion_tramite']
            data_tarea['fecha_asignacion'] = timezone.now()
            data_tarea['cod_estado_solicitud'] = 'Ep'

            vista_tareas = TareasAsignadasCreate()
            respuesta_tareas = vista_tareas.crear_asignacion_tarea(data_tarea)
            if respuesta_tareas.status_code != status.HTTP_201_CREATED:
                return respuesta_tareas
            data_tarea_respuesta = respuesta_tareas.data['data']

            # Teniendo la bandeja de tareas, la tarea ahora tenemos que asignar esa tarea a la bandeja de tareas
            id_tarea_asignada = data_tarea_respuesta['id_tarea_asignada']
            vista_asignacion = TareaBandejaTareasPersonaCreate()
            data_tarea_bandeja_asignacion = {}
            data_tarea_bandeja_asignacion['id_persona'] = id_persona_asignada
            data_tarea_bandeja_asignacion['id_tarea_asignada'] = id_tarea_asignada
            data_tarea_bandeja_asignacion['es_responsable_ppal'] = True
            respuesta_relacion = vista_asignacion.crear_tarea(data_tarea_bandeja_asignacion)
            if respuesta_relacion.status_code != status.HTTP_201_CREATED:
                return respuesta_relacion

            # CREAMOS LA ALERTA DE ASIGNACION A GRUPO
            persona = Personas.objects.filter(id_persona=id_persona_asignada).first()
            nombre_completo_persona = ''
            if persona:
                nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                                persona.primer_apellido, persona.segundo_apellido]
                nombre_completo_persona = ' '.join(item for item in nombre_list if item is not None)
                nombre_completo_persona = nombre_completo_persona if nombre_completo_persona != "" else None

            mensaje = "Tipo de solicitud : OPAS \n Unidad Organizacional : " + unidad_asignar.nombre + \
                      " \n Lider de Unidad Organizacional: " + nombre_completo_persona + \
                      " \n Fecha de asignacion : " + str(serializer.data['fecha_asignacion'])
            vista_alertas_programadas = AlertaEventoInmediadoCreate()
            data_alerta = {}
            data_alerta['cod_clase_alerta'] = 'Gst_SlALid'
            data_alerta['id_persona'] = id_persona_asignada
            data_alerta['id_elemento_implicado'] = serializer.data['id_asignacion_tramite']
            data_alerta['informacion_complemento_mensaje'] = mensaje

            respuesta_alerta = vista_alertas_programadas.crear_alerta_evento_inmediato(data_alerta)
            if respuesta_alerta.status_code != status.HTTP_200_OK:
                return respuesta_alerta

            # Validar si el líder de la subsección Planeación rechaza la asignación
            if data_in.get('rechazar_asignacion'):
                # Validar que exista la justificación
                justificacion_rechazo = data_in.get('justificacion_rechazo')
                if not justificacion_rechazo:
                    raise ValidationError("La justificación de rechazo es requerida.")

                # Actualizar estado de asignación cuando el líder de Planeación rechaza la asignación
                estado_rechazado = 'Re'
                fecha_rechazo = timezone.now()

                # Actualizar estado, fecha de elección y justificación de rechazo
                AsignacionTramites.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite']).update(
                    cod_estado_asignacion=estado_rechazado,
                    fecha_eleccion_estado=fecha_rechazo,
                    justificacion_rechazo=justificacion_rechazo
                )

                # Actualizar estado actual del trámite a EN ESPERA
                solicitud_tramite = SolicitudesTramites.objects.get(id_solicitud_tramite=data_in['id_solicitud_tramite'])
                solicitud_tramite.id_estado_actual_solicitud = '1'  # ID del estado EN ESPERA, ajusta según tu base de datos
                solicitud_tramite.save()

                # Mostrar el grillado con la información básica de la asignación
                grillado_info = {
                    'Acción': 'RECHAZO DE ASIGNACIÓN',
                    'Fecha de asignación': serializer.data['fecha_asignacion'],
                    'Fecha respuesta de asignación': fecha_rechazo,
                    'Asignado para': serializer.data['lider_subseccion'] if not data_in.get('asignar_a_lider_grupo') else serializer.data['lider_grupo'],
                    'Subsección' if not data_in.get('asignar_a_lider_grupo') else 'Grupo': {
                        'Código': unidad_asignar.codigo,
                        'Agrupación documental': 'SUB' if not data_in.get('asignar_a_lider_grupo') else 'GRU',
                        'Nombre': unidad_asignar.nombre
                    },
                    'Estado Asignación': 'RECHAZADO',
                    'Observación': justificacion_rechazo
                }

                # Cambiar estado de asignación a RECHAZADA y mostrar la información en la interfaz
                return Response({
                    'success': True,
                    'detail': "La asignación ha sido rechazada satisfactoriamente.",
                    'data': serializer.data,
                    'estado': data_estado,
                    'tarea': respuesta_relacion.data['data'],
                    'grillado_info': grillado_info
                }, status=status.HTTP_200_OK)

            # Actualizar estado de asignación cuando el líder de Planeación acepta la asignación
            estado_aceptado = None
            fecha_aceptacion = timezone.now()

            # Actualizar estado y fecha de asignación
            AsignacionTramites.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite']).update(
                cod_estado_asignacion=estado_aceptado,
                fecha_eleccion_estado=fecha_aceptacion
            )

            # Obtener la instancia de SolicitudesTramites
            solicitud_tramite = SolicitudesTramites.objects.get(id_solicitud_tramite=data_in['id_solicitud_tramite'])

            # Obtener el ID del estado actual
            id_estado_solicitud = solicitud_tramite.id_estado_actual_solicitud.id_estado_solicitud
            
            # Obtener la instancia del estado usando el ID
            estado_solicitud = EstadosSolicitudes.objects.get(id_estado_solicitud=id_estado_solicitud)


            # Crear nuevo estado EN GESTION para el trámite
            fecha_ini_estado_gestion = timezone.now()

            # Usar la instancia de Personas en lugar de su ID
            persona_genera_estado_gestion = Personas.objects.get(id_persona=data_in['id_persona_asignada'])

            # Crear registro en T255Estados_PQR_Otros_Tramites
            nuevo_estado_gestion = Estados_PQR.objects.create(
                id_tramite=solicitud_tramite,
                estado_solicitud=estado_solicitud,
                fecha_iniEstado=fecha_ini_estado_gestion,
                persona_genera_estado=persona_genera_estado_gestion
            )

            # Obtener el ID del nuevo estado EN GESTION
            id_estado_gestion = nuevo_estado_gestion.estado_solicitud.id_estado_solicitud

            # Actualizar el estado actual del trámite a EN GESTION
            solicitud_tramite.id_estado_actual_solicitud = estado_solicitud
            solicitud_tramite.save()
            estado_en_gestion = EstadosSolicitudes.objects.get(id_estado_solicitud=id_estado_gestion)

            # Actualizar el estado actual del trámite a EN GESTION
            solicitud_tramite = SolicitudesTramites.objects.get(id_solicitud_tramite=data_in['id_solicitud_tramite'])
            solicitud_tramite.id_estado_actual_solicitud = estado_en_gestion
            solicitud_tramite.save()

            # Mensaje de éxito
            success_message = "No puedes volver a realizar una asignación sobre el trámite " \
                              "porque ya fue asignado y aceptado por el líder de una subsección."

            return Response({
                'success': True,
                'detail': success_message,
                'data': serializer.data,
                'estado': data_estado,
                'tarea': respuesta_relacion.data['data'],
            }, status=status.HTTP_200_OK)

    def obtener_lider_subseccion(self, subseccion_id):
        # Consultar el líder de la Subsección Gestión Ambiental
        lider_subseccion = LideresUnidadesOrg.objects.filter(id_unidad_organizacional=subseccion_id).first()

        if lider_subseccion:
            # Obtener información del líder desde la tabla Personas
            persona_lider = lider_subseccion.id_persona
            nombre_completo_lider = f"{persona_lider.primer_nombre} {persona_lider.segundo_nombre} {persona_lider.primer_apellido} {persona_lider.segundo_apellido}"
            return nombre_completo_lider if nombre_completo_lider.strip() else None
        else:
            return None

    def tiene_serie_documental(self, subseccion_id, nombre_tramite):
        try:
            unidad_organizacional = UnidadesOrganizacionales.objects.get(
                id_unidad_organizacional=subseccion_id,
                cod_agrupacion_documental='SUB'
            )
        except UnidadesOrganizacionales.DoesNotExist:
            return False

        cat_series = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=unidad_organizacional)

        for cat_serie in cat_series:
            catalogo_serie = cat_serie.id_catalogo_serie
            serie_doc = SeriesDoc.objects.filter(id_ccd__id_ccd=catalogo_serie.id_catalogo_serie, nombre=nombre_tramite)
            
            if serie_doc.exists():
                return True

        return False
    


# class SeccionSubseccionPlaneacionAsignacionGet(generics.ListAPIView):
#     serializer_class = UnidadesOrganizacionalesSecSubVentanillaGetSerializer
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # Obtener el organigrama actual
#         organigrama = Organigramas.objects.filter(actual=True)
#         if not organigrama:
#             raise NotFound('No existe ningún organigrama activado')
#         if len(organigrama) > 1:
#             raise PermissionDenied('Existe más de un organigrama actual, contacte a soporte')
#         organigrama_actual = organigrama.first()

#         # Filtrar unidades organizacionales para obtener la subsección de Gestión Ambiental
#         unidad_gestion_ambiental = UnidadesOrganizacionales.objects.filter(
#             cod_agrupacion_documental='SUB',
#             id_organigrama=organigrama_actual.id_organigrama,
#             nombre__iexact='Planeación'
#         ).first()

#         # Verificar si hay subsección de Gestión Ambiental
#         if not unidad_gestion_ambiental:
#             raise NotFound('No hay subsección de Gestión Ambiental')

#         # Serializar la subsección de Gestión Ambiental
#         serializer = UnidadesOrganizacionalesSecSubVentanillaGetSerializer(
#             [unidad_gestion_ambiental],  
#             many=True
#         )

#         return Response({
#             'success': True,
#             'detail': 'Se encontró la subsección de Planeación',
#             'data': serializer.data
#         }, status=status.HTTP_200_OK)
    
class SeccionSubseccionPlaneacionAsignacionGet(generics.ListAPIView):
    serializer_class = UnidadesOrganizacionalesSecSubVentanillaGetSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtener el organigrama actual
        organigrama = Organigramas.objects.filter(actual=True)
        if not organigrama:
            raise NotFound('No existe ningún organigrama activado')
        if len(organigrama) > 1:
            raise PermissionDenied('Existe más de un organigrama actual, contacte a soporte')
        organigrama_actual = organigrama.first()

        # Buscar las series por nombre y obtener sus IDs
        series_a_buscar = ['Licencias', 'Permisos', 'Determinantes', 'Certificaciones', 'Registros']
        series_encontradas = SeriesDoc.objects.filter(nombre__in=series_a_buscar)
        ids_series_encontradas = series_encontradas.values_list('id_serie_doc', flat=True)

        # Buscar las unidades organizacionales relacionadas a las series encontradas
        unidades_relacionadas = CatalogosSeriesUnidad.objects.filter(id_catalogo_serie__id_serie_doc__in=ids_series_encontradas)
        unidades_organizacionales = unidades_relacionadas.values_list('id_unidad_organizacional', flat=True)

        # Obtener las unidades organizacionales
        unidades_organizacionales_info = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=unidades_organizacionales)

        # Serializar las unidades organizacionales encontradas
        serializer = UnidadesOrganizacionalesSecSubVentanillaGetSerializer(unidades_organizacionales_info, many=True)

        return Response({
            'success': True,
            'detail': 'Unidades organizacionales encontradas para las series especificadas',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    


class AsignacionTramitesGet(generics.ListAPIView):
    serializer_class = AsignacionTramiteGetSerializer
    queryset = AsignacionTramites.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,tra):
        
        instance = self.get_queryset().filter(id_solicitud_tramite=tra)
        if not instance:
            raise NotFound("No existen registros")
        
        serializer = self.serializer_class(instance,many=True)

        #return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'seccion':serializer_unidad.data,'hijos':serializer.data}}, status=status.HTTP_200_OK)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)

class TramitesCompletementosGet(generics.ListAPIView):
    serializer_class = TramitesComplementosUsu_PQRGetSerializer
    queryset = ComplementosUsu_PQR.objects.filter(id_solicitud_usu_PQR__id_solicitud_tramite__isnull=False, id_solicitud_usu_PQR__cod_tipo_oficio='R')
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_solicitud_tramite):
        instance = self.get_queryset().filter(id_solicitud_usu_PQR__id_solicitud_tramite=id_solicitud_tramite)
        if not instance:
            raise NotFound("No existen registros")
        
        serializador = self.serializer_class(instance, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)

class TramitesSolicitudDeDigitalizacionComplementoCreate(generics.CreateAPIView):
    serializer_class = SolicitudDeDigitalizacionPostSerializer
    serializer_complemento = ComplementosUsu_PQRPutSerializer
    queryset =SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]
    creador_estados = Estados_PQRCreate
    
    def post(self, request):
        fecha_actual = datetime.now()
        data_in = request.data

        complemento= ComplementosUsu_PQR.objects.filter(idComplementoUsu_PQR=request.data['id_complemento_usu_pqr']).first()
        if not complemento:
            raise NotFound("No existe el complemento del tramite elegido")
        
        if  not complemento.requiere_digitalizacion:
            raise ValidationError("No requiere digitalizacion")
        
        data_in['fecha_solicitud'] = datetime.now()
        data_in['digitalizacion_completada'] = False
        data_in['devuelta_sin_completar'] = False

        #valida si tiene solicitudess pendientes
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_complemento_usu_pqr=request.data['id_complemento_usu_pqr'])
        for solicitud in solicitudes:
            if  not solicitud.fecha_rta_solicitud:
                raise ValidationError('No se puede realizar la solicitud porque tiene pendientes')
        
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        #Actualizacion de fecha de complemento
        data_complemento = {}
        data_complemento['fecha_envio_definitivo_digitalizacion'] = datetime.now()
        
        complemento_serializer = self.serializer_complemento(complemento,data=data_complemento,partial=True )
        complemento_serializer.is_valid(raise_exception=True)
        complemento_serializer.save()
        
        #Actualizar registro en la T255
        estado_solicitud_a_usuario = Estados_PQR.objects.filter(solicitud_usu_sobre_PQR=complemento.id_solicitud_usu_PQR.id_solicitud_al_usuario_sobre_pqrsdf, estado_solicitud=6).first()
        if not estado_solicitud_a_usuario:
            raise ValidationError("No se encontró el estado RESPONDIDA de la solicitud del complemento elegido. Por favor validar")
        
        # #ASOCIAR ESTADO
        data_estado_asociado = {}
        data_estado_asociado['solicitud_usu_sobre_PQR'] = complemento.id_solicitud_usu_PQR.id_solicitud_al_usuario_sobre_pqrsdf
        data_estado_asociado['estado_solicitud'] = 9
        data_estado_asociado['estado_PQR_asociado'] = estado_solicitud_a_usuario.id_estado_PQR
        data_estado_asociado['fecha_iniEstado'] = fecha_actual
        data_estado_asociado['persona_genera_estado'] = request.user.persona.id_persona
        
        self.creador_estados.crear_estado(self,data_estado_asociado)
        
        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,'complemento':complemento_serializer.data}, status=status.HTTP_200_OK)

class AsignacionComplementoTramitesCreate(generics.CreateAPIView):
    serializer_class = AsignacionTramitesPostSerializer
    queryset = AsignacionTramites.objects.all()
    permission_classes = [IsAuthenticated]
    creador_estados = Estados_PQRCreate
    
    def post(self, request):
        id_complemento_usu_pqr = request.data['id_complemento_usu_pqr']
        
        complemento = ComplementosUsu_PQR.objects.filter(idComplementoUsu_PQR=id_complemento_usu_pqr).first()
        if not complemento:
            raise NotFound("No existe el complemento del tramite elegido")
        
        if complemento.requiere_digitalizacion:
            raise PermissionDenied('El complemento del trámite debe encontrarse digitalizado')
        
        solicitud_tramite = complemento.id_solicitud_usu_PQR.id_solicitud_tramite
        
        asignacion_tramite = AsignacionTramites.objects.filter(id_solicitud_tramite=solicitud_tramite.id_solicitud_tramite).first()
        cod_estado_asignacion_tramite = asignacion_tramite.cod_estado_asignacion
        if cod_estado_asignacion_tramite != 'Ac':
            raise PermissionDenied("No se puede realizar la asignación porque la asignación a grupo del trámite no ha sido aceptado")
        
        # Actualizar en T267
        complemento.complemento_asignado_unidad = True
        complemento.save()
        
        # Crear registro en T317
        tarea_tramite = TareasAsignadas.objects.filter(id_asignacion=asignacion_tramite.id_asignacion_tramite, cod_tipo_tarea='Rtra').first()
        if not tarea_tramite:
            raise ValidationError("No se encontró la tarea asignada del trámite. Por favor valide")
        
        AdicionalesDeTareas.objects.create(
            id_complemento_usu_pqr = complemento,
            id_tarea_asignada = tarea_tramite,
            fecha_de_adicion = datetime.now()
        )
        
        # Actualizar en T315 si aplica
        complementos_tramite = ComplementosUsu_PQR.objects.filter(id_solicitud_usu_PQR__id_solicitud_tramite=solicitud_tramite.id_solicitud_tramite)
        complementos_tramite_asignados = complementos_tramite.filter(complemento_asignado_unidad=True)
        
        if complementos_tramite.count() == complementos_tramite_asignados.count():
            tarea_tramite.requerimientos_pendientes_respuesta = False
            tarea_tramite.save()
        
        return Response({'success': True, 'detail':'Se realizó la asignación a grupo'}, status=status.HTTP_201_CREATED)




#DOCUMENTOS Y META-DATA
class AnexoMetaDataGet(generics.ListAPIView):
    serializer_class = MetadatosAnexosTmpSerializerGet
    queryset =Anexos.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
      
        instance =Anexos.objects.filter(id_anexo=pk).first()

        if not instance:
                raise NotFound("No existen registros")
        
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=instance.id_anexo).first()
        if not meta_data:
            raise NotFound("No existen registros")
   
        serializer= self.serializer_class(meta_data)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'id_anexo':instance.id_anexo,**serializer.data},}, status=status.HTTP_200_OK)




class AnexoDocumentoDigitalGet(generics.ListAPIView):
    serializer_class = AnexoArchivosDigitalesSerializer
    queryset =Anexos.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
      
        instance =Anexos.objects.filter(id_anexo=pk).first()

        if not instance:
                raise NotFound("No existen registros")
        
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=instance.id_anexo).first()
        if not meta_data:
            raise NotFound("No existen registros")
        archivo = meta_data.id_archivo_sistema
        serializer= self.serializer_class(archivo)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'id_anexo':instance.id_anexo,**serializer.data},}, status=status.HTTP_200_OK)





class CrearExpedienteTramite(generics.CreateAPIView):
    serializer_class = AperturaExpedienteSimpleSerializer
    serializer_class_complejo = AperturaExpedienteComplejoSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        data = request.data

        data_expediente = {}
        
        # Crear codigo expediente
        tripleta_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_cat_serie_und=data['id_cat_serie_und_org_ccd_trd_prop']).first()
        
        if not tripleta_trd:
            raise ValidationError('Debe enviar el id de la tripleta de TRD seleccionada')
        #PENDIENTE EL AÑO
        configuracion_expediente = ConfiguracionTipoExpedienteAgno.objects.filter(id_cat_serie_undorg_ccd = tripleta_trd.id_catserie_unidadorg).first()

        if not configuracion_expediente:
            raise ValidationError('No se encontró la configuración de expediente para la tripleta de TRD seleccionada')
        
        cod_unidad = tripleta_trd.id_cat_serie_und.id_unidad_organizacional.codigo
        cod_serie = tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_serie_doc.codigo
        cod_subserie = tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc.codigo if tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc else None
        
        codigo_exp_und_serie_subserie = cod_unidad + '.' + cod_serie + '.' + cod_subserie if cod_subserie else cod_unidad + '.' + cod_serie
        
        
        current_date = datetime.now()
        
        
        data_expediente['codigo_exp_und_serie_subserie'] = codigo_exp_und_serie_subserie
        data_expediente['codigo_exp_Agno'] = current_date.year
        
        # OBTENER CONSECUTIVO ACTUAL
        codigo_exp_consec_por_agno = None
        
        if configuracion_expediente.cod_tipo_expediente == 'C':
            # LLAMAR CLASE PARA GENERAR CONSECUTIVO
            fecha_actual = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            clase_consec = ConfiguracionTipoExpedienteAgnoGetConsect()
            codigo_exp_consec_por_agno = clase_consec.generar_radicado(
                tripleta_trd.id_catserie_unidadorg,
                request.user.persona.id_persona,
                fecha_actual
            )
            codigo_exp_consec_por_agno = codigo_exp_consec_por_agno.data.get('data').get('consecutivo_actual')
        else:
            expediente = ExpedientesDocumentales.objects.filter(id_cat_serie_und_org_ccd_trd_prop=tripleta_trd.id_catserie_unidadorg, codigo_exp_Agno=current_date.year).first()
        
            if expediente:
                raise ValidationError('Ya existe un expediente simple para este año en la Serie-Subserie-Unidad seleccionada')
            
        data_expediente['titulo_expediente'] = f"Expediente Tramite {codigo_exp_und_serie_subserie} {current_date.year}"
        data_expediente['descripcion_expediente'] = f"Expediente Tramite para la unidad {codigo_exp_und_serie_subserie} y el año {current_date.year}"
        data_expediente['palabras_clave_expediente'] = f"Expediente|Tramite|{codigo_exp_und_serie_subserie}|{current_date.year}"
        data_expediente['id_cat_serie_und_org_ccd_trd_prop'] = tripleta_trd.id_catserie_unidadorg
        data_expediente['id_trd_origen'] = tripleta_trd.id_trd.id_trd
        data_expediente['id_und_seccion_propietaria_serie'] = tripleta_trd.id_cat_serie_und.id_unidad_organizacional.id_unidad_organizacional
        data_expediente['id_serie_origen'] = tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_serie_doc.id_serie_doc
        data_expediente['id_subserie_origen'] = tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc.id_subserie_doc if tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc else None
        data_expediente['codigo_exp_consec_por_agno'] = codigo_exp_consec_por_agno
        data_expediente['estado'] = 'A'
        data_expediente['fecha_apertura_expediente'] = current_date
        data_expediente['fecha_folio_inicial'] = current_date
        data_expediente['cod_etapa_de_archivo_actual_exped'] = 'G'
        data_expediente['tiene_carpeta_fisica'] = False
        data_expediente['ubicacion_fisica_esta_actualizada'] = False
        data_expediente['creado_automaticamente'] = True
        data_expediente['cod_tipo_expediente'] = configuracion_expediente.cod_tipo_expediente
        data_expediente['id_unidad_org_oficina_respon_original'] = data['id_unidad_org_oficina_respon_original']
        data_expediente['id_und_org_oficina_respon_actual'] = data['id_unidad_org_oficina_respon_original']


        request.data['cod_tipo_expediente'] = configuracion_expediente.cod_tipo_expediente
        request.data['codigo_exp_und_serie_subserie'] = codigo_exp_und_serie_subserie

        
        if configuracion_expediente.cod_tipo_expediente == 'S':
            serializer = self.serializer_class(data=data_expediente, context = {'request':request})
            serializer.is_valid(raise_exception=True)
            expediente_creado = serializer.save()
        elif configuracion_expediente.cod_tipo_expediente == 'C':
            serializer = self.serializer_class_complejo(data=data_expediente, context = {'request':request})
            serializer.is_valid(raise_exception=True)
            expediente_creado = serializer.save()
        

        
        # CREAR INDICE - PENDIENTE VALIDAR SI ES CORRECTO REALIZARLO ASÍ
        IndicesElectronicosExp.objects.create(
            id_expediente_doc = expediente_creado,
            fecha_indice_electronico = current_date,
            abierto = True
        )
        
        # AUDITORIA
        usuario = request.user.id_usuario
        descripcion = {
            "CodigoExpUndSerieSubserie": str(codigo_exp_und_serie_subserie),
            "CodigoExpAgno": str(serializer.data.get('codigo_exp_Agno')),
        }
        if codigo_exp_consec_por_agno:
            descripcion['CodigoExpConsecPorAgno'] = str(codigo_exp_consec_por_agno)
        
        direccion = Util.get_client_ip(request)
        auditoria_data = {
            "id_modulo" : 188,
            "cod_permiso": "CR",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
        }
        Util.save_auditoria(auditoria_data)
            
        return Response({'success':True, 'detail':'Apertura realizada de manera exitosa', 'data':serializer.data}, status=status.HTTP_201_CREATED)



class CreateAutoInicio(generics.CreateAPIView):
    
    serializer_class = ActosAdministrativosCreateSerializer
    queryset = ActosAdministrativos

    def radicado_completo(self,radicado):
            
        cadena = ""
        if radicado:
            #radicado = obj.id_solicitud_tramite.id_radicado
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=radicado.agno_radicado,cod_tipo_radicado=radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= radicado.prefijo_radicado+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            return cadena
        return ""

    def detalle_tramite(self, radicado):
            filter = {}


            filter['radicate_bia__icontains'] = radicado

            
            tramites_values = Tramites.objects.filter(**filter).values()
            
            if tramites_values:
                organized_data = {
                    'procedure_id': tramites_values[0]['procedure_id'],
                    'radicate_bia': tramites_values[0]['radicate_bia'],
                    'proceeding_id': tramites_values[0]['proceeding_id'],
                }
                
                for item in tramites_values:
                    field_name = item['name_key']
                    if item['type_key'] == 'json':
                        value = json.loads(item['value_key'])
                    else:
                        value = item['value_key']
                    organized_data[field_name] = value
            else:
                raise NotFound('No se encontró el detalle del trámite elegido')
            
            return organized_data


    def nombre_persona(self,persona):
           
        nombre_completo_responsable = None
        if persona:
            nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                            persona.primer_apellido, persona.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
        return nombre_completo_responsable
    def acta_inicio(self,data,plantilla):

        context = data
        #print(context)

        #print(str(settings.BASE_DIR) +plantilla)
        #pathToTemplate = str(settings.BASE_DIR) + os.sep +str(plantilla)
        #outputPath = str(settings.BASE_DIR) +os.sep +'salida'+os.sep +str(plantilla)

        pathToTemplate = str(settings.MEDIA_ROOT) + os.sep +str(plantilla)
        outputPath = str(settings.MEDIA_ROOT) +os.sep+'pruebas.docx'

        #print(pathToTemplate)
        doc = DocxTemplate(pathToTemplate)
        doc.render(context)
        #doc.save(outputPath)
       
        return doc
    

    def document_to_inmemory_uploadedfile(self,doc):
        # Guardar el documento en un búfer de memoria
        buffer = BytesIO()
        doc.save(buffer)
        
        # Crear un objeto InMemoryUploadedFile
        file = InMemoryUploadedFile(
            buffer,  # El búfer de memoria que contiene los datos
            None,    # El campo de archivo (no es relevante en este contexto)
            'output.docx',  # El nombre del archivo
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # El tipo MIME del archivo
            buffer.tell(),  # El tamaño del archivo en bytes
            None     # El conjunto de caracteres (no es relevante en este contexto)
        )
        
        return file
    def post(self, request):
        from gestion_documental.views.trd_views import ConsecutivoTipologiaDoc
        vista_consecutivo_trd = ConsecutivoTipologiaDoc

        data_in = request.data
        request.data['plantilla'] = data_in['id_plantilla']
        request.data['variable'] = 'C'

        
        tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite= data_in['id_solicitud_tramite']).first()
        if not tramite:
            raise ValidationError("No se encontro el tramite")
        instance_radicado = tramite.id_radicado
        respuesta_consecutivo = vista_consecutivo_trd.consecutivo(ConsecutivoTipologiaDoc,request,None)
        
        if not respuesta_consecutivo:
            raise ValidationError("No se pudo crear el numero de auto")
        
        if respuesta_consecutivo.status_code != status.HTTP_201_CREATED:
            return respuesta_consecutivo
        data_consecutivo = respuesta_consecutivo.data['data']
        data_in['id_consec_por_nivel_tipologias_doc_agno'] = data_consecutivo['id_consecutivo']
       
        numero_auto = data_consecutivo['consecutivo']
        data_in['numero_acto_administrativo'] = numero_auto
        instancia_consecutivo = ConsecutivoTipologia.objects.filter(id_consecutivo_tipologia=data_consecutivo['id_consecutivo']).first()

        if not tramite.id_expediente:
            raise ValidationError("Este tramite no tiene expediente asociado")

            
        data_expediente = AperturaExpedienteComplejoSerializer(tramite.id_expediente).data
        num_exp=tramite.id_expediente.codigo_exp_und_serie_subserie +'-'+str(tramite.id_expediente.codigo_exp_Agno) +'-'+str(tramite.id_expediente.codigo_exp_consec_por_agno)

        plantilla = PlantillasDoc.objects.filter(id_plantilla_doc=data_in['id_plantilla']).first()
        if not plantilla:
            raise ValidationError("NO SE ENCONTRO PLANTILLA")


        #CONSULTA DATOS DEL TRAMITE DE SASOFTCO

        cadena_radicado = self.radicado_completo(instance_radicado)
        print(cadena_radicado)
        
        detalle_tramite_data = self.detalle_tramite(cadena_radicado)
        #print(detalle_tramite_data)
        context_auto={}
        
        context_auto['Auto'] = numero_auto
        context_auto['Expediente'] = num_exp
        titular = tramite.id_persona_titular
        nombre_usuario = self.nombre_persona(titular)
        context_auto['NombreTitular'] = nombre_usuario
        context_auto['TipoDocTitular'] = titular.tipo_documento.nombre
        context_auto['NumDocTitular'] = titular.numero_documento
        context_auto['RadicadoTramite'] = cadena_radicado
        context_auto['EmailTitular'] = titular.email
        #CORRESPONDENCIA
        context_auto['NumOficioReque '] ='{{NumOficioReque }}'
        context_auto['NumCorrespondenciaDespachada'] = '{{NumCorrespondenciaDespachada}}'
        context_auto['FechaCorrespondenciaDespachada'] = '{{FechaCorrespondenciaDespachada}}'

        #PARA LOS REQUERIMIENTOS  Y RESPUESTA A LOS REQUERIMIENTOS

        context_auto['NumRadicadoUsuario']='{{NumRadicadoUsuario}}'
        context_auto['FechaRadicadoUsuario'] = '{{FechaRadicadoUsuario}}'

        #PARA LIQUIDACION

        liquidacion_tramite =LiquidacionesBase.objects.filter(id_solicitud_tramite=tramite).first()
        if liquidacion_tramite:

            context_auto['ValorLiquidacion '] = liquidacion_tramite.valor_liq
            context_auto['NumeroReferencia'] = liquidacion_tramite.num_liquidacion
            context_auto['FechaReferenciaPago']  = liquidacion_tramite.fecha_liquidacion
        else:
            context_auto['ValorLiquidacion '] = '{{ValorLiquidacion }}'
            context_auto['NumeroReferencia'] = '{{NumeroReferencia}}'
            context_auto['FechaReferenciaPago']  = '{{FechaReferenciaPago}}'
        
        #PARA CONSTANCIA DE PAGO
        context_auto['NumRadicadoPago'] ='{{NumRadicadoPago}}'
        context_auto['FechaNumRadicadoPago'] = '{{FechaNumRadicadoPago }}'


        #PARA  CONCESION DE AGUAS SUPERFICIALES 

        if 'fuente_captacion' in detalle_tramite_data:
                fuente_captacion_json= detalle_tramite_data['fuente_captacion'][0]

                context_auto['NombreFuenteHidrica'] = fuente_captacion_json['Name_fuente_hidrica_value']
        else:
                context_auto['NombreFuenteHidrica'] = '{{NombreFuenteHidrica}}'

        if 'Npredio' in detalle_tramite_data:
                context_auto['NombrePredio'] = detalle_tramite_data['Npredio']
        else:
                context_auto['NombrePredio'] = '{{NombrePredio}}'

        if 'MatriInmobi' in detalle_tramite_data:
                context_auto['NMatriculaInm'] = detalle_tramite_data['MatriInmobi'] 
        else:
                context_auto['NMatriculaInm'] = '{{NMatriculaInm}}'
        
        if 'Municipio' in detalle_tramite_data:
            context_auto['NomMunicipio '] = detalle_tramite_data['Municipio']
        else:
            context_auto['NomMunicipio '] ='{{NomMunicipio}}'

        context_auto['NormatividadAguasSuperficiales'] = '{{NormatividadAguasSuperficiales }}' 

        #PARA CONCECION DE AGUAS SUBTERRANEAS
        if 'Ndivision' in detalle_tramite_data:
            context_auto['NomZona'] = detalle_tramite_data['Ndivision']
        else:
            context_auto['NomZona'] = '{{NomZona}}'

        context_auto['NomProyecto'] = tramite.nombre_proyecto
        
        context_auto['NormativaConcesionAguasSubterraneas'] = '{{NormativaConcesionAguasSubterraneas}}'

        if 'Tfuente' in detalle_tramite_data:
            context_auto['FuenteCaptacion '] = detalle_tramite_data['Tfuente']
        else:
            context_auto['FuenteCaptacion '] = '{{FuenteCaptacion }}'



        #PARA OCUPACION DE CAUSE 

        if 'Informacion_captacion' in detalle_tramite_data:
                fuente_captacion_json= detalle_tramite_data['Informacion_captacion'][0]
                # print(fuente_captacion_json)
                # #raise ValidationError('pere')
                if 'Nfuente' in fuente_captacion_json:

                    context_auto['nombre_fuente_hidrica'] = fuente_captacion_json['Nfuente']
                else: 
                    context_auto['nombre_fuente_hidrica'] = '{{nombre_fuente_hidrica}}'
        else:
                context_auto['nombre_fuente_hidrica'] = '{{nombre_fuente_hidrica}}'

        if 'Informacion_obra' in detalle_tramite_data:
            json_obra = detalle_tramite_data['Informacion_obra']
            if 'Tipo_ocupacion' in json_obra:
                context_auto['TipoObra'] = json_obra['Tipo_ocupacion']
            else:
                context_auto['TipoObra'] = '{{TipoObra}}'
        else:
            context_auto['TipoObra'] = '{{TipoObra}}'

        context_auto['NormativaOcupacionCauce'] ='{{NormativaOcupacionCauce}}'

        # INICIO VERTIMIENTO AL SUELO
        if 'Area' in detalle_tramite_data:
            context_auto['Area'] = detalle_tramite_data['Area']
        else:
            context_auto['Area'] = '{{Area}}'
        
        context_auto['NombrePropietarioPredio '] = '{{NombrePropietarioPredio}}' ##????????
              

        context_auto['NormativaVertimientoAlSuelo'] = '{{NormativaVertimientoAlSuelo }}'#?????

        # INICIO VERTIMIENTO AL AGUA
        context_auto['NormativaVertimientoAlAgua'] = '{{NormativaVertimientoAlAgua }}'#?????

        # PERMISO DE EMISIONES ATMOSFERICAS
        context_auto['TerminoOtorgaCumplirRequerimiento'] = '{{TerminoOtorgaCumplirRequerimiento}}'

        if 'Direccion' in detalle_tramite_data:
            context_auto['Direccion'] = detalle_tramite_data['Direccion']
        else:
            context_auto['Direccion'] = '{{Direccion}}'

        context_auto['TipoProceso'] = '{{TipoProceso}}' #CONSULTAR SASOFT


        #INICIO PROSPECCION Y EXPLORACIÓN
        context_auto['NormativaProspeccionYExploracion'] = '{{NormativaProspeccionYExploracion }}'#?????

        #AUTO INICIO APROVECHAMIENTO FORESTAL UNICO
        context_auto['NormativaAprocechamientoForestalUnico'] = '{{NormativaAprocechamientoForestalUnico }}'#?????

        #AUTO INICIO APROVECHAMIENTO FORESTAL PERSISTENTE
        context_auto['NormativaAprocechamientoForestalPersistente'] = '{{NormativaAprocechamientoForestalPersistente }}'#?????
        dato = self.acta_inicio(context_auto,plantilla.id_archivo_digital.ruta_archivo)

        memoria = self.document_to_inmemory_uploadedfile(dato)

        vista_archivos = ArchivosDgitalesCreate()
        ruta = "home,BIA,tramites,Autos"

        respuesta_archivo = vista_archivos.crear_archivo({"ruta":ruta,'es_Doc_elec_archivo':False},memoria)
        data_archivo = respuesta_archivo.data['data']
        if respuesta_archivo.status_code != status.HTTP_201_CREATED:
            return respuesta_archivo
        
        data_in['id_archivo_acto_administrativo'] =data_archivo['id_archivo_digital']
        data_in['fecha_acto_administrativo'] = datetime.now()
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance_archivo = ArchivosDigitales.objects.filter(id_archivo_digital=data_archivo['id_archivo_digital']).first()
        if not instance_archivo:
            raise NotFound("No se encontro el archivo")
        tramite.id_auto_inicio = instance
        tramite.fecha_inicio = datetime.now()
        tramite.save()
        instancia_consecutivo.id_tramite=tramite
        instancia_consecutivo.variables=context_auto
        instancia_consecutivo.id_archivo_digital = instance_archivo
        instancia_consecutivo.save()

        return Response({'success': True, 'detail':'Se creo el auto de inicio','data':{'auto':serializer.data,'archivo':data_archivo,'cosecutivo_tipologia':data_consecutivo}}, status=status.HTTP_200_OK)



class CrearExpediente(generics.CreateAPIView):
    serializer_class = None
    queryset = None

    def post(self,request):
        data_in = request.data
        vista_creadora_expediente = CrearExpedienteTramite()
        request.data['id_cat_serie_und_org_ccd_trd_prop'] = data_in['id_catalogo_serie_subserie']
        request.data['id_unidad_org_oficina_respon_original'] = data_in['id_und_org_seccion_asignada']
        request.data['id_und_org_oficina_respon_actual'] = data_in['id_und_org_seccion_asignada']
        id_solicitud_tramite = data_in['id_solicitud_tramite']

        tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not tramite:
            raise ValidationError('No se encontro Tramite asociado')
        
        # if tramite.id_expediente:    #DESCOMENTAR AL FINALIZAR LAS PRUEBAS
        #     raise ValidationError("Ya existe un expediente asociado ")
        
        request.data['id_persona_titular_exp_complejo'] = tramite.id_persona_titular.id_persona
        respuesta = vista_creadora_expediente.create(request)
        
        respuesta_expediente = respuesta.data['data']
        
        id_expediente = respuesta_expediente['id_expediente_documental']
        expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=id_expediente).first()
        if not expediente:
            raise NotFound("No se encontro el expediente")
        
        tramite.id_expediente = expediente
        tramite.fecha_expediente = respuesta_expediente['fecha_apertura_expediente']
        tramite.save()
        num_exp=tramite.id_expediente.codigo_exp_und_serie_subserie +'-'+str(tramite.id_expediente.codigo_exp_Agno) +'-'+str(tramite.id_expediente.codigo_exp_consec_por_agno)
        
        return Response({'success': True, 'detail':'Se creo el Expediente','data':{**respuesta_expediente,'numero_expediente':num_exp}}, status=status.HTTP_201_CREATED)

class CreateValidacionTareaTramite(generics.CreateAPIView):
    
    serializer_class = None
    queryset = None


    def archivo_temporal(self,data):
            buffer = BytesIO()

            p = canvas.Canvas(buffer)
            p.drawString(100, 800, 'Archivo No Digitalizado Solo Almacenado en Fisico (Buscar en Carpeta Física)')  # Agregar contenido al PDF, puedes omitir esto si todo el contenido está en el HTML
        
            y_position = 780  

            for key, value in data.items():
            
                p.drawString(100, y_position, f"{key}: {value}")
                y_position -= 20  
            

            p.showPage()
            p.save()

    
            pdf_bytes = buffer.getvalue()
            nombre_archivo='auto.pdf'
            pdf_content_file = ContentFile(pdf_bytes,name=nombre_archivo)

            return pdf_content_file

    def get_token_camunda(self,token):


        auth_headers = {
            "accept": "*/*",
            "Content-Type": "application/json-patch+json"
        }   
        #TOKEN PARA SASOFTCO
        url_login_token = "https://backendclerkapi.sedeselectronicas.com/api/Authentication/login-token-bia"
     
        payload={
            "access":token
        }

  
        try:
            response = requests.post(url_login_token,json=payload,headers=auth_headers)
            response.raise_for_status()  # Si hay un error en la solicitud, generará una excepción
            data = response.json()  # Convertimos los datos a JSON
            
            if 'userinfo' in data:
                if 'userinfo' in data['userinfo']:
                    info = data['userinfo']['userinfo']

                    token = info['tokens']['access']
                    return token
            return None
        except requests.RequestException as e:
            print(f"Error en la solicitud: {e}")
            return None  # Manejo de errores de solicitud


    def get_tramite_ventanilla_sasoft(self,radicado,token):

        #url = "https://backendclerkapi.sedeselectronicas.com/api/Interoperability/tasks"
        url = "https://backendclerkapi.sedeselectronicas.com/api/Interoperability/task-by-number-radicate/"+radicado
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

        try:
            response = requests.get(url,headers=headers)
            response.raise_for_status()  # Si hay un error en la solicitud, generará una excepción
            data = response.json()  # Convertimos los datos a JSON
            
            #print(data)
            return data
        except requests.RequestException as e:
            print(f"Error en la solicitud: {e}")
            return None  # Manejo de errores de solicitud

    def buscar_tramite(self,radicado):
       
        patron = r"([A-Z]+)-(\d{4})-(\d+)"
        coincidencia = re.match(patron, radicado)
        tramite = None
        if coincidencia:
            prefijo = coincidencia.group(1)
            año = coincidencia.group(2)
            entero = int(coincidencia.group(3))  # Convertir el entero a número para quitar ceros a la izquierda

            print(f"Prefijo: {prefijo}")
            print(f"Año: {año}")
            print(f"Entero: {entero}")
            tramite = SolicitudesTramites.objects.filter(id_radicado__prefijo_radicado=prefijo,id_radicado__agno_radicado=año,id_radicado__nro_radicado=entero).first()

        else:
            raise ValidationError ("No se encontro tramite asociado a este radicado")
       
        
        if not tramite:
            raise ValidationError ("No se encontro tramite asociado a este radicado")
        return tramite
        

    def post_tramite_camunda(self,token,data,id):



        #TOKEN PARA SASOFTCO

        #print(data)
        url_login_token = "https://backendclerkapi.sedeselectronicas.com/api/Interoperability/complete-task-assignee-group/"+id
        payload={"variables":data}
        auth_headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
        # payload={
        #     "nombre_de_usuario": "Seguridad",
        #     "password": "Seguridad12345+"
        # }
        
  
        try:
            response = requests.post(url_login_token,json=payload,headers=auth_headers)
            response.raise_for_status()  # Si hay un error en la solicitud, generará una excepción
            data = response.json()  # Convertimos los datos a JSON

            return data
        except requests.RequestException as e:
            error_message=''
            if e.response is not None:
                try:
                    error_details = e.response.json()
                    error_message += f" | Detalles del error: {error_details}"
                except ValueError:
                    error_message += f" | Respuesta del servidor: {e.response.text}"

            print("ERROR")
            raise ValidationError(error_message)
        
        except ValueError as e:
        # Capturar y manejar errores de decodificación JSON
            raise ValidationError(f"Error al decodificar la respuesta JSON: {e}")

    
    def post(self, request):

        #print(request.META.get('HTTP_AUTHORIZATION'))
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        data_in = request.data
        if not authorization_header:
            raise ValidationError("No se suministro un Token")

        token = authorization_header.split(' ')[1] if ' ' in authorization_header else authorization_header
        radicado = request.data['radicado']
        #raise ValidationError(radicado)
        
        
        token_camunda=None
        
        if 'access' in data_in:
            
            token_camunda=data_in['access']
            
        else:
            token_camunda = self.get_token_camunda(token)
        data = self.get_tramite_ventanilla_sasoft(radicado,token_camunda)
        
        
        if not data:
            raise ValidationError("No se encontro el tramite en bandeja de tareas.")
        print(data)



        id_instancia = data['processInstanceId']
        print(id_instancia)
        tramite=None
        if 'id_solicitud_tramite' in data_in and data_in['id_solicitud_tramite']:
            tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite']).first()
        else:
            tramite = self.buscar_tramite(radicado)

        if not tramite:
            raise ValidationError("NO se encontro tramite asociado a este radicado")
        
        print(tramite)
        #BUSCAR TRAMITE POR RADICADO

        #BUSCAR ASIGNACION
        asignacion = AsignacionTramites.objects.filter(id_solicitud_tramite=tramite,cod_estado_asignacion='Ac').first()
        if not asignacion:
            raise ValidationError("El tramite no a sigo aceptado por la unidad organizacional")



        unidad = asignacion.id_und_org_seccion_asignada

  
        #CON TRAMITE BUSCAR DOCUMENTO SOPORTE 
        auto = tramite.id_auto_inicio

        expediente = tramite.id_expediente

        if not expediente:
            raise NotFound("El tramite no tiene expediente asociado")
        

        num_exp=expediente.codigo_exp_und_serie_subserie +'-'+str(expediente.codigo_exp_Agno) +'-'+str(expediente.codigo_exp_consec_por_agno)
        if not auto:
            raise NotFound("No se encontro auto")
        
        archivo = auto.id_archivo_acto_administrativo
        if not archivo:
            raise NotFound("No tiene archivo asignado")
        directorio_raiz = str(settings.MEDIA_ROOT)

        pathToTemplate = directorio_raiz + os.sep +str(archivo.ruta_archivo)

        contenido =None
        contenido_base64=None
        if   os.path.exists(pathToTemplate):
                print("EXISTE")
                with open(pathToTemplate, 'rb') as file:
                    contenido = file.read()
                    contenido_base64 = base64.b64encode(contenido).decode('utf-8')
        else:
            raise ValidationError(" No se encontro el documento del auto")

            # print('NO EXISTE')
            # auto_consecutivo = auto.id_consec_por_nivel_tipologias_doc_agno
            # data_auto = auto_consecutivo.variables
            # respuesta_archivo_blanco= UtilsGestor.generar_archivo_blanco(data_auto)
                
            # if respuesta_archivo_blanco.status_code != status.HTTP_201_CREATED:
            #     return respuesta_archivo_blanco
            # ruta_archivo_blanco = respuesta_archivo_blanco.data['data']['ruta_archivo']
            # ruta_archivo_blanco = ruta_archivo_blanco.lstrip("/\\")

            # print("RUTA RAIZ ES: "+directorio_raiz)
            # print("RUTA DEL ARCHIVO: "+ruta_archivo_blanco)
            # if ruta_archivo_blanco.startswith("media" + os.sep):
            #     ruta_archivo_blanco = ruta_archivo_blanco[len("media" + os.sep):]
            # raise ValidationError(os.path.join(directorio_raiz, ruta_archivo_blanco))
            # full_ruta = os.path.normpath(os.path.join(directorio_raiz, ruta_archivo_blanco))
            # print("FULL RUTA: " + full_ruta)
            # with open(full_ruta, 'rb') as file:
            #         contenido = file.read()
            #         contenido_base64 = base64.b64encode(contenido)
                
        #CON AUTO BUSCAR NUERO DE AUTO Y DOCUMENTO
        print(type(contenido))
        numero_auto = auto.numero_acto_administrativo

        data_respuesta={}
        data_respuesta['NumeroAuto']={
            "type": "string",
            "value": numero_auto,
            "valueInfo": {
                "filename": "string",
                "mimetype": "string",
                "encoding": "string"
            }
        }
        data_respuesta['DocumentoAuto'] = {


            "type": "File",
            "value": contenido_base64,
            "valueInfo": {
            "mimetype": "application/octet-stream",   
            "encoding": "utf-8",
            "filename": str(archivo.nombre_de_Guardado)+'.'+str(archivo.formato)
            }
        }


        pago = tramite.id_pago_evaluacion

        if not pago:
            
            data_respuesta['NumeroPago']={

            "type": "string",
            "value": '00000',
            "valueInfo": {
                "filename": "string",
                "mimetype": "string",
                "encoding": "string"
            }
            }

            data_respuesta['SoportePago'] = {
            "type": "File",
            "value": contenido_base64,
            "valueInfo": {
            "mimetype": "application/octet-stream",
            "encoding": "utf-8",
            "filename": str(archivo.nombre_de_Guardado)+'.'+str(archivo.formato)
            }
            }
            
        # numero_pago = pago.id_liquidacion.num_liquidacion
        # SoportePago 

        # NumExp

        data_respuesta['NumExp']={
            "type": "String",
            "value": num_exp,
            "valueInfo": {
                "filename": "string",
                "mimetype": "string",
                "encoding": "string"
            }
        }

        # GrupoFunTramite 

        data_respuesta['GrupoFunTramite']={
            "type": "String",
            "value": unidad.nombre,
                  "valueInfo": {
                "filename": "string",
                "mimetype": "string",
                "encoding": "string"
            }
        }
        
        # dateAutoStart  #FECHA AUTO
        data_respuesta['dateAutoStart']={
            "type": "string",
            "value": str(auto.fecha_acto_administrativo.date()),
            "valueInfo": {
                "filename": "string",
                "mimetype": "string",
                "encoding": "string"
            }
        }
        # FNAuto #FECHA NOTIFICACION
        data_respuesta['FNAuto']={
            "type": "string",
            "value": str(auto.fecha_acto_administrativo.date()),
            "valueInfo": {
                "filename": "string",
                "mimetype": "string",
                "encoding": "string"
            }
        }
         
        # priorityProject #PRIORITARIO O NO
        data_respuesta['priorityProject']={
            "type": "boolean",
            "value": False,
                  "valueInfo": {
                "filename": "boolean",
                "mimetype": "boolean",
                "encoding": "boolean"
            }
        }
        respuesta = self.post_tramite_camunda(token_camunda,data_respuesta,id_instancia)
        print(respuesta)




        return Response(data_respuesta, status=status.HTTP_201_CREATED)


class BusquedaAvanzadaPlantillasConfiguradas(generics.ListAPIView):
    serializer_class = PlantillasDocBusquedaAvanzadaSerializer
    queryset = PlantillasDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        filter={}
        usuario = request.user.persona

        for key, value in request.query_params.items():

            if key == 'nombre':
                if value !='':
                    filter['nombre__icontains'] = value
            if key =='descripcion':
                if value != '':
                    filter['descripcion__icontains'] = value    
            if key =='tipologia':
                if value != '':
                    filter['id_tipologia_doc_trd__nombre__icontains'] = value
            if key =='disponibilidad':
                if value != '':
                    filter['cod_tipo_acceso__icontains'] = value
            if key =='extension':
                if value != '':
                    filter['id_archivo_digital__formato__icontains'] = value                 
                
        filter['activa']=True


        
        agno_actual = datetime.now().year

        plantilla = self.queryset.all().filter(**filter)
        plantillas_tipologia_configurada=[]
        for data in plantilla:
            config_tipologia = ConfigTipologiasDocAgno.objects.filter(id_tipologia_doc=data.id_tipologia_doc_trd, agno_tipologia = agno_actual).first()
            if config_tipologia:
                plantillas_tipologia_configurada.append(data)
        serializador = self.serializer_class(plantillas_tipologia_configurada,many=True)
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializador.data},status=status.HTTP_200_OK)
        


class SolicitudJuridicaTramitesCreate(generics.CreateAPIView):
    serializer_class = SolicitudJuridicaOPACreateSerializer
    serializer_tramite = TramitePutSerializer
    queryset = SolicitudesDeJuridica.objects.all()
    permission_classes = [IsAuthenticated]
    creador_estados = Estados_PQRCreate
    
    def post(self, request):
        fecha_actual = datetime.now()
      
        data_in = request.data
        solicitud_tramite = SolicitudesTramites.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite']).first()

        if not solicitud_tramite:
            raise NotFound("No existe el Tramite seleccionado.")

        if solicitud_tramite.requiere_digitalizacion and not solicitud_tramite.fecha_envio_definitivo_a_digitalizacion:
            raise ValidationError("Se debe completar la digitalización del Tramite antes de enviar la solicitud a jurídica")
        
        # instance = AsignacionTramites.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite'])
        # for asignacion in instance:
        #     if asignacion.cod_estado_asignacion != 'Ac':
        #         raise ValidationError("El OPA tiene que ser asignado a un grupo antes de enviar la solicitud a jurídica")
        
        solicitud_juridica = self.queryset.filter(id_solicitud_tramite=data_in['id_solicitud_tramite']).first()
        if solicitud_juridica:
            raise ValidationError("El Tramite ya fue enviado a revisión jurídica")
        
        #CREA UN ESTADO NUEVO T255
        data_estado = {}
        data_estado['id_tramite'] = request.data['id_solicitud_tramite']
        data_estado['estado_solicitud'] = 15
        data_estado['fecha_iniEstado'] = fecha_actual
        data_estado['persona_genera_estado'] = request.user.persona.id_persona
        respuesta_estado = self.creador_estados.crear_estado(self,data_estado)
        data_respuesta_estado_asociado = respuesta_estado.data['data']
        
        
        #CAMBIAMOS EL ESTADO ACTUAL DEL OPA
        serializador_opa = self.serializer_tramite(solicitud_tramite, data={'id_estado_actual_solicitud':15}, partial=True)
        serializador_opa.is_valid(raise_exception=True)
        serializador_opa.save()
        
        data_in['cod_tipo_solicitud_juridica'] = 'RE'
        data_in['fecha_solicitud'] = fecha_actual
        data_in['solicitud_completada'] = False
        data_in['solicitud_sin_completar'] = True
        data_in['id_persona_solicita_revision'] = request.user.persona.id_persona
        data_in['cod_estado_tipo_solicitud_juridica'] = 'NR'
        
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return Response({'succes': True, 'detail':'Se creo la solicitud de jurídica', 'data':serializer.data, 'estados':data_respuesta_estado_asociado}, status=status.HTTP_201_CREATED)


class listadoActos(generics.ListAPIView):
    serializer_class = AnexoArchivosDigitalesSerializer
    queryset = SolicitudesTramites.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
      
        instance = SolicitudesTramites.objects.filter(id_solicitud_tramite=pk).first()
        if not instance:
            raise ValidationError("No existe tramite asociado")

        if not instance:
                raise NotFound("No existen registros")
        
        acto = ActosAdministrativos.objects.filter(id_solicitud_tramite=instance).first()
        if not acto:
            raise NotFound("No existen registros")
        archivo = acto.id_archivo_acto_administrativo
        serializer= self.serializer_class(archivo)
        data_acto =ActosAdministrativosCreateSerializer(acto)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'acto':data_acto.data,'archivo':serializer.data},}, status=status.HTTP_200_OK)


 