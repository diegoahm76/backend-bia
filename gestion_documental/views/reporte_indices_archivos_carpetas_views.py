from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from gestion_documental.models.expedientes_models import  CierresReaperturasExpediente, ExpedientesDocumentales
from django.db.models import Count




from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
import os
from rest_framework.permissions import IsAuthenticated

from gestion_documental.serializers.reporte_indices_archivos_carpetas_serializers import ReporteIndicesTodosGetSerializer






class ReporteIndicesTodosGet(generics.ListAPIView):
    serializer_class = ReporteIndicesTodosGetSerializer
    queryset = ExpedientesDocumentales.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        
        simples_counts = ExpedientesDocumentales.objects.filter(cod_tipo_expediente='S').count()
        complejos_counts = ExpedientesDocumentales.objects.filter(cod_tipo_expediente='C').count()
        data ={}

        simples =ExpedientesDocumentales.objects.filter(cod_tipo_expediente='S')
        s_abierto = simples.filter(estado='A').count()
        s_cerrado = simples.filter(estado='C').count()



        complejos =ExpedientesDocumentales.objects.filter(cod_tipo_expediente='C')
        c_abierto = complejos.filter(estado='A').count()
        c_cerrado = complejos.filter(estado='C').count()

        #Reaperturados
        cierres_reaperturas = CierresReaperturasExpediente.objects.all()


        reaperturas_agrupados_simples = (
            CierresReaperturasExpediente.objects
            .filter(cod_operacion='R',id_expediente_doc__cod_tipo_expediente='S')  # Filtrar por el campo cod_operacion
            .values('id_expediente_doc')
            .annotate(cantidad=Count('id_expediente_doc'))
        )
        reaperturas_agrupados_simples = (
            CierresReaperturasExpediente.objects
            .filter(cod_operacion='R',id_expediente_doc__cod_tipo_expediente='C')  # Filtrar por el campo cod_operacion
            .values('id_expediente_doc')
            .annotate(cantidad=Count('id_expediente_doc'))
        )
        print(reaperturas_agrupados_simples)


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
        
