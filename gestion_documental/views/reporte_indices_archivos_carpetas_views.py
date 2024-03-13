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


from gestion_documental.serializers.reporte_indices_archivos_carpetas_serializers import ReporteIndicesTodosGetSerializer,SucursalesEmpresasSerializer,UnidadesGetSerializer,CatalogosSeriesUnidadGetSerializer
from transversal.models.entidades_models import SucursalesEmpresas
from transversal.models.organigrama_models import Organigramas, UnidadesOrganizacionales



class SerieSubserioUnidadGet(generics.ListAPIView):

    serializer_class = CatalogosSeriesUnidadGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get (self, request,uni):

        instance=CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=uni)

        if not instance:
            raise NotFound("No existen registros asociados.")
        
        serializador=self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data}, status=status.HTTP_200_OK)


class UnidadesOrganigramaActualGet(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer
    queryset = UnidadesOrganizacionales.objects.all()

    def get(self, request):
        organigrama = Organigramas.objects.filter(actual=True)
        if not organigrama:
            raise NotFound('No existe ningún organigrama activado')
        if len(organigrama) > 1:
            raise PermissionDenied('Existe más de un organigrama actual, contacte a soporte')
        
        organigrama_actual = organigrama.first()
        unidades_organigrama_actual = UnidadesOrganizacionales.objects.filter(id_organigrama=organigrama_actual.id_organigrama)
        serializer = self.serializer_class(unidades_organigrama_actual, many=True)
        return Response({'success':True, 'detail':'Consulta Exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)


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

        simples =instance.filter(cod_tipo_expediente='S')
        s_abierto = simples.filter(estado='A').count()
        s_cerrado = simples.filter(estado='C').count()
        
        simples_counts = instance.filter(cod_tipo_expediente='S').count()
        complejos_counts = instance.filter(cod_tipo_expediente='C').count()

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
            filtros_adicionales['id_expediente_doc__fecha_apertura_expediente__lte'] = fecha_fin

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

        reaperturados ={#reaperturas_agrupados_simples
            'name':'REAPERTURADOS',
            'data': [len(reaperturas_agrupados_simples),len(reaperturas_agrupados_complejos)],
            'total': len(reaperturas_agrupados_simples) + len(reaperturas_agrupados_complejos)
        }

        respuesta = []
        respuesta.append(creados)
        respuesta.append(abiertos)
        respuesta.append(cerrados)
        respuesta.append(reaperturados)

        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':{'series':respuesta, "categories": ["Simples", "Complejos"]}},status=status.HTTP_200_OK)
        


class SucursalesEmpresasGet(generics.ListAPIView):
    serializer_class = SucursalesEmpresasSerializer
    queryset = SucursalesEmpresas.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request,):
        instance = self.get_queryset()

        serializer = self.serializer_class(instance, many=True)

        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializer.data},status=status.HTTP_200_OK) 

class ReporteUnidadGet(generics.ListAPIView):
    queryset = ExpedientesDocumentales.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = None
    def get(self, request, uni):
        
        unidades_hijas = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre=uni).values_list('id_unidad_organizacional','nombre', named=True)
        creados =[]
        abiertos =[]
        cerrados = []
        reaperturados = []
        categorias = []


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

        
   

        for unidad,nombre in unidades_hijas:
            filter['id_und_org_oficina_respon_actual'] = unidad
            expedientes = ExpedientesDocumentales.objects.filter(**filter)
            creados.append(expedientes.count())
            abiertos.append(expedientes.filter(estado='A').count())
            cerrados.append(expedientes.filter(estado='C').count())
            contador = 0
            for expediente in expedientes:
                reaper = CierresReaperturasExpediente.objects.filter(id_expediente_doc=expediente.id_expediente_documental,cod_operacion='R')
                if reaper:
                    contador += 1
            reaperturados.append(contador)
            categorias.append(nombre)
        
        series =[]
        series.append({'name':'CREADOS','data':creados})
        series.append({'name':'ABIERTOS', 'data':abiertos})
        series.append({'name':'CERRADOS', 'data':cerrados})
        series.append({'name':'REAPERTURADOS', 'data':reaperturados})

        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':{'series':series,'categories':categorias}},status=status.HTTP_200_OK) 


class ReporteUnidadOficinaGet(generics.ListAPIView):
    queryset = ExpedientesDocumentales.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = None
    def get(self, request, uni):
        
        unidad = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=uni).first()
        filter={}
        if not unidad:
            raise NotFound('No existe registro')
        

        for key, value in request.query_params.items():

            if key == 'fecha_inicio':
                if value != '':
                    
                    filter['fecha_apertura_expediente__gte'] = datetime.strptime(value, '%Y-%m-%d').date()
                    fecha_inicio = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'fecha_fin':
                if value != '':
                    fecha_fin = datetime.strptime(value, '%Y-%m-%d').date()
                    filter['fecha_apertura_expediente__lte'] = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'serie_suberie':
                if value != '':
                    filter['id_cat_serie_und_org_ccd_trd_prop__id_cat_serie_und'] = value
        
        filter['id_und_org_oficina_respon_actual'] = uni
        
        expedientes = ExpedientesDocumentales.objects.filter(**filter)
        ids_expedientes = expedientes.values_list('id_expediente_documental', flat=True)
        abiertos = expedientes.filter(estado='A').count()
        cerrados = expedientes.filter(estado='C').count()

        reaperturas_agrupados = (
            CierresReaperturasExpediente.objects
            .filter(cod_operacion='R',id_expediente_doc__in=ids_expedientes)  # Filtrar por el campo cod_operacion
            .values('id_expediente_doc')
            .annotate(cantidad=Count('id_expediente_doc'))
        )

        series =[]
        series.append({'name':'CREADOS', 'data':len(expedientes)})
        series.append({'name':'ABIERTOS', 'data':abiertos})
        series.append({'name':'CERRADOS', 'data':cerrados})
        series.append({'name':'REAPERTURADOS', 'data':len(reaperturas_agrupados)})

        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':{'series':series,'categories':[unidad.nombre]}},status=status.HTTP_200_OK) 





class ReporteUnidadTotalUnidadGet(generics.ListAPIView):
    queryset = ExpedientesDocumentales.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = None
    def get(self, request, uni):
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

        unidades_hijas = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre=uni).values_list('id_unidad_organizacional','nombre', named=True)
        creados =[]
        abiertos =[]
        cerrados = []
        reaperturados = []
        
        categorias = []
        for unidad,nombre in unidades_hijas:
            filter['id_unidad_org_oficina_respon_original'] = unidad
            expedientes = ExpedientesDocumentales.objects.filter(**filter)
            creados.append(expedientes.count())
            categorias.append(nombre)
        
        expedientes_por_unidad = list(zip(creados, categorias))
        expedientes_por_unidad.sort(reverse=True)
        top_dos_unidades = expedientes_por_unidad[:2]
      
        categories = []
        data =[]
        series = []
        for creado,categoria in top_dos_unidades:
            categories.append(categoria)
            data.append(creado)

        series.append({'name':'Expedientes', 'data':data})



        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':{'series':series,'categories':categories}},status=status.HTTP_200_OK) 




class ReporteIndicesSedesGet(generics.ListAPIView):
    serializer_class = ReporteIndicesTodosGetSerializer
    queryset = ExpedientesDocumentales.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):

        filter={}
        fecha_inicio = None
        fecha_fin = None
        sucursal = None
        for key, value in request.query_params.items():

            if key == 'fecha_inicio':
                if value != '':
                    
                    filter['fecha_apertura_expediente__gte'] = datetime.strptime(value, '%Y-%m-%d').date()
                    fecha_inicio = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'fecha_fin':
                if value != '':
                    fecha_fin = datetime.strptime(value, '%Y-%m-%d').date()
                    filter['fecha_apertura_expediente__lte'] = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'id_sucursal':
                sucursal = value

        if not sucursal:
            instance = self.get_queryset().filter(**filter)
            sucursales = SucursalesEmpresas.objects.all()
            personas = [sucursal.id_persona_empresa.id_persona for sucursal in sucursales]
            
        if sucursal:
            sucursales = SucursalesEmpresas.objects.filter(id_sucursal_empresa = sucursal)
            personas = [sucursal.id_persona_empresa.id_persona for sucursal in sucursales]

           




        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':{'series':'respuesta', "categories": ["Simples", "Complejos"]}},status=status.HTTP_200_OK)
