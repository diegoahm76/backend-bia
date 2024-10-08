from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from gestion_documental.choices.pqrsdf_choices import TIPOS_PQR
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad
from gestion_documental.models.expedientes_models import  CierresReaperturasExpediente, ExpedientesDocumentales
from django.db.models import Count
from datetime import date, datetime



from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
import os
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta, timezone
from gestion_documental.models.radicados_models import PQRSDF, AsignacionPQR, EstadosSolicitudes
from gestion_documental.serializers.reporte_indices_archivos_carpetas_serializers import ReporteIndicesTodosGetSerializer,SucursalesEmpresasSerializer,UnidadesGetSerializer,CatalogosSeriesUnidadGetSerializer
from transversal.models.entidades_models import SucursalesEmpresas
from transversal.models.organigrama_models import Organigramas, UnidadesOrganizacionales







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

        vencidas = instance.filter(id_radicado__isnull=False).exclude(id_estado_actual_solicitud=14)
        today = datetime.now()
        contador = 0

        for v in vencidas:
            
            if today > v.fecha_radicado + timedelta(days=v.dias_para_respuesta):
                    contador += 1

        # print(contador)
        # print(radicadas)
        # print(en_gestion)
        # print(resueltas)

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
        


class ReporteIndicesSucursalesGet(generics.ListAPIView):
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
        sucursales =SucursalesEmpresas.objects.all()
        #1 RADICADO
        #2 EN GESTION
        #14 RESUELTA
        estados = [2,5,14]
        conteo_sucursales = []
        categories = []
        for s in sucursales:
            pqrsdfs = instance.filter(id_sucursal_especifica_implicada=s)
            conteo_estados =[]
      
            for estado in estados:
                radicados = pqrsdfs.filter(id_estado_actual_solicitud=estado).count()
                conteo_estados.append(radicados)
        
            conteo_sucursales.append(conteo_estados)
          
            categories.append(s.descripcion_sucursal)

       
        matriz_transpuesta = [[fila[i] for fila in conteo_sucursales] for i in range(len(conteo_sucursales[0]))]
        
        data =[]
        for x in range (len(estados)):
            nombre_estado = EstadosSolicitudes.objects.filter(id_estado_solicitud=estados[x]).first()
            nombre = None
            if nombre_estado:
                nombre = nombre_estado.nombre
            data.append({'name':nombre,'data':matriz_transpuesta[x]})

        
        
       
        today = datetime.now()
        contador = 0
        conte_vencidos =[]
        for s in sucursales:
            pqrsdfs = instance.filter(id_sucursal_especifica_implicada=s).exclude(id_estado_actual_solicitud=14)
            contador = 0
            for v in pqrsdfs:

                if v.dias_para_respuesta and  today > v.fecha_radicado + timedelta(days=v.dias_para_respuesta):
                    contador += 1
            conte_vencidos.append(contador)

        data.append({'name':'Vencidos', 'data':conte_vencidos})
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':{'series':data, "categories":categories}},status=status.HTTP_200_OK)
        
class ReporteIndicesSucursalesTiposPQRSDFGet(generics.ListAPIView):
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
        sucursales =SucursalesEmpresas.objects.all()
        #1 RADICADO
        #2 EN GESTION
        #14 RESUELTA
        
        conteo_sucursales = []
        categories = []
        
        for s in sucursales:
            pqrsdfs = instance.filter(id_sucursal_especifica_implicada=s)

            
            conteo_tipos =[]
      
            for tipo in TIPOS_PQR:
                radicados = pqrsdfs.filter(cod_tipo_PQRSDF=tipo[0]).count()
                conteo_tipos.append(radicados)
        
            conteo_sucursales.append(conteo_tipos)
          
            categories.append(s.descripcion_sucursal)

       
        matriz_transpuesta = [[fila[i] for fila in conteo_sucursales] for i in range(len(conteo_sucursales[0]))]
        
        data =[]
        for x in range (len(TIPOS_PQR)):
            nombre = TIPOS_PQR[x][1]
            data.append({'name':nombre,'data':matriz_transpuesta[x]})

        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':{'series':data, "categories":categories}},status=status.HTTP_200_OK)
        






class ReporteIndicesTiposSucursalesPQRSDFGet(generics.ListAPIView):
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
        sucursales =SucursalesEmpresas.objects.all()

        
        conteo_sucursales = []
        categories = []
        data =[]
        for s in sucursales:
            pqrsdfs = instance.filter(id_sucursal_especifica_implicada=s)

            
            conteo_tipos =[]
      
            for tipo in TIPOS_PQR:
                radicados = pqrsdfs.filter(cod_tipo_PQRSDF=tipo[0]).count()
                
                conteo_tipos.append(radicados)
        
            conteo_sucursales.append(conteo_tipos)
            data.append({'name':s.descripcion_sucursal,'data':conteo_tipos})
        
        
       
        for x in range (len(TIPOS_PQR)):
            categories.append( TIPOS_PQR[x][1])
            

        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':{'series':data, "categories":categories}},status=status.HTTP_200_OK)
        





class ReporteIndicesUnidadPQRSDFGet(generics.ListAPIView):
    serializer_class = None
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        #2 RADICADO
        #5 EN GESTION
        #14 RESUELTA
        estados = [2,5,14]

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
        
        organigrama = Organigramas.objects.filter(actual=True)
        if not organigrama:
            raise NotFound('No existe ningún organigrama activado')
        if len(organigrama) > 1:
            raise PermissionDenied('Existe más de un organigrama actual, contacte a soporte')
        
        organigrama_actual = organigrama.first()
        unidades_organigrama_actual = UnidadesOrganizacionales.objects.filter(id_organigrama=organigrama_actual.id_organigrama)
        asignaciones = AsignacionPQR.objects.filter(id_und_org_seccion_asignada__in=unidades_organigrama_actual,cod_estado_asignacion='Ac')

        conteo_unidades = []
        categories  = []
        for unidad in unidades_organigrama_actual:
            array =[]
            for estado in estados:
                conteo = asignaciones.filter(id_und_org_seccion_asignada=unidad, cod_estado_asignacion='Ac', id_pqrsdf__id_estado_actual_solicitud=estado).count()
                array.append(conteo)

            conteo_unidades.append(array)
            categories.append(unidad.nombre)
        matriz_transpuesta = [[fila[i] for fila in conteo_unidades] for i in range(len(conteo_unidades[0]))]
        print(matriz_transpuesta)

        data=[]
        data.append({'name':'Radicados', 'data':matriz_transpuesta[0]})
        data.append({'name':'En Gestión', 'data':matriz_transpuesta[1]})
        data.append({'name':'Resuelta', 'data':matriz_transpuesta[2]})


        today = datetime.now()
        contador = 0
        conte_vencidos =[]
        for s in unidades_organigrama_actual:
            
            contador = 0
            asignacion_unidad = asignaciones.filter(id_und_org_seccion_asignada=s)
            for v in asignacion_unidad:

                if v.id_pqrsdf.dias_para_respuesta and  today > v.id_pqrsdf.fecha_radicado + timedelta(days=v.id_pqrsdf.dias_para_respuesta):
                    contador += 1
            conte_vencidos.append(contador)

        data.append({'name':'Vencidos', 'data':conte_vencidos})


        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':{'series':data, "categories":categories}},status=status.HTTP_200_OK)
     