import copy
from datetime import datetime
from django.db import transaction
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from gestion_documental.choices.tipo_archivo_choices import tipo_archivo_CHOICES
from gestion_documental.models.bandeja_tareas_models import AdicionalesDeTareas, ReasignacionesTareas, TareasAsignadas
from gestion_documental.models.configuracion_tiempos_respuesta_models import ConfiguracionTiemposRespuesta
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, AsignacionOtros, AsignacionPQR, AsignacionTramites, BandejaTareasPersona, ComplementosUsu_PQR, Estados_PQR, MetadatosAnexosTmp, Otros, RespuestaPQR, SolicitudAlUsuarioSobrePQRSDF, TareaBandejaTareasPersona
from gestion_documental.models.trd_models import TipologiasDoc
from gestion_documental.serializers.bandeja_tareas_tramites_serializers import AnexosTramitesGetSerializer, ComplementosUsu_TramiteGetByIdSerializer, DetalleTramitesComplementosUsu_PQRGetSerializer, MetadatosAnexosTramitesTmpSerializerGet, ReasignacionesTareasTramitesCreateSerializer, ReasignacionesTareasgetTramitesByIdSerializer, SolicitudesTramitesDetalleGetSerializer, TareasAsignadasGetTramiteJustificacionSerializer, TareasAsignadasTramiteUpdateSerializer, TareasAsignadasTramitesGetSerializer

from gestion_documental.serializers.ventanilla_pqrs_serializers import AnexoArchivosDigitalesSerializer, Anexos_PQRAnexosGetSerializer, AnexosCreateSerializer, Estados_PQRPostSerializer, MetadatosAnexosTmpCreateSerializer, MetadatosAnexosTmpGetSerializer, PQRSDFGetSerializer, SolicitudAlUsuarioSobrePQRSDFCreateSerializer
from gestion_documental.utils import UtilsGestor
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.views.bandeja_tareas_views import TareaBandejaTareasPersonaCreate, TareaBandejaTareasPersonaUpdate, TareasAsignadasCreate
from seguridad.utils import Util
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.models.organigrama_models import UnidadesOrganizacionales
from tramites.models.tramites_models import SolicitudesTramites

from transversal.models.personas_models import Personas
from rest_framework.exceptions import ValidationError,NotFound




class TareasAsignadasGetTramitesByPersona(generics.ListAPIView):
    serializer_class = TareasAsignadasTramitesGetSerializer
    queryset = TareaBandejaTareasPersona.objects.all()
    permission_classes = [IsAuthenticated]

    
    def get(self, request,id):
        filter={}
       
        bandeja_tareas= BandejaTareasPersona.objects.filter(id_persona=id).first()

        if not bandeja_tareas:
            raise NotFound('No se encontro la bandeja de tareas')
        id_bandeja = bandeja_tareas.id_bandeja_tareas_persona
        #Buscamos la asignacion de tareas de la bandeja de tareas


       
        # if not tareas_asignadas:
        #     raise NotFound('No se encontro tareas asignadas')
        

        filter['id_bandeja_tareas_persona']= id_bandeja
        filter['id_tarea_asignada__cod_tipo_tarea'] = 'Rtra' 

        for key, value in request.query_params.items():

            if key == 'estado_asignacion':
                if value != '':
                    if value =='None':
                          filter['id_tarea_asignada__cod_estado_asignacion__isnull'] = True
                    else:
                        filter['id_tarea_asignada__cod_estado_asignacion'] = value
            if key == 'estado_tarea':
                if value != '':
                    filter['id_tarea_asignada__cod_estado_solicitud'] = value
            if key == 'fecha_inicio':
                if value != '':
                    
                    filter['id_tarea_asignada__fecha_asignacion__gte'] = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'fecha_fin':
                if value != '':
                    filter['id_tarea_asignada__fecha_asignacion__lte'] = datetime.strptime(value, '%Y-%m-%d').date()

            if key == 'requerimiento':
                if value != '':
                    filter['id_tarea_asignada__requerimientos_pendientes_respuesta'] = value
        #id_tarea_asignada
                    
        print(filter)
        #.filter(**filter).order_by('fecha_radicado')
        tareas_asignadas = self.get_queryset().filter(**filter).order_by('id_tarea_asignada__fecha_asignacion')
        #tareas_asignadas = TareaBandejaTareasPersona.objects.filter(id_bandeja_tareas_persona=id_bandeja)
        tareas = [tarea.id_tarea_asignada for tarea in tareas_asignadas]
       

        serializer = self.serializer_class(tareas, many=True)

        
        radicado_value = request.query_params.get('radicado')
        data_validada =[]
        data_validada = serializer.data
        if radicado_value != '':
            data_validada = [item for item in serializer.data if radicado_value in item.get('radicado', '')]
        else :
            data_validada = serializer.data
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_validada,}, status=status.HTTP_200_OK)



class DetalleSolicitudesTramitesGet(generics.ListAPIView):

    serializer_class = SolicitudesTramitesDetalleGetSerializer
    queryset = SolicitudesTramites.objects.all()


    def get(self, request, id):

        instance = self.get_queryset().filter(id_solicitud_tramite=id).first()
        if not instance:
            raise NotFound('No se encontro el otro')
        serializer = self.serializer_class(instance)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class TramitesInfoAnexosGet(generics.ListAPIView):
    serializer_class = AnexosTramitesGetSerializer
    queryset =SolicitudesTramites.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
        data=[]
        instance =self.queryset.filter(id_solicitud_tramite=pk).first()


        if not instance:
                raise NotFound("No existen registros")
        anexos_pqrs = Anexos_PQR.objects.filter(id_tramite=instance)
        for x in anexos_pqrs:
            info_anexo =x.id_anexo
            data_anexo = self.serializer_class(info_anexo)
            data.append(data_anexo.data)
        
        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data,}, status=status.HTTP_200_OK)
    



class TareasAsignadasTramitesRechazarUpdate(generics.UpdateAPIView):
    serializer_class = TareasAsignadasTramiteUpdateSerializer
    queryset = TareasAsignadas.objects.all()
    permission_classes = [IsAuthenticated]
    vista_asignacion = TareaBandejaTareasPersonaUpdate()

    def put(self,request,pk):
        
        
        data_in = request.data
        instance = TareasAsignadas.objects.filter(id_tarea_asignada=pk).first()
        
        
        if not instance:
            raise NotFound("No se existe un registro con este codigo.")
        
        if instance.cod_tipo_tarea != 'Rtra':
            raise ValidationError("No se puede rechazar una tarea sino es otro")
        data_in['cod_estado_asignacion'] = 'Re'

        id_tarea =instance.id_tarea_asignada
        data_asignacion={}

 
        data_asignacion['fecha_leida'] = datetime.now()
        data_asignacion['leida'] = True
        respuesta_asignacion_tarea = self.vista_asignacion.actualizacion_asignacion_tarea(data_asignacion,id_tarea)
       
        if respuesta_asignacion_tarea.status_code != status.HTTP_200_OK:
            return respuesta_asignacion_tarea
        
        data_asignacion = respuesta_asignacion_tarea.data['data']
        instance_previous=copy.copy(instance)
        print(data_in)
        serializer = self.serializer_class(instance,data=data_in, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        #EN CASO DE SER UN REGISTRO FRUTO DE DE UNA REASIGNACION EL PROCESO 
        id_asignacion = instance.id_asignacion
        if not id_asignacion:
            
            tarea = instance
            if tarea.id_asignacion:
                    id_asignacion = tarea.id_asignacion

            else:#QUIERE DECIR QUE ESTA TAREA FUE REASIGNADA
                while not  tarea.id_asignacion:
                    tarea = tarea.id_tarea_asignada_padre_inmediata
                   
                    if tarea.id_asignacion:
                
                        break
                id_asignacion = tarea.id_asignacion
                reasignacion = ReasignacionesTareas.objects.filter(id_tarea_asignada = tarea.id_tarea_asignada, cod_estado_reasignacion='Ep').first()
                if reasignacion:
                    reasignacion.cod_estado_reasignacion = 'Re'
                    reasignacion.justificacion_reasignacion_rechazada = data_in['justificacion_rechazo']
                    reasignacion.save()
        else:
            print(id_asignacion)
            asignacion = AsignacionTramites.objects.filter(id_asignacion_tramite=id_asignacion,cod_estado_asignacion__isnull=True).first()
                # raise ValidationError(asignacion.id_pqrsdf)
            if not asignacion:
                raise NotFound("No se encontro la asignacion")
            asignacion.cod_estado_asignacion = 'Re'
            asignacion.justificacion_rechazo = data_in['justificacion_rechazo']
            asignacion.save()

        
        return Response({'success':True,'detail':"Se actualizo la actividad Correctamente.","data":serializer.data,'data_asignacion':data_asignacion},status=status.HTTP_200_OK)


class TareasAsignadasAceptarTramiteUpdate(generics.UpdateAPIView):
    serializer_class = TareasAsignadasTramiteUpdateSerializer
    queryset = TareasAsignadas.objects.all()
    permission_classes = [IsAuthenticated]
    vista_asignacion = TareaBandejaTareasPersonaUpdate()
    @transaction.atomic
    def put(self,request,pk):
        
        #ACTUALIZA T315
        data_in = request.data
        instance = TareasAsignadas.objects.filter(id_tarea_asignada=pk).first()
        
        if not instance:
            raise NotFound("No se existe un registro con este codigo.")
        data_in['cod_estado_asignacion'] = 'Ac'
        data_in['cod_estado_solicitud'] = 'Ep'
        id_tarea =instance.id_tarea_asignada
        data_asignacion={}

 
        data_asignacion['fecha_leida'] = datetime.now()
        data_asignacion['leida'] = True
        respuesta_asignacion_tarea = self.vista_asignacion.actualizacion_asignacion_tarea(data_asignacion,id_tarea)
       
        if respuesta_asignacion_tarea.status_code != status.HTTP_200_OK:
            return respuesta_asignacion_tarea
        
        data_asignacion = respuesta_asignacion_tarea.data['data']
        instance_previous=copy.copy(instance)

        serializer = self.serializer_class(instance,data=data_in, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        #cambio de estado en asignacion en la t268
        id_asignacion = instance.id_asignacion
        print(id_asignacion)
        #VALIDACION ENTREGA 116

        if not id_asignacion:
            print('NO SE ENCONTRO ASIGNACION')
            print('TAREA PADRE ES ' +str(instance.id_tarea_asignada_padre_inmediata))
            tarea = instance
            if tarea.id_asignacion:
                    id_asignacion = tarea.id_asignacion

            else:#QUIERE DECIR QUE ESTA TAREA FUE REASIGNADA
                while not  tarea.id_asignacion:
                    tarea = tarea.id_tarea_asignada_padre_inmediata
                    print(tarea.id_asignacion)
                    if tarea.id_asignacion:
                        id_asignacion = tarea.id_asignacion
                        #print(id_asignacion)
                        tarea.cod_estado_solicitud = 'De'
                        tarea.save()
                        #raise ValidationError(str(tarea))
                        break
                
                ##CAMBIAMOS EL ESTADO DE LA TAREA PADRE A DELEGADA


                reasignacion = ReasignacionesTareas.objects.filter(id_tarea_asignada = tarea.id_tarea_asignada, cod_estado_reasignacion='Ep').first()
                if reasignacion:
                    reasignacion.cod_estado_reasignacion = 'Ac'
                    reasignacion.save()

        else:
            print(id_asignacion)
            asignacion = AsignacionTramites.objects.filter(id_asignacion_tramite=id_asignacion,cod_estado_asignacion__isnull=True).first()
            #asignacion = AsignacionOtros.objects.filter(id_asignacion_otros=id_asignacion,cod_estado_asignacion__isnull=True).first()
            #asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=id_asignacion,cod_estado_asignacion__isnull=True).first()
        
    
            if not asignacion:
                raise NotFound("No se encontro la asignacion")
            asignacion.cod_estado_asignacion = 'Ac'
            asignacion.save()
            
           

        return Response({'success':True,'detail':"Se acepto la pqrsdf Correctamente.","data":serializer.data,'data_asignacion':data_asignacion},status=status.HTTP_200_OK)
    


class ReasignacionesTareasTramitesCreate(generics.CreateAPIView):
    serializer_class = ReasignacionesTareasTramitesCreateSerializer
    queryset = ReasignacionesTareas.objects.all()
    vista_tareas = TareasAsignadasCreate()
    permission_classes = [IsAuthenticated]
    def post(self, request):


        data_in = request.data
        data_in['fecha_reasignacion'] = datetime.now()
        data_in['cod_estado_reasignacion'] = 'Ep'

        tarea = TareasAsignadas.objects.filter(id_tarea_asignada=data_in['id_tarea_asignada']).first()
        if not tarea:
            raise NotFound("No existen registros de tareas")
        
        if tarea.cod_estado_asignacion == 'Re':
            raise ValidationError("Esta tarea fue Rechazada ")
        tarea.cod_estado_solicitud = 'De'

        reasignadas = ReasignacionesTareas.objects.filter(id_tarea_asignada=tarea.id_tarea_asignada, cod_estado_reasignacion='Ep').first()

        if reasignadas:
            raise ValidationError("La tarea tiene una reasignacion pendiente por responder.")
        tarea.save()
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        ##CREAR NUEVO REGISTRO DE REASIGNACION DE TAREA T316
        data_tarea = {}
        data_tarea['cod_tipo_tarea'] = 'Rtra'
        data_tarea['id_asignacion'] = None
        data_tarea['fecha_asignacion'] = datetime.now()
        data_tarea['cod_estado_solicitud'] = 'Ep'
        data_tarea['id_tarea_asignada_padre_inmediata'] = tarea.id_tarea_asignada
        data_tarea['comentario_asignacion'] = data_in['comentario_reasignacion']
        respuesta_tareas = self.vista_tareas.crear_asignacion_tarea(data_tarea)
        if respuesta_tareas.status_code != status.HTTP_201_CREATED:
            return respuesta_tareas

        data_tarea_respuesta =respuesta_tareas.data['data']

        #ASIGNO LA NUEVA TAREA A LA BANDEJA DE LA PERSONA 
        vista_asignar_tarea =TareaBandejaTareasPersonaCreate()
        data_tarea_bandeja_asignacion = {}
        data_tarea_bandeja_asignacion['id_persona'] = data_in['id_persona_a_quien_se_reasigna']
        data_tarea_bandeja_asignacion['id_tarea_asignada'] = data_tarea_respuesta['id_tarea_asignada']
        data_tarea_bandeja_asignacion['es_responsable_ppal'] = False
        respuesta_relacion = vista_asignar_tarea.crear_tarea(data_tarea_bandeja_asignacion)
        if respuesta_relacion.status_code != status.HTTP_201_CREATED:
            return respuesta_relacion

   
        return Response({'succes': True, 'detail':'Se crearon los siguientes registros', 'data':serializer.data,'data_tarea_respuesta':data_tarea_respuesta}, status=status.HTTP_200_OK)
    


class ReasignacionesTramitesTareasgetById(generics.ListAPIView):
    serializer_class = ReasignacionesTareasgetTramitesByIdSerializer
    queryset = ReasignacionesTareas.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        instance = self.get_queryset().filter(id_tarea_asignada=pk)
        if not instance:
            raise NotFound("No existen registros")
        serializer = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)

    
class TramitesAnexoMetaDataGet(generics.ListAPIView):
    serializer_class = MetadatosAnexosTramitesTmpSerializerGet
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
    


class TareasAsignadasTramitesJusTarea(generics.UpdateAPIView):

    serializer_class = TareasAsignadasGetTramiteJustificacionSerializer
    queryset = TareasAsignadas.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        
        tarea = TareasAsignadas.objects.filter(id_tarea_asignada=pk).first()
        
        if not tarea:
            raise NotFound('No se encontro la tarea')
        if  tarea.cod_estado_asignacion == 'Ac':
            raise NotFound('Esta tarea fue aceptada')
        
        serializer = self.serializer_class(tarea)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data,}, status=status.HTTP_200_OK)



#Respuesta requerimientos hechos por el usuario 
    #T266SolicitudAlUsuarioSobrePQRSDF

class RequerimientosTramite(generics.ListAPIView):
    queryset = SolicitudAlUsuarioSobrePQRSDF.objects.all()
    serializer_class = ComplementosUsu_TramiteGetByIdSerializer
    permission_classes = [IsAuthenticated]

    def get (self,request,pk):
        #BUSCAMOS LA ID DEL TRAMITE 7266
        #instance = self.get_queryset().filter(id_solicitud_tramite=pk)
        complementos_tareas= AdicionalesDeTareas.objects.filter(id_tarea_asignada=pk)
#        print(complementos_tareas.first().id_complemento_usu_pqr)
        if not complementos_tareas:
            raise NotFound('No se encontraron registros')

        ids=list(complementos_tareas.values_list('id_complemento_usu_pqr', flat=True))


        
        complementos =  ComplementosUsu_PQR.objects.filter(idComplementoUsu_PQR__in=ids)

        serializer = self.serializer_class(complementos, many=True)

        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data, }, status=status.HTTP_200_OK)



class RespuestaTramitesInfoAnexosGet(generics.ListAPIView):
    serializer_class = AnexosTramitesGetSerializer
    queryset = ComplementosUsu_PQR.objects.all()
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
    
    
class ComplementoTramitesAnexoDocumentoDigitalGet(generics.ListAPIView):
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
    


class DetalleRespuestaTramitesByIdGet(generics.ListAPIView):
    serializer_class = DetalleTramitesComplementosUsu_PQRGetSerializer
    queryset = ComplementosUsu_PQR.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
        data=[]
        instance =self.queryset.filter(idComplementoUsu_PQR=pk).first()


        if not instance:
                raise NotFound("No existen registros")

        serializer = self.serializer_class(instance)        
        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    