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

from gestion_documental.models.radicados_models import  BandejaTareasPersona, TareaBandejaTareasPersona
from rest_framework.exceptions import ValidationError,NotFound
from gestion_documental.serializers.bandeja_tareas_opas_serializer import TareasAsignadasOpasGetSerializer

class TareasAsignadasGetOpasByPersona(generics.ListAPIView):
    serializer_class = TareasAsignadasOpasGetSerializer
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
        filter['id_tarea_asignada__cod_tipo_tarea'] = 'ROpa' 

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

