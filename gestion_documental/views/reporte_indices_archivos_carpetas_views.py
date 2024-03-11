from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from gestion_documental.models.expedientes_models import  CierresReaperturasExpediente, ExpedientesDocumentales
from django.db.models import Count
from datetime import date, datetime



from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
import os
from rest_framework.permissions import IsAuthenticated

from gestion_documental.serializers.reporte_indices_archivos_carpetas_serializers import ReporteIndicesTodosGetSerializer






class ReporteIndicesTodosGet(generics.ListAPIView):
    serializer_class = ReporteIndicesTodosGetSerializer
    queryset = ExpedientesDocumentales.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):

        filter={}
        fecha_inicio = None
        fecha_fin = None
        for key, value in request.query_params.items():

            if key == 'fecha_inicio':
                if value != '':
                    
                    filter['fecha_apertura_expediente__gte'] = datetime.strptime(value, '%Y-%m-%d').date()
                    fecha_inicio = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'fecha_fin':
                if value != '':
                    fecha_fin = datetime.strptime(value, '%Y-%m-%d').date()
                    filter['fecha_apertura_expediente__lte'] = datetime.strptime(value, '%Y-%m-%d').date()
                
        instance = self.get_queryset().filter(**filter)
        simples_counts = instance.filter(cod_tipo_expediente='S').count()
        complejos_counts = instance.filter(cod_tipo_expediente='C').count()
        data ={}

        simples =instance.filter(cod_tipo_expediente='S')
        s_abierto = simples.filter(estado='A').count()
        s_cerrado = simples.filter(estado='C').count()
        
        simples_counts = instance.filter(cod_tipo_expediente='S').count()
        complejos_counts = instance.filter(cod_tipo_expediente='C').count()
        data ={}

        simples =instance.filter(cod_tipo_expediente='S')
        s_abierto = simples.filter(estado='A').count()
        s_cerrado = simples.filter(estado='C').count()



        complejos =instance.filter(cod_tipo_expediente='C')
        c_abierto = complejos.filter(estado='A').count()
        c_cerrado = complejos.filter(estado='C').count()

        #Reaperturados
        filtros_adicionales= {}
        filtros_adicionales['cod_operacion'] ='R'
        filtros_adicionales['id_expediente_doc__cod_tipo_expediente'] = 'S' #filtro expediente SIMPLE
        if fecha_inicio :
            filtros_adicionales['id_expediente_doc__fecha_apertura_expediente__gte'] = fecha_inicio

        if fecha_fin :
            filtros_adicionales['fecha_apertura_expediente__lte'] = fecha_fin

        reaperturas_agrupados_simples = (
            CierresReaperturasExpediente.objects
            .filter(**filtros_adicionales)  # filtro para reapertura de un expendiente simple con un rango de fechas 
            .values('id_expediente_doc')
            .annotate(cantidad=Count('id_expediente_doc'))
        )
        filtros_adicionales['id_expediente_doc__cod_tipo_expediente'] = 'C' #filtro expediente Complejo
        reaperturas_agrupados_complejos = (
            CierresReaperturasExpediente.objects
            .filter(**filtros_adicionales)  # Filtrar por el campo cod_operacion
            .values('id_expediente_doc')
            .annotate(cantidad=Count('id_expediente_doc'))
        )
        #print(reaperturas_agrupados_simples)


        count_creados = [simples_counts,complejos_counts]
        creados = {
            'name':'CREADOS',
            'data':count_creados,
            'total': simples_counts + complejos_counts
        }

        
        datacon= [s_abierto,c_abierto]
        total = s_abierto + c_abierto

        abiertos = {
            'name':'ABIERTOS',
            'data' :datacon,
            'total': total
        }
        data_cont_cerrados= [s_cerrado,c_cerrado]
        total = s_cerrado + c_cerrado
        cerrados = {
            'name':'CERRADOS',
            'data' :data_cont_cerrados,
            'total': total

        }


        respuesta = []
        respuesta.append(creados)
        respuesta.append(abiertos)
        respuesta.append(cerrados)

    
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':{'series':respuesta, "categories": ["Simples", "Complejos"]}},status=status.HTTP_200_OK)
        
