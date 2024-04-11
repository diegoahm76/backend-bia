#BandejaTareasPersona
import ast
import hashlib
from django.db.models import Max
from reportlab.pdfgen import canvas
import io
import os
import json
from django.conf import settings
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

from gestion_documental.choices.tipo_archivo_choices import tipo_archivo_CHOICES

from gestion_documental.models.bandeja_tareas_models import AdicionalesDeTareas, ReasignacionesTareas, TareasAsignadas
from gestion_documental.models.expedientes_models import DocumentosDeArchivoExpediente, ExpedientesDocumentales, Docs_IndiceElectronicoExp, IndicesElectronicosExp
from gestion_documental.models.configuracion_tiempos_respuesta_models import ConfiguracionTiemposRespuesta
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, AsignacionPQR, BandejaTareasPersona, ComplementosUsu_PQR, Estados_PQR, MetadatosAnexosTmp, RespuestaPQR, SolicitudAlUsuarioSobrePQRSDF, TareaBandejaTareasPersona, Otros
from gestion_documental.models.trd_models import TipologiasDoc
from gestion_documental.serializers.bandeja_tareas_serializers import AdicionalesDeTareasGetByTareaSerializer, Anexos_RequerimientoCreateSerializer, AnexosComplementoGetByComBandejaTareasSerializer, BandejaTareasPersonaCreateSerializer, ComplementosUsu_PQRGetByIdSerializer, DetalleRequerimientoSerializer, LiderUnidadGetSerializer, MetadatosAnexoerializerGet, PQRSDFDetalleRequerimiento, PQRSDFTitularGetBandejaTareasSerializer, PersonaUnidadSerializer, ReasignacionesTareasCreateSerializer, ReasignacionesTareasgetByIdSerializer, ReasignacionesTareasgetByIdTareaSerializer, RequerimientoSobrePQRSDFCreateSerializer, RequerimientoSobrePQRSDFGetSerializer, RespuestasPQRGetSeralizer, TareaBandejaTareasPersonaCreateSerializer, TareaBandejaTareasPersonaUpdateSerializer, TareasAnexoArchivosDigitalesSerializer, TareasAsignadasCreateSerializer, TareasAsignadasGetJustificacionSerializer, TareasAsignadasGetSerializer, TareasAsignadasUpdateSerializer, UnidadOrganizacionalBandejaTareasSerializer
from gestion_documental.serializers.ventanilla_pqrs_serializers import Anexos_PQRAnexosGetSerializer, AnexosCreateSerializer, Estados_PQRPostSerializer, MetadatosAnexosTmpCreateSerializer, MetadatosAnexosTmpGetSerializer, PQRSDFGetSerializer, SolicitudAlUsuarioSobrePQRSDFCreateSerializer
from gestion_documental.utils import UtilsGestor
from gestion_documental.serializers.expedientes_serializers import ArchivoSoporteSerializer, DocsIndiceElectronicoSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from seguridad.utils import Util
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.models.organigrama_models import UnidadesOrganizacionales

from transversal.models.personas_models import Personas
from rest_framework.exceptions import ValidationError,NotFound


class BandejaTareasPersonaCreate(generics.CreateAPIView):
    serializer_class = BandejaTareasPersonaCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = BandejaTareasPersona.objects.all()


    def crear_bandeja(self,data):
        data_in = data
        data_in['pendientes_leer'] = True
        id_persona = data_in['id_persona']
        persona = Personas.objects.filter(id_persona=id_persona).first()

        if not persona:
            raise NotFound('No se encontro la persona')
        
        bandeja = BandejaTareasPersona.objects.filter(id_persona=id_persona).first()

        if bandeja:
            raise ValidationError('Ya existe una bandeja para esta persona')
        
        serializer = BandejaTareasPersonaCreateSerializer(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance=serializer.save()
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_201_CREATED)


    def post(self, request):
        data = request.data
        respuesta = self.crear_bandeja(data)
        return respuesta
    

class TareasAsignadasCreate(generics.CreateAPIView):
    serializer_class = TareasAsignadasCreateSerializer
    queryset = TareasAsignadas.objects.all()
    permission_classes = [IsAuthenticated]


    def crear_asignacion_tarea(self,data):
        data_in = data
        # id_bandeja_tareas = data_in['id_bandeja_tareas']
        # bandeja_tareas = BandejaTareasPersona.objects.filter(id_persona=id_bandeja_tareas).first()

        # if not bandeja_tareas:
        #     raise NotFound('No se encontro la bandeja de tareas')
        
        # tareas_asignadas = TareasAsignadas.objects.filter(id_bandeja_tareas=id_bandeja_tareas).first()

        # if tareas_asignadas:
        #     raise ValidationError('Ya existe una asignacion de tareas para esta bandeja de tareas')
        
        serializer = TareasAsignadasCreateSerializer(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance=serializer.save()
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_201_CREATED)
    def post(self, request):
       
        data_in = request.data 
        respuesta = self.crear_asignacion_tarea(data_in)
        return respuesta
    


class TareaBandejaTareasPersonaCreate(generics.CreateAPIView):
    serializer_class = TareaBandejaTareasPersonaCreateSerializer
    queryset = TareaBandejaTareasPersona.objects.all()
    permission_classes = [IsAuthenticated]


    def crear_tarea(self,data):
        
        id_persona = data['id_persona']
        bandeja = BandejaTareasPersona.objects.filter(id_persona=id_persona).first()
        id_bandeja =None
        if bandeja:
            id_bandeja = bandeja.id_bandeja_tareas_persona#BandejaTareasPersona
            bandeja.pendientes_leer = True
            bandeja.save()
        else:
            vista_bandeja = BandejaTareasPersonaCreate()
            respuesta_bandeja = vista_bandeja.crear_bandeja(data)
            if respuesta_bandeja.status_code != status.HTTP_201_CREATED:
                return respuesta_bandeja
            id_bandeja = respuesta_bandeja.data['data']['id_bandeja_tareas_persona']
  
        data['id_bandeja_tareas_persona'] = id_bandeja
        serializer = TareaBandejaTareasPersonaCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_201_CREATED)

    def post(self, request):

        data = request.data
        respuesta = self.crear_tarea(data)
        return respuesta
    

class TareasAsignadasGetByPersona(generics.ListAPIView):
    serializer_class = TareasAsignadasGetSerializer
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

        for key, value in request.query_params.items():

            if key == 'tipo_tarea':
                if value !='':
                    filter['id_tarea_asignada__cod_tipo_tarea'] = value
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
        if radicado_value != '':
            data_validada = [item for item in serializer.data if radicado_value in item.get('radicado', '')]
        else :
            data_validada = serializer.data
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_validada,}, status=status.HTTP_200_OK)


#detalle de una pqrsdf por id

#PQRSDFGetSerializer
class PQRSDFDetalleGetById(generics.ListAPIView):
    serializer_class = PQRSDFGetSerializer
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request,id):
        pqrsdf = PQRSDF.objects.filter(id_PQRSDF=id).first()
        if not pqrsdf:
            raise NotFound('No se encontro la pqrsdf')
        serializer = self.serializer_class(pqrsdf)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    

class TareaBandejaTareasPersonaUpdate(generics.UpdateAPIView):#ACTUALIZACION ASIGNACION DE TAREA
    serializer_class = TareaBandejaTareasPersonaUpdateSerializer
    queryset = TareaBandejaTareasPersona.objects.all()
    permission_classes = [IsAuthenticated]
    
    def actualizacion_asignacion_tarea(self,data,pk):
       
        instance = TareaBandejaTareasPersona.objects.filter(id_tarea_asignada=pk).first()
        
        if not instance:
            raise NotFound("No se existe un registro con este codigo.")
        


        
        serializer = self.serializer_class(instance,data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance =serializer.save()
                #verifica si la bandeja de tareas tiene pendientes por leer y cambia el estado segun el caso
        bandeja_tareas = instance.id_bandeja_tareas_persona
        tareas = TareaBandejaTareasPersona.objects.filter(id_bandeja_tareas_persona=bandeja_tareas,leida=False)
        if tareas.count() == 0:
            bandeja_tareas.pendientes_leer = False
            bandeja_tareas.save()
      


        
        return Response({'success':True,'detail':"Se actualizo la actividad Correctamente.","data":serializer.data},status=status.HTTP_200_OK)


    
    def put(self,request,tarea):
        data = request.data
        respuesta = self.actualizacion_asignacion_tarea(data,tarea)
        return respuesta
    

class TareasAsignadasRechazarUpdate(generics.UpdateAPIView):
    serializer_class = TareasAsignadasUpdateSerializer
    queryset = TareasAsignadas.objects.all()
    permission_classes = [IsAuthenticated]
    vista_asignacion = TareaBandejaTareasPersonaUpdate()

    def put(self,request,pk):
        
        
        data_in = request.data
        instance = TareasAsignadas.objects.filter(id_tarea_asignada=pk).first()
        
        if not instance:
            raise NotFound("No se existe un registro con este codigo.")
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
            asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=id_asignacion,cod_estado_asignacion__isnull=True).first()
                # raise ValidationError(asignacion.id_pqrsdf)
            if not asignacion:
                raise NotFound("No se encontro la asignacion")
            asignacion.cod_estado_asignacion = 'Re'
            asignacion.justificacion_rechazo = data_in['justificacion_rechazo']
            asignacion.save()

        
        return Response({'success':True,'detail':"Se actualizo la actividad Correctamente.","data":serializer.data,'data_asignacion':data_asignacion},status=status.HTTP_200_OK)

class TareasAsignadasAceptarUpdate(generics.UpdateAPIView):
    serializer_class = TareasAsignadasUpdateSerializer
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
            asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=id_asignacion,cod_estado_asignacion__isnull=True).first()
        
    
            if not asignacion:
                raise NotFound("No se encontro la asignacion")
            asignacion.cod_estado_asignacion = 'Ac'
            asignacion.save()
            
            print(asignacion.id_pqrsdf)

        return Response({'success':True,'detail':"Se acepto la pqrsdf Correctamente.","data":serializer.data,'data_asignacion':data_asignacion},status=status.HTTP_200_OK)
    

class TareasAsignadasJusTarea(generics.UpdateAPIView):

    serializer_class = TareasAsignadasGetJustificacionSerializer
    queryset = TareasAsignadas.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,id):
        
        tarea = TareasAsignadas.objects.filter(id_tarea_asignada=id).first()
        
        if not tarea:
            raise NotFound('No se encontro la tarea')
        if  tarea.cod_estado_asignacion == 'Ac':
            raise NotFound('Esta tarea fue aceptada')
        
        serializer = self.serializer_class(tarea)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data,}, status=status.HTTP_200_OK)
        






class ComplementoTareaGetByTarea(generics.ListAPIView):
    serializer_class = AdicionalesDeTareasGetByTareaSerializer
    queryset = AdicionalesDeTareas.objects.all()

    def get(self, request,tarea):

        instance = TareasAsignadas.objects.filter(id_tarea_asignada=tarea).first()
        
        if not instance.id_asignacion:
            aux = instance
            while aux:
                aux=aux.id_tarea_asignada_padre_inmediata
                if  aux and aux.id_asignacion:
                    instance = aux 
                    break
            
            #raise ValidationError('No se encontro la asignacion')
        print(instance)
        complemento = AdicionalesDeTareas.objects.filter(id_tarea_asignada=instance)
        
        print(complemento)
        if not complemento:
            raise NotFound("No se encontro el complemento")
      
        serializer = self.serializer_class(complemento,many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data,}, status=status.HTTP_200_OK)
    

class ComplementosUsu_PQRGetDetalleById(generics.ListAPIView):

    serializer_class = ComplementosUsu_PQRGetByIdSerializer
    queryset =ComplementosUsu_PQR.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        
        instance = self.get_queryset().filter(idComplementoUsu_PQR=pk).first()
        if not instance:
            raise NotFound("No existen registros")
        
        serializador = self.serializer_class(instance)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
    
class ComplementoPQRSDFInfoAnexosGet(generics.ListAPIView):
    serializer_class = AnexosComplementoGetByComBandejaTareasSerializer
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

class ComplementoMetaDataGetByIdAnexo(generics.ListAPIView):
    serializer_class = MetadatosAnexoerializerGet
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
    
class DocumentoDigitalAnexoGet(generics.ListAPIView):
    serializer_class = TareasAnexoArchivosDigitalesSerializer
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
    
#ENTREGA 103 REQUERIMIENTO SOBRE PQRSDF 
class PQRSDFPersonaTitularGet(generics.ListAPIView):
    serializer_class = PQRSDFTitularGetBandejaTareasSerializer
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,pqr):
        
        instance = self.get_queryset().filter(id_PQRSDF=pqr).first()
        if not instance:
            raise NotFound("No existen registros")
        persona_titular = instance.id_persona_titular 
        serializer = self.serializer_class(persona_titular)

        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)


class PQRSDFPersonaRequerimientoGet(generics.ListAPIView):
    serializer_class = PQRSDFTitularGetBandejaTareasSerializer
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request):
        persona = request.user.persona
        

        serializer = self.serializer_class(persona)

        #return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'seccion':serializer_unidad.data,'hijos':serializer.data}}, status=status.HTTP_200_OK)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    

class PQRSDFDetalleRequerimientoGet(generics.ListAPIView):
    serializer_class = DetalleRequerimientoSerializer
    queryset = SolicitudAlUsuarioSobrePQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,pk):
        
        instance = self.get_queryset().filter(id_solicitud_al_usuario_sobre_pqrsdf=pk).first()
        if not instance:
            raise NotFound("No existen registros")
        
        serializer = self.serializer_class(instance)

      
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    

class RequerimientosPQRSDFGetByPQRSDF(generics.ListAPIView):

    serializer_class = RequerimientoSobrePQRSDFGetSerializer
    queryset =SolicitudAlUsuarioSobrePQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pqr):
        
        instance = self.get_queryset().filter(id_pqrsdf=pqr,cod_tipo_oficio='R')
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

class AnexosCreate(generics.CreateAPIView):
    serializer_class = AnexosCreateSerializer
    queryset = Anexos.objects.all()
    permission_classes = [IsAuthenticated]
    archivos_Digitales = ArchivosDgitalesCreate()

    def crear_anexo(self,data):
        data_in = data


        data_in['ya_digitalizado'] = True
        serializer = AnexosCreateSerializer(data=data_in)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'succes': True, 'detail':'Se creo el anexo', 'data':serializer.data,}, status=status.HTTP_200_OK)

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


class RequerimientoSobrePQRSDFCreate(generics.CreateAPIView):
    serializer_class = RequerimientoSobrePQRSDFCreateSerializer
    serializer_class_anexo_pqr = Anexos_RequerimientoCreateSerializer
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
            raise ValidationError("Se requiere informacion del Requerimiento")
        
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
        total_folios =0
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
            if data_anexo['numero_folios']:
                total_folios = total_folios + data_anexo['numero_folios']
 
        # raise ValidationError("SIU")
        data_in['fecha_solicitud'] =fecha_actual
        data_in['cod_tipo_oficio'] ='R'
        data_in['id_persona_solicita'] = request.user.persona.id_persona
        data_in['id_und_org_oficina_solicita'] = id_unidad
        data_in['id_estado_actual_solicitud'] = 1 # 254 Estado guardado
        data_in['fecha_ini_estado_actual'] = fecha_actual
        data_in['cantidad_anexos'] =len(data_anexos)
        data_in['nro_folios_totales'] = total_folios

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
            "id_modulo" : 181,
            "cod_permiso": "CR",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        #BUSCA LA TAREA Y COLOCA LOS ATRIBUTOS DE REQUERIMIENTOS PENDIENTES A TRUE
        if  not 'id_tarea' in request.data:
            raise ValidationError("Debe enviarse la id de la tarea")
        tarea = TareasAsignadas.objects.filter(id_tarea_asignada=request.data['id_tarea']).first()

        if not tarea:
            raise ValidationError("No se encontro la tarea")
        asignacion_tarea = TareaBandejaTareasPersona.objects.filter(id_tarea_asignada=tarea.id_tarea_asignada,es_responsable_ppal=True)
        if asignacion_tarea:
            tarea.requerimientos_pendientes_respuesta = True
            tarea.save()



        print(tarea)
        
        return Response({'succes': True, 'detail':'Se crearon los siguientes registros', 'data':serializer.data,"estado":data_respuesta_estado_asociado,'anexos':data_anexos,'relacion_pqr':relacion_pqr}, status=status.HTTP_200_OK)


class AnexosFGetByRequerimiento(generics.ListAPIView):

    serializer_class = Anexos_PQRAnexosGetSerializer
    queryset = Anexos_PQR.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,re):
        
        instance = self.get_queryset().filter(id_solicitud_usu_sobre_PQR=re)
        if not instance:
            raise NotFound("No existen registros")
        
        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
       
class MetadatosAnexosRequerimientoGetByIdAnexo(generics.ListAPIView):

    serializer_class = MetadatosAnexosTmpGetSerializer
    queryset =MetadatosAnexosTmp.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        
        instance = self.get_queryset().filter(id_anexo=pk).first()
        if not instance:
            raise NotFound("No existen registros")
        
        serializador = self.serializer_class(instance)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
    

#Reasignacion de tarea
    
class UnidadOrganizacionalUsuarioBandeja(generics.ListAPIView):
    serializer_class = UnidadOrganizacionalBandejaTareasSerializer
    queryset = UnidadesOrganizacionales.objects.all()
    def get(self,request,pk):
        persona = Personas.objects.filter(id_persona=pk).first()
        if not persona:
            raise NotFound("No existen Persona")
        unidad = persona.id_unidad_organizacional_actual
        if not unidad:
            raise NotFound("Este Usuario no tiene unidad organizacional asignada")
        serializer = self.serializer_class(unidad)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class UnidadOrganizacionalHijasByUnidadId(generics.ListAPIView):
    serializer_class = UnidadOrganizacionalBandejaTareasSerializer
    queryset = UnidadesOrganizacionales.objects.all()

    def get_units_recursive(self, unidad):
        """
        Función recursiva para obtener todas las unidades asociadas a una unidad dada.

        Args:
            unidad: La unidad organizacional actual.

        Returns:
            Lista de unidades asociadas.
        """
        unidades_asociadas = [unidad]
    
        # Obtiene las unidades hijas recursivamente
        unidades_hijas = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre=unidad.id_unidad_organizacional)

        for unidad_hija in unidades_hijas:
            unidades_asociadas.extend(self.get_units_recursive(unidad_hija))

        return unidades_asociadas
    def get(self,request,pk):
    

        unidad_padre = UnidadesOrganizacionales.objects.get(id_unidad_organizacional=pk)

        if not unidad_padre:
            raise NotFound("No existen registros")

        unidades_asociadas = self.get_units_recursive(unidad_padre)

        serializer = self.serializer_class(unidades_asociadas, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data}, status=status.HTTP_200_OK)

class PersonaLiderUnidadGetByUnidad(generics.ListAPIView):
    serializer_class = LiderUnidadGetSerializer
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

class PersonasUnidadGetByUnidad(generics.ListAPIView):
    serializer_class = PersonaUnidadSerializer
    queryset = Personas.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,uni):
        
        unidad = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = uni).first()
        if not unidad:
            raise NotFound("No existen registros")
        personas = Personas.objects.filter(id_unidad_organizacional_actual=uni)
        seralizer = self.serializer_class(personas,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':seralizer.data}, status=status.HTTP_200_OK)
    

class ReasignacionesTareasCreate(generics.CreateAPIView):
    serializer_class = ReasignacionesTareasCreateSerializer
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
        tarea.cod_estado_solicitud = 'De'
        tarea.save()
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        ##CREAR NUEVO REGISTRO DE REASIGNACION DE TAREA T316
        data_tarea = {}
        data_tarea['cod_tipo_tarea'] = 'Rpqr'
        data_tarea['id_asignacion'] = None
        data_tarea['fecha_asignacion'] = datetime.now()
        data_tarea['cod_estado_solicitud'] = 'Ep'
        data_tarea['id_tarea_asignada_padre_inmediata'] = tarea.id_tarea_asignada
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

        #CAMBIO EL ESTADO DE LA TAREA PADRE EN ESPERA
        return Response({'succes': True, 'detail':'Se crearon los siguientes registros', 'data':serializer.data,'data_tarea_respuesta':data_tarea_respuesta}, status=status.HTTP_200_OK)
    
class ReasignacionesTareasgetById(generics.ListAPIView):
    serializer_class = ReasignacionesTareasgetByIdSerializer
    queryset = ReasignacionesTareas.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        instance = self.get_queryset().filter(id_tarea_asignada=pk)
        if not instance:
            raise NotFound("No existen registros")
        serializer = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)

class ReasignacionTareasAsignadasJusTarea(generics.UpdateAPIView):

    serializer_class = TareasAsignadasGetJustificacionSerializer
    queryset = TareasAsignadas.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        
        tarea = TareasAsignadas.objects.filter(id_tarea_asignada=pk).first()
        
        reasignacion = ReasignacionesTareas.objects.filter(id_tarea_asignada=pk,cod_estado_reasignacion='Re').order_by('-fecha_reasignacion').first()
        if not reasignacion:
            raise ValidationError('la tarea no fue rechazada')
        data = {}
        data['id_tarea_asignada'] = tarea.id_tarea_asignada
        data['tarea_hija'] = reasignacion.id_tarea_asignada.id_tarea_asignada
        data['justificacion_rechazo'] = reasignacion.justificacion_reasignacion_rechazada


        
        serializer = self.serializer_class(tarea)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': data,}, status=status.HTTP_200_OK)
        
class ReasignacionTareasGetByIdTarea(generics.UpdateAPIView):

    serializer_class = ReasignacionesTareasgetByIdTareaSerializer
    queryset = TareasAsignadas.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        
        tarea = TareasAsignadas.objects.filter(id_tarea_asignada=pk).first()
        if not tarea:
            raise NotFound("No existen registros")
        
        reasignacion = ReasignacionesTareas.objects.filter(id_tarea_asignada=pk)
        if not reasignacion:
            raise ValidationError('la tarea  fue rechazada')


        serializer = self.serializer_class(reasignacion,many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data,}, status=status.HTTP_200_OK)
    

class RespuestaPQRSDFByPQR(generics.UpdateAPIView):

    serializer_class = RespuestasPQRGetSeralizer
    queryset = RespuestaPQR.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pqr):
        
        respuesta = self.get_queryset().filter(id_pqrsdf=pqr)
        if not respuesta:
            raise NotFound("No existen registros")

        serializer = self.serializer_class(respuesta,many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data,}, status=status.HTTP_200_OK)
        

class ArchiarSolicitudOtros(generics.UpdateAPIView):
    serializer_class = ArchivoSoporteSerializer

    def post(self,request):
        data_in = request.data
        #data_in = json.loads(data_total.get('data'))
        #anexo = request.FILES.get('anexo')
        persona_logueada = request.user.persona

        solicitud_otros = Otros.objects.filter(id_otros=data_in['id_otros']).first()
        expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=data_in['id_expediente_documental']).first()


        data_docarch = {
           # "identificacion_doc_en_expediente": data_in['identificacion_doc_en_expediente'],
            "nombre_asignado_documento": data_in['nombre_asignado_documento'],
            "fecha_creacion_doc": data_in['fecha_creacion_doc'],
            "fecha_incorporacion_doc_a_Exp": data_in['fecha_incorporacion_doc_a_Exp'],
            "descripcion": data_in['descripcion'],
            "asunto": data_in['asunto'],
            "cod_categoria_archivo": data_in['cod_categoria_archivo'],
            "es_version_original": True,
            "tiene_replica_fisica": data_in['tiene_replica_fisica'],
            "nro_folios_del_doc": data_in['nro_folios_del_doc'],
            "cod_origen_archivo": data_in['cod_origen_archivo'],
            "id_tipologia_documental": data_in['id_tipologia_documental'],
            "codigo_tipologia_doc_prefijo": data_in['codigo_tipologia_doc_prefijo'],
            "codigo_tipologia_doc_agno": data_in['codigo_tipologia_doc_agno'],
            "codigo_tipologia_doc_consecutivo": data_in['codigo_tipologia_doc_consecutivo'],
            "es_un_archivo_anexo": False,
            "anexo_corresp_a_lista_chequeo": False,
            "cantidad_anexos": solicitud_otros.cantidad_anexos,
            "palabras_clave_documento": data_in['palabras_clave_documento'],
            "sub_sistema_incorporacion": "GEST",
            "documento_requiere_rta": False,
            "creado_automaticamente": False,
            "id_und_org_oficina_creadora": persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional,
            "id_persona_que_crea": persona_logueada.id_persona,
            "id_und_org_oficina_respon_actual": persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional,
        }
        data_docarch['id_expediente_documental'] = data_in['id_expediente_documental']

        # orden_expediente = await DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=data_in['id_expediente_documental']).aaggregate(Max('orden_en_expediente', default=0))
        # print(orden_expediente['orden_en_expediente__max'])
        # #ultimo_orden = orden_expediente['orden_en_expediente__max'] if orden_expediente['orden_en_expediente__max'] else 0
        # ultimo_orden = orden_expediente['orden_en_expediente__max']
        #ultimo_orden = self.orden_expediente(data_in['id_expediente_documental'])
        orden_expediente = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=data_in['id_expediente_documental']).order_by('orden_en_expediente').last()
        print(orden_expediente.orden_en_expediente)
        ultimo_orden = orden_expediente.orden_en_expediente
        data_docarch['orden_en_expediente'] = ultimo_orden + 1
        cantidad_digitos = len(str(ultimo_orden))

        if expediente.cod_tipo_expediente == "S":
            i = 0
            while cantidad_digitos != 10:
                cantidad_digitos = cantidad_digitos + 1
                i = i + 1
            data_docarch['identificacion_doc_en_expediente'] = f"{expediente.codigo_exp_Agno}{expediente.cod_tipo_expediente}{str(ultimo_orden).zfill(i)}"
        else:
            cantidad_digitos = cantidad_digitos + len(str(expediente.codigo_exp_consec_por_agno))
            i = 0
            while cantidad_digitos != 10:
                cantidad_digitos = cantidad_digitos + 1
                i = i + 1
            data_docarch['identificacion_doc_en_expediente'] = f"{expediente.codigo_exp_Agno}{expediente.cod_tipo_expediente}{expediente.codigo_exp_consec_por_agno}{str(ultimo_orden).zfill(i)}"

        anexo = self.crear_pdf(data_in)
        print(anexo)
        # ruta = os.path.join("home", "BIA", "Gestor", "GDEA", str(expediente.codigo_exp_Agno))

        # # md5_hash = hashlib.md5()
        # # for chunk in anexo.chunks():
        # #     md5_hash.update(chunk)

        # hash_md5 = hashlib.md5(anexo).hexdigest()
        # print(hash_md5)

        # data_archivo = {
        #     #'name': f"otros-{data_docarch['identificacion_doc_en_expediente']}",
        #     'es_Doc_elec_archivo': True,
        #     'ruta': ruta,
        #     'md5_hash': hash_md5
        # }
            
        # archivo_class = ArchivosDgitalesCreate()
        # respuesta = archivo_class.crear_archivo(data_archivo, anexo)

        # id_archivo_doc_recibido = respuesta.data.get('data').get('id_archivo_digital')

        data_docarch['id_archivo_sistema'] = 7

        serializer = self.serializer_class(data=data_docarch)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()


        return Response({'success': True, 'detail': 'Se archivó el soporte correctamente', 'data': serializer.data}, status=status.HTTP_200_OK)

    
    def crear_pdf(self, data):


        #buffer = io.BytesIO()
        ruta = str(settings.BASE_DIR) + "/static/media/home/BIA/Otros/otros.pdf"
        c = canvas.Canvas(ruta)

        c.drawString(200, 820, "INFORMACIÓN DE LA SOLICITUD OTROS")

        c.rect(20, 720, 550, 80)
        c.drawString(30, 770, "Nombre de la Persona Titular: Brayan Barragan")
        c.drawString(30, 740, "Número de Documento: 1193515179")

        c.rect(20, 595, 550, 100)
        c.drawString(30, 670, "Nombre de la Persona que Interpone: Brayan Barragan")
        c.drawString(30, 640, "Número de Documento: 1193515179")
        c.drawString(30, 610, "Relación con el Titular: Apoderado")

        c.rect(20, 230, 550, 340)
        c.drawString(30, 550, "Fecha de Registro: 27/07/2000")
        c.drawString(30, 520, "Medio de Solicitud: Pagina Web")
        c.drawString(30, 490, "Forma de Presentación: USB")
        c.drawString(30, 460, "Asunto: sdadasdasd")
        c.drawString(30, 430, "Descripción: dsadasdasdas")
        c.drawString(30, 400, "Cantidad de Anexos: 4")
        c.drawString(30, 370, "Número de Folios en Total: 32")
        c.drawString(30, 340, "Nombre de la Persona que Recibio: Daniela Castro")
        c.drawString(30, 310, "Sucursal de Recepción Física: sede principal")
        c.drawString(30, 280, "Radicado: 32")
        c.drawString(30, 250, "Fecha de Radicado: 27/07/2000")


        c.showPage()
        c.save()

        #buffer.seek(0)

        # Ahora puedes usar 'buffer' como una variable que contiene tu PDF.
        # Por ejemplo, puedes guardarlo en una variable así:
        #pdf_en_variable = buffer.getvalue()

        # Recuerda cerrar el buffer cuando hayas terminado
        #buffer.close()
        with open(ruta, 'rb') as archivo_pdf:
            contenido_pdf = archivo_pdf.read()
        return contenido_pdf
    
    def crear_indice(self, data):
        serializer_class = DocsIndiceElectronicoSerializer

        id_indice = IndicesElectronicosExp.objects.filter(id_expediente_documental=data['id_expediente_documental']).first().id_indice_electronico_exp

        data_indice = {
            "id_indice_electronico_exp": id_indice,
            "id_doc_archivo_exp": data['id_documento_archivo'],
            "identificación_doc_exped": data['identificacion_doc_en_expediente'],
            "nombre_documento": data['nombre_asignado_documento'],
            "id_tipologia_documental": data['id_tipologia_documental'],
            "fecha_creacion_doc": data['fecha_creacion_doc'],
            "fecha_incorporacion_exp": data['fecha_incorporacion_doc_a_Exp'],
            "valor_huella": "123456789",
            "funcion_resumen": "MD5",
            "orden_doc_expediente": data['orden_en_expediente'],
            
        }

        
