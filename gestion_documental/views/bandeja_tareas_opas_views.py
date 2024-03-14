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
from gestion_documental.models.bandeja_tareas_models import ReasignacionesTareas, TareasAsignadas

from gestion_documental.models.radicados_models import  AsignacionTramites, BandejaTareasPersona, TareaBandejaTareasPersona
from rest_framework.exceptions import ValidationError,NotFound
from gestion_documental.serializers.bandeja_tareas_opas_serializer import OpaTramiteDetalleGetBandejaTareasSerializer, OpaTramiteTitularGetBandejaTareasSerializer, SolicitudesTramitesOpaDetalleSerializer, TareasAsignadasOpasGetSerializer, TareasAsignadasOpasUpdateSerializer
from gestion_documental.views.bandeja_tareas_views import TareaBandejaTareasPersonaUpdate
from tramites.models.tramites_models import PermisosAmbSolicitudesTramite, SolicitudesTramites

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




class DetalleOpaGetbyId(generics.ListAPIView):
    serializer_class = SolicitudesTramitesOpaDetalleSerializer
    queryset = PermisosAmbSolicitudesTramite.objects.all()
    permission_classes = [IsAuthenticated]

    
    def get(self, request,id):
        instance =self.queryset.filter(id_solicitud_tramite=id,id_permiso_ambiental__cod_tipo_permiso_ambiental='O').first()

        if not instance:
            raise NotFound("No existen Opa asociada a esta id.")
        

        serializador = self.serializer_class(instance)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)



class TareasAsignadasAceptarOpaUpdate(generics.UpdateAPIView):
    serializer_class = TareasAsignadasOpasUpdateSerializer
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
                    
                    if tarea.id_asignacion:
                        id_asignacion = tarea.id_asignacion
                       
                        tarea.cod_estado_solicitud = 'De'
                        tarea.save()
                       
                        break
                
                ##CAMBIAMOS EL ESTADO DE LA TAREA PADRE A DELEGADA

                reasignacion = ReasignacionesTareas.objects.filter(id_tarea_asignada = tarea.id_tarea_asignada, cod_estado_reasignacion='Ep').first()
                if reasignacion:
                    reasignacion.cod_estado_reasignacion = 'Ac'
                    reasignacion.save()

        else:
            #print(id_asignacion)
            asignacion = AsignacionTramites.objects.filter(id_asignacion_tramite=id_asignacion,cod_estado_asignacion__isnull=True).first()
            #asignacion = AsignacionOtros.objects.filter(id_asignacion_otros=id_asignacion,cod_estado_asignacion__isnull=True).first()
            #asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=id_asignacion,cod_estado_asignacion__isnull=True).first()
            if not asignacion:
                raise NotFound("No se encontro la asignacion")
            asignacion.cod_estado_asignacion = 'Ac'
            asignacion.save()
            #print(data_in)
            #print(asignacion)
           
           

        return Response({'success':True,'detail':"Se acepto la pqrsdf Correctamente.","data":serializer.data,'data_asignacion':data_asignacion},status=status.HTTP_200_OK)
    


class TareasAsignadasOpasRechazarUpdate(generics.UpdateAPIView):
    serializer_class = TareasAsignadasOpasUpdateSerializer
    queryset = TareasAsignadas.objects.all()
    permission_classes = [IsAuthenticated]
    vista_asignacion = TareaBandejaTareasPersonaUpdate()
    @transaction.atomic
    def put(self,request,pk):
        
        data_in = request.data
        instance = TareasAsignadas.objects.filter(id_tarea_asignada=pk).first()
        
        if not instance:
            raise NotFound("No se existe un registro con este codigo.")
        
        if instance.cod_tipo_tarea != 'ROpa':
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
        #print(data_in)
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
            #print(id_asignacion)
            asignacion = AsignacionTramites.objects.filter(id_asignacion_tramite=id_asignacion,cod_estado_asignacion__isnull=True).first()
                # raise ValidationError(asignacion.id_pqrsdf)
            if not asignacion:
                raise NotFound("No se encontro la asignacion")
            asignacion.cod_estado_asignacion = 'Re'
            asignacion.justificacion_rechazo = data_in['justificacion_rechazo']
            asignacion.save()
       
        
        return Response({'success':True,'detail':"Se actualizo la actividad Correctamente.","data":serializer.data,'data_asignacion':data_asignacion},status=status.HTTP_200_OK)

#REQUERIMIENTO SOBRE OPA 
    

class OpaPersonaTitularGet(generics.ListAPIView):
    serializer_class = OpaTramiteTitularGetBandejaTareasSerializer
    queryset = SolicitudesTramites.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,tra):
        
        instance = self.get_queryset().filter(id_solicitud_tramite=tra).first()

        

        if not instance:
            raise NotFound("No existen registros")
        persona_titular = instance.id_persona_titular 
        serializer = self.serializer_class(persona_titular)

        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)

class OpaTramiteDetalleGet(generics.ListAPIView):
    serializer_class = OpaTramiteDetalleGetBandejaTareasSerializer
    queryset = SolicitudesTramites.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request, tra):

        instance = self.get_queryset().filter(id_solicitud_tramite=tra).first()


        if not instance:
            raise NotFound("No existen registros")
        serializer = self.serializer_class(instance)


        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)