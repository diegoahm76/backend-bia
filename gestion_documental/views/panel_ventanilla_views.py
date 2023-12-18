from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad
from gestion_documental.models.configuracion_tiempos_respuesta_models import ConfiguracionTiemposRespuesta
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, AsignacionPQR, ComplementosUsu_PQR, Estados_PQR, EstadosSolicitudes, InfoDenuncias_PQRSDF, MetadatosAnexosTmp, SolicitudAlUsuarioSobrePQRSDF, SolicitudDeDigitalizacion, T262Radicados
from gestion_documental.models.trd_models import TipologiasDoc
from gestion_documental.serializers.permisos_serializers import DenegacionPermisosGetSerializer, PermisosGetSerializer, PermisosPostDenegacionSerializer, PermisosPostSerializer, PermisosPutDenegacionSerializer, PermisosPutSerializer, SerieSubserieUnidadCCDGetSerializer
from gestion_documental.serializers.ventanilla_pqrs_serializers import AnexoArchivosDigitalesSerializer, Anexos_PQRAnexosGetSerializer, Anexos_PQRCreateSerializer, AnexosComplementoGetSerializer, AnexosCreateSerializer, AnexosDocumentoDigitalGetSerializer, AnexosGetSerializer, AsignacionPQRGetSerializer, AsignacionPQRPostSerializer, ComplementosUsu_PQRGetSerializer, ComplementosUsu_PQRPutSerializer, Estados_OTROSSerializer, Estados_PQRPostSerializer, Estados_PQRSerializer, EstadosSolicitudesGetSerializer, InfoDenuncias_PQRSDFGetByPqrsdfSerializer, LiderGetSerializer, MetadatosAnexosTmpCreateSerializer, MetadatosAnexosTmpGetSerializer, MetadatosAnexosTmpSerializerGet, PQRSDFCabezeraGetSerializer, PQRSDFDetalleSolicitud, PQRSDFGetSerializer, PQRSDFHistoricoGetSerializer, PQRSDFPutSerializer, PQRSDFTitularGetSerializer, SolicitudAlUsuarioSobrePQRSDFCreateSerializer, SolicitudAlUsuarioSobrePQRSDFGetDetalleSerializer, SolicitudAlUsuarioSobrePQRSDFGetSerializer, SolicitudDeDigitalizacionGetSerializer, SolicitudDeDigitalizacionPostSerializer, UnidadesOrganizacionalesSecSubVentanillaGetSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from seguridad.utils import Util
from gestion_documental.utils import UtilsGestor
from datetime import date, datetime
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from transversal.models.lideres_models import LideresUnidadesOrg
from django.db.models import Max
from transversal.models.organigrama_models import Organigramas, UnidadesOrganizacionales
import json


from gestion_documental.choices.tipo_archivo_choices import tipo_archivo_CHOICES

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
    #queryset =PQRSDF.objects.all()
    queryset = PQRSDF.objects.annotate(mezcla=Concat(F('id_radicado__prefijo_radicado'), Value('-'), F('id_radicado__agno_radicado'),
                                                      Value('-'), F('id_radicado__nro_radicado'), output_field=CharField()))
                                              
    permission_classes = [IsAuthenticated]


    def get (self, request):
        tipo_busqueda = 'PQRSDF'
        data_respuesta = []
        filter={}
        
        for key, value in request.query_params.items():

            if key == 'radicado':
                if value !='':
                    filter['mezcla__icontains'] = value
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
        
        if tipo_busqueda == 'PQRSDF':
            filter['id_radicado__isnull'] = False
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
    permission_classes = [IsAuthenticated]
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
    queryset_prueba = PQRSDF.objects.annotate(combinacion=Concat(F('id_radicado__prefijo_radicado'), Value('-'), F('id_radicado__agno_radicado'), Value('-'), F('id_radicado__nro_radicado'), output_field=CharField())
)
    permission_classes = [IsAuthenticated]


        
    def get (self, request):
        tipo_busqueda = 'PQRSDF'
        data_respuesta = []
        filter={}
        historico =Historico_Solicitud_PQRSDFGet()
        data_histo = []
        for key, value in request.query_params.items():

            if key == 'radicado':
                if value !='':
                    filter['combinacion__icontains'] = value
 
            if key =='estado_actual_solicitud':
                if value != '':
                    filter['id_estado_actual_solicitud__estado_solicitud__nombre__icontains'] = value    

        
        
        instance = self.queryset_prueba.filter(**filter).order_by('fecha_radicado')

        if not instance:
            raise NotFound("No existen registros")
        for x in instance:
            print(x.combinacion)
            respuesta = historico.get(self,x.id_PQRSDF)
            #print()
            data_histo.append({'cabecera':self.serializer_class(x).data,'detalle':respuesta.data['data']})

                #data_respuesta.append(historico.get(self,x.id_PQRSDF).data['data'])

            #serializador = self.serializer_class(instance,many=True)
            #data_respuesta = serializador.data
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_histo,}, status=status.HTTP_200_OK)


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
    

class AsignacionPQRCreate(generics.CreateAPIView):
    serializer_class = AsignacionPQRPostSerializer
    queryset =AsignacionPQR.objects.all()
    permission_classes = [IsAuthenticated]
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
        if contador == 0:
            raise ValidationError("No se puede realizar la asignación de la PQRSDF a una  unidad organizacional seleccionada porque no tiene serie  documental de PQRSDF")
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

        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,'estado':data_estado}, status=status.HTTP_200_OK)




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
        data_in['fecha_creacion_doc'] = date.today()
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
class VistaCreadoraArchivo3(generics.CreateAPIView):

    def post(self,request):
        data = request.data
        respuesta= UtilsGestor.generar_archivo_blanco(data)
        return respuesta