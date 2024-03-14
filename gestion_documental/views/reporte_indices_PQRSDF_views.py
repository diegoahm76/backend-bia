from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad
from gestion_documental.models.expedientes_models import  CierresReaperturasExpediente, ExpedientesDocumentales
from django.db.models import Count
from datetime import date, datetime



from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
import os
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta, timezone
from gestion_documental.models.radicados_models import PQRSDF
from gestion_documental.serializers.reporte_indices_archivos_carpetas_serializers import ReporteIndicesTodosGetSerializer,SucursalesEmpresasSerializer,UnidadesGetSerializer,CatalogosSeriesUnidadGetSerializer







class ReporteIndicesTodosGet(generics.ListAPIView):
    serializer_class = None
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):

        filter={}
        fecha_inicio = None
        fecha_fin = None
        for key, value in request.query_params.items():

            if key == 'fecha_inicio':
                if value != '':
                    
                    filter['fecha_registro__gte'] = datetime.strptime(value, '%Y-%m-%d').date()
                    fecha_inicio = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'fecha_fin':
                if value != '':
                    fecha_fin = datetime.strptime(value, '%Y-%m-%d').date()
                    filter['fecha_registro__lte'] = datetime.strptime(value, '%Y-%m-%d').date()
                
        instance = self.get_queryset().filter(**filter)
        radicadas = instance.filter(id_estado_actual_solicitud=2).count()
        en_gestion = instance.filter(id_estado_actual_solicitud=5).count()
        resueltas = instance.filter(id_estado_actual_solicitud=14).count()

        vencidas = instance.filter(id_radicado__isnull=False)
        today = datetime.now()
        contador = 0

        for v in vencidas:
            
            if today > v.fecha_radicado + timedelta(days=v.dias_para_respuesta):
                    contador += 1

        print(contador)
        print(radicadas)
        print(en_gestion)
        print(resueltas)

        series = []

        data_radicados ={}
        data_radicados['name'] = 'Radicados'
        data_radicados['data'] = [radicadas]
        data_radicados['total'] = radicadas
        series.append(data_radicados)
        data_en_gestion ={}
        data_en_gestion['name'] = 'En Gestión'
        data_en_gestion['data'] = [en_gestion]
        data_en_gestion['total'] = en_gestion
        series.append(data_en_gestion)
        data_resueltas ={}
        data_resueltas['name'] = 'Resueltas'
        data_resueltas['data'] = [resueltas]
        data_resueltas['total'] = resueltas
        series.append(data_resueltas)
        data_vencidos ={}
        data_vencidos['name'] = 'Vencidos'
        data_vencidos['data'] = [contador]
        data_vencidos['total'] = contador
        series.append(data_vencidos)



        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':{'series':series, "categories": ["TOTAL"]}},status=status.HTTP_200_OK)
        
