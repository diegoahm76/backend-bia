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
from gestion_documental.models.bandeja_tareas_models import TareasAsignadas
from gestion_documental.models.radicados_models import PQRSDF, BandejaTareasPersona, TareaBandejaTareasPersona
from gestion_documental.serializers.bandeja_tareas_serializers import BandejaTareasPersonaCreateSerializer, TareaBandejaTareasPersonaCreateSerializer, TareaBandejaTareasPersonaUpdateSerializer, TareasAsignadasCreateSerializer, TareasAsignadasGetSerializer, TareasAsignadasUpdateSerializer
from gestion_documental.serializers.ventanilla_pqrs_serializers import PQRSDFGetSerializer
from transversal.models.personas_models import Personas
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from transversal.models.base_models import ApoderadoPersona

class BandejaTareasPersonaCreate(generics.CreateAPIView):
    serializer_class = BandejaTareasPersonaCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = BandejaTareasPersona.objects.all()


    def crear_bandeja(self,data):
        data_in = data
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
            id_bandeja = bandeja.id_bandeja_tareas_persona
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
    queryset = TareasAsignadas.objects.all()
    permission_classes = [IsAuthenticated]

    
    def get(self, request,id):
        bandeja_tareas= BandejaTareasPersona.objects.filter(id_persona=id).first()

        if not bandeja_tareas:
            raise NotFound('No se encontro la bandeja de tareas')
        id_bandeja = bandeja_tareas.id_bandeja_tareas_persona
        #Buscamos la asignacion de tareas de la bandeja de tareas
        tareas_asignadas = TareaBandejaTareasPersona.objects.filter(id_bandeja_tareas_persona=id_bandeja)
        if not tareas_asignadas:
            raise NotFound('No se encontro tareas asignadas')
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
        
        instance_previous=copy.copy(instance)
        serializer = self.serializer_class(instance,data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
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
        
        return Response({'success':True,'detail':"Se actualizo la actividad Correctamente.","data":serializer.data,'data_asignacion':data_asignacion},status=status.HTTP_200_OK)



