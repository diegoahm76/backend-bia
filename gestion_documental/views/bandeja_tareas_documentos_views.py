import copy
from datetime import datetime, date, timedelta
import json
from django.db.models import Q
from django.forms import model_to_dict
import os
from django.db import transaction
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max

from gestion_documental.choices.tipo_archivo_choices import tipo_archivo_CHOICES

from transversal.serializers.personas_serializers import PersonasSerializer
from transversal.models.personas_models import Personas

from gestion_documental.models.bandeja_tareas_models import AdicionalesDeTareas, ReasignacionesTareas, TareasAsignadas
from gestion_documental.models.configuracion_tiempos_respuesta_models import ConfiguracionTiemposRespuesta
from gestion_documental.models.radicados_models import AsignacionDocs, Anexos, Anexos_PQR, AsignacionOtros, AsignacionPQR, BandejaTareasPersona, ComplementosUsu_PQR, Estados_PQR, MetadatosAnexosTmp, Otros, RespuestaPQR, SolicitudAlUsuarioSobrePQRSDF, TareaBandejaTareasPersona
from gestion_documental.models.trd_models import TipologiasDoc
from gestion_documental.serializers.bandeja_tareas_otros_serializers import AnexosOtrosGetSerializer, DetalleOtrosGetSerializer, MetadatosAnexosOtrosTmpSerializerGet, TareasAsignadasOotrosUpdateSerializer, TareasAsignadasOtrosGetSerializer
from gestion_documental.serializers.bandeja_tareas_serializers import ReasignacionesTareasOtrosCreateSerializer, ReasignacionesTareasgetOtrosByIdSerializer, TareasAsignadasGetJustificacionSerializer
from gestion_documental.serializers.bandeja_tareas_documentos_serializars import TareasAsignadasDocsGetSerializer
from gestion_documental.serializers.bandeja_tareas_documentos_serializars import AsignacionDocsPostSerializer

from gestion_documental.serializers.ventanilla_pqrs_serializers import Anexos_PQRAnexosGetSerializer, AnexosCreateSerializer, Estados_PQRPostSerializer, MetadatosAnexosTmpCreateSerializer, MetadatosAnexosTmpGetSerializer, PQRSDFGetSerializer, SolicitudAlUsuarioSobrePQRSDFCreateSerializer
from gestion_documental.utils import UtilsGestor
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.views.bandeja_tareas_views import TareaBandejaTareasPersonaCreate, TareaBandejaTareasPersonaUpdate, TareasAsignadasCreate
from seguridad.utils import Util
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.models.organigrama_models import UnidadesOrganizacionales

from transversal.models.personas_models import Personas
from rest_framework.exceptions import ValidationError,NotFound

from transversal.views.alertas_views import AlertaEventoInmediadoCreate



class DetalleOtrosGet(generics.ListAPIView):

    serializer_class = DetalleOtrosGetSerializer
    queryset = Otros.objects.all()


    def get(self, request, id):

        instance = self.get_queryset().filter(id_otros=id).first()
        if not instance:
            raise NotFound('No se encontro el otro')
        serializer = self.serializer_class(instance)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class TareasAsignadasDocsGet(generics.ListAPIView):
    serializer_class = TareasAsignadasDocsGetSerializer
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
        filter['id_tarea_asignada__cod_tipo_tarea'] = 'RDocs' 

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



#PENDIENTE
class TareasAsignadasAceptarDocsUpdate(generics.UpdateAPIView):
    serializer_class = TareasAsignadasOotrosUpdateSerializer
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
        else:
            asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=id_asignacion,cod_estado_asignacion__isnull=True).first()
            #asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=id_asignacion,cod_estado_asignacion__isnull=True).first()
        
    
            if not asignacion:
                raise NotFound("No se encontro la asignacion")
            asignacion.cod_estado_asignacion = 'Ac'
            asignacion.save()
            
            print(asignacion.id_consecutivo)

        return Response({'success':True,'detail':"Se acepto el documento Correctamente.","data":serializer.data,'data_asignacion':data_asignacion},status=status.HTTP_200_OK)
    



class TareasAsignadasDocsRechazarUpdate(generics.UpdateAPIView):
    serializer_class = TareasAsignadasOotrosUpdateSerializer
    queryset = TareasAsignadas.objects.all()
    permission_classes = [IsAuthenticated]
    vista_asignacion = TareaBandejaTareasPersonaUpdate()

    def put(self,request,pk):
        
        
        data_in = request.data
        instance = TareasAsignadas.objects.filter(id_tarea_asignada=pk).first()
        
        
        if not instance:
            raise NotFound("No se existe un registro con este codigo.")
        
        if instance.cod_tipo_tarea != 'RDocs':
            raise ValidationError("No se puede rechazar una tarea que no es de tipo documentos")
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
        else:
            asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=id_asignacion,cod_estado_asignacion__isnull=True).first()
                # raise ValidationError(asignacion.id_pqrsdf)
            if not asignacion:
                raise NotFound("No se encontro la asignacion")
            asignacion.cod_estado_asignacion = 'Re'
            asignacion.justificacion_rechazo = data_in['justificacion_rechazo']
            asignacion.firma = False
            asignacion.save()

        
        return Response({'success':True,'detail':"Se actualizo la actividad Correctamente.","data":serializer.data,'data_asignacion':data_asignacion},status=status.HTTP_200_OK)




class AsignacionDocCreate(generics.CreateAPIView):
    serializer_class = AsignacionDocsPostSerializer
    queryset =AsignacionDocs.objects.all()
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data_in = request.data

        if not 'id_consecutivo' in data_in:
            raise ValidationError("No se envio el documento con el consecutivo de la tipologia")
        
        if not 'firma' in data_in:
            raise ValidationError("No se envio la firma del documento")
        
        instance= AsignacionDocs.objects.filter(id_consecutivo = data_in['id_consecutivo'], id_persona_asignada = data_in['id_persona_asignada']).first()
        #for asignacion in instance:
            #print(asignacion)
        if instance:
            if instance.cod_estado_asignacion == 'Ac':
                raise ValidationError("La solicitud  ya fue Aceptada.")
            if  not instance.cod_estado_asignacion:
                raise ValidationError("La solicitud esta pendiente por respuesta.")
        max_consecutivo = AsignacionDocs.objects.filter(id_consecutivo=data_in['id_consecutivo']).aggregate(Max('consecutivo_asign_x_doc'))

        if max_consecutivo['consecutivo_asign_x_doc__max'] == None:
             ultimo_consec= 1
        else:
            ultimo_consec = max_consecutivo['consecutivo_asign_x_doc__max'] + 1
        
        unidad_asignar = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=request.user.persona.id_unidad_organizacional_actual.id_unidad_organizacional).first()
        if not unidad_asignar:
            raise ValidationError("No existe la unidad asignada")
        
        data_in['id_und_org_seccion_asignada'] = unidad_asignar.id_unidad_organizacional
        #VALIDACION ENTREGA 102 SERIE PQRSDF
       
        # if contador == 0:
        #     raise ValidationError("No se puede realizar la asignación de la PQRSDF a una  unidad organizacional seleccionada porque no tiene serie  documental de PQRSDF")
        data_in['consecutivo_asign_x_doc'] = ultimo_consec 
        data_in['fecha_asignacion'] = datetime.now()
        data_in['id_persona_asigna'] = request.user.persona.id_persona
        data_in['cod_estado_asignacion'] = None
        data_in['asignacion_de_ventanilla'] = False

        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        #Crear tarea y asignacion de tarea
       
        id_persona_asiganada = serializer.data['id_persona_asignada']

 
        #Creamos la tarea 315
        data_tarea = {}
        data_tarea['cod_tipo_tarea'] = 'RDocs'
        data_tarea['id_asignacion'] = serializer.data['id_asignacion_doc']
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
       
        mensaje = "Le acaba de llenar un documento para que lo revise"
        vista_alertas_programadas = AlertaEventoInmediadoCreate()
        data_alerta = {}
        data_alerta['cod_clase_alerta'] = 'Gst_SlALid'
        data_alerta['id_persona'] = id_persona_asiganada
        data_alerta['id_elemento_implicado'] = serializer.data['id_asignacion_doc']
        data_alerta['informacion_complemento_mensaje'] = mensaje

        respuesta_alerta = vista_alertas_programadas.crear_alerta_evento_inmediato(data_alerta)
        if respuesta_alerta.status_code != status.HTTP_200_OK:
            return respuesta_alerta


        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,'tarea':respuesta_relacion.data['data']}, status=status.HTTP_200_OK)


class ObtenerPersonasConBandejaTareas(generics.ListAPIView):
    serializer_class = PersonasSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Personas.objects.all()
        tipo_documento = request.query_params.get('tipo_documento')
        if tipo_documento:
            queryset = queryset.filter(tipo_documento__cod_tipo_documento=tipo_documento)
        
        identificacion = request.query_params.get('identificacion')
        if identificacion:
            queryset = queryset.filter(numero_documento=identificacion)

        primer_nombre = request.query_params.get('primer_nombre')
        if primer_nombre:
            queryset = queryset.filter(primer_nombre__icontains=primer_nombre)

        primer_apellido = request.query_params.get('primer_apellido')
        if primer_apellido:
            queryset = queryset.filter(primer_apellido__icontains=primer_apellido)
            
        serializer = self.serializer_class(queryset, many=True)
        data = [bandeja for bandeja in serializer.data if bandeja['tiene_usuario']]
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': data}, status=status.HTTP_200_OK)
    
class ObternerAsignacionesDocumentos(generics.ListAPIView):
    serializer_class = AsignacionDocsPostSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = AsignacionDocs.objects.all()
        
        consecutivo = request.query_params.get('id_consecutivo')
        if not consecutivo:
            raise ValidationError("No se envio el consecutivo")

        queryset = queryset.filter(id_consecutivo=consecutivo)
        
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data}, status=status.HTTP_200_OK)
    
class CancelarAsignacionDocumentos(generics.UpdateAPIView):
    serializer_class = AsignacionDocsPostSerializer
    permission_classes = [IsAuthenticated]
    vista_asignacion = TareaBandejaTareasPersonaUpdate()

    def put(self, request, pk):
        instance = AsignacionDocs.objects.get(id_asignacion_doc=pk)
        current_date = datetime.now()
        if not instance:
            raise NotFound("No se encontro la asignacion")
        data = request.data

        data['cod_estado_asignacion'] = 'Ca'
        data['fecha_eleccion_estado'] = current_date
        data['firma'] = False
        serializer = self.serializer_class(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        tarea = TareasAsignadas.objects.get(id_asignacion=instance.id_asignacion_doc, cod_tipo_tarea='RDocs')
        tarea.cod_estado_solicitud = 'Ca'
        tarea.cod_estado_asignacion = 'Ca'
        tarea.save()

        data_asignacion={}

 
        data_asignacion['fecha_leida'] = current_date
        data_asignacion['leida'] = True
        respuesta_asignacion_tarea = self.vista_asignacion.actualizacion_asignacion_tarea(data_asignacion,tarea.id_tarea_asignada)

        if respuesta_asignacion_tarea.status_code != status.HTTP_200_OK:
            return respuesta_asignacion_tarea

        return Response({'success': True, 'detail': 'Se cancelo la asignacion correctamente', 'data': serializer.data}, status=status.HTTP_200_OK)





# class ReasignacionesTareasOtroCreate(generics.CreateAPIView):
#     serializer_class = ReasignacionesTareasOtrosCreateSerializer
#     queryset = ReasignacionesTareas.objects.all()
#     vista_tareas = TareasAsignadasCreate()
#     permission_classes = [IsAuthenticated]
#     def post(self, request):


#         data_in = request.data
#         data_in['fecha_reasignacion'] = datetime.now()
#         data_in['cod_estado_reasignacion'] = 'Ep'

#         tarea = TareasAsignadas.objects.filter(id_tarea_asignada=data_in['id_tarea_asignada']).first()
#         if not tarea:
#             raise NotFound("No existen registros de tareas")
        
#         if tarea.cod_estado_asignacion == 'Re':
#             raise ValidationError("Esta tarea fue Rechazada ")
#         tarea.cod_estado_solicitud = 'De'

#         reasignadas = ReasignacionesTareas.objects.filter(id_tarea_asignada=tarea.id_tarea_asignada, cod_estado_reasignacion='Ep').first()

#         if reasignadas:
#             raise ValidationError("La tarea tiene una reasignacion pendiente por responder.")
#         tarea.save()
#         serializer = self.serializer_class(data=data_in)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         ##CREAR NUEVO REGISTRO DE REASIGNACION DE TAREA T316
#         data_tarea = {}
#         data_tarea['cod_tipo_tarea'] = 'ROtro'
#         data_tarea['id_asignacion'] = None
#         data_tarea['fecha_asignacion'] = datetime.now()
#         data_tarea['cod_estado_solicitud'] = 'Ep'
#         data_tarea['id_tarea_asignada_padre_inmediata'] = tarea.id_tarea_asignada
#         data_tarea['comentario_asignacion'] = data_in['comentario_reasignacion']
#         respuesta_tareas = self.vista_tareas.crear_asignacion_tarea(data_tarea)
#         if respuesta_tareas.status_code != status.HTTP_201_CREATED:
#             return respuesta_tareas

#         data_tarea_respuesta =respuesta_tareas.data['data']

#         #ASIGNO LA NUEVA TAREA A LA BANDEJA DE LA PERSONA 
#         vista_asignar_tarea =TareaBandejaTareasPersonaCreate()
#         data_tarea_bandeja_asignacion = {}
#         data_tarea_bandeja_asignacion['id_persona'] = data_in['id_persona_a_quien_se_reasigna']
#         data_tarea_bandeja_asignacion['id_tarea_asignada'] = data_tarea_respuesta['id_tarea_asignada']
#         data_tarea_bandeja_asignacion['es_responsable_ppal'] = False
#         respuesta_relacion = vista_asignar_tarea.crear_tarea(data_tarea_bandeja_asignacion)
#         if respuesta_relacion.status_code != status.HTTP_201_CREATED:
#             return respuesta_relacion

   
#         return Response({'succes': True, 'detail':'Se crearon los siguientes registros', 'data':serializer.data,'data_tarea_respuesta':data_tarea_respuesta}, status=status.HTTP_200_OK)
    


# class ReasignacionesOtrosTareasgetById(generics.ListAPIView):
#     serializer_class = ReasignacionesTareasgetOtrosByIdSerializer
#     queryset = ReasignacionesTareas.objects.all()
#     permission_classes = [IsAuthenticated]
#     def get(self, request,pk):
#         instance = self.get_queryset().filter(id_tarea_asignada=pk)
#         if not instance:
#             raise NotFound("No existen registros")
#         serializer = self.serializer_class(instance,many=True)
#         return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
