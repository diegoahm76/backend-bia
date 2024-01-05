#BandejaTareasPersona
import ast
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

from gestion_documental.models.bandeja_tareas_models import AdicionalesDeTareas, TareasAsignadas
from gestion_documental.models.configuracion_tiempos_respuesta_models import ConfiguracionTiemposRespuesta
from gestion_documental.models.radicados_models import PQRSDF, Anexos, AsignacionPQR, BandejaTareasPersona, Estados_PQR, MetadatosAnexosTmp, SolicitudAlUsuarioSobrePQRSDF, TareaBandejaTareasPersona
from gestion_documental.models.trd_models import TipologiasDoc
from gestion_documental.serializers.bandeja_tareas_serializers import AdicionalesDeTareasGetByTareaSerializer, Anexos_RequerimientoCreateSerializer, BandejaTareasPersonaCreateSerializer, PQRSDFDetalleRequerimiento, PQRSDFTitularGetBandejaTareasSerializer, RequerimientoSobrePQRSDFCreateSerializer, RequerimientoSobrePQRSDFGetSerializer, TareaBandejaTareasPersonaCreateSerializer, TareaBandejaTareasPersonaUpdateSerializer, TareasAsignadasCreateSerializer, TareasAsignadasGetJustificacionSerializer, TareasAsignadasGetSerializer, TareasAsignadasUpdateSerializer
from gestion_documental.serializers.ventanilla_pqrs_serializers import AnexosCreateSerializer, Estados_PQRPostSerializer, MetadatosAnexosTmpCreateSerializer, PQRSDFGetSerializer, SolicitudAlUsuarioSobrePQRSDFCreateSerializer
from gestion_documental.utils import UtilsGestor
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from seguridad.utils import Util

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
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


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
        #cambia el estado de la tarea en la t268
        id_asignacion = instance.id_asignacion
        asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=id_asignacion).first()

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
   
    def put(self,request,pk):
        
        
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
        #asignacion = AsignacionPQR.objects.filter(id_asignacion=id_pqrsdf)
        asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=id_asignacion, cod_estado_asignacion__isnull=True).first()

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
        complemento = AdicionalesDeTareas.objects.filter(id_tarea_asignada=tarea)
        
        print(complemento)
        if not complemento:
            raise NotFound("No se encontro el complemento")
      
        serializer = self.serializer_class(complemento,many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data,}, status=status.HTTP_200_OK)
    


#detalle tarea 
    
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
    serializer_class = PQRSDFDetalleRequerimiento
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,pqr):
        
        instance = self.get_queryset().filter(id_PQRSDF=pqr).first()
        if not instance:
            raise NotFound("No existen registros")
        persona_titular = instance.id_persona_titular 
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

        return Response({'succes': True, 'detail':'Se crearon los siguientes registros', 'data':serializer.data,"estado":data_respuesta_estado_asociado,'anexos':data_anexos,'relacion_pqr':relacion_pqr}, status=status.HTTP_200_OK)
