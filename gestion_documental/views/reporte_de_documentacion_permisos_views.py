from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad
from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
from gestion_documental.models.plantillas_models import AccesoUndsOrg_PlantillaDoc, PlantillasDoc
from gestion_documental.models.tca_models import TablasControlAcceso
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, FormatosTiposMedio, TablaRetencionDocumental, TipologiasDoc
from gestion_documental.serializers.permisos_serializers import DenegacionPermisosGetSerializer
from gestion_documental.serializers.plantillas_serializers import AccesoUndsOrg_PlantillaDocCreateSerializer, AccesoUndsOrg_PlantillaDocGetSerializer, OtrasTipologiasSerializerGetSerializer, PlantillasDocBusquedaAvanzadaDetalleSerializer, PlantillasDocBusquedaAvanzadaSerializer, PlantillasDocCreateSerializer, PlantillasDocGetSeriallizer, PlantillasDocSerializer, PlantillasDocUpdateSerializer, TipologiasDocSerializerGetSerializer
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
import os
from rest_framework.permissions import IsAuthenticated
import json
from gestion_documental.serializers.trd_serializers import DenegacionPermisosGetUnidadSerializer, PermisosUndsOrgActualesSerieExpCCDSerializer, SerieSubserieReporteSerializer, TablaRetencionDocumentalPermisosGetsSerializer, UnidadSeccionSubseccionGetSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.views.permisos_views import DenegacionPermisosGetView, UnidadesExternasPermisosGetView
from transversal.models.organigrama_models import UnidadesOrganizacionales

#TablaRetencionDocumental
class TRDCCDOrganigramaGet(generics.ListAPIView):
    serializer_class = TablaRetencionDocumentalPermisosGetsSerializer
    queryset = TablaRetencionDocumental.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        
                
        #intance = self.queryset.all().filter(id_plantilla_doc=pk)
        intance = TablaRetencionDocumental.objects.filter(fecha_puesta_produccion__isnull=False)
        for i in intance:
            tca = TablasControlAcceso.objects.filter(id_trd=i.id_trd)  
            print(tca)

        serializador = self.serializer_class(intance,many=True)
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializador.data},status=status.HTTP_200_OK)
        

class UnidadesSeccionSubseccionGet(generics.ListAPIView):
    serializer_class = UnidadSeccionSubseccionGetSerializer
    queryset = TablaRetencionDocumental.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,trd):
        
        catalogo_ids = CatSeriesUnidadOrgCCDTRD.objects.filter(id_trd=trd).values_list('id_cat_serie_und', flat=True)#T218CatSeries_UndOrg_CCD_TRD
        
        catalogo_ids_list = list(catalogo_ids)
        
        catalogo_series_unidad= CatalogosSeriesUnidad.objects.filter(id_cat_serie_und__in=catalogo_ids_list).order_by('id_unidad_organizacional')

        unidades=[]
        
        for x in catalogo_series_unidad.distinct():
            
            unidad=x.id_unidad_organizacional
            if unidad.cod_agrupacion_documental:
                serializer = self.serializer_class(unidad)
                unidades.append(serializer.data)
        #serializer = self.serializer_class(catalogo_series_unidad,many=True)
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':unidades},status=status.HTTP_200_OK)
    

#PermisosUndsOrgActualesSerieExpCCD
class ReportePermisosUndsOrgActualesSerieExpCCDGet(generics.ListAPIView):
    serializer_class = PermisosUndsOrgActualesSerieExpCCDSerializer
    serializer_serie_subserie = SerieSubserieReporteSerializer
    serializer_class_seccion_subseccion = UnidadSeccionSubseccionGetSerializer
    queryset = PermisosUndsOrgActualesSerieExpCCD.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,cat):
        #nstance = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=cat).values_list('id_cat_serie_und', flat=True)
        instance2 = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=cat)
        unidad = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=cat).first()
        if not unidad:
            raise NotFound("No existen registros asociados.")
        if not instance2:
            raise NotFound("No existen registros asociados.")
        data_unidad = self.serializer_class_seccion_subseccion(unidad).data
        dic = {}
        data = []
        for x in instance2:
            dic = {}
            print(x.id_catalogo_serie.id_serie_doc)
            #data.append()
            permisos = PermisosUndsOrgActualesSerieExpCCD.objects.filter(id_cat_serie_und_org_ccd=x)
           
            dic['serie_subserie'] = self.serializer_serie_subserie(x.id_catalogo_serie,many=False).data
            dic['permisos'] = self.serializer_class(permisos,many=True).data
            data.append(dic)
        
        # if not instance:
        #     raise NotFound("No existen registros asociados.")
        #raise ValidationError("SI")
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':{'unidad':data_unidad,'series':data}},status=status.HTTP_200_OK)
    

# class DenegacionPermisosGetByUnidadView(generics.ListAPIView):
#     serializer_class = DenegacionPermisosGetUnidadSerializer 
#     queryset = PermisosUndsOrgActualesSerieExpCCD.objects.filter()
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request, uni):
#         data=[]
#         catalogos = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=uni)
#         #print(catalogos)
#         for  cat in catalogos:
#             print(cat)
#             serializador = None
            
#             denegacion_permisos = self.queryset.filter(id_cat_serie_und_org_ccd=cat.id_cat_serie_und, id_und_organizacional_actual=None).first()
#             serializador = self.serializer_class(denegacion_permisos)
#             data.append(serializador.data)
#         return Response({'succes': True, 'detail':'Resultados encontrados', 'data':data}, status=status.HTTP_200_OK)
    
class PermisosExpedientesNoPropios(generics.ListAPIView):
    serializer_class = DenegacionPermisosGetSerializer
    queryset = PermisosUndsOrgActualesSerieExpCCD.objects.filter()
    permission_classes = [IsAuthenticated]
    serializer_serie_subserie = SerieSubserieReporteSerializer
    def get(self, request, uni):
        instance2 = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=uni)

        permisos = UnidadesExternasPermisosGetView()
        denegacion = DenegacionPermisosGetView()
        data=[]
        for x in instance2:
            
            response = permisos.get( request, x.id_cat_serie_und)
            response_permisos = denegacion.get( request, x.id_cat_serie_und)
            data.append({
                'catalogo':self.serializer_serie_subserie(x.id_catalogo_serie,many=False).data,
                'permisos':response.data['data'],
                'denegacion':response_permisos.data['data']
                })
        return Response({'succes': True, 'detail':'Resultados encontrados', 'data':data}, status=status.HTTP_200_OK)